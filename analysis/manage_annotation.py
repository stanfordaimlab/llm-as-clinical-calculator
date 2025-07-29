# %%

import numpy as np
from llm_calc.lib.experiment import ls_client, make_df
from llm_calc.lib.config import config
from llm_calc.lib.datamodel import Arm, ArmSlug, Model, ModelSlug
from llm_calc.lib.datacore import datacore
from os.path import join as path_join
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from llm_calc.util import util
import plotly.express as px

# %%

# Get original annotation DF
filename = path_join(
    config.RESULTS_DATA_PATH, "annotation", f"all_error_class_runs_original.pkl"
)
loaded_df: pd.DataFrame = pd.read_pickle(filename)

# %% ━━━━━━━━━━━━━━━━━━━━━━━━━━━ Update status of runs ━━━━━━━━━━━━━━━━━━━━━━━━━━ #

# Make a copy of the input dataframe
dfu = loaded_df.copy()

# Drop columns error_class_one, error_class_two, notes if they exist
dfu.drop(
    columns=[
        "error_class_one",
        "error_class_two",
        "notes",
        "flagged_for_review",
        "ec_assistant_response",
        "ec_feedback",
        "eca_guess_error_class_one",
        "eca_guess_error_class_two",
        "eca_guess_explanation",
    ],
    inplace=True,
    errors="ignore",
)

# Get run IDs
run_ids = dfu["id"].tolist()
print(f"Querying LangSmith for info from {len(run_ids)} runs...")
current_runs_df = make_df(ls_client.list_runs(run_ids=run_ids))
print(f"Received data re {len(current_runs_df)} runs from LangSmith")

# get the annotations for all runs in the database
error_class_one_df = make_df(
    ls_client.list_feedback(run_ids=run_ids, feedback_key=["error classification"])
)
error_class_two_df = make_df(
    ls_client.list_feedback(
        run_ids=run_ids, feedback_key=["error classification second error"]
    )
)
flag_df = make_df(
    ls_client.list_feedback(run_ids=run_ids, feedback_key=["flag for review"])
)

exemplar_df = make_df(
    ls_client.list_feedback(run_ids=run_ids, feedback_key=["exemplar"])
)


notes_df = make_df(ls_client.list_feedback(run_ids=run_ids, feedback_key=["note"]))
eca_df = make_df(
    ls_client.list_feedback(run_ids=run_ids, feedback_key=["ec_assistant_response"])
)
ec_feedback_df = make_df(
    ls_client.list_feedback(run_ids=run_ids, feedback_key=["ec_feedback"])
)

eca_guess_one_df = make_df(
    ls_client.list_feedback(run_ids=run_ids, feedback_key=["eca_guess_error_class_one"])
)

eca_guess_two_df = make_df(
    ls_client.list_feedback(run_ids=run_ids, feedback_key=["eca_guess_error_class_two"])
)

eca_guess_explanation_df = make_df(
    ls_client.list_feedback(run_ids=run_ids, feedback_key=["eca_guess_explanation"])
)

remove_df = make_df(
    ls_client.list_feedback(run_ids=run_ids, feedback_key=["remove_from_annotation"])
)

# --- get revisions which will override the original error classifications
revised_class_one_df = make_df(
    ls_client.list_feedback(run_ids=run_ids, feedback_key=["revised_error_class_one"])
)
revised_class_two_df = make_df(
    ls_client.list_feedback(run_ids=run_ids, feedback_key=["revised_error_class_two"])
)

# Report on the number of runs with each type of feedback
print(f"Found {len(error_class_one_df)} runs with error_class_one feedback")
print(f"Found {len(error_class_two_df)} runs with error_class_two feedback")
print(f"Found {len(flag_df)} runs with flagged feedback")
print(f"Found {len(notes_df)} note entries")
print(f"Found {len(eca_df)} ec_assistant_response entries")
print(f"Found {len(ec_feedback_df)} ec_feedback entries")
print(
    f"Found {len(eca_guess_one_df)} eca_guess_error_class_one (assistant attenpt at classification) entries"
)
print(f"Found {len(eca_guess_two_df)} eca_guess_error_class_two entries")
print(f"Found {len(eca_guess_explanation_df)} eca_guess_explanation entries")
print(f"Found {len(remove_df)} remove_from_annotation entries")
print(f"Found {len(revised_class_one_df)} revised_error_class_one entries")
print(f"Found {len(revised_class_two_df)} revised_error_class_two entries")

# Merge dfu with error_class_one_df to get the first error classification
dfu = dfu.merge(
    error_class_one_df[["run_id", "value"]],
    left_on="id",
    right_on="run_id",
    how="left",
    suffixes=("_x1", "_y1"),
)
dfu.rename(columns={"value": "error_class_one"}, inplace=True)
print(f"Added error_class_one to dataframe, now has {len(dfu)} rows")

