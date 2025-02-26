import copy
import datetime
import json
import random

from sympy.plotting.textplot import is_valid

from llm_calc.lib.handler import LLMHandler

from distlib.markers import evaluator
from duckdb import description as duckdb_description
from tornado.process import task_id
import asyncio
from typing import List, Tuple

from transformers.models.align.modeling_align import correct_pad

from globals import *
from llm_calc.lib import vignette
from llm_calc.lib.datamodel import *
from llm_calc.lib.handler import LLMResult
from llm_calc.util import util
from llm_calc.lib.config import config
import pandas as pd
import os
import urllib3
import duckdb
import yaml
from InquirerPy import inquirer, get_style
from llm_calc.lib.datacore import datacore

# langsmith
from langsmith import Client as LangsmithClient, RunTree
from langchain.smith import RunEvalConfig, run_on_dataset, arun_on_dataset
from langsmith.schemas import Example, Run
from langsmith.evaluation import evaluate as ls_evaluate
from langsmith.evaluation import LangChainStringEvaluator

# debug
from IPython import embed as ipython_embed

from llm_calc.util.util import is_valid_json

ls_client = LangsmithClient()
from llm_calc.app import display


def new_experiment(
    disable_git_warn: bool = False,
    number_of_cases: int = 0,
    description: str = None,
    include_only_one_arm: ArmSlug = None,
    use_last_dataset: bool = False,  # if True, will use the last dataset instead of creating a new one
    **kwargs,
):
    import asyncio
    import subprocess

    """
    Create a new experiment
    :return:
    """
    util.log_task("Creating a new experiment")
    display.log(b"Creating a new experiment")

    slug = util.gen_two_word_slug()
    util.log_mini_task(f"Experiment will be known by slug: {slug}")

    from InquirerPy import get_style

    style = get_style(
        {"message": "gray", "answer": "italic", "answered_question": "gray"}
    )

    if not description:
        description = inquirer.text(
            message="Description: ",
            instruction="Enter a description for the experiment: ___",
            transformer=lambda x: f"{x}",
            amark=" " * 15,
            qmark=" " * 15,
            style=style,
        ).execute()

    if not number_of_cases:
        number_of_cases = inquirer.text(
            message="Number of cases per calculator: ___",
            transformer=lambda x: f"{x}",
            amark=" " * 15,
            qmark=" " * 15,
            style=style,
        ).execute()

    if not disable_git_warn:
        # check if git status is clean
        git_status = (
            subprocess.check_output(["git", "status", "--porcelain"])
            .strip()
            .decode("utf-8")
        )
        if git_status:
            util.log_error(
                "Git status is not clean. Please commit your "
                "changes before starting an experiment.",
                will_exit=True,
            )
            return None

    # get the most recent git hash
    git_hash = (
        subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8")
    )
    util.log_mini_task(f"Git hash before starting the experiment: {git_hash}")

    if use_last_dataset:
        # TODO: Implement logic to skip case generation
        util.log_task(
            "Using last dataset -- ignore the following lines about case generation"
        )
    if not use_last_dataset:
        # generate cases
        clear_cases = vignette.clear_cases()
        if not clear_cases:
            util.log_error("Error clearing cases. Please check the logs.")
            return

        # generate cases
        cases = vignette.gen_all_cases(number_of_cases)
        saved = vignette.save_cases(cases, config.CASE_LOCAL_PATH, slug)
        if not saved:
            util.log_error("Error saving cases. Please check the logs.")
            return

    cases = vignette.load_cases(config.CASE_LOCAL_PATH)

    if not cases:
        util.log_error(
            "No cases found for this experiment. Please generate cases first."
        )
        return

    experiment = Experiment(
        slug=slug,
        description=description,
        git_hash_before_start=git_hash,
        start_datetime=None,
        end_datetime=None,
        is_completed=False,
        number_of_cases=number_of_cases,
        cases=cases,
    )

    datacore.add_experiment(copy.copy(experiment))

    util.log_success(f"Experiment {slug} created successfully :sparkles:")

    proceed = util.confirm("Do you want to run the experiment now?")
    if proceed:
        results = run_experiment(experiment, include_only_one_arm, use_last_dataset)
        return results
    else:
        util.log_task("Experiment created but not run")
        quit()


