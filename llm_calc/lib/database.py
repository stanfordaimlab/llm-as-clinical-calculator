from globals import *
from llm_calc.lib.datamodel import *
from llm_calc.util import util
from llm_calc.lib.config import config
import pandas as pd
import os
import urllib3
import duckdb
import yaml
from typing import List, Optional


class Datacore:
    models: Optional[List[Model]] = None
    arms: Optional[List[Arm]] = None
    criterion_options: Optional[List[CriterionOption]] = None
    calculators: Optional[List[Calculator]] = None
    vignette_templates: Optional[List[VignetteTemplate]] = None
    cases: Optional[List[Case]] = None
    case_criteria: Optional[List[CaseCriterion]] = None
    error_types: Optional[List[ErrorType]] = None


# ------ inputs ------


def build_inputs_database():
    """
    1. Downloads the database from Google Sheets
    2. Loads the database into memory
    3. Validates the database
    4. Saves the database to disk in DuckDB format

    :return:
    """
    util.log_task("Building Inputs Database")
    # Get Data from Google Sheets
    # download Excel file to DATA_DIR
    util.log_mini_task("Downloading XLSX from Google Sheets")
    if not os.path.exists(config.DATABASE_BUILD_DIR):
        os.makedirs(config.DATABASE_BUILD_DIR)
    url = config.DATABASE_REMOTE_XLSX_URL
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    with open(config.DATABASE_LOCAL_XLSX_PATH, "wb") as f:
        f.write(r.data)

    ### Load Data and Data Validation
    # ----------------------------------------------------------------------
    util.log_mini_task("Loading data and validating")

    # models
    models = [e.value for e in ModelSlug]

    # calculators
    calculator_df = pd.read_excel(
        config.DATABASE_LOCAL_XLSX_PATH, sheet_name="calculator"
    )
    calculator_df.slug = calculator_df.slug.astype("category")
    calculators = calculator_df

    # arms
    arms = pd.read_excel(config.DATABASE_LOCAL_XLSX_PATH, sheet_name="arm")
    arms.slug = arms.slug.astype("category")

    # criterion options
    criterion_options = pd.read_excel(
        config.DATABASE_LOCAL_XLSX_PATH, sheet_name="criterion_option"
    )
    criterion_options.criterion_slug = criterion_options.criterion_slug.astype(
        "category"
    )
    criterion_options.calculator_slug = criterion_options.calculator_slug.astype(
        "category"
    )

    ### Create Database
    # ----------------------------------------------------------------------
    util.log_mini_task("Creating DuckDB database")

    # create data
    # create dictionary of tables
    tables = {
        "models": pd.DataFrame(models, columns=["slug"]),
        "calculators": calculators,
        "arms": arms,
        "criterion_options": criterion_options,
    }

    proceed = util.confirm(
        "This will overwrite the existing inputs database. Do you want to continue?"
    )
    if not proceed:
        util.log_warning("Database creation aborted")
        return

    try:
        for t_name, t in tables.items():
            with duckdb.connect(config.DATABASE_PATH) as con:
                con.execute(f"DROP TABLE IF EXISTS {t_name}")
                con.execute(f"CREATE TABLE {t_name} AS SELECT * FROM t")

        util.log_mini_task("Database created")
    except Exception as e:
        util.log_warning("Error creating database", e)


def get_vignette_templates():
    """
    Get all vignette templates from YAML file collection.
    :return: List[VignetteTemplate]
    """
    v = 0
    vignettes = []
    calculators = get_selected_calculators()

    # for each calculator, read a file with the slug of the calculator as filename
    for key, calculator in calculators.iterrows():
        vignette_path = os.path.join(
            config.VIGNETTE_LOCAL_PATH, f"{calculator.slug}.yaml"
        )
        with open(vignette_path, "rb") as f:
            templates_yaml = f.read()
        # deserialize the yaml file
        templates = yaml.safe_load(templates_yaml)
        for row in templates:
            vignettes += [
                VignetteTemplate(
                    id=v, template=row["template"], calculator_slug=calculator.slug
                )
            ]
            v += 1
    vignettes = pd.DataFrame(vignettes)
    return vignettes


def get_models():
    """
    Get all models. Note this isn't a database call but instead just a
    list of all model enums from the ModelSlug enum in datamodel.py
    This is expanded in Datacore
    :return:
    """
    # models
    models = pd.DataFrame([{"slug": e.value} for i, e in enumerate(ModelSlug)])
    return models


