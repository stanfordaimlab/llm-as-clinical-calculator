# %% Imports
from ast import dump
from enum import Enum
from re import sub
import time
from weakref import ref
from groq import BaseModel
from langsmith import evaluate, Client
from langsmith.schemas import Example, Run
from numpy import number
from sympy import EulerGamma
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
import os
from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic

filename = path_join(
    config.RESULTS_DATA_PATH, "annotation", f"all_error_class_runs_master.pkl"
)
annotation_df: pd.DataFrame = pd.read_pickle(filename)

exclude_already_guessed = True
list_of_run_ids_to_be_annotated = []
if exclude_already_guessed:
    print("WARNING: Excluding already guessed runs.")
    missing_guess = annotation_df["eca_guess_error_class_one"] == ""
    # or annotation_df["eca_guess_error_class_two"] == "" \
    # or annotation_df["eca_guess_explanation"] == "" or annotation_df["eca_guess_error_class_one"].isnull() or \
    #     annotation_df["eca_guess_error_class_two"].isna() or annotation_df["eca_guess_explanation"].isna()
    list_of_run_ids_to_be_annotated = annotation_df[missing_guess].id.to_list()
else:
    print("NOT excluding already guessed runs.")
    list_of_run_ids_to_be_annotated = annotation_df.id.to_list()

print(f"Number of runs to be annotated: {len(list_of_run_ids_to_be_annotated)}")

from langsmith.evaluation import evaluate_existing

if os.getenv("ANTHROPIC_API_KEY"):
    print("Anthropic API key found.")
else:
    print("No Anthropic API key found.")

## %% Classes for LLMJudge


class ErrorClass(Enum):
    # interpretation_error', 'calculation_error', 'incorrect_formula', 'assignment_error', 'incorrect_criteria', 'i_cannot_tell', 'software_error/other', 'incorrect_reportinginterpretation_error', 'calculation_error', 'incorrect_formula', 'assignment_error', 'incorrect_criteria', 'i_cannot_tell', 'software_error_other', 'incorrect_reporting
    # "Interpretation Error", "Calculation Error", "Incorrect Formula", "Assignment Error", "Incorrect Criteria", "I cannot tell", "Software Error/Other", "Incorrect Reporting"]
    interpretation_error = "Interpretation Error"
    calculation_error = "Calculation Error"
    incorrect_formula = "Incorrect Formula"
    assignment_error = "Assignment Error"
    incorrect_criteria = "Incorrect Criteria"
    i_cannot_tell = "I cannot tell"
    software_error_other = "Software Error/Other"
    incorrect_reporting = "Incorrect Reporting"
    no_error = "No Error"


class Response(BaseModel):
    error_class_one: ErrorClass = Field(
        description="Best guess at which is the primary error"
    )
    error_class_two: ErrorClass = Field(
        description="Best guess at which is the secondary error"
    )
    explanation: str = Field(
        description="Rationale for why these two errors were chosen"
    )


class LLMJudge:
    # Initialize Anthropic client
    # noinspection PyArgumentList
    def __init__(self):
        self.llm = ChatAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model_name="claude-3-5-sonnet-20241022",
            temperature=0.1,
            timeout=300,
            stop=None,
        )

    def invoke(self, prompt) -> Response:
        # return Response(error_class_one=ErrorClass.interpretation_error, error_class_two=ErrorClass.no_error, explanation="Testing") #type: ignore
        return self.llm.invoke(prompt)  # type: ignore


llm_judge = LLMJudge()


## %% Create main find_error function


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

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━ make tool call prompt ━━━━━━━━━━━━━━━━━━━━━━━━━━ #
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
    # ━━━━━━━━━━━━━━━━━━━━━━ make reference material prompt ━━━━━━━━━━━━━━━━━━━━━━ #
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

    # get reference material from data/build_database/reference_material/md/{calculator_slug}.md
    calculator_reference_material_md = ""
    try:
        with open(
            f"{config.DATABASE_BUILD_DIR}/reference_material/md/{calculator_slug.value}.md",
            "r",
        ) as f:
            calculator_reference_material_md = f.read()
    except FileNotFoundError as e:
        print(f"Reference material not found for {calculator_slug.value}.")
        util.var_dump(e)
        calculator_reference_material_md = "No reference material found."
    calculator_reference_material = f"""
----------------- REFERENCE MATERIAL -------------------    
{calculator_reference_material_md}
    """

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

We are conducting a research project to evaluate the ability of AI to perform clinical calculations; we need your assistance in identifying the errors in the AI's steps. Please respond with your best estimate for the cause of the AI's error. 