def list_experiments():
    from rich.table import Table

    experiments = datacore.get_experiments()
    if not experiments:
        util.log_error("No experiments found")
        return
    else:
        df = pd.DataFrame(experiments)
        util.tab(df, tbformat="pipe")


def clear_experiments():
    from rich.table import Table

    cleared = datacore.clear_experiments()
    if not cleared:
        util.log_error("Error clearing experiments. Please check the logs.")
        return False
    else:
        util.log_success("Experiments cleared successfully")
        return True


def load_and_run_experiment(slug: str):
    """
    Load and run an experiment
    :param slug: str: The slug of the experiment
    :return:
    """
    experiment = datacore.get_experiment_by_slug(slug)
    if not experiment:
        util.log_error(f"Experiment {slug} not found")
        return

    util.log_task(f"Running experiment {slug}")
    run_experiment(experiment)


def run_experiment(
    experiment: Experiment,
    include_only_one_arm: ArmSlug = None,
    use_last_dataset: bool = False,
):
    """
    Run an experiment
    :return:
    """
    import datetime

    experiment.start_datetime = util.get_timestamp()
    util.log_mini_task(f"Starting experiment {experiment.slug}...")
    util.h1(f"Experiment Overview: {experiment.slug}")

    cases = experiment.cases

    dataset_name = experiment.slug
    arms = datacore.arms
    bullet_list_of_arms = "\n\t   ".join([f"  - {arm.slug}" for arm in arms])
    experiment_block = f"""
    Experiment: {experiment.slug}
    Description: {experiment.description}
    Start datetime: {experiment.start_datetime}
    Number of cases: {len(cases)}
    Number of arms:  {len(arms)}
    Dataset name: {dataset_name}
    Arms: 
    {bullet_list_of_arms}
    """

    util.rprint(experiment_block)

    queue: List[RequestTask] = []
    queue_by_arm = {arm_slug.name: [] for arm_slug in [arm.slug for arm in arms]}

    # run each case in each arm
    # being arm
    for arm in arms:
        new_tasks = generate_arm_req_tasks(arm, cases)
        queue_by_arm[arm.slug.name] = new_tasks
        queue.extend(new_tasks)

    util.log_success(f"Experiement successfully prepared")

    util.h1(f"Experiment: {experiment.slug} - Running Tasks")

    util.log_warning(
        "Experiments here do not map perfectly to the LangSmith API; in langsmith, "
        "experiements are per arm, with the slug being the experiment name combined with the arm name"
    )
    util.log_task(f"Queued {len(queue)} tasks across {len(arms)} arms")

    observer = Observer()

    if use_last_dataset:
        # todo this is expensive
        util.log_task("Using last dataset -- getting slug")
        datasets = make_df(ls_client.list_datasets())
        last_dataset_name = datasets.iloc[0]["name"]
        dataset_name = last_dataset_name

    observer.register(experiment, cases, dataset_name)

    # llm = config.DEFAULT_LLM
    llm = datacore.get_model_by_slug(ModelSlug.gpt4o).get_llm()

    # arms requiring sleep afterwards are those that use llama
    arms_requiring_sleep = [
        ArmSlug.llama_base,
        ArmSlug.llama_rag,
        ArmSlug.llama_ci,
        ArmSlug.llama_rag_ci,
        ArmSlug.llama_omc,
    ]

    if include_only_one_arm:
        run_arm_function_by_arm_slug = {
            ArmSlug.gpt4_base: run_base_arm,
            ArmSlug.gpt4_rag: run_rag_arm,
            ArmSlug.gpt4_ci: run_code_interpreter_arm,
            ArmSlug.gpt4_rag_ci: run_code_interpreter_rag_arm,
            ArmSlug.gpt4_omc: run_omc,
            ArmSlug.llama_base: run_base_arm,
            ArmSlug.llama_rag: run_rag_arm,
            ArmSlug.llama_ci: run_code_interpreter_arm,
            ArmSlug.llama_rag_ci: run_code_interpreter_rag_arm,
            ArmSlug.llama_omc: run_omc,
        }

        arm_config = {"experiment": experiment, "observer": observer}

        arm = datacore.get_arm_by_slug(include_only_one_arm)
        # case switch for arm
        run_arm_function_by_arm_slug[include_only_one_arm](arm.slug, arm_config)

    # ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ run all arms ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

    if not include_only_one_arm:

        run_arm_function_by_arm_slug = {
            ArmSlug.gpt4_base: run_base_arm,
            ArmSlug.gpt4_rag: run_rag_arm,
            ArmSlug.gpt4_ci: run_code_interpreter_arm,
            ArmSlug.gpt4_rag_ci: run_code_interpreter_rag_arm,
            ArmSlug.gpt4_omc: run_omc,
            ArmSlug.llama_base: run_base_arm,
            ArmSlug.llama_rag: run_rag_arm,
            ArmSlug.llama_ci: run_code_interpreter_arm,
            ArmSlug.llama_rag_ci: run_code_interpreter_rag_arm,
            ArmSlug.llama_omc: run_omc,
        }

        arm_config = {"experiment": experiment, "observer": observer}

        # limit arms to last two
        # arms = arms[-1:]

        # run all arms
        selected_arms = [
            datacore.get_arm_by_slug(arm_slug)
            for arm_slug in config.DEFAULT_SELECTED_ARM_SLUGS
        ]
        for arm in selected_arms:
            run_arm_function_by_arm_slug[arm.slug](arm.slug, arm_config)

            # sleep after running arms that require it
            if arm.slug in arms_requiring_sleep:
                util.log_success(
                    f"Sleeping for {config.BETWEEN_ARM_WAIT_TIME} seconds before running "
                    f"the next arm"
                )
                util.wait(config.BETWEEN_ARM_WAIT_TIME)
            else:
                util.log_success(f"No sleep required after running arm {arm.slug}")

    # ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ end experiment ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

    experiment.end_datetime = util.get_timestamp()
    util.log_mini_task(f"Experiment ended at {experiment.end_datetime}")
    experiment.is_completed = True

    util.log_success(f"Experiment {experiment.slug} completed successfully :sparkles:")

    create_annotation_pipeline(dataset_name)

    return experiment


