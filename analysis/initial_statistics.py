# %% md
# # Import
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
# load data
df = pd.read_pickle(
    path_join(config.RESULTS_DATA_PATH, "most_recent/dataset_results_most-recent.pkl")
)
# %% md
# # Data Exploration
# %%
df.shape
# %%
pd.DataFrame(df.columns)
# %%
arm_names = [
    "Llama Base",
    "Llama + CI",
    "Llama + RAG",
    "Llama + RAG + CI",
    "Llama + OMC",
    "GPT4 Base",
    "GPT4 + CI",
    "GPT4 + RAG",
    "GPT4 + RAG + CI",
    "GPT4 + OMC",
]
# [a.name for a in arms]
model_names = [m.name for m in models]
calculator_names = [c.pretty_slug for c in calculators]
# %%
arm = datacore.arms

ordering = {
    "performance": ["Correct", "Incorrect", "No valid output"],
    "arm_name": [
        "Llama Base",
        "Llama + CI",
        "Llama + RAG",
        "Llama + RAG + CI",
        "Llama + OMC",
        "GPT4 Base",
        "GPT4 + CI",
        "GPT4 + RAG",
        "GPT4 + RAG + CI",
        "GPT4 + OMC",
    ],
    # [a.name for a in datacore.arms],
    "models": [m.name for m in datacore.models],
}
# %%
df.groupby(["arm_name"], observed=True).was_correct.mean() * 100
# %% md
#
# %%
df.groupby(["arm_name"], observed=True).was_correct.value_counts()
# %% md
# # GEE comparison all arms to llama_base
# %% md
# ### GEE Model
#
# We employed a Generalized Estimating Equations (GEE) approach with a logistic link function to analyze the binary outcome data (correct/incorrect responses) while accounting for the repeated measures design, where each model configuration evaluated the same set of patient cases. Patient ID was specified as the clustering variable to account for within-patient correlation of responses. The model used an independence working correlation structure, and robust standard errors were computed to account for potential misspecification of the correlation structure. We used the Benjamini-Hochberg false discovery rate (FDR) correction to account for multiple comparisons across.
#
# Model performance was additionally summarized using descriptive statistics, including the mean proportion of correct responses and standard errors for each configuration. All statistical analyses were performed using Python's statsmodels package. Statistical significance was set at α = 0.05.
# %% md
# ## Comparison with llama base
# %%
# patient_id is case_id aka vignette, so these will be our levels for a MLM
# we have 1000 vignettes tested by 10 models, so there should be 9000 duplicates
foo: pd.Series = df.patient_id
foo.duplicated().sum()
# %%
stats_df = pd.DataFrame(
    {
        "was_correct": df.was_correct.astype("float").to_numpy(),
        "arm_name": df.arm_slug.astype("string").to_numpy(),
        "patient_id": df.patient_id.astype("int").to_numpy(),
    }
)

# Create dummy variables and convert to float explicitly
arm_dummies = pd.get_dummies(stats_df["arm_name"], prefix="arm").astype(float)

# Drop the reference level ('Llama Base') manually
reference_col = [col for col in arm_dummies.columns if "llama_base" in col][0]
arm_dummies = arm_dummies.drop(columns=[reference_col])

# Convert to numpy arrays with correct types
y = stats_df["was_correct"].values
groups = stats_df["patient_id"].values
X = sm.add_constant(
    arm_dummies
)  # No need to call .values since we're already working with floats

# Fit the model using numpy arrays directly
model = sm.GEE(
    y,
    X,
    groups=groups,
    family=sm.families.Binomial(),
    cov_struct=sm.cov_struct.Independence(),
)

result = model.fit()
result.summary()

# %%
# Store column names for later reference
column_names = ["const"] + list(arm_dummies.columns)

# Calculate odds ratios and confidence intervals
odds_ratios = pd.DataFrame(
    {
        "Odds Ratio": np.exp(result.params),
        "CI Lower": np.exp(result.conf_int()[0]),
        "CI Upper": np.exp(result.conf_int()[1]),
        "P Value": result.pvalues,
    },
    index=column_names,
)

odds_ratios

# %%
# Add FDR-corrected p-values
_, odds_ratios["FDR Adjusted P"], _, _ = multipletests(result.pvalues, method="fdr_bh")

