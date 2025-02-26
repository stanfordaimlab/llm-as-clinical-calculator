from globals import *
from llm_calc.lib.datamodel import *
from llm_calc.lib.config import config
from llm_calc.util import util
import llm_calc.lib.database as database
import pandas as pd
import os
import urllib3
import duckdb


@dataclass
class Datacore:
    """
    Datacore is a class that holds all the data for the LLM experiements.
    It is responsible for loading the data from the database, and providing
    the data to the rest of the application.
    """

    models: Optional[List[Model]] = None
    arms: Optional[List[Arm]] = None
    criterion_options: Optional[List[CriterionOption]] = None
    calculators: Optional[List[Calculator]] = None
    vignette_templates: Optional[List[VignetteTemplate]] = None
    cases: Optional[List[Case]] = None
    case_criteria: Optional[List[CaseCriterion]] = None
    error_types: Optional[List[ErrorType]] = None
    _experiments: Optional[List[Experiment]] = None

    class Config:
        arbitrary_types_allowed = True

    def initialize(self, build_database=False):
        if build_database:
            database.build_inputs_database()
        self.models = [Model(**row) for _, row in database.get_models().iterrows()]
        self.arms = [Arm(**row) for _, row in database.get_arms().iterrows()]
        self.criterion_options = [
            CriterionOption(**row)
            for _, row in database.get_criterion_options().iterrows()
        ]
        self.calculators = [
            Calculator(**row) for _, row in database.get_calculators().iterrows()
        ]
        self.vignette_templates = database.get_vignette_templates()
        self._experiments = [
            Experiment(**row) for _, row in database.get_experiments().iterrows()
        ]

        # self.cases = database.get_cases()
        # self.case_criteria = database.get_case_criteria()
        # self.error_types = database.get_error_types()

    def get_calculators(self):
        default_calculator_slugs = config.get("DEFAULT_SELECTED_CALCULATORS_SLUGS")
        return [
            calc for calc in self.calculators if calc.slug in default_calculator_slugs
        ]

    def add_experiment(self, experiment: Experiment):
        if self._experiments is None:
            self._experiments = [experiment]
        else:
            self._experiments.append(experiment)
        # save to disk
        database.save_experiment(experiment)

    def get_calculator_by_slug(self, slug: str) -> Calculator:
        return next((calc for calc in self.calculators if calc.slug == slug), None)

    def get_experiments(self):
        return self._experiments

    def get_experiment_by_slug(self, slug: str):
        return next(
            (experiment for experiment in self._experiments if experiment.slug == slug),
            None,
        )

    def clear_experiments(self):
        self._experiments = []
        return database.clear_experiments()

    def get_model_by_slug(self, slug: str):
        return next((model for model in self.models if model.slug == slug), None)

    def get_arm_by_slug(self, slug: str):
        return next((arm for arm in self.arms if arm.slug == slug), None)

    def get_llm_by_arm_slug(self, arm_slug: ArmSlug):
        """
        for a given arm slug, find the associated llm (via model) and return it
        :param arm_slug: ArmSlug
        :return: LLM: Runnable
        """
        arm: Arm = self.get_arm_by_slug(arm_slug)
        return self.get_model_by_slug(arm.model).get_llm()


datacore = Datacore()
datacore.initialize()