def get_arms():
    """
    Get all arms of the study from the database.
    :return:
    """
    with get_connection() as con:
        arms = con.execute("SELECT * FROM arms").fetchdf()
    return arms


def get_criterion_options():
    """
    Get all criterion options from the database.
    :return:
    """
    with get_connection() as con:
        criterion_options = con.execute("SELECT * FROM criterion_options").fetchdf()
    return criterion_options


def get_calculators():
    """
    Get all calculators from the database.
    :return:
    """
    with get_connection() as con:
        calculators = con.execute("SELECT * FROM calculators").fetchdf()
    # convert to Calculator objects
    # calculators = [Calculator(**row) for _, row in calculators.iterrows()]
    return calculators


def get_selected_calculators(c: List[CalculatorSlug] = None):
    """
    Get all calculators from the database. if c is provided, only return those calculators
    otherwise return the default  calculators
    :return:
    """
    if c is None:
        c = config.get("DEFAULT_SELECTED_CALCULATORS_SLUGS")
    with get_connection() as con:
        calculators = con.execute("SELECT * FROM calculators").fetchdf()
    return calculators[calculators.slug.isin(c)]


def get_connection(db: str = "inputs"):
    """
    Get a connection to the DuckDB database
    :return: con: DuckDBPyConnection
    """
    if db == "inputs":
        con = duckdb.connect(config.DATABASE_PATH)
    elif db == "experiments":
        con = duckdb.connect(config.EXPERIMENTS_DATABASE_PATH)
    else:
        raise ValueError("Invalid database")
    return con


# ------ experiments ----------


def build_experiments_database():
    """
    1. Creates an empty DuckDB database
    2. Creates the experiments table with a sample experiment
    3. Deletes the sample experiment
    :return:
    """
    util.log_task("Building Experiments Database")
    util.log_mini_task("Creating empty DuckDB database")

    sample_case = Case(
        id=0,
        name="John Doe",
        calculator_slug=CalculatorSlug.meldna,
        vignette="This is a sample vignette",
        options=None,
        correct_output=None,
        correct_output_notes=None,
        given_output=None,
        is_correct=None,
    )

    sample_experiment = Experiment(
        slug=util.gen_two_word_slug(),
        description="This is a sample experiment",
        git_hash_before_start="",
        start_datetime="",
        end_datetime="",
        is_completed=False,
        number_of_cases=10,
        cases=[sample_case],
    )

    exp_df = pd.DataFrame(
        [sample_experiment], columns=sample_experiment.__dataclass_fields__.keys()
    )

    tables = {"experiments": exp_df}

    proceed = util.confirm(
        "This will overwrite the existing experiments database. Do you want to continue?"
    )
    if not proceed:
        util.log_warning("Database creation aborted")
        return

    try:
        for t_name, t in tables.items():
            with duckdb.connect(config.EXPERIMENTS_DATABASE_PATH) as con:
                con.execute(f"DROP TABLE IF EXISTS {t_name}")
                con.execute(f"CREATE TABLE {t_name} AS SELECT * FROM t")
                con.commit()

        util.log_mini_task("Database created")

        # delete the sample experiment
        with duckdb.connect(config.EXPERIMENTS_DATABASE_PATH) as con:
            con.execute("DELETE FROM experiments")
            con.commit()

        util.log_mini_task("Sample experiment deleted")

    except Exception as e:
        util.log_warning("Error creating database", e)


def get_experiments():
    """
    Get all experiments from the database.
    :return: DataFrame of experiments
    """
    with get_connection("experiments") as con:
        experiments = con.execute("SELECT * FROM experiments").fetchdf()
    return experiments


def save_experiment(experiment: Experiment):
    """
    Save an experiment to the database
    :param experiment: Experiment
    :return:
    """
    # save to disk
    # save to DuckDB database
    from pydantic import Field

    # cannot support serializing cases so is dropped
    experiment.cases = []

    df = pd.DataFrame([experiment])
    with get_connection("experiments") as con:
        con.append("experiments", df)
        con.commit()
    return None


def clear_experiments():
    """
    Clear all experiments from the database
    :return:
    """
    with get_connection("experiments") as con:
        con.execute("DELETE FROM experiments")
        con.commit()
    return True


if __name__ == "__main__":
    print(
        "This file is not meant to be run directly. Please import it in another file."
    )
