from langchain_core.tools import tool
import requests
from llm_calc.tools import openmedcalc
from llm_calc.tools.openmedcalc import util, UberCalcRequestMeld
from llm_calc.tools.openmedcalc import CalcResponse
from llm_calc.tools.openmedcalc import api_datamodel

from typing import Any
from langchain_core.tools import StructuredTool

from llm_calc.lib.config import config
from llm_calc.util.util import log_success

# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ HELPER FUNCTIONS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒


# convert CalcResponse to a dict
def convert_response_to_dict(response: CalcResponse) -> dict | str:
    return {
        "success": response.success,
        "score": response.score,
        "message": response.message,
        "additional_info": response.additional_info,
    }


# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ CALCULATORS AS TOOLS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

# -------------------- MELD-Na --------------------
from llm_calc.tools.openmedcalc.api_datamodel import CalcRequestMeldNa


def _calculate_meld_na(**params) -> dict | str:
    """
    Calculate the MELD-Na (Model for End-Stage Liver Disease Sodium) score.

    This function sends a POST request to the /meld-na endpoint of the OpenMedCalc API
    to calculate the MELD-Na score for an individual.
    """

    # Validation with Pydantic
    try:
        request = CalcRequestMeldNa.model_validate(params)
        return convert_response_to_dict(openmedcalc.calculate_meld_na(request))
    except Exception as e:
        # get traceback string
        traceback_str = "Error:" + str(e.__traceback__)
        return traceback_str


# -------------------- Caprini VTE --------------------
from llm_calc.tools.openmedcalc.api_datamodel import CalcRequestCapriniVte
from llm_calc.tools.openmedcalc.api_datamodel import (
    Mobility as MobilityEnum,
    SurgeryType as SurgeryTypeEnum,
    Sex as SexEnum,
)


def _calculate_caprini_vte(**params) -> dict:
    """
    Calculate the Caprini Score for Venous Thromboembolism (VTE) risk.

    This function sends a POST request to the /caprini-vte endpoint of the OpenMedCalc API
    to calculate the Caprini VTE risk score.

    """

    # Validation with Pydantic
    try:
        request = CalcRequestCapriniVte.model_validate(params)
        return convert_response_to_dict(openmedcalc.calculate_caprini(request))
    except Exception as e:
        # get traceback string
        traceback_str = "Error:" + str(e.__traceback__)
        return traceback_str


# -------------------- Wells DVT --------------------
from llm_calc.tools.openmedcalc.api_datamodel import CalcRequestWellsDvt


def _calculate_wells_dvt(**params) -> dict | str:
    """
    Calculate the Wells' Criteria for Deep Vein Thrombosis (DVT).

    This function sends a POST request to the /wells-dvt endpoint of the OpenMedCalc API
    to calculate the Wells' DVT score.
    """

    remainder = """
        Args:
        active_cancer (bool): Active cancer (treatment or palliation within 6 months).
        bedridden_recently (bool): Bedridden recently (>3 days) or major surgery within 12 weeks.
        calf_swelling (bool): Calf swelling >3 cm compared to the other leg.
        collateral_veins (bool): Collateral (nonvaricose) superficial veins.
        entire_leg_swollen (bool): Entire leg swollen.
        localized_tenderness (bool): Localized tenderness along deep venous system.
        pitting_edema (bool): Pitting edema confined to symptomatic leg.
        paralysis_paresis_or_plaster (bool): Paralysis, paresis, or recent plaster immobilization of lower extremity.
        previous_dvt (bool): Previously documented DVT.
        alternative_diagnosis_as_likely (bool): Alternative diagnosis to DVT as likely or more likely.

    Returns:
        dict: A dictionary containing the calculation results, including:
            - success (bool): Whether the calculation was successful.
            - score (int): The calculated Wells' DVT score.
            - message (str): A summary of the results.
            - additional_info (str): Additional information about the calculation.

    Raises:
        requests.RequestException: If there's an error with the API request.
        ValueError: If the API returns an unexpected response format.
    """

    # Validation with Pydantic
    try:
        request = CalcRequestWellsDvt.model_validate(params)
        return convert_response_to_dict(openmedcalc.calculate_wells_dvt(request))
    except Exception as e:
        # get traceback string
        traceback_str = "The Last Tool Call Had An Error:" + str(e.__traceback__)
        return traceback_str


