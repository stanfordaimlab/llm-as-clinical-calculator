# %%
from IPython.lib.deepreload import reload
import jedi

# %%
from llm_calc.lib.experiment import ls_client, make_df
from llm_calc.lib.config import config
from llm_calc.lib.datamodel import Arm, ArmSlug, Model, ModelSlug
from llm_calc.lib.datacore import datacore
from os.path import join as path_join
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from llm_calc.util import util
import jedi  # for autocompletion
import numpy as np


# arms = datacore.arms
# models = datacore.models
# calculators = datacore.calculators

# %%
filename = path_join(
    config.RESULTS_DATA_PATH, "annotation", f"all_error_class_runs_master.pkl"
)
df: pd.DataFrame = pd.read_pickle(filename)

# %%
# remove runs that had timeout errors and were not included in analysis
# (were re-run after annotation database was complete)
df.remove_from_annotation.value_counts()
to_remove = df[df.remove_from_annotation == "yes"]
df = df.drop(to_remove.index)
df.shape

# %%

# Replace the phrase "I cannot tell" with "Indeterminate" in error_class
df["error_class_one"] = df["error_class_one"].replace("I cannot tell", "Indeterminate")
df["error_class_two"] = df["error_class_two"].replace("I cannot tell", "Indeterminate")


# %%
# make a new df with one row per calculator-arm
error_df = pd.DataFrame()
rows = []

calculators = df.calculator_slug.unique().tolist()
arms = df.arm_slug.unique().tolist()
error_classes = df.error_class_one.unique().tolist()

print("for each calculator-arm, make a row for each error_class")
print("using the following calculators, arms, and error_classes")
print("calculators:", calculators)
print("arms:", arms)
print("error_classes:", error_classes)

for calculator in calculators:
    for arm in arms:
        for error_class in error_classes:
            row = {
                "calculator": calculator,
                "arm": arm,
                "calculator_arm": f"{calculator}_{arm}",
                "error_class": error_class,
            }
            rows = rows + [row]
error_df = pd.DataFrame(rows)

# get count from df for each calculator-arm-error_class
error_df["count_errors"] = 0.0
for index, row in error_df.iterrows():
    calculator = row["calculator"]
    arm = row["arm"]
    error_class = row["error_class"]
    count = len(
        df[
            (df.calculator_slug == calculator)
            & (df.arm_slug == arm)
            & (
                (df.error_class_one == error_class)
                | (df.error_class_two == error_class)
            )
        ]
    )
    error_df.at[index, "count_errors"] = count

# get total count for each calculator-arm
# IMPORTANT: this needs to be from error_df, not df, otherwise we will get the number of runs
# rather than the number of errors
error_df["count_errors_for_calculator_arm"] = 0.0
for index, row in error_df.iterrows():
    calculator = row["calculator"]
    arm = row["arm"]
    count = error_df[(error_df.calculator == calculator) & (error_df.arm == arm)][
        "count_errors"
    ].sum()
    error_df.at[index, "count_errors_for_calculator_arm"] = count

# calculate the proportion of each error_class for each calculator-arm
error_df["proportion_ec_calc_arm"] = (
    error_df["count_errors"] / error_df["count_errors_for_calculator_arm"]
)

# check that the proportions sum to 1 for each calculator-arm
# first, exclude calculator-arms with only no errors
has_errors = error_df[error_df.count_errors_for_calculator_arm > 0]
valid_check = np.isclose(
    has_errors.groupby("calculator_arm").proportion_ec_calc_arm.sum(), 1.0
)
valid_check.all()
if not valid_check.all():
    raise ValueError("proportions do not sum to 1 for each calculator-arm")

# %% descriptive stats
error_df.groupby("error_class").agg(
    {"count_errors": ["sum", "mean", "std"], "proportion_ec_calc_arm": ["mean", "std"]}
)

# %%
# get full results pkl as run_df - this represents all runs
run_df = pd.read_pickle(
    path_join(config.RESULTS_DATA_PATH, "most_recent/dataset_results_most-recent.pkl")
)

# %%
# get total count and count of was_correct from df for each calculator-arm combination
error_df["count_was_correct"] = 0
error_df["count_incorrect"] = 0
error_df["count_not_valid"] = 0
error_df["count_total"] = 0
error_df["proportion_correct"] = 0.0
error_df["proportion_incorrect"] = 0.0
error_df["proportion_not_valid"] = 0.0


