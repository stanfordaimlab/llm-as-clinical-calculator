import json
import os
from dotenv import load_dotenv
import pandas as pd
from numpy import number

from typing import Any
from sqlalchemy.dialects.mssql.information_schema import columns
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_together import ChatTogether


from langchain.agents import AgentExecutor

from llm_calc.tools import structured_output

load_dotenv()

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from pydantic.dataclasses import dataclass


# ---------------- models (LLMs) ----------------
class ModelSlug(str, Enum):
    """
    options for the model to use include:
    - gpt4o_mini
    - gpt4o
    - gpt4
    - gpt3_5
    - llama3
    - llama3_tools
    """

    gpt4o_mini = "gpt4o_mini"
    gpt4o = "gpt4o"
    gpt4 = "gpt4"
    gpt3_5 = "gpt3_5"
    llama3 = "llama3"
    llama3_tools = "llama3_tools"
    llama3_1 = "llama3_1"
    claude = "claude"


class ChatHyperbolic(ChatOpenAI):
    def __init__(self, model, temperature):
        api_key = os.getenv("HYPERBOLIC_API_KEY")
        base_url = "https://api.hyperbolic.xyz/v1"

        super().__init__(
            model=model, temperature=temperature, api_key=api_key, base_url=base_url
        )


@dataclass
class Model:
    # https://www.braintrust.dev/docs/cookbook/recipes/LLaMa-3_1-Tools

    slug: ModelSlug
    name: Optional[str] = "name"

    def __init__(self, slug: ModelSlug):
        self.name = slug.value.upper()

    class Config:
        arbitrary_types_allowed = True

    def get_llm(self):
        from langchain_experimental.llms import ChatLlamaAPI
        from llm_calc.tools import structured_output
        from llamaapi import LlamaAPI
        from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

        temperature = 0.1
        # # Replace 'Your_API_Token' with your actual API token
        # llama = LlamaAPI(os.getenv("LLAMA_API_KEY"))
        #
        #
        # endpoint_url = "https://lotsq8mywxvrcvm9.us-east-1.aws.endpoints.huggingface.cloud"
        # endpoint_url_openai_spec = "https://lotsq8mywxvrcvm9.us-east-1.aws.endpoints.huggingface.cloud/v1/"
        # api_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-70B"
        # hf_endpoint = HuggingFaceEndpoint(
        #     temperature=0,
        #     endpoint_url=api_url,
        #     max_new_tokens=2000,
        #     huggingfacehub_api_token=os.getenv("HUGGINGFACE_API_TOKEN")
        # )
        #
        # from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
        #
        # hf_llm = HuggingFaceEndpoint(
        #     repo_id="meta-llama/Llama-3.1-70B",
        #     task="text-generation",
        #     max_new_tokens=5012,
        #     do_sample=False,
        #     repetition_penalty=1.03,
        # )

        from langchain_fireworks import ChatFireworks

        chat_fireworks = ChatFireworks(
            model="accounts/fireworks/models/llama-v3p1-70b-instruct",
            temperature=temperature,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            # other params...
        )

        chat_open_router_llama = ChatOpenAI(
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
            model_name="meta-llama/llama-3.1-70b-instruct",
            temperature=temperature,
            model_kwargs={"parallel_tool_calls": False},
            seed=1,
            #             "provider": {
            #   "quantizations": [
            #     "bf16"
            #   ]
            # },
        )

        chat_open_router_gpt4 = ChatOpenAI(
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
            model_name="openai/gpt-4o",
            temperature=temperature,
            model_kwargs={"parallel_tool_calls": False},
            seed=1,
        )

        chat_openai_gpt4 = ChatOpenAI(
            model="gpt-4o",
            temperature=temperature,
            model_kwargs={"parallel_tool_calls": False},
            seed=1,
        )

        model_definition = {
            ModelSlug.gpt4o_mini: ChatOpenAI(
                model="gpt-4o-mini", temperature=temperature
            ),
            ModelSlug.gpt4o: chat_open_router_gpt4,
            ModelSlug.gpt4: ChatOpenAI(model="gpt-4-turbo", temperature=temperature),
            ModelSlug.gpt3_5: ChatOpenAI(
                model="gpt-3.5-turbo", temperature=temperature
            ),
            ModelSlug.llama3: ChatGroq(
                model="llama3-70b-8192", temperature=temperature
            ),
            ModelSlug.llama3_tools: ChatGroq(
                model="llama3-groq-70b-8192-tool-use-preview", temperature=temperature
            ),
            ModelSlug.llama3_1: chat_open_router_llama,
            ModelSlug.claude: ChatAnthropic(
                model="claude-3-5-sonnet-20240620", temperature=temperature
            ),
        }

        llm = model_definition[self.slug]
        llm.name = self.slug.value
        return llm