# Merge dfu with error_class_two_df to get the second error classification
dfu = dfu.merge(
    error_class_two_df[["run_id", "value"]],
    left_on="id",
    right_on="run_id",
    how="left",
    suffixes=("_x2", "_y2"),
)
dfu.rename(columns={"value": "error_class_two"}, inplace=True)
print(f"Added error_class_two to dataframe, now has {len(dfu)} rows")

# drop previous merge columns
dfu.drop(columns=["run_id_x1", "run_id_y1"], inplace=True, errors="ignore")
dfu.drop(columns=["run_id_x2", "run_id_y2"], inplace=True, errors="ignore")
dfu.drop(columns=["run_id_x_eca", "run_id_y_eca"], inplace=True, errors="ignore")


# Add notes, ec_assistant_responses, and ec_feedback to the dataframe
# they required concatenation because of multiple entries
dfu["notes"] = dfu["id"].apply(
    lambda x: "\n\n".join(notes_df[notes_df["run_id"] == x]["comment"])
)
dfu["ec_assistant_responses"] = dfu["id"].apply(
    lambda x: "\n\n".join(eca_df[eca_df["run_id"] == x]["comment"])
)
dfu["ec_feedback"] = dfu["id"].apply(
    lambda x: "\n\n".join(ec_feedback_df[ec_feedback_df["run_id"] == x]["comment"])
)
dfu["eca_guess_error_class_one"] = dfu["id"].apply(
    lambda x: "\n\n".join(eca_guess_one_df[eca_guess_one_df["run_id"] == x]["comment"])
)

dfu["eca_guess_error_class_two"] = dfu["id"].apply(
    lambda x: "\n\n".join(eca_guess_two_df[eca_guess_two_df["run_id"] == x]["comment"])
)

dfu["eca_guess_explanation"] = dfu["id"].apply(
    lambda x: "\n\n".join(
        eca_guess_explanation_df[eca_guess_explanation_df["run_id"] == x]["comment"]
    )
)

dfu["flagged_for_review"] = dfu["id"].apply(
    lambda x: "\n\n".join(flag_df[flag_df["run_id"] == x]["value"])
)
dfu["exemplar"] = dfu["id"].apply(
    lambda x: "\n\n".join(exemplar_df[exemplar_df["run_id"] == x]["value"])
)

dfu["remove_from_annotation"] = dfu["id"].apply(
    lambda x: "\n\n".join(remove_df[remove_df["run_id"] == x]["value"])
)

# revisions
dfu["revised_error_class_one"] = dfu["id"].apply(
    lambda x: "\n\n".join(
        revised_class_one_df[revised_class_one_df["run_id"] == x]["value"]
    )
)
dfu["revised_error_class_two"] = dfu["id"].apply(
    lambda x: "\n\n".join(
        revised_class_two_df[revised_class_two_df["run_id"] == x]["value"]
    )
)

print(
    f"Added notes, ec_assistant_response, and ec_feedback to dataframe, now has {len(dfu)} rows"
)

# mark the runs with an error_class_one as having an annotation_status of 'annotated'
dfu.loc[dfu["error_class_one"].notnull(), "annotation_status"] = "annotated"

# create a variable to store primary error class OR pending
dfu["error_class_one_or_pending"] = dfu["error_class_one"].fillna("PENDING")

# set url
dfu["url"] = dfu.app_path.map(lambda x: "https://smith.langchain.com" + str(x))

# %%  ━━━━━━━━━━━━━━━━ have the revisions override the main data ━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

# if the revised error class one is not null, replace the error class one with the revised error class one

has_revised_error_class_one = dfu["revised_error_class_one"] != ""
dfu.loc[has_revised_error_class_one, "error_class_one"] = dfu["revised_error_class_one"]
print(f"Revised error class one for {has_revised_error_class_one.sum()} runs")

# if the revised error class two is not null, replace the error class two with the revised error class two
has_revised_error_class_two = dfu["revised_error_class_two"] != ""
dfu.loc[has_revised_error_class_two, "error_class_two"] = dfu["revised_error_class_two"]
print(f"Revised error class two for {has_revised_error_class_two.sum()} runs")

# %%  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ pre-export cleaning ━━━━━━━━━━━━━━━━━━━━━━━━━━━ #


# make the flagged_for_review column a boolean
dfu["flagged_for_review"] = dfu["flagged_for_review"].apply(lambda x: x != "")