def generate_arm_req_tasks(arm: Arm, cases: List[Case]):
    """
    Start an arm
    :return: request_tasks: List[RequestTask]
    """
    request_tasks: List[RequestTask] = []

    for case in cases:
        new_task = RequestTask(
            slug=util.generate_random_string(),
            case=case,
            arm=arm,
            model=datacore.get_model_by_slug(arm.model),
            llm_result=None,
        )
        request_tasks.append(new_task)

    util.log_mini_task(f"Generated tasks for {arm.slug}")
    return request_tasks


# Annotation
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░


def make_df(matrix):
    df = pd.DataFrame(matrix)
    final = df
    try:
        cols = [i[0] for i in df.iloc[0]]
        df.columns = cols
        final = df.map(lambda x: x[1])
    except Exception as e:
        util.log_error(f"Error creating dataframe: {str(e)}")
    return final


def create_annotation_pipeline(dataset_name: str):
    """
    Create an annotation pipeline for the dataset
    :param dataset_name: str: The name of the dataset
    :return:
    """
    util.log_task("Creating annotation pipeline")
    try:
        datasets = make_df(ls_client.list_datasets())
        dataset_queues = pd.DataFrame(
            ls_client.list_annotation_queues(name=dataset_name)
        )

        if len(dataset_queues) > 0:
            dataset_queues_df = make_df(dataset_queues)
            queue = dataset_queues_df.iloc[0]
            queue_id = queue["id"]
            queue_name = queue["name"]
            q_url = f"https://smith.langchain.com/o/80231dbb-1e31-4379-b804-df697b777bc6/annotation-queues/{str(queue_id)}?peekedRun="
            util.log_mini_task(f"Queue already exsists: {queue_name} located at: ")
            print(q_url)
        else:
            # make annotation queue
            queue = ls_client.create_annotation_queue(
                name=dataset_name, description=f"annotation queue for {dataset_name}"
            )
            queue_id = queue.id
            queue_name = queue.name
            q_url = f"https://smith.langchain.com/o/80231dbb-1e31-4379-b804-df697b777bc6/annotation-queues/{str(queue_id)}?peekedRun="
            util.log_mini_task(f"Created queue: {queue_name} located at:")
            print(q_url)
        util.log_mini_task("Will move any error/incorrect questions to it now")
        # Load the dataset
        dataset = ls_client.read_dataset(dataset_name=dataset_name)
        dataset_id = dataset.id
        last_experiments = make_df(
            ls_client.list_projects(reference_dataset_id=dataset_id)
        )
        exp_runs = pd.DataFrame()
        for i, experiment in last_experiments.iterrows():
            # print(experiment)
            bar = make_df(ls_client.list_runs(is_root=True, project_id=experiment.id))
            exp_runs = pd.concat([exp_runs, bar])
        feedback_stats = pd.json_normalize(exp_runs.feedback_stats)
        exp_runs = pd.concat([exp_runs, feedback_stats.reindex(exp_runs.index)], axis=1)

        # incorrect or errored runs
        incorrect_runs = exp_runs[exp_runs["% correct (all).avg"] == 0]
        if len(incorrect_runs) > 0:
            # add runs to annotation queue
            ls_client.add_runs_to_annotation_queue(
                queue_id=queue_id, run_ids=incorrect_runs.id
            )
            util.log_mini_task(
                f"Added {len(incorrect_runs)} runs to queue {queue_name}"
            )
        else:
            util.log_mini_task(f"No incorrect runs found for {dataset_name}")
    except Exception as e:
        util.log_error(f"Error creating annotation pipeline: {str(e)}")
        return