# ---------------- calculators ----------------
class CalculatorSlug(str, Enum):
    psiport = "psiport"
    ariscat = "ariscat"
    cci = "cci"
    hmair = "hmair"
    grace = "grace"
    gupta = "gupta"
    osms = "osms"
    abg = "abg"
    pecarn = "pecarn"
    sirs = "sirs"
    freewater = "freewater"
    ag = "ag"
    ciwa = "ciwa"
    ascvd = "ascvd"
    caprini = "caprini"
    ldl = "ldl"
    gad7 = "gad7"
    fena = "fena"
    framingham = "framingham"
    sofa = "sofa"
    curb65 = "curb65"
    gcs = "gcs"
    stopbang = "stopbang"
    perc = "perc"
    mme = "mme"
    meldna = "meldna"
    phq9 = "phq9"
    centor = "centor"
    mivf = "mivf"
    nacorrection = "nacorrection"
    steroidconversion = "steroidconversion"
    hasbled = "hasbled"
    wellsdvt = "wellsdvt"
    fibrosis4 = "fibrosis4"
    heart = "heart"
    cps = "cps"
    nihss = "nihss"
    rcri = "rcri"
    duedates = "duedates"
    ibw = "ibw"
    qtc = "qtc"
    mdrdgfr = "mdrdgfr"
    wellspe = "wellspe"
    bmibsa = "bmibsa"
    ascvd2013 = "ascvd2013"
    cacorrection = "cacorrection"
    map = "map"
    chadsvasc = "chadsvasc"
    ckdepi = "ckdepi"
    crcl = "crcl"
    BASE = "BASE"


@dataclass
class Calculator:
    id: int
    name: str
    description: str
    slug: CalculatorSlug
    pretty_slug: str
    minimum_score: Optional[Any]
    maximum_score: Optional[Any]
    mild_cutoff: Optional[Any]
    severe_cutoff: Optional[Any]


# ---------------- vignette templates ----------------


@dataclass
class VignetteTemplate:
    id: int
    template: str
    calculator_slug: CalculatorSlug


# ---------------- arms ----------------


class ArmSlug(str, Enum):
    gpt4_base = "gpt4_base"
    gpt4_ci = "gpt4_ci"
    gpt4_rag = "gpt4_rag"
    gpt4_rag_ci = "gpt4_rag_ci"
    gpt4_omc = "gpt4_omc"
    llama_base = "llama_base"
    llama_ci = "llama_ci"
    llama_rag = "llama_rag"
    llama_rag_ci = "llama_rag_ci"
    llama_omc = "llama_omc"
    claude_base = "claude_base"
    claude_omc = "claude_omc"


@dataclass
class Arm:
    id: int
    name: str
    slug: ArmSlug
    description: str
    model: ModelSlug
    use_rag: bool
    use_ci: bool
    use_omc: bool


# ---------------- criteria ----------------


