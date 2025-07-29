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

# %% import run data

df = pd.read_pickle(
    path_join(config.RESULTS_DATA_PATH, "most_recent/dataset_results_most-recent.pkl")
)

# %%
print(df.memory_usage(deep=True).sort_values(ascending=False))

# %% reduce size

df_mini = df.drop(
    columns=[
        "outputs",
        "feedback_stats",
        "steps",
        "raw_response",
        "intermediate_steps",
        "child_run_ids",
        "parent_run_id",
        "attachments",
        "tags",
        "manifest_id",
        "session_id",
        "criteria",
        "events",
        "inputs",
        "reference_example_id",
        "reference_answer",
        "output_object",
        "output_explanation",
        "adjusted_clinical_error_real",
        "adjusted_clinical_error_absolute",
        "error_real",
        "error_absolute",
    ]
)


# %% upload to google sheets

# connect to google spreadsheets
import gspread
from gspread_dataframe import set_with_dataframe
import scipy as sp

gc = gspread.service_account()
spreadsheet = gc.open("LLMCalc Annotation Results")
if spreadsheet:
    print(f"Connected to Google Sheet {spreadsheet.title} at {spreadsheet.url}")

# upload raw data
worksheet_name = "raw_run_data"
raw_run_data_sheet = spreadsheet.worksheet(worksheet_name)
raw_run_data_sheet.clear()


from rich.progress import Spinner


print("Uploading raw run data to Google Sheet...")
set_with_dataframe(raw_run_data_sheet, df_mini)

print(f"Uploaded raw run data to Google Sheet {worksheet_name}")