# Calculate descriptive statistics
desc_stats = (
    stats_df.groupby("arm_name")["was_correct"]
    .agg(
        [
            "count",
            "mean",
            ("std_err", lambda x: np.sqrt(x.mean() * (1 - x.mean()) / len(x))),
            "std",
        ]
    )
    .round(4)
)
desc_stats


# %%
# Calculate predicted probabilities
unique_arms = np.sort(stats_df["arm_name"].unique())
predictions = []
for arm in unique_arms:
    new_row = np.zeros(len(column_names))
    new_row[0] = 1  # constant term
    if arm != "Llama Base":  # reference level
        col_name = f"arm_{arm}"
        if col_name in column_names:
            new_row[column_names.index(col_name)] = 1
    pred_prob = result.predict(new_row)[0]
    predictions.append({"Arm": arm, "Predicted Probability": pred_prob})

predictions_df = pd.DataFrame(predictions)
predictions_df


# %% md
# ## Determining 95% CI
#
# For each model configuration, we calculated the proportion of correct responses and corresponding 95% confidence intervals using Wilson's score method.
#
#
# %%
def calculate_proportion_ci(successes, n, method="wilson"):
    """
    Calculate confidence interval for a proportion

    Parameters:
    successes: number of successes (correct responses)
    n: total number of trials
    method: 'normal' for normal approximation or 'wilson' for Wilson score interval

    Returns:
    tuple of (proportion, lower_ci, upper_ci, se)
    """
    p = successes / n

    if method == "normal":
        # Normal approximation
        se = np.sqrt(p * (1 - p) / n)
        ci_lower = p - 1.96 * se
        ci_upper = p + 1.96 * se
    else:
        # Wilson score interval (more robust, especially for proportions near 0 or 1)
        z = 1.96  # 95% confidence
        denominator = 1 + z**2 / n
        center = (p + z**2 / (2 * n)) / denominator
        spread = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denominator
        ci_lower = center - spread
        ci_upper = center + spread
        se = spread / z

    return p, ci_lower, ci_upper, se


# Calculate CIs for each arm
arms_data = {
    "llama_base": 0.114,
    "llama_ci": 0.183,
    "llama_rag": 0.403,
    "llama_rag_ci": 0.535,
    "llama_omc": 0.840,
    "gpt4_base": 0.361,
    "gpt4_ci": 0.460,
    "gpt4_rag": 0.768,
    "gpt4_rag_ci": 0.823,
    "gpt4_omc": 0.952,
}

results = {}
n = 1000  # sample size per arm

for arm, prop in arms_data.items():
    successes = int(prop * n)  # convert proportion to count
    p, lower, upper, se = calculate_proportion_ci(successes, n, method="wilson")
    results[arm] = {
        "standard_error": f"{se:.3f}",
        "proportion": f"{p:.3f}",
        "lower": f"{lower:.3f}",
        "upper": f"{upper:.3f}",
        "95% CI": f"({lower:.3f}-{upper:.3f})",
        "percentage": f"{p*100:.1f}%",
        "percentage_CI": f"({lower*100:.1f}%-{upper*100:.1f}%)",
    }

# Create a formatted table
results_df = pd.DataFrame.from_dict(results, orient="index")
print("\nResults with 95% Confidence Intervals:")
results_df

# %%

# %% md
# ## Incremental comparison
#
# To assess the incremental value of each additional tool (Code Interpreter, RAG, and OpenMedCalc), we performed pairwise comparisons between adjacent configurations within each LLM family (Llama and GPT-4), ordered by their performance. For these post-hoc comparisons, we calculated the difference in coefficients and their standard errors, deriving z-statistics and corresponding p-values. Effect sizes are reported as odds ratios with 95% confidence intervals, and absolute performance differences are presented as percentage point improvements.
# %%
from os import rename
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
import pandas as pd


def compare_arms(coef1, se1, coef2, se2):
    """
    Perform statistical comparison between two arms
    Returns difference and p-value
    """
    coef_diff = coef1 - coef2
    se_diff = np.sqrt(se1**2 + se2**2)
    z_stat = coef_diff / se_diff
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    odds_ratio = np.exp(coef_diff)
    return {
        "difference": coef_diff,
        "p_value": p_value,
        "odds_ratio": odds_ratio,
        "z_stat": z_stat,
    }