for i, row in error_df.iterrows():
    calculator = row["calculator"]
    arm = row["arm"]
    count_errors = row["count_errors"]
    proportion_ec_calc_arm = row["proportion_ec_calc_arm"]
    count_total = len(
        run_df[(run_df.calculator_slug == calculator) & (run_df.arm_slug == arm)]
    )
    count_correct = len(
        run_df[
            (run_df.calculator_slug == calculator)
            & (run_df.arm_slug == arm)
            & (run_df.was_correct == True)
        ]
    )
    # changed to just count invalid answers as incorrect
    count_invalid = 0
    # count_invalid = len(
    #     run_df[
    #         (run_df.calculator_slug == calculator)
    #         & (run_df.arm_slug == arm)
    #         & (run_df.final_answer_valid == False)
    #     ]
    # )
    count_incorrect = count_total - count_correct - count_invalid
    proportion_correct = count_correct / count_total
    proportion_incorrect = count_incorrect / count_total
    proportion_invalid = count_invalid / count_total
    error_df.at[i, "count_total"] = count_total
    error_df.at[i, "count_correct"] = count_correct
    error_df.at[i, "count_incorrect"] = count_incorrect
    error_df.at[i, "count_invalid"] = count_invalid
    error_df.at[i, "proportion_correct"] = proportion_correct
    error_df.at[i, "proportion_incorrect"] = proportion_incorrect
    error_df.at[i, "proportion_not_valid"] = proportion_invalid

# to make the error class plot, we will use a plotly horizontal histogram with each calculator-arm as a bar
# and the proportion of each error class as the colors dividing each bar
# since some runs have multiple error classes, and all calculator-arms have different counts of errors,
# we need to adjust the proportion of each error class by the total number of errors for each calculator-arm
error_df["proportion_error_adjusted"] = (
    error_df.proportion_ec_calc_arm * error_df.proportion_incorrect
)
error_df["errors_by_class_adjusted"] = (
    error_df.proportion_error_adjusted * error_df.count_total
)


# %%
# for each calculator-arm, the sum of all errors_by_class_adjusted plus
# the counts of correct and invalid should equal the total count of runs


error_df["errors_by_class_checksum"] = error_df.groupby("calculator_arm")[
    "errors_by_class_adjusted"
].transform("sum")
error_df["check_sum_zero"] = (
    error_df["errors_by_class_checksum"]
    + error_df["count_invalid"]
    + error_df["count_correct"]
    - error_df["count_total"]
)

checksum = np.isclose(error_df["check_sum_zero"], 0.0).all()
if not checksum:
    raise ValueError("ERROR: check_sum_zero is not zero for some calculator-arms")
else:
    print("check_sum_zero is zero for all calculator-arms")

# %%
# make a new df called plot_df. for each calculator-arm, there will be one row for correct
# with the count of correct answers,
# one row for invalid with the count of invalid, and
# a row for each error class with the adjusted count
plot_rows = []

for calculator_arm in error_df.calculator_arm.unique():
    correct = error_df[(error_df.calculator_arm == calculator_arm)][
        "count_correct"
    ].values[0]
    invalid = error_df[(error_df.calculator_arm == calculator_arm)][
        "count_invalid"
    ].values[0]
    error_classes = error_df[(error_df.calculator_arm == calculator_arm)]
    for i, row in error_classes.iterrows():
        error_class = row["error_class"]
        count = row["errors_by_class_adjusted"]
        calculator = row["calculator"]
        arm = row["arm"]
        plot_rows = plot_rows + [
            {
                "calculator_arm": calculator_arm,
                "error_class": error_class,
                "count": count,
                "calculator": calculator,
                "arm": arm,
                "correct_for_sorting": correct,
            }
        ]
    plot_rows = plot_rows + [
        {
            "calculator_arm": calculator_arm,
            "error_class": "Correct",
            "count": correct,
            "calculator": calculator,
            "arm": arm,
            "correct_for_sorting": correct,
        }
    ]
    plot_rows = plot_rows + [
        {
            "calculator_arm": calculator_arm,
            "error_class": "No valid response",
            "count": invalid,
            "calculator": calculator,
            "arm": arm,
            "correct_for_sorting": correct,
        }
    ]

plot_df = pd.DataFrame(plot_rows)
plot_df


# %%
plot_df["calculator"] = plot_df.calculator.apply(
    lambda x: datacore.get_calculator_by_slug(x).pretty_slug
)
plot_df["arm"] = plot_df.arm.apply(lambda x: datacore.get_arm_by_slug(x).name)

