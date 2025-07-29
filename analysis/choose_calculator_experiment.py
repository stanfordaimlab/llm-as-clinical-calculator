# %% Import the necessary libraries

from fileinput import filename
from llm_calc.lib.experiment import ls_client, make_df
from llm_calc.lib.config import config
from llm_calc.lib.datamodel import Arm, ArmSlug, Model, ModelSlug
from llm_calc.lib.datacore import datacore
from os.path import join as path_join
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

arms = datacore.arms
models = datacore.models
calculators = datacore.calculators
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from llm_calc.lib.datacore import datacore
from llm_calc.lib.datamodel import Arm, Model
from typing import List, Dict, Any
from llm_calc.util import util
import jedi

# get the arm and model objects
arms = datacore.arms
models: List[Model] = datacore.models


# %%
# load data
df = pd.read_pickle(
    path_join(config.RESULTS_DATA_PATH, "most_recent/dataset_results_most-recent.pkl")
)

rdf = pd.DataFrame()
# get 10 cases from each calculator
for calculator in calculators:
    rows = df[df.calculator_slug == calculator.slug.value].head(10)
    rdf = pd.concat([rdf, rows])

print(rdf.calculator_slug.value_counts())
print("number of unique patients: ", len(rdf.patient_id.unique()))

# %% export the data
filename = path_join(
    config.RESULTS_DATA_PATH, "most_recent/choose_calculator_experiment_original.pkl"
)
rdf.to_pickle(filename)
print("Data exported to: ", filename)

# %%

# load the modified data
df = pd.read_pickle(
    path_join(
        config.RESULTS_DATA_PATH,
        "most_recent/choose_calculator_experiment_modified.pkl",
    )
)