# Arm Runners
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░


def run_base_arm(arm_slug: ArmSlug, arm_config: dict):
    experiment, observer = arm_config["experiment"], arm_config["observer"]
    from llm_calc.tools.code_interpreter import CodeInterpreterTool

    llm = datacore.get_llm_by_arm_slug(arm_slug)
    util.h2(f"Launching base agent - Using model: {llm.name}")
    from llm_calc.agents.base_agent import BaseAgent

    # b = BaseAgent(llm)
    # chain_execution_func = b.execute
    # handler = LLMHandler(chain_execution_func)

    ci = CodeInterpreterTool()
    ci.initialize_with_llm(llm)
    ci.initialize_base_tool()
    chain_execution_func = ci.execute_with_base
    handler = LLMHandler(chain_execution_func, experiment, arm_slug)

    observer.evaluate(handler.execute, experiment, arm_slug)
    ci.close_all()


def run_rag_arm(arm_slug: ArmSlug, arm_config: dict):
    experiment, observer = arm_config["experiment"], arm_config["observer"]
    llm = datacore.get_llm_by_arm_slug(arm_slug)
    util.h2(f"Launching RAG agent - Using model: {llm.name}")
    from llm_calc.tools.code_interpreter import CodeInterpreterTool

    ci = CodeInterpreterTool()
    ci.initialize_with_llm(llm)
    ci.initialize_rag_tool()
    chain_execution_func = ci.execute_with_rag_only
    handler = LLMHandler(chain_execution_func, experiment, arm_slug)

    observer.evaluate(handler.execute, experiment, arm_slug)
    ci.close_all()


def run_code_interpreter_arm(arm_slug: ArmSlug, arm_config: dict):
    experiment, observer = arm_config["experiment"], arm_config["observer"]
    llm = datacore.get_llm_by_arm_slug(arm_slug)
    util.h2(f"Launching Code Interpreter agent - Using model: {llm.name}")
    from llm_calc.tools.code_interpreter import CodeInterpreterTool

    ci = CodeInterpreterTool()
    ci.initialize_code_interpreter()
    ci.initialize_with_llm(llm)
    chain_execution_func = ci.execute
    handler = LLMHandler(chain_execution_func, experiment, arm_slug)

    observer.evaluate(handler.execute, experiment, arm_slug)
    ci.close_all()