# Create dictionary of coefficients and standard errors
model_stats = {
    "llama_base": {
        "coef": -2.0505,
        "se": 0.100,
        "perf": 0.114,
    },  # const term represents llama_base
    "llama_ci": {"coef": -2.0505 + 0.5544, "se": 0.119, "perf": 0.183},
    "llama_rag": {"coef": -2.0505 + 1.6575, "se": 0.110, "perf": 0.403},
    "llama_rag_ci": {"coef": -2.0505 + 2.1907, "se": 0.113, "perf": 0.535},
    "llama_omc": {"coef": -2.0505 + 3.7087, "se": 0.123, "perf": 0.840},
    "gpt4_base": {"coef": -2.0505 + 1.4795, "se": 0.104, "perf": 0.361},
    "gpt4_ci": {"coef": -2.0505 + 1.8902, "se": 0.108, "perf": 0.460},
    "gpt4_rag": {"coef": -2.0505 + 3.2476, "se": 0.116, "perf": 0.768},
    "gpt4_rag_ci": {"coef": -2.0505 + 3.5873, "se": 0.121, "perf": 0.823},
    "gpt4_omc": {"coef": -2.0505 + 5.0379, "se": 0.173, "perf": 0.952},
}

# Define the order for each LLM
llama_order = ["llama_base", "llama_ci", "llama_rag", "llama_rag_ci", "llama_omc"]
gpt4_order = ["gpt4_base", "gpt4_ci", "gpt4_rag", "gpt4_rag_ci", "gpt4_omc"]


def analyze_incremental_improvements(model_order, model_stats):
    results = []
    p_values = []  # Store p-values for later FDR correction

    for i in range(len(model_order) - 1):
        current = model_order[i]
        next_model = model_order[i + 1]

        comparison = compare_arms(
            model_stats[next_model]["coef"],
            model_stats[next_model]["se"],
            model_stats[current]["coef"],
            model_stats[current]["se"],
        )

        perf_diff = model_stats[next_model]["perf"] - model_stats[current]["perf"]
        p_values.append(comparison["p_value"])

        results.append(
            {
                "previous_arm": current,
                "arm": next_model,
                "previous_arm_performance": model_stats[current]["perf"],
                "performance": model_stats[next_model]["perf"],
                "absolute_improvement": perf_diff,
                "odds_ratio": comparison["odds_ratio"],
                "p_value": comparison["p_value"],
                "z_stat": comparison["z_stat"],
            }
        )

    # Convert to DataFrame
    results_df = pd.DataFrame(results)

    # Calculate FDR-adjusted p-values for this set of comparisons
    _, bonferroni_adjusted_p, _, _ = multipletests(p_values, method="bonferroni")
    _, holm_adjusted_p, _, _ = multipletests(p_values, method="holm")
    results_df["raw_p_value"] = p_values
    results_df["holm_adjusted_p"] = holm_adjusted_p
    results_df["bonferroni_adjusted_p"] = bonferroni_adjusted_p

    return results_df


# Generate results for both LLMs
llama_results = analyze_incremental_improvements(llama_order, model_stats)
gpt4_results = analyze_incremental_improvements(gpt4_order, model_stats)

comparison_df = (
    pd.concat([llama_results, gpt4_results], keys=["Llama", "GPT-4"])
    .reset_index(level=0, names=["LLM"])
    .reset_index(drop=True)
)
# %%
# merge comparison_df with results_df
master_df = pd.merge(
    results_df, comparison_df, how="left", left_index=True, right_on="arm"
)
master_df.loc[master_df.previous_arm.isna(), "is_base_model"] = True
master_df.loc[~master_df.previous_arm.isna(), "is_base_model"] = False


master_df["arm_name"] = master_df.arm.apply(lambda x: datacore.get_arm_by_slug(x).name)
master_df["percent_correct"] = master_df.proportion.astype("float") * 100
master_df["upper_error_in_percent"] = (
    master_df.upper.astype("float") * 100 - master_df.percent_correct
)
master_df["lower_error_in_percent"] = (
    master_df.percent_correct - master_df.lower.astype("float") * 100
)

master_df.reset_index(drop=True, inplace=True)
master_df
# %% md
# # Figures and Tables Export
# %% md
# ### Comparison without P value adjustment
# %%
import plotly.express as px
import xxhash

# Create the base bar chart
fig = px.bar(
    master_df,
    x="arm_name",
    y="percent_correct",
    error_y="upper_error_in_percent",
    error_y_minus="lower_error_in_percent",
    labels={"index": "Arm", "proportion": "Percent correct"},
)

