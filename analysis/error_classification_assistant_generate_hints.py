from ast import dump
from re import sub
from groq import BaseModel
from langsmith import evaluate, Client
from langsmith.schemas import Example, Run
from numpy import number
from llm_calc.lib import vignette
from llm_calc.lib.experiment import ls_client, make_df
from llm_calc.lib.config import config
from llm_calc.tools.structured_output import FinalResponse
from llm_calc.lib.datamodel import (
    Arm,
    ArmSlug,
    CalculatorSlug,
    Model,
    ModelSlug,
    CriterionOption,
    Case,
)
from llm_calc.lib.datacore import datacore
from os.path import join as path_join
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from llm_calc.util import util
from IPython import embed
import json
import openai
from anthropic import Anthropic
import os

filename = path_join(
    config.RESULTS_DATA_PATH, "annotation", f"all_error_class_runs_master.pkl"
)
annotation_df: pd.DataFrame = pd.read_pickle(filename)
list_of_run_ids_to_be_annotated = annotation_df.id.to_list()


from langsmith.evaluation import evaluate_existing

openai_client = openai.Client()


meld_breakdown = """
MELD(i) = 0.957 * ln(Cr) + 0.378 * ln(bilirubin) + 1.120 * ln(INR) + 0.643
Then, round to the tenth decimal place and multiply by 10. 
If MELD(i) > 11, perform additional MELD calculation as follows:
MELD = MELD(i) + 1.32 * (137 - Na) - [ 0.033 * MELD(i) * (137 - Na) ]
Additional rules:
- All values in US units (Cr and bilirubin in mg/dL, Na in mEq/L, and INR unitless).
- If bilirubin, Cr, or INR is <1.0, use 1.0.
- If any of the three following is true, use Cr 4.0:
    - Cr >4.0.
    - ≥2 dialysis treatments within the prior 7 days.
    - 24 hours of continuous veno-venous hemodialysis (CVVHD) within the prior 7 days.
- If Na <125 mmol/L, use 125. If Na >137 mmol/L, use 137.
- Maximum MELD = 40.
"""