You will then classify that error into one of the following categories:
    - Interpretation Error: Inadequate understanding or misinterpretation of the medical information presented in the question leads to 1) ignored criteria that was met, or 2) inclusion of a criteria that was not met.
    - Incorrect Criteria: Criteria are missing or there is a hallucination of non-existent criteria.
    - Assignment Error: Improper application of correctly-identified criteria. Appropriate criteria were selected but an incorrect score is assigned.
    - Incorrect Formula: An incorrect equation is chosen to represent the scoring mechanism of the calculation task.
    - Calculation Error: The correct formula is chosen, such as taking the sum of all subscores, but the actual mathematical computation carried out was incorrect.
    - Incorrect Reporting: The correct score is calculated, but some component of reporting that score to the user is inaccurate.
    - I cannot tell: The error is not classifiable into any of the above categories.
    - Software Error/Other: The error is due to a software bug or some other reason not covered by the above categories. This category does not include errors arising from improper tool use (e.g., invalid inputs to a calculator or code interpreter syntax errors).
    - No error: None
    
You will provide the class of the first error in error_class_one. If there is a second error, you will provide the class of the second error in error_class_two. You will also provide an explanation for why you chose the answers you chose.

Depending on the calculation task and tools available, you may be provided with a list of intermediate steps that the AI took to arrive at its answer, as well as reference material concerning the calculation task at hand.

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
    # add tool prompt if there was a tool call
    total_prompt = error_classification_prompt_template
    if number_of_tool_calls > 0:
        total_prompt += tool_use_prompt

    # add reference material if there is any
    if calculator_reference_material_md != "No reference material found.":
        total_prompt += calculator_reference_material

    llm_judge_response: Response = llm_judge.invoke(total_prompt)

    # print(f"""
    #     ────────────────────────────── PROMPT TO ERROR-FINDING ASSISTANT ────────────────────────────────────
    #     {total_prompt}
    #     ────────────────────────────── RESPONSE FROM ERROR-FINDING ASSISTANT ────────────────────────────────────
    #     {llm_judge_response}
    # """)

    score_one = 0 if llm_judge_response.error_class_one is ErrorClass.no_error else 1
    score_two = 0 if llm_judge_response.error_class_two is ErrorClass.no_error else 1

    return {
        "results": [
            # Provide the key, score and other relevant information for each metric
            {
                "key": "eca_guess_error_class_one",
                "score": score_one,
                "comment": llm_judge_response.error_class_one.value,
            },
            {
                "key": "eca_guess_error_class_two",
                "score": score_two,
                "comment": llm_judge_response.error_class_two.value,
            },
            {
                "key": "eca_guess_explanation",
                "score": 1,
                "comment": llm_judge_response.explanation,
            },
        ]
    }


# %% Outer find_error function


def error_classification_assistant(run: Run, example: Example):

    # print(f"Checking run {run.id} for annotation.")
    if run.id not in list_of_run_ids_to_be_annotated:
        return {
            "results": [
                # Provide the key, score and other relevant information for each metric
                {
                    "key": "eca_guess_error_class_one",
                    "score": 0,
                    "comment": "Skipping - not in list of runs to be annotated.",
                },
                {
                    "key": "eca_guess_error_class_two",
                    "score": 0,
                    "comment": "Skipping - not in list of runs to be annotated.",
                },
                {
                    "key": "eca_guess_explanation",
                    "score": 0,
                    "comment": "Skipping - not in list of runs to be annotated.",
                },
            ]
        }
    else:
        print(f"Found run {run.id} in list of runs to be annotated.")

    error_classification_results = find_error(run, example)
    return error_classification_results


# %% Run the evaluation

# for testing: chosen_datasets = [ "giant-steak" ]
#  everything except "proud-yam" and "goofy-tower"
# chosen_datasets = [
#     "loud-company",
#     "sedate-bidding",
#     "puny-gasket",
#     "crazy-textbook",
#     "quarrelsome-pinkie",
#     "disagreeable-apple",
#     "confused-intent",
#     "yielding-gearshift",
#     "hissing-boatload",
#     "proud-yam",
#     "productive-independent",
#     "overt-reclamation",
#     "melted-cage",
#     "efficacious-romaine",
#     "successful-angina",
#     "known-increase",
#     "pastoral-constitution",
# ]

# first run
# chosen_datasets = [ "proud-yam" ]

# second run
# chosen_datasets = ["goofy-tower"]

# third run
chosen_datasets = [
    "proud-yam",
    "goofy-tower",
    "loud-company",
    "sedate-bidding",
    "puny-gasket",
    "crazy-textbook",
    "quarrelsome-pinkie",
    "disagreeable-apple",
    "confused-intent",
    "yielding-gearshift",
    "hissing-boatload",
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

# %%
