# %%
from IPython.lib.deepreload import reload
from pandas import Series

# %%
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
from statsmodels.stats.multitest import multipletests
import statsmodels.api as sm
from llm_calc.lib.datacore import datacore
from llm_calc.lib.datamodel import Arm, Model
from typing import List, Dict, Any
from llm_calc.util import util

# get the arm and model objects
arms = datacore.arms
models: List[Model] = datacore.models

# %%

table_df = pd.read_csv(config.RESULTS_DATA_PATH + "/exploratory_analysis.csv")

# in calculator column, remove everthing after  (
table_df["Calculator"] = table_df["Calculator"].apply(lambda x: x.split("(")[0])

# %%

# expand the errors_by_class column, seperated by commas by creating a new row for each error class
table_df["errors_by_class"] = table_df[
    table_df["errors_by_class"].notna()
].errors_by_class.apply(lambda x: x.split(","))


# make a new row for each error class
table_df = table_df.explode("errors_by_class")

# %%
error_table_df = table_df[table_df["errors_by_class"].notna()]
error_table_df

# %%

error_table_df_unstacked = (
    error_table_df.groupby(["Calculator", "errors_by_class"])
    .response_correct.count()
    .reset_index()
)
error_table_df_unstacked
# %%


print(
    error_table_df_unstacked.to_latex(
        # multicolumn=True,
        # multirow=True,
        # sparsify=True,
        index=False,
        bold_rows=False,
        escape=True,
        column_format="|l|l|l|l|l|l|l|l|l|",
        float_format="%.2g",
    )
)
# %%

# %% md
# # Remaining
# %%
