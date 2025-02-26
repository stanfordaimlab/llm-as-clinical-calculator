import json

from parsy import success

from llm_calc.util import util
from llm_calc.lib import database
from llm_calc.lib.config import config
from llm_calc.lib.datacore import datacore
from llm_calc.lib.datamodel import *
import yaml
from faker import Faker

fake = Faker()

import numpy as np

random_seed = np.random.RandomState(seed=0)


def gen_all_cases(number_of_cases: int = 1):
    """
    Generate all cases and their vignettes
    :param number_of_cases: int: The number of cases to generate for each calculator
    :return: List[Case]: A list of cases with vignettes
    """
    util.log_task("Generating all cases")
    cases = []
    Faker.seed(0)
    case_id = config.STARTING_CASE_ID
    for calc in datacore.get_calculators():
        cases += gen_cases(number_of_cases, calc.slug, case_id)
        case_id += number_of_cases
    return cases


def gen_cases(
    number_of_cases: int, selected_calc_slug: CalculatorSlug, starting_case_id: int
):
    """
    Generate a number of cases and their vignettes
    :param
        number_of_cases: int: The number of cases to generate
        selected_calc_slug: CalculatorSlug: The calculator slug for which to generate cases
    :return: List[Case]: A list of cases with vignettes
    """

    util.log_mini_task(
        f"Generating {number_of_cases} case(s) for {selected_calc_slug.value}"
    )
    cases: List[Case] = []
    for i in range(int(number_of_cases)):
        case_id = starting_case_id + i
        case = Case(
            id=case_id,
            name="Patient "
            + fake.last_name(),  # Name - for easy identification later, not fed to LLM
            calculator_slug=selected_calc_slug,
            vignette=None,
            options=None,
            correct_output=None,
            correct_output_notes=None,
            given_output=None,
            is_correct=None,
        )
        case.vignette, case.options = build_single_vignette(
            selected_calc_slug, seed=case_id
        )

        case.correct_output, case.correct_output_notes = calculate_output_for_case(case)

        util.log_mini_task(
            f"─── Case {i}: {case.vignette[:30]}... Answer: {case.correct_output}"
        )

        cases.append(case)
    return cases


def calculate_output_for_case(case: Case):
    """
    Calculate the correct output for a case
    :param case: Case: The case to calculate the output for
    :return:
        output: str: The correct output for the case
        output_notes: str: Any notes about the output
    """

    calculator_slug = case.calculator_slug
    calculator = datacore.get_calculator_by_slug(calculator_slug)

    # first we need to make a dictionary that stores the criterion options by their criterion slug
    criterion_options = {}
    for option in case.options:
        criterion_options[option.criterion_slug] = option

    score: int = 0
    output: str = ""
    output_notes: str = ""
    match calculator.slug:
        # ---------------------- Caprini ----------------------
        case CalculatorSlug.caprini:
            # just add up the points for each criterion
            for option in case.options:
                score += option.score_effect
            output = str(score)
            output_notes = str(case)

        # ---------------------- Wells DVT ----------------------
        case CalculatorSlug.wellsdvt:
            # just add up the points for each criterion
            for option in case.options:
                score += option.score_effect
            output = str(score)
            output_notes = str(case)

        #  ---------------------- MeldNa ----------------------
        case CalculatorSlug.meldna:
            # needs actual calculation; rely on openmedcalc
            #
            from llm_calc.tools.openmedcalc import calculate_meld_na, CalcRequestMeldNa

            creatinine = float(criterion_options[CriterionSlug.creatinine].input_string)
            inr = float(criterion_options[CriterionSlug.inr].input_string)
            bilirubin = float(criterion_options[CriterionSlug.bilirubin].input_string)
            sodium = float(criterion_options[CriterionSlug.sodium].input_string)
            is_on_dialysis = (
                criterion_options[CriterionSlug.is_on_dialysis].name
                == "Is_On_Dialysis_True"
            )

            request = CalcRequestMeldNa(
                creatinine=creatinine,
                inr=inr,
                bilirubin=bilirubin,
                sodium=sodium,
                is_on_dialysis=is_on_dialysis,
            )
            # request.creatinine = creatinine
            # request.inr = inr
            # request.bilirubin = bilirubin
            # request.sodium = sodium
            # request.is_on_dialysis = is_on_dialysis
            output_notes = str(request)
            result = calculate_meld_na(request)
            output = str(result.score)

        #  ---------------------- SOFA ----------------------
        case CalculatorSlug.sofa:
            # Calculate SOFA score based on criteria
            # just add up the points for each criterion
            # Note: Urine output is fixed at 1000/24h to avoid more complex math needed
            for option in case.options:
                score += option.score_effect
            output = str(score)
            output_notes = str(case)

        #  ---------------------- PSI/PORT ----------------------
        case CalculatorSlug.psiport:
            for option in case.options:
                score += option.score_effect
            output = str(score)
            output_notes = str(case)

        #  ---------------------- CCI ----------------------
        case CalculatorSlug.cci:
            # Calculate CCI score based on criteria
            # just add up the points for each criterion
            for option in case.options:
                score += option.score_effect
            output = str(score)
            output_notes = str(case)

        #  ---------------------- GAD-7 ----------------------
        case CalculatorSlug.gad7:
            # Calculate GAD-7 score based on criteria
            # just add up the points for each criterion
            for option in case.options:
                score += option.score_effect
            output = str(score)
            output_notes = str(case)

        #  ---------------------- ARISCAT ----------------------
        case CalculatorSlug.ariscat:
            # Calculate ARISCAT score based on criteria
            for option in case.options:
                score += option.score_effect
            output = str(score)
            output_notes = str(case)

        #  ---------------------- NIHSS ----------------------
        case CalculatorSlug.nihss:
            # Calculate NIHSS score based on criteria
            for option in case.options:
                score += option.score_effect
            output = str(score)
            output_notes = str(case)

        #  ---------------------- HASBLED ----------------------
        case CalculatorSlug.hasbled:
            score = 0
            for option in case.options:
                score += option.score_effect
            output = str(score)
            output_notes = str(case)

    return output, output_notes