# -------------------- ARISCAT --------------------

# Import the CalcRequest
from llm_calc.tools.openmedcalc.api_datamodel import CalcRequestAriscat

# Import the enums used in the request
from llm_calc.tools.openmedcalc.api_datamodel import (
    SurgicalIncision as SurgicalIncisionEnum,
)


def _calculate_ariscat(**params) -> dict | str:
    """
    Calculate the ARISCAT (Assess Respiratory Risk in Surgical Patients in Catalonia) score for postoperative pulmonary complications.

    This function sends a POST request to the /ariscat endpoint of the OpenMedCalc API
    to calculate the ARISCAT score.
    """

    remainder = """
    Args:
        age (int): Patient's age in years (range: 18-120).
        spo2 (float): Preoperative SpO2 (%) (range: 70-100).
        respiratory_infection (bool): Respiratory infection in the last month.
        anemia (bool): Preoperative anemia (Hb ≤ 10 g/dL).
        surgical_incision (str): Type of surgical incision ('peripheral', 'upper abdominal', or 'intrathoracic').
        duration_of_surgery (int): Estimated duration of surgery in minutes.
        emergency_procedure (bool): Whether it's an emergency procedure.

    Returns:
        dict: A dictionary containing the calculation results, including:
            - success (bool): Whether the calculation was successful.
            - score (int): The calculated ARISCAT score.
            - risk_class (str): The risk classification (e.g., 'Low risk', 'Intermediate risk', 'High risk').
            - message (str): A summary of the results.
            - additional_info (str): Additional information about the calculation.

    Raises:
        requests.RequestException: If there's an error with the API request.
        ValueError: If the API returns an unexpected response format or if input validation fails.
    """

    # Validation with Pydantic
    try:
        request = CalcRequestAriscat.model_validate(params)
        return convert_response_to_dict(openmedcalc.calculate_ariscat(request))
    except Exception as e:
        # get traceback string
        traceback_str = "Error:" + str(e.__traceback__)
        return traceback_str


# -------------------- CCI --------------------


def _calculate_cci(**params) -> dict | str:
    """
    Calculate the Charlson Comorbidity Index (CCI).

    This function sends a POST request to the /cci endpoint of the OpenMedCalc API
    to calculate the CCI score.
    """

    # Validation with Pydantic
    try:
        request = CalcRequestCCI.model_validate(params)
        return convert_response_to_dict(openmedcalc.calculate_cci(request))
    except Exception as e:
        # get traceback string
        traceback_str = "Error:" + str(e.__traceback__)
        return traceback_str


# -------------------- SOFA --------------------

from llm_calc.tools.openmedcalc.api_datamodel import CalcRequestSOFA


def _calculate_sofa(**params) -> dict | str:
    """
    Calculate the Sequential Organ Failure Assessment (SOFA) score.

    This function sends a POST request to the /sofa endpoint of the OpenMedCalc API
    to calculate the SOFA score.
    """

    # Validation with Pydantic
    try:
        request = CalcRequestSOFA.model_validate(params)
        return convert_response_to_dict(openmedcalc.calculate_sofa(request))
    except Exception as e:
        # get traceback string
        traceback_str = "Error:" + str(e.__traceback__)
        return traceback_str


from llm_calc.tools.openmedcalc.api_datamodel import CalcRequestCCI


# -------------------- PSI/PORT --------------------

from llm_calc.tools.openmedcalc.api_datamodel import CalcRequestPsiPort
from llm_calc.tools.openmedcalc.api_datamodel import Sex