def run_code_interpreter_rag_arm(arm_slug: ArmSlug, arm_config: dict):
    experiment, observer = arm_config["experiment"], arm_config["observer"]
    llm = datacore.get_llm_by_arm_slug(arm_slug)
    util.h2(f"Launching Code Interpreter + RAG agent - Using model: {llm.name}")
    from llm_calc.tools.code_interpreter import CodeInterpreterTool

    ci = CodeInterpreterTool()
    ci.initialize_code_interpreter()
    ci.initialize_with_llm(llm)
    ci.initialize_rag_tool()
    chain_execution_func = ci.execute_with_rag_and_ci
    handler = LLMHandler(chain_execution_func, experiment, arm_slug)
    observer.evaluate(handler.execute, experiment, arm_slug)
    ci.close_all()


def run_omc(arm_slug: ArmSlug, arm_config: dict):
    experiment, observer = arm_config["experiment"], arm_config["observer"]
    llm = datacore.get_llm_by_arm_slug(arm_slug)
    util.h2(f"Launching OpenMedCalc agent - Using model: {llm.name}")
    from llm_calc.tools.code_interpreter import CodeInterpreterTool

    ci = CodeInterpreterTool()
    ci.initialize_with_llm(llm)
    ci.initialize_omc_tool()

    chain_execution_func = ci.execute_with_omc
    handler = LLMHandler(chain_execution_func, experiment, arm_slug)
    observer.evaluate(handler.execute, experiment, arm_slug)
    ci.close_all()
    # omc = OpenMedCalcTool()
    # omc.set_llm(llm)
    # omc.ingest_api()
    # chain_execution_func = omc.execute
    # handler = LLMHandler(chain_execution_func, arm_slug)
    # observer.evaluate(handler.execute, experiment, arm_slug)


# Evaluators
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

# Define evaluators


def flatten_run_tree(root_run):
    flat_list = []

    def recursive_flatten(run):
        # Add current run's information to the flat list
        flat_list.append((run.name, run.run_type))

        # Recursively process child runs
        for child_run in run.child_runs:
            recursive_flatten(child_run)

    # Start the recursion with the root run
    recursive_flatten(root_run)

    return flat_list


def did_run_tool(root_run: Run, example: Example, expected_tool_call=None) -> dict:
    """
    Check if certain tool was run
    NOTE: RAG is not classified as a tool and is run during prompt generation automatically; so
    it is not included in this function.
    """
    flat_run_tree = flatten_run_tree(root_run)

    key = f"{expected_tool_call} was run"

    # find whether first in tuple for each element in flat_run_tree is the expected tool call
    for run in flat_run_tree:
        if run[0] == expected_tool_call:
            return {"score": 100, "key": key}

    return {"score": None, "key": key}


def did_run_ci(run: Run, example: Example) -> dict:
    """
    Check if the code interpreter tool was run
    """
    return did_run_tool(run, example, "code_interpreter")


def did_run_omc(run: Run, example: Example) -> dict:
    """
    Check if the open med calc tool was run
    """
    output = 0
    total_score = 0

    # get names of all the OMC tools from omc toolkit
    from llm_calc.tools.openmedcalc.calculators_as_tools import omc_toolkit_all

    # omc toolkit is technically a list of functions, so we need to get the names of the functions
    omc_tool_names = [tool.name for tool in omc_toolkit_all]

    # check for each individual tool calculate_meld_na calculate_wells_dvt calculate_caprini_vte
    for tool_name in omc_tool_names:
        score = did_run_tool(run, example, tool_name)["score"]
        total_score += score

    if total_score > 0:
        output = 100

    return {"score": output, "key": "OMC_run"}


def did_run_omc_verbose(run: Run, example: Example) -> dict:
    """
    Check if the open med calc tool was run
    """
    output = None
    total_score = 0
    ran_tool_name = ""

    # get names of all the OMC tools from omc toolkit
    from llm_calc.tools.openmedcalc.calculators_as_tools import omc_toolkit_all

    # omc toolkit is technically a list of functions, so we need to get the names of the functions
    omc_tool_names = [tool.name for tool in omc_toolkit_all]

    # check for each individual tool calculate_meld_na calculate_wells_dvt calculate_caprini_vte
    for tool_name in omc_tool_names:
        score = did_run_tool(run, example, tool_name)["score"]
        if score > 0:
            ran_tool_name = tool_name
        total_score += score

    if total_score > 0:
        output = 100

    return {"score": output, "key": f"{ran_tool_name} was run"}