class CriterionSlug(str, Enum):
    caprini_age = "caprini_age"
    caprini_sex = "caprini_sex"
    recent_history = "recent_history"
    venous_disease = "venous_disease"
    mobility = "mobility"
    other_pmh = "other_pmh"
    bmi = "bmi"
    surgery = "surgery"
    wells_cancer = "wells_cancer"
    wells_bedridden = "wells_bedridden"
    wells_swelling = "wells_swelling"
    wells_collateral = "wells_collateral"
    wells_entire_leg = "wells_entire_leg"
    wells_tenderness = "wells_tenderness"
    wells_pitting = "wells_pitting"
    wells_paralysis = "wells_paralysis"
    wells_prev_dvt = "wells_prev_dvt"
    wells_alternative = "wells_alternative"
    sodium = "sodium"
    bilirubin = "bilirubin"
    creatinine = "creatinine"
    inr = "inr"
    is_on_dialysis = "is_on_dialysis"
    sofa_pao2 = "sofa_pao2"
    sofa_fio2 = "sofa_fio2"
    sofa_mechanical_ventilation = "sofa_mechanical_ventilation"
    sofa_platelets = "sofa_platelets"
    sofa_glasgow_coma_scale = "sofa_glasgow_coma_scale"
    sofa_bilirubin = "sofa_bilirubin"
    sofa_hypotension_and_or_pressors = "sofa_hypotension_and_or_pressors"
    sofa_creatinine = "sofa_creatinine"
    sofa_urine_output = "sofa_urine_output"
    cci_age = "cci_age"
    cci_myocardial_infarction = "cci_myocardial_infarction"
    cci_congestive_heart_failure = "cci_congestive_heart_failure"
    cci_peripheral_vascular_disease = "cci_peripheral_vascular_disease"
    cci_cerebrovascular_disease = "cci_cerebrovascular_disease"
    cci_dementia = "cci_dementia"
    cci_chronic_pulmonary_disease = "cci_chronic_pulmonary_disease"
    cci_rheumatic_disease = "cci_rheumatic_disease"
    cci_peptic_ulcer_disease = "cci_peptic_ulcer_disease"
    cci_liver_disease = "cci_liver_disease"
    cci_diabetes = "cci_diabetes"
    cci_hemiplegia_or_paraplegia = "cci_hemiplegia_or_paraplegia"
    cci_renal_disease = "cci_renal_disease"
    cci_solid_tumor = "cci_solid_tumor"
    cci_leukemia = "cci_leukemia"
    cci_lymphoma = "cci_lymphoma"
    cci_aids_hiv = "cci_aids_hiv"
    ariscat_age = "ariscat_age"
    ariscat_spo2 = "ariscat_spo2"
    ariscat_respiratory_infection = "ariscat_respiratory_infection"
    ariscat_anemia = "ariscat_anemia"
    ariscat_surgical_incision = "ariscat_surgical_incision"
    ariscat_duration_of_surgery = "ariscat_duration_of_surgery"
    ariscat_emergency_procedure = "ariscat_emergency_procedure"
    psiport_age = "psiport_age"
    psiport_sex = "psiport_sex"
    psiport_nursing_home_resident = "psiport_nursing_home_resident"
    psiport_neoplastic_disease = "psiport_neoplastic_disease"
    psiport_liver_disease = "psiport_liver_disease"
    psiport_congestive_heart_failure = "psiport_congestive_heart_failure"
    psiport_cerebrovascular_disease = "psiport_cerebrovascular_disease"
    psiport_renal_disease = "psiport_renal_disease"
    psiport_altered_mental_status = "psiport_altered_mental_status"
    psiport_respiratory_rate = "psiport_respiratory_rate"
    psiport_systolic_bp = "psiport_systolic_bp"
    psiport_pulse = "psiport_pulse"
    psiport_temperature = "psiport_temperature"
    psiport_ph = "psiport_ph"
    psiport_bun = "psiport_bun"
    psiport_sodium = "psiport_sodium"
    psiport_glucose = "psiport_glucose"
    psiport_hematocrit = "psiport_hematocrit"
    psiport_pao2 = "psiport_pao2"
    psiport_pleural_effusion = "psiport_pleural_effusion"
    gad7_feeling_nervous = "gad7_feeling_nervous"
    gad7_cant_stop_worrying = "gad7_cant_stop_worrying"
    gad7_worrying_too_much = "gad7_worrying_too_much"
    gad7_trouble_relaxing = "gad7_trouble_relaxing"
    gad7_restlessness = "gad7_restlessness"
    gad7_easily_annoyed = "gad7_easily_annoyed"
    gad7_feeling_afraid = "gad7_feeling_afraid"
    gad7_difficulty = "gad7_difficulty"
    hasbled_hypertension = "hasbled_hypertension"
    hasbled_renal_disease = "hasbled_renal_disease"
    hasbled_liver_disease = "hasbled_liver_disease"
    hasbled_stroke_history = "hasbled_stroke_history"
    hasbled_prior_major_bleeding = "hasbled_prior_major_bleeding"
    hasbled_labile_inr = "hasbled_labile_inr"
    hasbled_age = "hasbled_age"
    hasbled_drugs = "hasbled_drugs"
    hasbled_alcohol = "hasbled_alcohol"
    nihss_consciousness = "nihss_consciousness"
    nihss_questions = "nihss_questions"
    nihss_commands = "nihss_commands"
    nihss_gaze = "nihss_gaze"
    nihss_visual_fields = "nihss_visual_fields"
    nihss_facial_palsy = "nihss_facial_palsy"
    nihss_motor_arm_left = "nihss_motor_arm_left"
    nihss_motor_arm_right = "nihss_motor_arm_right"
    nihss_motor_leg_left = "nihss_motor_leg_left"
    nihss_motor_leg_right = "nihss_motor_leg_right"
    nihss_ataxia = "nihss_ataxia"
    nihss_sensory = "nihss_sensory"
    nihss_language = "nihss_language"
    nihss_dysarthria = "nihss_dysarthria"
    nihss_extinction = "nihss_extinction"