fig.update_layout(
    width=800,
    height=600,
    font=dict(family="Arial", size=12, color="Black"),
    plot_bgcolor="white",
    margin_t=0,
    margin_b=40,
    margin_l=0,
    margin_r=0,
    margin_pad=0,
    xaxis_title="Arm",
    yaxis_title="Percent Correct",
)

# Add P-value annotations with vertical offset
vertical_spacing = 6  # Base spacing between bars and annotations

# Get the x-axis positions (0, 1, 2, etc.)
arm_positions = {arm: i for i, arm in enumerate(master_df["arm_name"])}

# Determine what the pixel width of each bar is
bar_width = fig.layout.width / len(master_df["arm_name"])
half_bar_width = bar_width / 2
unit = fig.layout.width / 1000

for i, row in master_df.iterrows():

    if not row.is_base_model:

        # Get arm names and p-value
        arm1 = row["previous_arm"]
        arm2 = row["arm"]

        adjustment_method = "No adjustment"
        p_value = row.raw_p_value

        # Find corresponding rows in master_df
        arm1_data = master_df.iloc[i - 1]
        arm2_data = row

        # Calculate y-position for annotation
        max_height = max(
            arm1_data["percent_correct"]
            + arm1_data["upper_error_in_percent"]
            + vertical_spacing * 1.5,
            arm2_data["percent_correct"] + arm2_data["upper_error_in_percent"],
        )
        y_pos = max_height + vertical_spacing

        # Add connecting line using arm names (Plotly will map to correct positions)
        fig.add_shape(
            type="line",
            x0=arm1_data.arm_name,
            y0=y_pos,
            x1=arm2_data.arm_name,
            y1=y_pos,
            line=dict(color="black", width=1),
        )
        fig.add_shape(
            type="line",
            x0=arm1_data.arm_name,
            y0=y_pos,
            x1=arm1_data.arm_name,
            y1=y_pos - 4,
            line=dict(color="black", width=1),
        )
        fig.add_shape(
            type="line",
            x0=arm2_data.arm_name,
            y0=y_pos,
            x1=arm2_data.arm_name,
            y1=y_pos - 4,
            line=dict(color="black", width=1),
        )

        # Add P-value text using numerical positions for midpoint
        x_pos1 = arm_positions[arm1_data.arm_name]
        x_pos2 = arm_positions[arm2_data.arm_name]
        x_mid = (x_pos1 + x_pos2) / 2

        fig.add_annotation(
            x=master_df["arm_name"].iloc[int(x_mid)],  # Convert back to categorical
            y=y_pos + 1,
            text=f"P = {p_value:.1E}",
            showarrow=False,
            font=dict(size=12),
            xshift=unit * 45,
            yshift=unit * 5,
        )

fig.add_annotation(
    x=1,  # Convert back to categorical
    y=90,
    text=f"*P values adjusted using <br> {adjustment_method}",
    showarrow=False,
    font=dict(size=12),
    # xshift= unit * 45,
    # yshift= unit * 5
)


util.save_fig(
    fig,
    f"bar_chart_of_arm_performance_with_adjusted_p_values_using_{adjustment_method}",
)
fig.show()


# %% md
# ### Adjustment with Holm-Bonferroni
# %%
import plotly.express as px
import xxhash

# Create the base bar chart
fig = px.bar(
    master_df,
    x="arm_name",
    y="percent_correct",
    error_y="upper_error_in_percent",
    error_y_minus="lower_error_in_percent",
    labels={"index": "Arm", "proportion": "Percent correct"},
)

fig.update_layout(
    width=1400,
    height=700,
    font=dict(family="Arial", size=18, color="Black"),
    plot_bgcolor="white",
    margin_t=0,
    margin_b=40,
    margin_l=0,
    margin_r=0,
    margin_pad=0,
    xaxis_title="Arm",
    yaxis_title="Percent Correct",
)

# Add P-value annotations with vertical offset
vertical_spacing = 6  # Base spacing between bars and annotations

# Get the x-axis positions (0, 1, 2, etc.)
arm_positions = {arm: i for i, arm in enumerate(master_df["arm_name"])}

# Determine what the pixel width of each bar is
bar_width = fig.layout.width / len(master_df["arm_name"])
half_bar_width = bar_width / 2
unit = fig.layout.width / 1000