def save_cases(cases: List[Case], filename: str, dataset_name: str):
    """
    Save a list of cases to a file
    :param cases: List[Case]: A list of cases
    :param filename: str: The filename to save the cases to
    :return: success: bool: True if the cases were saved successfully
    """
    util.log_task(f"Saving cases to ...{filename[15:]}")

    import dataclasses
    from typing import List
    from pydantic import RootModel

    json_string = "[\n"
    for case in cases:
        json_string += RootModel[Case](case).model_dump_json(indent=4) + ",\n"
    json_string = json_string[:-2] + "\n]"

    with open(filename, "w") as f:
        f.write(json_string)

    # # save to datset_name + ".json" as well
    # with open(dataset_name + ".json", "w") as f:
    #     f.write(json_string)

    return True


def load_cases(filename: str):
    """
    Load a list of cases from a file
    :param filename: str: The filename to load the cases from
    :return: List[Case]: A list of cases
    """
    util.log_task(f"Loading cases from ...{filename[15:]}")
    cases: List[Case] = []
    with open(filename, "r") as f:
        cases = json.load(f)
    # convert the json to Case objects
    for i, case in enumerate(cases):
        cases[i] = Case(**case)
    return cases


def clear_cases():
    """
    Clear all cases
    :return: success: bool: True if the cases were cleared successfully
    """
    success: bool = False
    proceed = util.confirm(
        "Are you sure you want to clear all cases? (delete cases.json)?"
    )
    if proceed:
        util.log_task("Clearing all cases")
        with open("cases.json", "w") as f:
            f.write("[]")
            success = True
        util.log_success("Cases cleared successfully")
    return success


# ----------------- VIGNETTE -----------------


# TODO could be implemented per template
def build_single_vignette(selected_calc_slug: CalculatorSlug, seed: int):
    """
    Build a single vignette for the specified calculator.

    This function selects a vignette template for the given calculator slug, validates the template criteria
    against the available criteria options, and fills the template with randomly selected options.

    :param selected_calc_slug: CalculatorSlug - The slug identifying the calculator for which the vignette is to be built.
    :return: tuple - A tuple containing:
        - template_string (str): The filled vignette template as a string.
        - selected_options (List[CriterionOption]): A list of selected criterion options used to fill the template.
    """
    import re

    # get the vignette template for the calculator
    templates = pd.DataFrame(datacore.vignette_templates)
    templates = templates[templates.calculator_slug == selected_calc_slug]

    # get the criteria from the template
    # each template contains criteria placeholders enclosed in {}
    template_criteria = []
    for t in templates.iterrows():
        criteria = re.findall(r"\{(.*?)}", t[1].template)
        for c in criteria:
            template_criteria.append(c)

    # remove duplicates
    template_criteria = list(set(template_criteria))
    template_criteria = [CriterionSlug(c) for c in template_criteria]
    # print(template_criteria)

    # get the criterion options for the calculator
    criterion_options = pd.DataFrame(datacore.criterion_options)
    sel_criterion_options = criterion_options[
        criterion_options["calculator_slug"] == selected_calc_slug
    ]
    calculator_criteria = sel_criterion_options.criterion_slug.unique()
    calculator_criteria = [CriterionSlug(c) for c in calculator_criteria]
    # print(calculator_criteria)

    # get the "BASE" criteria which are common to all calculators; stored in the same place
    base_criteria = criterion_options[
        criterion_options["calculator_slug"] == CalculatorSlug.BASE
    ]
    base_criteria = base_criteria.criterion_slug.unique()
    base_criteria = [CriterionSlug(c) for c in base_criteria]

    # remove any base criteria from the template criteria
    specific_template_criteria = [
        c for c in template_criteria if c not in base_criteria
    ]

    # error if there is disagreement between the template and the criterion options
    if set(specific_template_criteria) != set(calculator_criteria):
        util.log_error(
            f"Disagreement between template and criterion options for {selected_calc_slug.value}"
        )
    else:
        util.log(
            f"Agreement between template and criterion options for {selected_calc_slug.value}"
        )

    # now the templates has been validated, we can build a vignette.
    # we will choose a template at random
    template = templates.sample(n=1, random_state=seed)
    template_string = template.template.values[0]

    # sort template criteria to ensure consistent ordering (important for reproducibility)
    template_criteria.sort()

    # now we need to fill in the template with the criterion options
    # we will choose a random option for each criterion
    selected_options = []
    c_seed = seed
    for c in template_criteria:
        # each patient-criterium pair should have a unique seed
        selected_option = criterion_options[
            criterion_options.criterion_slug == c
        ].sample(n=1, random_state=c_seed)
        selected_options += selected_option.to_dict("records")
        template_string = template_string.replace(
            f"{{{c.value}}}", selected_option.input_string.values[0]
        )
        c_seed += 1

    # revert the criterion options to a list of CriterionOption objects
    selected_options = [CriterionOption(**row) for row in selected_options]
    # template_string = f"Case # {seed}: {template_string}"

    return template_string, selected_options


if __name__ == "__main__":
    print(save_cases(gen_all_cases(), "cases.json"))
    # print(datacore.get_default_calculators())
    print(
        "This file is not meant to be run directly. Please import it in another file."
    )