# %%
plot_df.arm.unique()

# %%

color_sequence = [
    "rgb(56, 133, 22)",
    "rgb(184, 131, 225)",
    "rgb(127, 60, 141)",
    "rgb(242, 183, 1)",
    "rgb(231, 63, 116)",
    "rgb(146, 48, 48)",
    "rgb(97, 139, 225)",
    "rgb(120, 200, 200)",
    "rgb(100, 100, 100)",
]

# %%
from cProfile import label
import plotly.express as px

# sort by highest count of correct answers within arm
plot_df = plot_df.sort_values(by=["correct_for_sorting"], ascending=[True])
plot_df = plot_df.sort_values(by=["arm", "correct_for_sorting"], ascending=[True, True])
# error_class_categories = plot_df.error_class.unique().tolist()

# Create the plot
fig = px.histogram(
    plot_df,
    x="count",
    y="calculator",
    facet_col="arm",
    facet_col_wrap=2,
    color="error_class",
    orientation="h",
    labels={
        "errors_by_class_adjusted": "Adjusted Errors",
        "calculator_arm": "Calculator-Arm",
    },
    category_orders={
        "error_class": ["Correct"]
        + [
            "Interpretation Error",
            "Incorrect Criteria",
            "Assignment Error",
            "Incorrect Formula",
            "Calculation Error",
            "Incorrect Reporting",
            "Indeterminate",
            "Software Error/Other",
        ],
        # + ["No valid response"],
        "calculator": calculators,
        "arm": [
            "Llama Base",
            "GPT4 Base",
            "Llama + CI",
            "GPT4 + CI",
            "Llama + RAG",
            "GPT4 + RAG",
            "Llama + RAG + CI",
            "GPT4 + RAG + CI",
            "Llama + OMC",
            "GPT4 + OMC",
        ],
        #     GPT4 + CI', 'GPT4 + OMC', 'GPT4 + RAG', 'GPT4 + RAG + CI',
        #    'GPT4 Base', 'Llama + CI', 'Llama + OMC', 'Llama + RAG',
        #    'Llama + RAG + CI', 'Llama Base'
    },
    color_discrete_sequence=color_sequence,
    facet_col_spacing=0.01,
    facet_row_spacing=0.03,
)

# Update layout for better visualization
fig.update_layout(
    width=800,
    height=800,
    legend_title="",
    legend_x=-0.5,
    legend_y=1,
    legend_xanchor="left",
    legend_yanchor="top",
    xaxis_title="Number of questions",
    yaxis_title="Calculation Task",
    font=dict(family="Roboto", size=10, color="Black"),
    # title_font_size=24,
    plot_bgcolor="white",
    margin_t=50,
    margin_b=50,
    margin_l=50,
    margin_r=50,
    margin_pad=5,
)

fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
# Update x-axes and y-axes for better visualization
# fig.update_yaxes(matches=None)
fig.update_yaxes(title="", selector=0)
fig.update_yaxes(title="", selector=2)
fig.update_yaxes(title="Calculation Task", selector=4)
fig.update_yaxes(title="", selector=6)
fig.update_yaxes(title="", selector=8)

fig.update_xaxes(title="Number of questions", selector=1)

# Show the plot
fig.show()

util.save_fig(fig, "error_class_histogram")


# %%
util.h1("error report statistics")

df["tool_config"] = df["arm"].apply(
    lambda x: x.replace("llama_", "").replace("gpt4_", "")
)
print("total trials annotated:", df.id.count())
util.h3("breakdown of trials:")  # --------------------
print(df.groupby(["llm"]).id.count().reset_index())
print(df.groupby(["tool_config"]).id.count().reset_index())

filename = path_join(config.RESULTS_DATA_PATH, "annotated_trials_counts.xlsx")
df.to_excel(filename)

util.h3("breakdown of errors:")  # --------------------
error_class_one_df = df.copy()
error_class_one_df["error_class"] = error_class_one_df["error_class_one"]
error_class_two_df = df.copy()
error_class_two_df["error_class"] = error_class_two_df["error_class_two"]
all_annotated_errors_df = pd.concat([error_class_one_df, error_class_two_df])
total_errors = all_annotated_errors_df.error_class.count()
print("total errors found:", total_errors)
print(
    "errors by LLM:", all_annotated_errors_df.groupby(["llm"]).id.count().reset_index()
)
print(
    "errors by tool:",
    all_annotated_errors_df.groupby(["tool_config"]).id.count().reset_index(),
)
print(
    "errors by class:",
    all_annotated_errors_df.groupby(["error_class"]).id.count().reset_index(),
)