for i, row in master_df.iterrows():

    if not row.is_base_model:

        # Get arm names and p-value
        arm1 = row["previous_arm"]
        arm2 = row["arm"]

        adjustment_method = "Holm-Bonferroni"
        p_value = row.holm_adjusted_p

        # Find corresponding rows in master_df
        arm1_data = master_df.iloc[i - 1]
        arm2_data = row

        # Calculate y-position for annotation
        max_height = max(
            arm1_data["percent_correct"]
            + arm1_data["upper_error_in_percent"]
            + vertical_spacing * 1.5,
            arm2_data["percent_correct"] + arm2_data["upper_error_in_percent"],
        )
        y_pos = max_height + vertical_spacing

        # Add connecting line using arm names (Plotly will map to correct positions)
        fig.add_shape(
            type="line",
            x0=arm1_data.arm_name,
            y0=y_pos,
            x1=arm2_data.arm_name,
            y1=y_pos,
            line=dict(color="black", width=1),
        )
        fig.add_shape(
            type="line",
            x0=arm1_data.arm_name,
            y0=y_pos,
            x1=arm1_data.arm_name,
            y1=y_pos - 4,
            line=dict(color="black", width=1),
        )
        fig.add_shape(
            type="line",
            x0=arm2_data.arm_name,
            y0=y_pos,
            x1=arm2_data.arm_name,
            y1=y_pos - 4,
            line=dict(color="black", width=1),
        )

        # Add P-value text using numerical positions for midpoint
        x_pos1 = arm_positions[arm1_data.arm_name]
        x_pos2 = arm_positions[arm2_data.arm_name]
        x_mid = (x_pos1 + x_pos2) / 2

        fig.add_annotation(
            x=master_df["arm_name"].iloc[int(x_mid)],  # Convert back to categorical
            y=y_pos + 1,
            text=f"P = {p_value:.1E}",
            showarrow=False,
            font=dict(size=15),
            xshift=unit * 45,
            yshift=unit * 5,
        )

fig.add_annotation(
    x=1,  # Convert back to categorical
    y=90,
    text=f"*P values adjusted using <br> {adjustment_method}",
    showarrow=False,
    font=dict(size=12),
    # xshift= unit * 45,
    # yshift= unit * 5
)


util.save_fig(
    fig,
    f"bar_chart_of_arm_performance_with_adjusted_p_values_using_{adjustment_method}",
)
fig.show()


# %% md
# ### Adjustment with older Bonferroni
# %%
import plotly.express as px
import xxhash

# Create the base bar chart
fig = px.bar(
    master_df,
    x="arm_name",
    y="percent_correct",
    error_y="upper_error_in_percent",
    error_y_minus="lower_error_in_percent",
    labels={"index": "Arm", "proportion": "Percent correct"},
)

fig.update_layout(
    width=800,
    height=600,
    font=dict(family="Arial", size=12, color="Black"),
    plot_bgcolor="white",
    margin_t=0,
    margin_b=40,
    margin_l=0,
    margin_r=0,
    margin_pad=0,
    xaxis_title="Arm",
    yaxis_title="Percent Correct",
)

# Add P-value annotations with vertical offset
vertical_spacing = 6  # Base spacing between bars and annotations

# Get the x-axis positions (0, 1, 2, etc.)
arm_positions = {arm: i for i, arm in enumerate(master_df["arm_name"])}

# Determine what the pixel width of each bar is
bar_width = fig.layout.width / len(master_df["arm_name"])
half_bar_width = bar_width / 2
unit = fig.layout.width / 1000

for i, row in master_df.iterrows():

    if not row.is_base_model:

        # Get arm names and p-value
        arm1 = row["previous_arm"]
        arm2 = row["arm"]

        adjustment_method = "Bonferroni"
        p_value = row.bonferroni_adjusted_p

        # Find corresponding rows in master_df
        arm1_data = master_df.iloc[i - 1]
        arm2_data = row

        # Calculate y-position for annotation
        max_height = max(
            arm1_data["percent_correct"]
            + arm1_data["upper_error_in_percent"]
            + vertical_spacing * 1.5,
            arm2_data["percent_correct"] + arm2_data["upper_error_in_percent"],
        )
        y_pos = max_height + vertical_spacing

        # Add connecting line using arm names (Plotly will map to correct positions)
        fig.add_shape(
            type="line",
            x0=arm1_data.arm_name,
            y0=y_pos,
            x1=arm2_data.arm_name,
            y1=y_pos,
            line=dict(color="black", width=1),
        )
        fig.add_shape(
            type="line",
            x0=arm1_data.arm_name,
            y0=y_pos,
            x1=arm1_data.arm_name,
            y1=y_pos - 4,
            line=dict(color="black", width=1),
        )
        fig.add_shape(
            type="line",
            x0=arm2_data.arm_name,
            y0=y_pos,
            x1=arm2_data.arm_name,
            y1=y_pos - 4,
            line=dict(color="black", width=1),
        )

        # Add P-value text using numerical positions for midpoint
        x_pos1 = arm_positions[arm1_data.arm_name]
        x_pos2 = arm_positions[arm2_data.arm_name]
        x_mid = (x_pos1 + x_pos2) / 2

        fig.add_annotation(
            x=master_df["arm_name"].iloc[int(x_mid)],  # Convert back to categorical
            y=y_pos + 1,
            text=f"P = {p_value:.1E}",
            showarrow=False,
            font=dict(size=12),
            xshift=unit * 45,
            yshift=unit * 5,
        )

