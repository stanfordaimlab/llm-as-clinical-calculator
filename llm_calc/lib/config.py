from os import getenv as os_getenv
from os.path import join as path_join
from llm_calc.lib.datamodel import *


class Config:
    def __init__(self):
        self.options = {}

        # Starting case ID (to continue a simulation)
        self.STARTING_CASE_ID = 500

        # Calculators
        self.DEFAULT_SELECTED_CALCULATORS_SLUGS = [
            CalculatorSlug.nihss,
            CalculatorSlug.hasbled,
            CalculatorSlug.meldna,
            CalculatorSlug.gad7,
            CalculatorSlug.sofa,
            CalculatorSlug.psiport,
            CalculatorSlug.wellsdvt,
            CalculatorSlug.caprini,
            CalculatorSlug.cci,
            CalculatorSlug.ariscat,
        ]

        # arms
        self.DEFAULT_SELECTED_ARM_SLUGS = [
            # ArmSlug.llama_base,
            ArmSlug.llama_ci,
            # ArmSlug.llama_rag,
            # ArmSlug.llama_rag_ci,
            # ArmSlug.llama_omc,
            # ArmSlug.gpt4_base,
            # ArmSlug.gpt4_ci,
            # ArmSlug.gpt4_rag,
            # ArmSlug.gpt4_rag_ci,
            # ArmSlug.gpt4_omc,
        ]

        # Initialize all configuration options
        self.ROOT_DIR = os_getenv("PROJECT_ROOT_DIR")
        self.DISABLE_OVERWRITE_WARNINGS = False

        # Paths
        self.DATABASE_BUILD_DIR = path_join(self.ROOT_DIR, "data/build_database")
        self.DATABASE_PATH = path_join(
            self.ROOT_DIR, "data/database/inputs_database.db"
        )
        self.DATABASE_REMOTE_XLSX_URL = "https://alx.gd/llm-calc-build-database"
        self.DATABASE_LOCAL_XLSX_PATH = path_join(self.DATABASE_BUILD_DIR, "data.xlsx")
        self.RESULTS_DATA_PATH = path_join(self.ROOT_DIR, "data/results")
        self.FIGURE_PATH = path_join(self.ROOT_DIR, "data/results/figures/from_code")

        # RAG
        self.RAG_DIR = path_join(
            self.ROOT_DIR, "data/build_database/reference_material"
        )

        # OpenAPI / OpenMedCalc
        self.ALLOW_DANGEROUS_REQUEST = True
        self.OPEN_API_SPEC_PATH = path_join(
            self.ROOT_DIR, "omc_api_definition/openapi.yaml"
        )

        # LLMs
        self.DEFAULT_LLM_NAME = ModelSlug.gpt4o_mini
        self.PARSER_LLM_NAME = (
            ModelSlug.gpt4o_mini
        )  # used for last-ditch parsing non-structured outputs
        self.DEFAULT_HUMAN_INPUT = (
            "I have a patient that I'd like to tell you about; I need your help."
            " They are a 41-year-old man who is being evaluated for a liver "
            "transplant. Their serum sodium is 132, serum bilirubin is 1, "
            "serum creatinine is 1.3, and INR is 1.5. They are not on dialysis."
            " What is their MELD-Na score?"
        )

        # Experiments
        self.EXPERIMENTS_DATABASE_PATH = path_join(
            self.ROOT_DIR, "data/database/experiments_database.db"
        )

        # Runtime
        self.DEFAULT_NUMBER_OF_CASES = 10
        self.CASE_LOCAL_PATH = path_join(
            self.ROOT_DIR, "data", "build_database", "cases", "cases.json"
        )
        self.VIGNETTE_LOCAL_PATH = path_join(
            self.ROOT_DIR, "data", "build_database", "vignette_templates"
        )

        # Agents
        self.AGENTS_ARE_VERBOSE = False

        # LLM settings
        self.LLM_MAX_NUM_RETRIES = 5  # number of retries for LLM requests if there is an error within model or refusal to answer
        self.LLM_RETRY_SLEEP = 5  # number of seconds to wait before retrying a request to the LLM in case of an rate limit error
        self.BETWEEN_ARM_WAIT_TIME = 0  # 5 * 60
        self.MAX_CONCURRENCY_LLAMA = 20
        self.MAX_CONCURRENCY_GPT4 = 20

        # Observability (LangSmith)
        self.LANGSMITH_PROJECT_NAME = os_getenv("LANGCHAIN_PROJECT")
        self.LANGCHAIN_PROJECT_NAME = os_getenv("LANGCHAIN_PROJECT")

        self.OMC_BASE_URL = "http://localhost:8000/api"

        self.DEFAULT_LLM = Model(slug=self.DEFAULT_LLM_NAME).get_llm()
        self.PARSER_LLM = Model(slug=self.PARSER_LLM_NAME).get_llm()

        # Set all options in self.options
        for key, value in self.__dict__.items():
            if key.isupper():
                self.set(key, value)

    def set(self, key, value):
        self.options[key] = value

    def get(self, key, default=None):
        return self.options.get(key, default)

    def config_table(self):
        from rich.table import Table

        table = Table(title="Configuration", width=80)
        table.add_column("Variable", justify="right", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        for k, v in self.options.items():
            table.add_row(k, str(v))
        return table


# Create a global instance of the Config class
config = Config()

if __name__ == "__main__":
    print(
        "This file is not meant to be run directly. Please import it in another file."
    )