filename = path_join(config.RESULTS_DATA_PATH, "identified_error_class_counts.xlsx")
all_annotated_errors_df.to_excel(filename)

util.h3("breakdown of errors extrapolated to arm-calc pair")  # --------------------
plot_df["tool_config"] = plot_df["arm"].apply(
    lambda x: x.replace("Llama", "").replace("GPT4", "").replace("+", "").strip()
)
plot_df["llm"] = plot_df["arm"].apply(
    lambda x: x.replace("+ RAG", "")
    .replace("+ CI", "")
    .replace("+ OMC", "")
    .replace("Base", "")
    .strip()
)
print("errors by class:", plot_df.groupby(["error_class"])["count"].sum().reset_index())
print(
    "errors by LLM:",
    plot_df.groupby(["llm", "error_class"])["count"].sum().reset_index(),
)
print(
    "errors by tool:",
    plot_df.groupby(["tool_config", "error_class"])["count"].sum().reset_index(),
)
print(
    "errors by arm:",
    plot_df.groupby(["arm", "error_class"])["count"].sum().reset_index(),
)

filename = path_join(config.RESULTS_DATA_PATH, "extrapolated_error_class_counts.xlsx")
plot_df.to_excel(filename)

# %%

# make latex tables
ldf = plot_df.groupby(["error_class"])["count"].sum().reset_index()
filename = path_join(config.RESULTS_DATA_PATH, "tables", "errors_by_class.tex")
ldf.to_latex(
    filename,
    multicolumn=True,
    multirow=True,
    sparsify=True,
    index=True,
    bold_rows=False,
    escape=True,
    column_format="|l|l|l|l|l|l|l|l|l|",
    float_format="%.0f",
)

ldf = plot_df.groupby(["llm", "error_class"])["count"].sum().reset_index()
filename = path_join(config.RESULTS_DATA_PATH, "tables", "errors_by_llm.tex")
ldf.to_latex(
    filename,
    multicolumn=True,
    multirow=True,
    sparsify=True,
    index=True,
    bold_rows=False,
    escape=True,
    column_format="|l|l|l|l|l|l|l|l|l|",
    float_format="%.0f",
)

ldf = plot_df.groupby(["tool_config", "error_class"])["count"].sum().reset_index()
filename = path_join(config.RESULTS_DATA_PATH, "tables", "errors_by_tool_config.tex")
ldf.to_latex(
    filename,
    multicolumn=True,
    multirow=True,
    sparsify=True,
    index=True,
    bold_rows=False,
    escape=True,
    column_format="|l|l|l|l|l|l|l|l|l|",
    float_format="%.0f",
)

ldf = plot_df.groupby(["arm", "error_class"])["count"].sum().reset_index()
filename = path_join(config.RESULTS_DATA_PATH, "tables", "errors_by_arm.tex")
ldf.to_latex(
    filename,
    multicolumn=True,
    multirow=True,
    sparsify=True,
    index=True,
    bold_rows=False,
    escape=True,
    column_format="|l|l|l|l|l|l|l|l|l|",
    float_format="%.0f",
)

# %%

# connect to google spreadsheets
import gspread
from gspread_dataframe import set_with_dataframe
import scipy as sp

gc = gspread.service_account()
spreadsheet = gc.open("LLMCalc Annotation Results")
if spreadsheet:
    print(f"Connected to Google Sheet {spreadsheet.title} at {spreadsheet.url}")

worksheet_name, dataframe_to_upload = "extrapolated_error_class_counts", plot_df
this_sheet = spreadsheet.worksheet(worksheet_name)
this_sheet.clear()
print("Uploading to Google Sheet...")
set_with_dataframe(this_sheet, dataframe_to_upload)

worksheet_name, dataframe_to_upload = (
    "identified_error_class_counts",
    all_annotated_errors_df,
)
this_sheet = spreadsheet.worksheet(worksheet_name)
this_sheet.clear()
print("Uploading to Google Sheet...")
set_with_dataframe(this_sheet, dataframe_to_upload)

worksheet_name, dataframe_to_upload = "annotated_trials_counts", df
this_sheet = spreadsheet.worksheet(worksheet_name)
this_sheet.clear()
print("Uploading to Google Sheet...")
set_with_dataframe(this_sheet, dataframe_to_upload)