fig.add_annotation(
    x=1,  # Convert back to categorical
    y=90,
    text=f"*P values adjusted using <br> {adjustment_method}",
    showarrow=False,
    font=dict(size=12),
    # xshift= unit * 45,
    # yshift= unit * 5
)


util.save_fig(
    fig,
    f"bar_chart_of_arm_performance_with_adjusted_p_values_using_{adjustment_method}",
)
fig.show()


# %% md
# ### Make table
# %%
master_df.columns

# %%

correct_df = df[df.was_correct == True]
correct_df.groupby(["arm_name"], observed=True).id.count()
correct_count = (
    correct_df.groupby(["arm_name"], observed=True)
    .id.count()
    .reset_index()
    .reset_index()
)
correct_count.columns = ["id", "arm_name", "cor"]
correct_count.reset_index(inplace=True)
correct_count = correct_count.set_index("arm_name")
# master_df.reset_index(inplace=True)
master_df = master_df.set_index("arm_name")
master_df["correct_count"] = correct_count.cor
master_df["correct_count"]
correct_count.cor

master_df.reset_index(inplace=True)
master_df["tool_config"] = master_df["arm"].apply(lambda x: x.split("_")[1])
master_df["model"] = master_df["arm"].apply(lambda x: x.split("_")[0])
master_df["absolute_improvement"] = master_df["absolute_improvement"] * 100.0
# master_df['par_up_low'] = str(master_df['lower'].round(2) * 100) + "-" + str(master_df['lower_error_in_percent'].round(2) * 100)
master_df

# %%
# Create a column with X% (Y% - Z%) format for display
master_df["percent_correct_formatted"] = (
    master_df["percent_correct"].round(1).astype(str)
    + " "
    + master_df["percentage_CI"].replace("\%", "")
)


# Select relevant columns for the table
table_df = master_df[
    [
        "model",
        "tool_config",
        "correct_count",
        "percent_correct_formatted",
        "absolute_improvement",
        "odds_ratio",
        "raw_p_value",
        "holm_adjusted_p",
        "bonferroni_adjusted_p",
    ]
]

# Rename columns for better readability
table_df.columns = [
    "LLM",
    "Tools",
    "Correct (count)",
    "Percent Correct",
    "absolute_improvement",
    "odds_ratio",
    "Raw P-value",
    "HB-adjusted P",
    "Bonferroni-adjusted P",
]


# Display the table
filename = path_join(config.RESULTS_DATA_PATH, "annotation", f"main_results_table.csv")
table_df.to_csv(filename, index=False)

table_df
# %%
lat_df = table_df.set_index(["LLM", "Tools"])

# format the P values with "%.1e"
lat_df["Raw P-value"] = lat_df["Raw P-value"].apply(lambda x: f"{x:.1e}")
lat_df["HB-adjusted P"] = lat_df["HB-adjusted P"].apply(lambda x: f"{x:.1e}")
lat_df["Bonferroni-adjusted P"] = lat_df["Bonferroni-adjusted P"].apply(
    lambda x: f"{x:.1e}"
)
# table_df.fillna("NA", inplace=True)

print(
    lat_df.to_latex(
        multicolumn=True,
        multirow=True,
        sparsify=True,
        index=True,
        bold_rows=True,
        escape=True,
        column_format="|l|l|l|l|l|l|l|l|l|",
        float_format="%.2g",
    )
)
# %%

# %% md
# # Remaining
# %%