def find_error(run: Run, example: Example):

    outputs = run.outputs
    final_response = FinalResponse(**outputs.get("details", {}).get("output_object"))

    # Gather LLM inputs
    intermediate_steps = outputs.get("details", {}).get("intermediate_steps")
    number_of_tool_calls = len(intermediate_steps)
    tool_use_prompt = ""
    if number_of_tool_calls > 0:
        last_tool = intermediate_steps[-1]
        last_tool_name = last_tool[0].get("tool")
        last_tool_inputs = last_tool[0].get("tool_input")
        last_tool_response = last_tool[1]
        tool_use_prompt = f"""
The AI used a total of {number_of_tool_calls} tool(s) to arrive at its answer. The last tool used had the name of "{last_tool_name}." The AI called this tool with the following inputs:
    
    > {last_tool_inputs} 

From that tool call, they received the following response: 

    > {last_tool_response}

"""

    case_obj = outputs.get("details", {}).get("case")
    case = Case(**case_obj)
    vignette = case.vignette
    calculator_slug = case.calculator_slug
    calculator_name = datacore.get_calculator_by_slug(calculator_slug).name
    correct_answer = case.correct_output
    # print(correct_answer)
    # print(case_obj, vignette, calculator_slug, calculator_name, correct_answer)

    # # Get LLM output
    given_answer = final_response.answer
    able_to_answer = final_response.able_to_answer
    given_explanation = final_response.explanation

    # score breakdown
    score_breakdown = ""
    if calculator_slug == CalculatorSlug.meldna:
        score_breakdown = meld_breakdown
    else:
        subtotal = []
        for option in case.options:
            subtotal = subtotal + [option.score_effect]
            if option.score_effect == 0:
                score_breakdown += f"   > No points for {option.name} \n"
            elif option.score_effect == 1 or option.score_effect == -1:
                score_breakdown += (
                    f"   > {option.score_effect} point for {option.name} \n"
                )
            else:
                score_breakdown += (
                    f"   > {option.score_effect} points for {option.name} \n"
                )
        subtotal_string = " + ".join([str(i) for i in subtotal])
        score_breakdown += (
            f"\n   For a total of: {subtotal_string} = {correct_answer} \n"
        )
    # print(score_breakdown)
    old = """
    If you find multiple errors, please list them in order of importance, for example, "1. No points were added for the patients' age (should have scored 2 points). 2. Excessive points were added for diabetes (2 instead of 1)."
"""
    error_classification_prompt_template = f"""
------------------------- YOUR TASK ----------------------

We are conducting a research project to evaluate the ability of AI to perform clinical calculations; we need your assistance in identifying the errors in the AI's steps. Please respond with your best estimate for the cause of the AI's error. Please respond with a short summary keep your answers short and to the point, fewer than 90 words and 500 characters.  If you find multiple errors, please list them in order of importance. If you cannot find an error, just respond "No error found." 
---------------------- CASE DETAILS ----------------------

The AI was given the following clinical case: 

    > {vignette}

The correct answer was: 

    > {correct_answer}
    
The correct answer should have been calculated as follows:

{score_breakdown}


---------------------- AI RESPONSE ----------------------

The AI's answer was:

    > {given_answer}
    
The AI's explanation was: 

    > {given_explanation}

"""

    total_prompt = error_classification_prompt_template
    if number_of_tool_calls > 0:
        total_prompt += tool_use_prompt

    # Initialize Anthropic client
    anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    messages = [{"role": "user", "content": f"{total_prompt}"}]

    # Create completion with Claude
    completion = anthropic.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=messages,
        system="You are operating in Concise Mode. Provide direct, focused answers while maintaining quality and completeness. For code and artifacts, maintain full functionality.",
    )

    llm_judge_response = completion.content[0].text

    # print("\n\n────────────────────────────── PROMPT TO ERROR-FINDING ASSISTANT ────────────────────────────────────\n",
    #       total_prompt,
    #       "────────────────────────────── RESPONSE FROM ERROR-FINDING ASSISTANT ────────────────────────────────────\n",
    #       llm_judge_response)

    return {
        "results": [
            # Provide the key, score and other relevant information for each metric
            {"key": "prompt_to_ec_assistant", "score": 1, "comment": total_prompt},
            {"key": "ec_assistant_response", "score": 1, "comment": llm_judge_response},
        ]
    }


def error_classification_assistant(run: Run, example: Example):

    # inputs = run.inputs

    if run.id not in list_of_run_ids_to_be_annotated:
        return {
            "results": [
                # Provide the key, score and other relevant information for each metric
                {
                    "key": "prompt_to_ec_assistant",
                    "score": 0,
                    "comment": "Not in annotation queue.",
                },
                {
                    "key": "ec_assistant_response",
                    "score": 0,
                    "comment": "Not in annotation queue.",
                },
            ]
        }
    else:
        print(f"Found run {run.id} in list of runs to be annotated.")

    error_classification_results = find_error(run, example)
    return error_classification_results


#  everything except "proud-yam", "goofy-tower",
chosen_datasets = [
    "loud-company",
    "sedate-bidding",
    "puny-gasket",
    "crazy-textbook",
    "quarrelsome-pinkie",
    "disagreeable-apple",
    "confused-intent",
    "yielding-gearshift",
    "hissing-boatload",
    "proud-yam",
    "productive-independent",
    "overt-reclamation",
    "melted-cage",
    "efficacious-romaine",
    "successful-angina",
    "known-increase",
    "pastoral-constitution",
]


print(f"Chosen datasets: \n" + "\n".join(chosen_datasets))

exp_runs = pd.DataFrame()
all_experiments = pd.DataFrame()
for dataset_name in chosen_datasets:
    util.h2(f"Getting dataset {dataset_name}")
    dataset = ls_client.read_dataset(dataset_name=dataset_name)
    dataset_id = dataset.id
    last_experiments = make_df(ls_client.list_projects(reference_dataset_id=dataset_id))
    all_experiments = pd.concat([all_experiments, last_experiments])

experiment_names = all_experiments.name.to_list()

print(f"All experiments: {experiment_names}")
for experiment_name in experiment_names:
    util.h1(f"Getting experiment {experiment_name}")
    evaluate_existing(experiment_name, evaluators=[error_classification_assistant])