def _calculate_psi_port(**params) -> dict | str:
    """
    Calculate the Pneumonia Severity Index (PSI) / Patient Outcomes Research Team (PORT) Score.

    This function sends a POST request to the /psi-port endpoint of the OpenMedCalc API
    to calculate the PSI/PORT score.
    """

    # Validation with Pydantic
    try:
        request = CalcRequestPsiPort.model_validate(params)
        return convert_response_to_dict(openmedcalc.calculate_psi_port(request))
    except Exception as e:
        # get traceback string
        traceback_str = "Error:" + str(e.__traceback__)
        return traceback_str


# -------------------- GAD7 --------------------

from llm_calc.tools.openmedcalc.api_datamodel import CalcRequestGAD7
from llm_calc.tools.openmedcalc.api_datamodel import GAD7Frequency, GAD7Difficulty


def _calculate_gad7(**params) -> dict | str:
    """
    Calculate the GAD-7 (Generalized Anxiety Disorder-7) score.

    This function sends a POST request to the /gad7 endpoint of the OpenMedCalc API
    to calculate the GAD-7 score.
    """

    # Validation with Pydantic
    try:
        request = CalcRequestGAD7.model_validate(params)
        return convert_response_to_dict(openmedcalc.calculate_gad7(request))
    except Exception as e:
        # get traceback string
        traceback_str = "Error:" + str(e.__traceback__)
        return traceback_str


# -------------------- HAS-BLED --------------------

from llm_calc.tools.openmedcalc.api_datamodel import CalcRequestHASBLED


def _calculate_hasbled(**params) -> dict | str:
    """
    Calculate the HAS-BLED score for major bleeding risk.

    This function sends a POST request to the /hasbled endpoint of the OpenMedCalc API
    to calculate the HAS-BLED score.
    """

    # Validation with Pydantic
    try:
        request = CalcRequestHASBLED.model_validate(params)
        return convert_response_to_dict(openmedcalc.calculate_hasbled(request))
    except Exception as e:
        traceback_str = "Error" + str(e.__traceback__)
        return traceback_str


# -------------------- NIHSS --------------------

from llm_calc.tools.openmedcalc.api_datamodel import CalcRequestNIHSS
from llm_calc.tools.openmedcalc.api_datamodel import (
    NIHSSConsciousness,
    NIHSSQuestions,
    NIHSSCommands,
    NIHSSGaze,
    NIHSSVisualFields,
    NIHSSFacialPalsy,
    NIHSSMotorArm,
    NIHSSMotorLeg,
    NIHSSAtaxia,
    NIHSSSensory,
    NIHSSLanguage,
    NIHSSDysarthria,
    NIHSSExtinction,
)


def _calculate_nihss(**params) -> dict | str:
    """
    Calculate the NIH Stroke Scale/Score (NIHSS).

    This function sends a POST request to the /nihss endpoint of the OpenMedCalc API
    to calculate the NIHSS score.
    """

    # Validation with Pydantic
    try:
        request = CalcRequestNIHSS.model_validate(params)
        return convert_response_to_dict(openmedcalc.calculate_nihss(request))
    except Exception as e:
        traceback_str = "Error" + str(e.__traceback__)
        return traceback_str


# Make structured tools from the functions
# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

# def _calculate_meld_na(
# def _calculate_caprini_vte(
# def _calculate_wells_dvt(
# def _calculate_ariscat(
# def _calculate_sofa(
# def _calculate_cci(
# def _calculate_psi_port(
# def _calculate_gad7(
# def _calculate_hasbled(
# def _calculate_nihss(


from pydantic import ValidationError
from typing import Type


def tool_validation_exception_handler(e: Any, *args: Any, **kwargs: Any):
    # get traceback string
    # from IPython import embed; embed()
    traceback_str = "This tool you called had an error: " + str(e)
    return traceback_str