@dataclass
class CriterionOption:
    name: str
    input_string: str
    criterion_slug: CriterionSlug
    calculator_slug: CalculatorSlug
    score_effect: int

    # modify the __repr__ method to return a string representation of the object
    # in the form of CriteriaSlug | input_string | score_effect
    def __repr__(self):
        trunc_input = (
            self.input_string[:20] + "..."
            if len(self.input_string) > 20
            else self.input_string
        )
        # foo = f"{self.criterion_slug.value}|{self.name}|{trunc_input}|{self.score_effect}"
        foo = f"{self.name}"
        # foo = json.dumps({ "name": self.name, "input_string": self.input_string, "score_effect": self.score_effect })
        return foo

    # as above for print
    def __str__(self):
        return self.__repr__()


# ================ after casegen ================


@dataclass
class CaseCriterion:
    id: int
    case_slug: Enum
    criterion_slug: Enum
    calculator_slug: CalculatorSlug
    value: str


@dataclass
class ErrorType:
    id: int
    name: str


@dataclass
class Case:
    id: int
    name: str
    calculator_slug: CalculatorSlug
    vignette: Optional[str]
    options: Optional[List[CriterionOption]]
    correct_output: Optional[str]
    correct_output_notes: Optional[str]
    given_output: Optional[str]
    is_correct: Optional[bool]


# ---------------- result ----------------


@dataclass
class LLMInput:
    """
    Used to pass the inputs and metadata of experiements
    """

    human_input: str
    case: Case


@dataclass
class LLMResult:
    """
    Used to pass the results and metadata of experiements
    """

    # case_id: Optional[int] # arm_id: Optional[int] # model_id: Optional[int]
    arm_slug: Optional[ArmSlug] = None
    experiment: Optional[Any] = None
    was_error: Optional[bool] = None
    output_string: Optional[str] = None
    output_string_is_valid_json: Optional[bool] = None
    output_object: Optional[dict] = None  # TODO: change to RawLLMOutputObject
    exception: Optional[Any] = None
    exception_message: Optional[str] = None
    exception_traceback: Optional[str] = None
    extracted_answer: Optional[float] = None
    was_answer_correct: Optional[bool] = None
    num_errored_attempts: Optional[int] = None
    num_attempts: Optional[int] = None
    errored_attempts: Optional[Any] = None
    case: Optional[dict] = None
    raw_response: Any = None
    intermediate_steps: Optional[Any] = None
    human_input: Optional[str] = None
    run: Optional[Any] = None

    def from_dict(self, data):
        # check if is instance of LLMResult
        if isinstance(data, LLMResult):
            return data

        # check if is instance of dict
        elif isinstance(data, dict):
            for field in data:
                setattr(self, field, data[field])
            return self

        # if not instance of LLMResult or dict, return None
        return None


# ================ experiments ================


@dataclass
class Experiment:
    slug: str
    description: str
    git_hash_before_start: Optional[str]
    start_datetime: Optional[str]
    end_datetime: Optional[str]
    is_completed: bool
    number_of_cases: int
    cases: Optional[List[Case]]


@dataclass
class RequestTask:
    slug: str
    case: Case
    arm: Arm
    model: Model
    llm_result: Optional[LLMResult] = None
    is_complete: bool = False
    number_of_attempts: int = 0


# =========== master database/datacore ============


def df_to_classed_list(class_to_convert, pandas_df):
    collection_of_self = pandas_df.apply(lambda row: class_to_convert(*row), axis=1)
    return collection_of_self


if __name__ == "__main__":
    print("hello world")