#  flatten the 'extra' column and outputs column
dfu = pd.concat([dfu.drop(["extra"], axis=1), dfu["extra"].apply(pd.Series)], axis=1)
dfu = pd.concat(
    [dfu.drop(["metadata"], axis=1), dfu["metadata"].apply(pd.Series)], axis=1
)
dfu = pd.concat(
    [dfu.drop(["outputs"], axis=1), dfu["outputs"].apply(pd.Series)], axis=1
)
dfu = pd.concat(
    [dfu.drop(["details"], axis=1), dfu["details"].apply(pd.Series)], axis=1
)
dfu = pd.concat(
    [dfu.drop(["output_object"], axis=1), dfu["output_object"].apply(pd.Series)], axis=1
)

# case includes: 'id', 'name', 'calculator_slug', 'vignette', 'options', 'correct_output', 'correct_output_notes', 'given_output', 'is_correct'
case_df = dfu["case"].apply(pd.Series)[["name", "calculator_slug", "correct_output"]]
case_df = case_df.rename(
    {"name": "patient_name", "calculator_slug": "calculator_slug"}, axis="columns"
)
dfu = pd.concat([dfu.drop(["case"], axis=1), case_df], axis=1)

# %%  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ export ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

# export the dfu to a pkl file and csv file
filename = path_join(
    config.RESULTS_DATA_PATH, "annotation", f"all_error_class_runs_master.pkl"
)
dfu.to_pickle(filename)
print(f"{len(dfu)} rows written to {filename}")

filename = path_join(
    config.RESULTS_DATA_PATH, "annotation", f"all_error_class_runs_master.xlsx"
)
dfu.to_excel(filename)
print(f"{len(dfu)} rows written to {filename}")

df = dfu


# %%  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ flagged ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

flag_df = make_df(
    ls_client.list_feedback(run_ids=run_ids, feedback_key=["flag for review"])
)

filename = path_join(
    config.RESULTS_DATA_PATH, "annotation", f"flagged_annotations.xlsx"
)
flag_df.to_excel(filename)
print(f"{len(flag_df)} rows written to {filename}")

filename = path_join(config.RESULTS_DATA_PATH, "annotation", f"flagged_annotations.pkl")
flag_df.to_pickle(filename)
print(f"{len(flag_df)} rows written to {filename}")


# %%  ━ tag the removed runs ━ #

# there were a set of runs that had errors (timeouts, etc) that were removed
# from the results but remained in the annotation data; these need to be tagged
# to reveal any non-removed runs that errored out

# those that didn't error out are perfectly valid error classification runs

exp = df.experiment.reset_index()
exp.columns = ["id", "experiment_name", "data"]
df["experiment_name"] = exp["experiment_name"]
df.experiment_name

# productive-independent with arm llama_ci
# goofy-tower with arm llama_omc
# puny-gasket with arm llama_rag_ci
# quarrelsome-pinkie with arm gpt4_rag_ci
# proud-yam with arm gpt4_rag_ci
# productive-independent with arm llama_rag_ci
# known-increase with arm gpt4_ci

to_tag = [
    ("productive-independent", "llama_ci"),
    ("goofy-tower", "llama_omc"),
    ("puny-gasket", "llama_rag_ci"),
    ("quarrelsome-pinkie", "gpt4_rag_ci"),
    ("proud-yam", "gpt4_rag_ci"),
    ("productive-independent", "llama_rag_ci"),
    ("known-increase", "gpt4_ci"),
]

df["was_post_hoc_removed"] = False
for experiment_name, arm in to_tag:
    df.loc[
        (df.experiment_name == experiment_name) & (df.arm == arm),
        "was_post_hoc_removed",
    ] = True

df.was_post_hoc_removed.value_counts()


# %%  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ figure ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #


# Create a bar chart for annotation progress
progress = df.groupby(["assigned_to", "annotation_status"]).size().unstack().fillna(0)
fig = px.bar(
    progress.reset_index(),
    x="assigned_to",
    y=["annotated"],
    title="Annotation Progress by User",
    labels={"value": "Number of Annotations", "assigned_to": "User"},
    barmode="stack",
    width=800,
    height=500,
)
util.save_fig(fig, "annotation_progress")

# %%  ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ #
#                              SEND TO GOOGLE DOCS                             #
# ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ #

# create special version of the dataframe for export
dfe = df.copy().reset_index(drop=True)