# meld_na
calculate_meld_na_tool = StructuredTool.from_function(
    func=_calculate_meld_na,
    name="calculate_meld_na",
    description=_calculate_meld_na.__doc__,
    args_schema=api_datamodel.CalcRequestMeldNa,
    handle_validation_error=tool_validation_exception_handler,
    handle_tool_error=True,
)

# caprini_vte
calculate_caprini_vte_tool = StructuredTool.from_function(
    func=_calculate_caprini_vte,
    name="calculate_caprini_vte",
    description=_calculate_caprini_vte.__doc__,
    args_schema=api_datamodel.CalcRequestCapriniVte,
    handle_validation_error=tool_validation_exception_handler,
    handle_tool_error=True,
)

# wells_dvt
calculate_wells_dvt_tool = StructuredTool.from_function(
    func=_calculate_wells_dvt,
    name="calculate_wells_dvt",
    description=_calculate_wells_dvt.__doc__,
    args_schema=api_datamodel.CalcRequestWellsDvt,
    handle_validation_error=tool_validation_exception_handler,
    handle_tool_error=True,
)

# ariscat
calculate_ariscat_tool = StructuredTool.from_function(
    func=_calculate_ariscat,
    name="calculate_ariscat",
    description=_calculate_ariscat.__doc__,
    args_schema=api_datamodel.CalcRequestAriscat,
    handle_validation_error=tool_validation_exception_handler,
    handle_tool_error=True,
)

# sofa
calculate_sofa_tool = StructuredTool.from_function(
    func=_calculate_sofa,
    name="calculate_sofa",
    description=_calculate_sofa.__doc__,
    args_schema=api_datamodel.CalcRequestSOFA,
    handle_validation_error=tool_validation_exception_handler,
    handle_tool_error=True,
)

# cci
calculate_cci_tool = StructuredTool.from_function(
    func=_calculate_cci,
    name="calculate_cci",
    description=_calculate_cci.__doc__,
    args_schema=api_datamodel.CalcRequestCCI,
    handle_validation_error=tool_validation_exception_handler,
    handle_tool_error=True,
)
# psi_port
calculate_psi_port_tool = StructuredTool.from_function(
    func=_calculate_psi_port,
    name="calculate_psi_port",
    description=_calculate_psi_port.__doc__,
    args_schema=api_datamodel.CalcRequestPsiPort,
    handle_validation_error=tool_validation_exception_handler,
    handle_tool_error=True,
)

# gad7
calculate_gad7_tool = StructuredTool.from_function(
    func=_calculate_gad7,
    name="calculate_gad7",
    description=_calculate_gad7.__doc__,
    args_schema=api_datamodel.CalcRequestGAD7,
    handle_validation_error=tool_validation_exception_handler,
    handle_tool_error=True,
)

# hasbled
calculate_hasbled_tool = StructuredTool.from_function(
    func=_calculate_hasbled,
    name="calculate_hasbled",
    description=_calculate_hasbled.__doc__,
    args_schema=api_datamodel.CalcRequestHASBLED,
    handle_validation_error=tool_validation_exception_handler,
    handle_tool_error=True,
)

# nihss
calculate_nihss_tool = StructuredTool.from_function(
    func=_calculate_nihss,
    name="calculate_nihss",
    description=_calculate_nihss.__doc__,
    args_schema=api_datamodel.CalcRequestNIHSS,
    handle_validation_error=tool_validation_exception_handler,
    handle_tool_error=True,
)

# Update the omc_toolkit list
omc_toolkit_all = [
    calculate_meld_na_tool,
    calculate_wells_dvt_tool,
    calculate_caprini_vte_tool,
    calculate_ariscat_tool,
    calculate_sofa_tool,
    calculate_cci_tool,
    calculate_psi_port_tool,
    calculate_gad7_tool,
    calculate_hasbled_tool,
    calculate_nihss_tool,
]

omc_toolkit_by_name = {tool.name: tool for tool in omc_toolkit_all}