def grade_any_answer(run: Run, example: Example) -> dict:
    """
    This function compares the extracted answer from the run to the correct answer in the example.
    It will assign a grade of zero if the extracted answer is in the incorrect format
    :param run:
    :param example:
    :return: dict with score
    """
    run_id = str(run.id)
    try:
        llm_result: LLMResult = run.outputs.get("details")
        json_answer = llm_result.output_string
        output = util.coerce_json_decode(json_answer)
        extracted_answer = output["answer"]
        correct_answer = example.outputs.get("ex_output_answer")
        correct = int(extracted_answer) == (correct_answer)
        score = 100 if correct else 0
        return {"score": score, "key": "% correct (all)"}
    except:
        util.log(f"Warning: Grade any answer failed for run {run_id}")
        return {"score": 0, "key": "% correct (all)"}


def grade_complete_answer(run: Run, example: Example) -> dict:
    """
    This function compares the extracted answer from the run to the correct answer in the example.
    It will error if the extracted answer is in the incorrect format and be blank
    :param run:
    :param example:
    :return: dict with score
    """

    run_id = str(run.id)
    try:
        llm_result: LLMResult = run.outputs.get("details")
        json_answer = llm_result.output_string
        output = util.coerce_json_decode(json_answer)
        extracted_answer = output["answer"]
        correct_answer = example.outputs.get("ex_output_answer")
        correct = int(extracted_answer) == (correct_answer)
        score = 100 if correct else 0
        return {"score": score, "key": "% correct (complete)"}
    except:
        util.log(f"Warning: Grade complete answer failed for run {run_id}")
        pass


def runtime_error_count(run: Run, example: Example) -> dict:
    """
    This function compares the extracted answer from the run to the correct answer in the example
    :param run:
    :param example:
    :return: dict with score
    """
    run_id = str(run.id)

    try:
        llm_result: LLMResult = run.outputs.get("details")
        num_error_attempts = int(llm_result.num_errored_attempts)
        return {"score": num_error_attempts}
    except Exception as e:
        util.log_warning(
            f"Cannot count runtime errors for run {run_id} (generally due to an "
            f"error within LLMHandler, prior to LLMHandler, or within "
            f"runtime_error_count. "
            f"Setting to 100%. Exception: {str(e)}"
        )
        num_error_attempts = 5
        return {"score": num_error_attempts}
        pass


def final_answer_valid(run: Run, example: Example) -> dict:
    """
    This function checks if the coerced json string is valid
    :param run:
    :param example:
    :return: dict with score
    """
    # from langchain.evaluation import JsonValidityEvaluator

    # from IPython import embed as ipython_embed
    # ipython_embed()

    results = run.outputs.get("details")
    llm_result: LLMResult = LLMResult().from_dict(results)
    score = 0
    try:
        answer = llm_result.output_object["answer"]
        # if answer is integer or float, return 1
        if isinstance(answer, (int, float)):
            return {"score": 100, "key": "Final answer valid"}
    except Exception as e:
        util.log_error(f"Final answer valid failed: {str(e)}")
        return {"score": 0, "key": "Final answer valid"}


# Observer
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# this class manages uploading the dataset to langsmith, running the experiment,
# and coordinating the evaluation of the experiment