# removed unnecessary columns
dfe = dfe[
    [
        "id",
        "name",
        "start_time",
        "run_type",
        "end_time",
        "assigned_to",
        "annotation_status",
        "index",
        "error_class_one",
        "error_class_two",
        "flagged_for_review",
        "notes",
        "url",
        "revision_id",
        "arm",
        "experiment",
        "llm",
        "description",
        "arm_slug",
        "exception",
        "exception_message",
        "exception_traceback",
        "was_answer_correct",
        "num_errored_attempts",
        "num_attempts",
        "errored_attempts",
        "intermediate_steps",
        "human_input",
        "answer",
        "able_to_answer",
        "explanation",
        "error",
        "ec_assistant_responses",
        "error_class_one_or_pending",
        "patient_name",
        "calculator_slug",
        "correct_output",
        "eca_guess_error_class_one",
        "eca_guess_error_class_two",
        "eca_guess_explanation",
        "was_post_hoc_removed",
        "remove_from_annotation",
        "exemplar",
        # 'serialized',
        # 'events',
        # 'inputs',
        # 'reference_example_id',
        # 'parent_run_id',
        # 'tags',
        # 'attachments',
        # 'session_id',
        # 'child_run_ids',
        # 'child_runs',
        # 'feedback_stats',
        # 'app_path',
        # 'manifest_id',
        # 'status',
        # 'prompt_tokens',
        # 'completion_tokens',
        # 'total_tokens',
        # 'first_token_time',
        # 'total_cost',
        # 'prompt_cost',
        # 'completion_cost',
        # 'parent_run_ids',
        # 'trace_id',
        # 'dotted_order',
        # 'in_dataset',
        # 'runtime',
        # 'ls_model_name',
        # 'number_of_cases',
        # 'version',
        # 'num_repetitions',
        # 'example_version',
        # 'ls_method',
        # 'output',
        # 'experiment',
        # 'was_error',
        # 'output_string',
        # 'output_string_is_valid_json',
        # 'output_object',
        # 'extracted_answer',
        # 'case',
        # 'raw_response',
        # 'run',
    ]
]

# rename answer to model_answer, able_to_answer to model_able_to_answer, explanation to model_explanation
dfe.rename(
    columns={
        "answer": "model_answer",
        "able_to_answer": "model_able_to_answer",
        "explanation": "model_explanation",
    },
    inplace=True,
)

# rename error to runtime_error
dfe.rename(columns={"error": "runtime_error"}, inplace=True)

# %%
# connect to google spreadsheets
import gspread
from gspread_dataframe import set_with_dataframe
import scipy as sp

gc = gspread.service_account()
spreadsheet = gc.open("LLMCalc Annotation Results")
if spreadsheet:
    print(f"Connected to Google Sheet {spreadsheet.title} at {spreadsheet.url}")
# %%
# upload raw data
raw_data_sheet = spreadsheet.worksheet("raw_annotation_data")
raw_data_sheet.clear()
set_with_dataframe(raw_data_sheet, dfe)

# %% ━━━━━━━━━━━━━━━━━━━━━━━━━ items with unclear status ━━━━━━━━━━━━━━━━━━━━━━━━ #

# get rows with queued status but error_class_one is not null, error_class_two is not null, or notes are present
items_with_unclear_status = dfe[
    (dfe.annotation_status == "queued")
    & (dfe.error_class_one.notnull() | dfe.error_class_two.notnull() | dfe.notes)
]

# upload items with unclear status to google sheet
items_with_unclear_status_sheet = spreadsheet.worksheet("items_with_unclear_status")
items_with_unclear_status_sheet.clear()
set_with_dataframe(items_with_unclear_status_sheet, items_with_unclear_status)

print(
    f"Found {len(items_with_unclear_status)} items with unclear status; uploading "
    f"to Google Sheet at {items_with_unclear_status_sheet.url}"
)

# %% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ possible duplicates ━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

# get possible duplicate rows
possible_duplicates = dfe[dfe.id.duplicated()]

# upload possible duplicates to google sheet
possible_duplicate_classifications_sheet = spreadsheet.worksheet(
    "possible_duplicate_classifications"
)
possible_duplicate_classifications_sheet.clear()
set_with_dataframe(possible_duplicate_classifications_sheet, possible_duplicates)

print(
    f"Found {len(possible_duplicates)} possible duplicate rows; uploading "
    f"to Google Sheet at {possible_duplicate_classifications_sheet.url}"
)


# %% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ flagged ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

# get rows with flagged_for_review
flagged_items = dfe[dfe.flagged_for_review]
# upload flagged items to google sheet
flagged_items_sheet = spreadsheet.worksheet("flagged_items")
flagged_items_sheet.clear()
set_with_dataframe(flagged_items_sheet, flagged_items)


# %% ━━━━━━━━ by user
# by user
alex_df = dfe[dfe.assigned_to == "Alex Goodell"]
simon_df = dfe[dfe.assigned_to == "Simon Chu"]
larry_df = dfe[dfe.assigned_to == "Larry Chu"]

alex_sheet = spreadsheet.worksheet("alex_goodell_raw_data")
simon_sheet = spreadsheet.worksheet("simon_chu_raw_data")
larry_sheet = spreadsheet.worksheet("larry_chu_raw_data")

alex_sheet.clear()
simon_sheet.clear()
larry_sheet.clear()

set_with_dataframe(alex_sheet, alex_df)
set_with_dataframe(simon_sheet, simon_df)
set_with_dataframe(larry_sheet, larry_df)