class Observer:
    def __init__(self):
        self._observers = []

    def register(self, experiment, cases, dataset_name):

        # check if dataset exists
        already_uploaded = ls_client.has_dataset(dataset_name=dataset_name)
        if already_uploaded:
            self._dataset = ls_client.read_dataset(dataset_name=dataset_name)
            util.log_task("Dataset already uploaded to LangSmith")
            return

        # convert tasks to a dataframe
        # tdf = pd.DataFrame([task.__dict__ for task in tasks])

        # expand cases into columns
        # cdf = pd.DataFrame(tdf.case.to_list())

        # cdf["case_repr"] = cdf.apply(lambda x: x.to_dict(), axis=1)
        # from IPython import embed as ipython_embed
        # ipython_embed()
        df = pd.DataFrame([case for case in cases])
        # for each case, add a field with the representation of the case
        df["case"] = df.apply(lambda x: x.to_dict(), axis=1)
        df["case_json"] = df.case.apply(lambda x: json.dumps(x))
        # changed to just options for now
        df["case_options"] = df.apply(lambda x: x.to_dict()["options"], axis=1)
        df["case_options_text"] = df.case_options.apply(
            lambda x: ",".join([str(op) for op in x])
        )

        df["additional_case_details_answer"] = df["correct_output"]
        df["additional_case_details_options"] = df["case_options_text"]
        df["additional_case_details_all_case_details"] = df["case"]
        df["additional_case_details_all_case_details_json"] = df["case_json"]

        description = experiment.description
        # dataset = ls_client.create_dataset(dataset_name, description=description)
        # ls_client.create_examples(
        #     inputs=[{"vignette": row["vignette"]} for index, row in df.iterrows()],
        #     outputs=[{"ex_output_answer" : row["correct_output"]} for index, row in df.iterrows()],
        #     dataset_id=dataset.id,
        # )

        # add output keys

        df["ex_output_answer"] = df["correct_output"]

        df["human_input"] = df["vignette"]
        # dataset_name = "AnesthesiaQA_v_0.2"
        dataset_name = dataset_name
        # dataset_name = "prompt-engineering-multiQA"

        input_keys = [
            "human_input",
            "additional_case_details_options",
            "additional_case_details_answer",
            "additional_case_details_all_case_details",
            "additional_case_details_all_case_details_json",
        ]
        output_keys = ["ex_output_answer"]

        # dataset = self._client.create_dataset(dataset_name, description=description)
        from langsmith import schemas as ls_schemas

        dataset = ls_client.upload_dataframe(
            df=df,
            input_keys=input_keys,
            output_keys=output_keys,
            name=dataset_name,
            description=description,
            data_type=ls_schemas.DataType.kv,
        )

        url = dataset.url
        id = dataset.id

        self._dataset = dataset

        if dataset:
            util.log_task(f"Dataset uploaded to LangSmith; opening in browser: {url}")
            util.tprint(df.head(5))

        import webbrowser

        # webbrowser.open(url)

    def run_on_dataset(self, chain, experiment):
        print("error here")
        return None

    def evaluate(self, chain_function, experiment, arm_slug: ArmSlug):
        from langsmith.evaluation import evaluate

        arm = datacore.get_arm_by_slug(arm_slug)

        experiment_name = arm_slug.name + "___on_dataset_" + experiment.slug + "_"
        evaluators = [
            grade_any_answer,
            grade_complete_answer,
            final_answer_valid,
            runtime_error_count,
            did_run_ci,
            did_run_omc,
            did_run_omc_verbose,
        ]

        llama_slugs = [
            ArmSlug.llama_base,
            ArmSlug.llama_rag,
            ArmSlug.llama_ci,
            ArmSlug.llama_rag_ci,
            ArmSlug.llama_omc,
        ]

        max_concurrency = config.MAX_CONCURRENCY_GPT4
        if arm_slug in llama_slugs:
            max_concurrency = config.MAX_CONCURRENCY_LLAMA

        run_result = evaluate(
            chain_function,
            client=ls_client,
            data=self._dataset.name,
            experiment_prefix=experiment_name,
            evaluators=evaluators,
            max_concurrency=max_concurrency,
            # evaluation=eval_config,
            # project_name=config.MAX_CONCURRENCY_GPT4,
            # Any experiment metadata can be specified here
            # metadata={"prompt-sha": 'huzah',  'model': 'bar'}
            metadata={
                "arm": arm_slug.name,
                "experiment": experiment.slug,
                "ls_model_name": arm.model.value,
                "llm": arm.model.value,
                "description": experiment.description,
                "number_of_cases": experiment.number_of_cases,
                "version": "1.0.0",
            },
        )

        if run_result:
            util.log_mini_task(f"Run on dataset began for {experiment_name}")
            util.log_mini_task(run_result)

        return run_result
