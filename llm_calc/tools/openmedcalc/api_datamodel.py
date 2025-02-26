from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum, IntEnum

var_description = dict()


# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ enums ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒


class CCIDiabetesType(Enum):
    NONE = "NONE"
    UNCOMPLICATED = "UNCOMPLICATED"
    END_ORGAN_DAMAGE = "END_ORGAN_DAMAGE"


class CCISolidTumor(Enum):
    NO = "NO"
    YES_LOCALIZED = "YES_LOCALIZED"
    YES_WITH_METASTASIS = "YES_WITH_METASTASIS"


class CCILiverDisease(Enum):
    NO = "NO"
    YES_MILD = "YES_MILD"
    YES_MODERATE_SEVERE = "YES_MODERATE_SEVERE"


class SurgeryType(Enum):
    none = "not scheduled for surgery"
    minor = "minor surgery"
    major = "major surgery (not lower extremity)"
    major_lower_extremity = "major lower extremity surgery"


class Mobility(Enum):
    ambulatory = "normal/ambulatory"
    bedrest = "bedrest < 72 hours and/or only walking in room"
    confined = "confined to bed >72 hours"


class Sex(Enum):
    male = "M"
    female = "F"


class SurgicalIncision(Enum):
    peripheral = "Peripheral"
    upper_abdominal = "Upper abdominal"
    intrathoracic = "Intrathoracic"


# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ field descriptions ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒


# general ------------------------------------------------------

var_description["success"] = Field(
    ...,
    title="Success",
    description="Describes whether the calculation was successful or not.",
)
var_description["message"] = Field(
    ...,
    title="Result message",
    description="Summarizes the results of the calculation",
)
var_description["additional_info"] = Field(
    ...,
    title="Result information",
    description="Summarizes important information about the calculation",
)

# meld ------------------------------------------------------

var_description["inr"] = Field(
    ...,
    title="International Normalized Ratio",
    description="This is the patient's INR value and should be between 0 and 10, and should include one decimal place.",
    examples=[1.0, 1.5, 2.0],
    gt=0.1,
    lt=10.1,
)
var_description["is_on_dialysis"] = Field(
    title="Is the patient on dialysis?",
    description="Dialysis at least twice in the past seven days or 24-hours of continuous hemodialysis within the "
    "prior 7 days.",
)
var_description["bilirubin"] = Field(
    title="Serum bilirubin",
    description="This is the patient's total bilirubin value in mg/dL and should be between 0 and 10 and include one decimal place.",
    examples=[1.0, 2.5],
    gt=0.2,
    lt=35.2,
)
var_description["creatinine"] = Field(
    title="Serum creatinine",
    description="This is the patient's serum creatinine in mg/dL and should be between 0 and 10 and include one decimal place.",
    examples=[1.2, 2.0],
    gt=0.1,
    lt=15.1,
)
var_description["sodium"] = Field(
    title="Serum sodium",
    description="Also known as 'Na.' This is the patient's serum sodium in mg/dL and should be in a range between "
    "110 and 160.",
    examples=[132, 141],
    gt=110,
    lt=160,
)

# caprini ------------------------------------------------------

var_description["age"] = Field(
    ..., title="Age", description="Age in years", gt=18, lt=120
)
var_description["sex"] = Field(
    ..., title="Sex", description="Recognized sex of the patient, M or F"
)
var_description["type_of_surgery"] = Field(
    ...,
    title="Type of surgery",
    description="Minor surgery does not refer to type of surgery but rather length of anesthesia <45 minutes. Major "
    "surgery refers to procedures with general or regional anesthesia time exceeding 45 minutes. Major"
    "lower extremity surgery refers to procedures anesthesia time exceeding 45 minutes and involving "
    "the hip, knee, thigh, or ankle. The only accepted inputs are: 'not scheduled for surgery', 'minor "
    "surgery', 'major lower extremity surgery', or 'major surgery (not lower extremity)'.",
)
var_description["recent_major_surgery"] = Field(
    ...,
    title="Recent major surgery",
    description="In last 30 days, has patient had major surgery, defined as anesthesia time >45 minutes? Note that if they are admitted for surgery, this does not count.",
)
var_description["recent_chf"] = Field(
    ...,
    title="Recent congestive heart failure",
    description="In last 30 days, has patient had heart failure?",
)
var_description["recent_sepsis"] = Field(
    ...,
    title="Recent sepsis",
    description="In last 30 days, has patient had sepsis, been hospitalized for an infection, or required IV "
    "antibiotics. Do not count pneumonia under this category?",
)
var_description["recent_pna"] = Field(
    ...,
    title="Recent pneumonia",
    description="In last 30 days, has patient had pneumonia or recieved IV antibiotics for a lung infection?",
)
var_description["recent_preg"] = Field(
    ...,
    title="Recent pregnancy or postpartum",
    description="In last 30 days, has patient been pregnant or postpartum?",
)

var_description["recent_cast"] = Field(
    ...,
    title="Recent immobilizing plaster cast",
    description="In last 30 days, has patient had an immobilizing plaster cast?",
)
var_description["recent_lower_extremity_or_hip_or_pelvis_fracture"] = Field(
    ...,
    title="Recent hip, pelvis, or leg fracture",
    description="In last 30 days, has patient had a hip, pelvis, or leg fracture?",
)
var_description["recent_stroke"] = Field(
    ...,
    title="Recent stroke",
    description="In last 30 days, has patient had stroke?",
)
var_description["recent_trauma"] = Field(
    ...,
    title="Recent multiple trauma",
    description="In last 30 days, has patient had multiple trauma?",
)
var_description["recent_spinal_cord_injury"] = Field(
    ...,
    title="Recent acute spinal cord injury causing paralysis",
    description="In last 30 days, has patient had a acute spinal cord injury causing paralysis?",
)
var_description["varicose_veins"] = Field(
    ...,
    title="Varicose veins",
    description="Does the patient have varicose veins?",
)
var_description["current_swollen_legs"] = Field(
    ...,
    title="Current swollen legs",
    description="Does the patient have a current swollen legs?",
)
var_description["current_central_venous_access"] = Field(
    ...,
    title="Current central venous access",
    description="Does the patient have a current central venous access?",
)
var_description["history_of_dvt_pe"] = Field(
    ...,
    title="History of DVT/PE",
    description="Does the patient have a history of DVT/PE?",
)
var_description["family_history_of_thrombosis"] = Field(
    ...,
    title="Family history of thrombosis",
    description="Does the patient have a family history of thrombosis?",
)
var_description["positive_factor_v_leiden"] = Field(
    ...,
    title="Positive Factor V Leiden",
    description="Does the patient have a positive Factor V Leiden?",
)
var_description["positive_prothrombin_20210a"] = Field(
    ...,
    title="Positive prothrombin 20210A",
    description="Does the patient have a positive prothrombin 20210A?",
)
var_description["elevated_serum_homocysteine"] = Field(
    ...,
    title="Elevated serum homocysteine",
    description="Does the patient have a elevated serum homocysteine?",
)
var_description["positive_lupus_anticoagulant"] = Field(
    ...,
    title="Positive lupus anticoagulant",
    description="Does the patient have a positive lupus anticoagulant?",
)
var_description["elevated_anticardiolipin_antibody"] = Field(
    ...,
    title="Elevated anticardiolipin antibody",
    description="Does the patient have a elevated anticardiolipin antibody?",
)
var_description["heparin_induced_thrombocytopenia"] = Field(
    ...,
    title="Heparin-induced thrombocytopenia",
    description="Does the patient have heparin-induced thrombocytopenia?",
)
var_description["other_congenital_or_acquired_thrombophilia"] = Field(
    ...,
    title="Other congenital or acquired thrombophilia",
    description="Does the patient have any other congenital or acquired thrombophilia?",
)
var_description["mobility"] = Field(
    ...,
    title="Mobility",
    description="There are three categories of mobility: 'normal/ambulatory', 'bedrest or only walking in room',"
    " or 'confined to bed >72 hours'.",
)
var_description["history_of_inflammatory_bowel_disease"] = Field(
    ...,
    title="History of inflammatory bowel disease",
    description="Does the patient have a history of inflammatory bowel disease?",
)
var_description["bmi"] = Field(
    ..., title="BMI", description="Body mass index (BMI) of patient in kg/m2?"
)
var_description["acute_mi"] = Field(
    ...,
    title="Acute MI",
    description="Does the patient have an acute MI?",
)
var_description["copd"] = Field(
    ...,
    title="COPD",
    description="Does the patient have COPD?",
)
var_description["present_or_previous_malignancy"] = Field(
    ...,
    title="Present or previous malignancy",
    description="Does the patient have a present or previous malignancy?",
)
var_description["other_risk_factors"] = Field(
    ...,
    title="Other risk factors",
    description="Does the patient have any other risk factors for VTE?",
)

# wells dvt ------------------------------------------------------

var_description["active_cancer"] = Field(
    ...,
    title="Active cancer",
    description="Does the patient have active cancer (treatment or palliation within 6 months)?",
)
var_description["bedridden_or_major_surgery_recently"] = Field(
    ...,
    title="Bedridden or major surgery recently",
    description="Has the patient been bedridden recently (greater than 3 days) or had major surgery within 12 weeks?",
)
var_description["calf_swelling"] = Field(
    ...,
    title="Calf swelling",
    description="Does the patient have calf swelling greater than 3 cm compared to the other leg? (measured 10 cm below tibial tuberosity)",
)
var_description["collateral_veins"] = Field(
    ...,
    title="Collateral veins",
    description="Does the patient have collateral (nonvaricose) superficial veins?",
)
var_description["entire_leg_swollen"] = Field(
    ...,
    title="Entire leg swollen",
    description="Does that patient have an entire leg which is swollen?",
)
var_description["localized_tenderness"] = Field(
    ...,
    title="Localized tenderness",
    description="Does the patient have localized tenderness along a deep venous system?",
)
var_description["pitting_edema"] = Field(
    ...,
    title="Pitting edema",
    description="Does the patient have pitting edema, confined to symptomatic leg?",
)
var_description["paralysis_paresis_or_plaster"] = Field(
    ...,
    title="Paralysis, paresis, or plaster immobilization",
    description="Does the patient have paralysis, paresis, or recent plaster immobilization of the lower extremity?",
)
var_description["previous_dvt"] = Field(
    ...,
    title="Previously documented DVT",
    description="Does the patient have previously-documented DVT?",
)
var_description["alternative_diagnosis_as_likely"] = Field(
    ...,
    title="Alternative diagnosis to DVT",
    description="Does the patient have alternative diagnosis to DVT as likely or more likely?",
)

# PSI / PORT ------------------------------------------------------

var_description["nursing_home_resident"] = Field(
    ...,
    title="Nursing home resident",
    description="Is the patient a nursing home resident?",
)
var_description["neoplastic_disease"] = Field(
    ...,
    title="Neoplastic disease",
    description="Does the patient have neoplastic disease?",
)
var_description["liver_disease"] = Field(
    ...,
    title="Liver disease",
    description="Does the patient have liver disease?",
)
var_description["congestive_heart_failure"] = Field(
    ...,
    title="Congestive heart failure",
    description="Does the patient have congestive heart failure?",
)
var_description["cerebrovascular_disease"] = Field(
    ...,
    title="Cerebrovascular disease",
    description="Does the patient have cerebrovascular disease?",
)
var_description["renal_disease"] = Field(
    ...,
    title="Renal disease",
    description="Does the patient have renal disease?",
)
var_description["altered_mental_status"] = Field(
    ...,
    title="Altered mental status",
    description="Does the patient have altered mental status?",
)
var_description["respiratory_rate"] = Field(
    ...,
    title="Respiratory rate",
    description="Respiratory rate in breaths per minute",
    gt=0,
    lt=100,
)
var_description["systolic_bp"] = Field(
    ...,
    title="Systolic blood pressure",
    description="Systolic blood pressure in mmHg",
    examples=[95, 161],
    gt=0,
    lt=300,
)
var_description["temperature"] = Field(
    ...,
    title="Temperature",
    description="Temperature in degrees Celsius, and include one decimal place",
    examples=[37.2, 39.9],
    gt=0,
    lt=50,
)
var_description["pulse"] = Field(
    ..., title="Pulse", description="Pulse in beats per minute", gt=0, lt=300
)
var_description["ph"] = Field(
    ...,
    title="pH",
    description="The patients pH; should include precision to two decimal places",
    gt=6.40,
    lt=8.40,
    examples=[7.32, 7.45],
)

var_description["glucose"] = Field(
    ..., title="Glucose", description="Glucose in mg/dL", gt=0, lt=1000
)

var_description["bun"] = Field(
    ..., title="BUN", description="Blood urea nitrogen in mg/dL", gt=0, lt=100
)
var_description["sodium_mmol_L"] = Field(
    ...,
    title="Serum sodium in mmol/L",
    description="Also known as 'Na.' This is the patient's serum sodium in mmol/L and should be in a range between "
    "136 and 145 mmol/L",
)
var_description["hematocrit"] = Field(
    ..., title="Hematocrit", description="Hematocrit in %", gt=0, lt=100
)
var_description["pao2"] = Field(
    ..., title="PaO2", description="PaO2 in mmHg", gt=0, lt=1000, examples=[60, 80]
)
var_description["pleural_effusion"] = Field(
    ...,
    title="Pleural effusion",
    description="Does the patient have a pleural effusion?",
    examples=[True, False],
)

# Charlson Comorbidity Index (CCI) variables -----------------------------------------------------
# -

var_description["cci_myocardial_infarction"] = Field(
    ...,
    title="Myocardial infarction",
    description="History of definite or probable MI (EKG changes and/or enzyme changes)?",
)
var_description["cci_congestive_heart_failure"] = Field(
    ...,
    title="Congestive heart failure",
    description="Does the patient have a history of congestive heart failure? ",
)
var_description["cci_peripheral_vascular_disease"] = Field(
    ...,
    title="Peripheral vascular disease",
    description="Does the patient have a history of peripheral vascular disease?",
)
var_description["cci_cerebrovascular_disease"] = Field(
    ...,
    title="Cerebrovascular disease",
    description="Does the patient have a history of cerebrovascular disease?",
)
var_description["cci_dementia"] = Field(
    ...,
    title="Dementia",
    description="Does the patient have an form of dementia?",
)
var_description["cci_chronic_pulmonary_disease"] = Field(
    ...,
    title="COPD",
    description="Does the patient have chronic obstructive pulmonary disease (COPD), including emphysema and/or chronic bronchitis?",
)
var_description["cci_rheumatic_disease"] = Field(
    ...,
    title="Rheumatic disease",
    description="Rheumatic disease",
)
var_description["cci_peptic_ulcer_disease"] = Field(
    ...,
    title="Peptic ulcer disease",
    description="Peptic ulcer disease",
)

var_description["cci_diabetes"] = Field(
    ...,
    title="whether the patient has diabetes, uncomplicated, or with chronic complications",
    description="whether the patient has diabetes, uncomplicated, or with chronic complications",
)
var_description["cci_hemiplegia_or_paraplegia"] = Field(
    ...,
    title="Hemiplegia or paraplegia",
    description="Hemiplegia or paraplegia",
)
var_description["cci_renal_disease"] = Field(
    ...,
    title="Renal disease",
    description="Does the patient have moderate-to-severe CKD? "
    "Defined as moderate = creatinine >3 mg/dL (0.27 mmol/L)"
    "Severe = on dialysis, status post kidney transplant, uremia",
)

var_description["cci_liver_disease"] = Field(
    ...,
    title="None, mild, or moderate-to-severe liver disease",
    description="Does the patient have liver disease, and if so, is it mild or moderate-to-severe? "
    "mild = chronic hepatitis (or cirrhosis without portal hypertension),"
    "moderate = cirrhosis and portal hypertension but no variceal bleeding history, "
    "Severe = cirrhosis and portal hypertension with variceal bleeding history.",
)
var_description["cci_solid_tumor"] = Field(
    ...,
    title="Whether the patient has a solid tumor, localized, or metastasic",
    description="Whether the patient has a solid tumor, localized, or metastasic tumor",
)
var_description["cci_aids_hiv"] = Field(
    ...,
    title="HIV/AIDS",
    description="Does the patient have a history of HIV or AIDS?",
)
var_description["cci_leukemia"] = Field(
    ...,
    title="leukemia",
    description="Has the patient been diagnosed with, or have a history of, leukemia? (not including lymphoma)",
)
var_description["cci_lymphoma"] = Field(
    ...,
    title="lymphoma",
    description="Has the patient been diagnosed with, or have a history of, lymphoma? (not including leukemia)",
)

# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ response and request model ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒


# basic response model
class CalcResponse(BaseModel):
    success: bool = var_description["success"]
    score: Optional[int]
    message: Optional[str] = var_description["message"]
    additional_info: Optional[str] = var_description["additional_info"]


# original meld
class CalcRequestMeld(BaseModel):
    is_on_dialysis: bool = var_description["is_on_dialysis"]
    creatinine: float = var_description["creatinine"]
    bilirubin: float = var_description["bilirubin"]
    inr: float = var_description["inr"]


# meld sodium
class CalcRequestMeldNa(BaseModel):
    is_on_dialysis: bool = var_description["is_on_dialysis"]
    creatinine: float = var_description["creatinine"]
    bilirubin: float = var_description["bilirubin"]
    inr: float = var_description["inr"]
    sodium: float = var_description["sodium"]


class CalcRequestCapriniVte(BaseModel):
    age: int = var_description["age"]
    sex: Sex = var_description["sex"]
    type_of_surgery: SurgeryType = var_description["type_of_surgery"]
    recent_major_surgery: bool = var_description["recent_major_surgery"]
    recent_chf: bool = var_description["recent_chf"]
    recent_sepsis: bool = var_description["recent_sepsis"]
    recent_pna: bool = var_description["recent_pna"]
    recent_preg: bool = var_description["recent_preg"]
    recent_cast: bool = var_description["recent_cast"]
    recent_lower_extremity_or_hip_or_pelvis_fracture: bool = var_description[
        "recent_lower_extremity_or_hip_or_pelvis_fracture"
    ]
    recent_stroke: bool = var_description["recent_stroke"]
    recent_trauma: bool = var_description["recent_trauma"]
    recent_spinal_cord_injury: bool = var_description["recent_spinal_cord_injury"]
    varicose_veins: bool = var_description["varicose_veins"]
    current_swollen_legs: bool = var_description["current_swollen_legs"]
    current_central_venous_access: bool = var_description[
        "current_central_venous_access"
    ]
    history_of_dvt_pe: bool = var_description["history_of_dvt_pe"]
    family_history_of_thrombosis: bool = var_description["family_history_of_thrombosis"]
    positive_factor_v_leiden: bool = var_description["positive_factor_v_leiden"]
    positive_prothrombin_20210a: bool = var_description["positive_prothrombin_20210a"]
    elevated_serum_homocysteine: bool = var_description["elevated_serum_homocysteine"]
    positive_lupus_anticoagulant: bool = var_description["positive_lupus_anticoagulant"]
    elevated_anticardiolipin_antibody: bool = var_description[
        "elevated_anticardiolipin_antibody"
    ]
    heparin_induced_thrombocytopenia: bool = var_description[
        "heparin_induced_thrombocytopenia"
    ]
    other_congenital_or_acquired_thrombophilia: bool = var_description[
        "other_congenital_or_acquired_thrombophilia"
    ]
    mobility: Mobility = var_description["mobility"]
    history_of_inflammatory_bowel_disease: bool = var_description[
        "history_of_inflammatory_bowel_disease"
    ]
    bmi: int = var_description["bmi"]
    acute_mi: bool = var_description["acute_mi"]
    copd: bool = var_description["copd"]
    present_or_previous_malignancy: bool = var_description[
        "present_or_previous_malignancy"
    ]
    other_risk_factors: bool = var_description["other_risk_factors"]


# -------------  wells DVT -----------------
class CalcRequestWellsDvt(BaseModel):
    active_cancer: bool = var_description["active_cancer"]
    bedridden_or_major_surgery_recently: bool = var_description[
        "bedridden_or_major_surgery_recently"
    ]
    calf_swelling: bool = var_description["calf_swelling"]
    collateral_veins: bool = var_description["collateral_veins"]
    entire_leg_swollen: bool = var_description["entire_leg_swollen"]
    localized_tenderness: bool = var_description["localized_tenderness"]
    pitting_edema: bool = var_description["pitting_edema"]
    paralysis_paresis_or_plaster: bool = var_description["paralysis_paresis_or_plaster"]
    previous_dvt: bool = var_description["previous_dvt"]
    alternative_diagnosis_as_likely: bool = var_description[
        "alternative_diagnosis_as_likely"
    ]


# -------------  PSI/PORT  -----------------
class CalcRequestPsiPort(BaseModel):
    age: int = var_description["age"]
    sex: Sex = var_description["sex"]
    nursing_home_resident: bool = var_description["nursing_home_resident"]
    neoplastic_disease: bool = var_description["neoplastic_disease"]
    liver_disease: bool = var_description["liver_disease"]
    congestive_heart_failure: bool = var_description["congestive_heart_failure"]
    cerebrovascular_disease: bool = var_description["cerebrovascular_disease"]
    renal_disease: bool = var_description["renal_disease"]
    altered_mental_status: bool = var_description["altered_mental_status"]
    respiratory_rate: int = var_description["respiratory_rate"]
    systolic_bp: int = var_description["systolic_bp"]
    temperature: float = var_description["temperature"]
    pulse: int = var_description["pulse"]
    ph: float = var_description["ph"]
    bun: int = var_description["bun"]
    sodium_mmol_L: int = var_description["sodium_mmol_L"]
    glucose: int = var_description["glucose"]
    hematocrit: int = var_description["hematocrit"]
    pao2: int = var_description["pao2"]
    pleural_effusion: int = var_description["pleural_effusion"]


# ARISCAT Score
class CalcRequestAriscat(BaseModel):
    age: int = Field(..., title="Age", description="Age in years", ge=0, le=120)
    preoperative_spo2: int = Field(
        ...,
        title="Preoperative SpO2",
        description="Preoperative SpO2 in percentage",
        ge=0,
        le=100,
        examples=[95, 98],
    )
    respiratory_infection_with_fever_and_antibiotics: bool = Field(
        ...,
        title="Respiratory infection in the last month",
        description="Either upper or lower (i.e., URI, bronchitis, pneumonia), with fever AND antibiotic treatment",
    )
    preoperative_anemia: bool = Field(
        ...,
        title="Preoperative anemia",
        description="Preoperative anemia (Hgb ≤10 g/dL)",
    )
    surgical_incision: SurgicalIncision = Field(
        ...,
        title="Surgical incision",
        description="Type of surgical incision: Peripheral, Upper abdominal, or Intrathoracic",
    )
    duration_of_surgery: float = Field(
        ...,
        title="Duration of surgery",
        description="Duration of surgery in hours, with 1 decimal place precision",
    )
    emergency_procedure: bool = Field(
        ...,
        title="Emergency procedure",
        description="Is the surgery marked as an emergency procedure?",
    )


# Charlson Comorbidity Index (CCI)
class CalcRequestCCI(BaseModel):
    age: int = var_description["age"]
    myocardial_infarction: bool = var_description["cci_myocardial_infarction"]
    congestive_heart_failure: bool = var_description["cci_congestive_heart_failure"]
    peripheral_vascular_disease: bool = var_description[
        "cci_peripheral_vascular_disease"
    ]
    cerebrovascular_disease: bool = var_description["cci_cerebrovascular_disease"]
    dementia: bool = var_description["cci_dementia"]
    chronic_pulmonary_disease: bool = var_description["cci_chronic_pulmonary_disease"]
    rheumatic_disease: bool = var_description["cci_rheumatic_disease"]
    peptic_ulcer_disease: bool = var_description["cci_peptic_ulcer_disease"]
    liver_disease: CCILiverDisease = var_description["cci_liver_disease"]
    diabetes: CCIDiabetesType = var_description["cci_diabetes"]
    hemiplegia_or_paraplegia: bool = var_description["cci_hemiplegia_or_paraplegia"]
    renal_disease: bool = var_description["cci_renal_disease"]
    solid_tumor: CCISolidTumor = var_description["cci_solid_tumor"]
    leukemia: bool = var_description["cci_leukemia"]
    lymphoma: bool = var_description["cci_lymphoma"]
    aids_hiv: bool = var_description["cci_aids_hiv"]


# GAD7
class GAD7Frequency(Enum):
    NOT_AT_ALL = "NOT_AT_ALL"
    SEVERAL_DAYS = "SEVERAL_DAYS"
    MORE_THAN_HALF_THE_DAYS = "MORE_THAN_HALF_THE_DAYS"
    NEARLY_EVERY_DAY = "NEARLY_EVERY_DAY"


class GAD7Difficulty(Enum):
    NOT_AT_ALL = "NOT_AT_ALL"
    SOMEWHAT_DIFFICULT = "SOMEWHAT_DIFFICULT"
    VERY_DIFFICULT = "VERY_DIFFICULT"
    EXTREMELY_DIFFICULT = "EXTREMELY_DIFFICULT"


class CalcRequestGAD7(BaseModel):
    feeling_nervous: GAD7Frequency = Field(
        ...,
        title="feeling_nervous",
        description="How often does the patient report feeling nervous, anxious, or on edge?",
    )
    cant_stop_worrying: GAD7Frequency = Field(
        ...,
        title="cant_stop_worrying",
        description="How often does the patient report not being able to stop or control worrying?",
    )
    worrying_too_much: GAD7Frequency = Field(
        ...,
        title="worrying_too_much",
        description="How often does the patient report worrying too much about different things?",
    )
    trouble_relaxing: GAD7Frequency = Field(
        ...,
        title="trouble_relaxing",
        description="How often does the patient report trouble relaxing?",
    )

    restlessness: GAD7Frequency = Field(
        ...,
        title="restlessness",
        description="How often does the patient report being so restless that it's hard to sit still?",
    )
    easily_annoyed: GAD7Frequency = Field(
        ...,
        title="easily_annoyed",
        description="How often does the patient report becoming easily annoyed or irritable?",
    )
    feeling_afraid: GAD7Frequency = Field(
        ...,
        title="feeling_afraid",
        description="How often does the patient report feeling afraid as if something awful might happen?",
    )
    difficulty: GAD7Difficulty = Field(
        ...,
        title="difficulty",
        description="In relation to these issues, how difficult is it for the patient to do work, take care of things at home, or get along with other people?",
    )


# HAS-BLED


class CalcRequestHASBLED(BaseModel):
    hypertension: bool = Field(
        ...,
        title="Hypertension",
        description="Does the patient have uncontrolled hypertension, defined as >160 mmHg systolic?",
    )
    severe_renal_disease: bool = Field(
        ...,
        title="Severe renal disease",
        description="Is the patient receiving dialysis, has received a kidney transplant, or has a Cr >2.26 mg/dL?",
    )
    severe_liver_disease: bool = Field(
        ...,
        title="Sever liver disease",
        description="Does the patient have a history of cirrhosis or bilirubin >2x normal with AST/ALT/AP >3x normal",
    )
    stroke_history: bool = Field(
        ...,
        title="Stroke history",
        description="Does the patient have a history of a stroke?",
    )

    prior_major_bleeding: bool = Field(
        ...,
        title="Does the patient have a history of prior major bleeding or predisposition to bleeding",
    )
    labile_inr: bool = Field(
        ...,
        title="Labile INR",
        description="Does the patient have high or unstable INRs (with time in normal/therapeutic range <60%)?",
    )
    age: int = Field(..., title="Age", description="Age in years")
    drugs: bool = Field(
        ...,
        title="Drugs",
        description="Does the patient take any drugs that increase the risk of bleeding? Do they take anti-platelet medication such as aspirin, clopidogrel, or NSAIDs?",
    )
    alcohol: bool = Field(
        ...,
        title="Alcohol use",
        description="Does the patient consume ≥8 alcoholic drinks per week?",
    )


# NIHSS


class NIHSSConsciousness(Enum):
    ALERT = "ALERT"
    NOT_ALERT = "NOT_ALERT"
    OBTUNDED = "OBTUNDED"
    COMA = "COMA"


class NIHSSQuestions(Enum):
    ANSWERS_BOTH = "ANSWERS_BOTH"
    ANSWERS_ONE = "ANSWERS_ONE"
    ANSWERS_NEITHER = "ANSWERS_NEITHER"


class NIHSSCommands(Enum):
    PERFORMS_BOTH = "PERFORMS_BOTH"
    PERFORMS_ONE = "PERFORMS_ONE"
    PERFORMS_NEITHER = "PERFORMS_NEITHER"


class NIHSSGaze(Enum):
    NORMAL = "NORMAL"
    PARTIAL_GAZE_PALSY = "PARTIAL_GAZE_PALSY"
    FORCED_DEVIATION = "FORCED_DEVIATION"


class NIHSSVisualFields(Enum):
    NO_VISUAL_LOSS = "NO_VISUAL_LOSS"
    PARTIAL_HEMIANOPIA = "PARTIAL_HEMIANOPIA"
    COMPLETE_HEMIANOPIA = "COMPLETE_HEMIANOPIA"
    BILATERAL_HEMIANOPIA = "BILATERAL_HEMIANOPIA"


class NIHSSFacialPalsy(Enum):
    NORMAL = "NORMAL"
    MINOR = "MINOR"
    PARTIAL = "PARTIAL"
    COMPLETE = "COMPLETE"


class NIHSSMotorArm(Enum):
    NO_DRIFT = "NO_DRIFT"
    DRIFT = "DRIFT"
    SOME_EFFORT_AGAINST_GRAVITY = "SOME_EFFORT_AGAINST_GRAVITY"
    NO_EFFORT_AGAINST_GRAVITY = "NO_EFFORT_AGAINST_GRAVITY"
    NO_MOVEMENT = "NO_MOVEMENT"


class NIHSSMotorLeg(Enum):
    NO_DRIFT = "NO_DRIFT"
    DRIFT = "DRIFT"
    SOME_EFFORT_AGAINST_GRAVITY = "SOME_EFFORT_AGAINST_GRAVITY"
    NO_EFFORT_AGAINST_GRAVITY = "NO_EFFORT_AGAINST_GRAVITY"
    NO_MOVEMENT = "NO_MOVEMENT"


class NIHSSAtaxia(Enum):
    ABSENT = "ABSENT"
    PRESENT_IN_ONE_LIMB = "PRESENT_IN_ONE_LIMB"
    PRESENT_IN_TWO_LIMBS = "PRESENT_IN_TWO_LIMBS"


class NIHSSSensory(Enum):
    NORMAL = "NORMAL"
    MILD_TO_MODERATE_LOSS = "MILD_TO_MODERATE_LOSS"
    SEVERE_TO_TOTAL_LOSS = "SEVERE_TO_TOTAL_LOSS"


class NIHSSLanguage(Enum):
    NO_APHASIA = "NO_APHASIA"
    MILD_TO_MODERATE_APHASIA = "MILD_TO_MODERATE_APHASIA"
    SEVERE_APHASIA = "SEVERE_APHASIA"
    MUTE = "MUTE"


class NIHSSDysarthria(Enum):
    NORMAL = "NORMAL"
    MILD_TO_MODERATE = "MILD_TO_MODERATE"
    SEVERE = "SEVERE"


class NIHSSExtinction(Enum):
    NO_ABNORMALITY = "NO_ABNORMALITY"
    VISUAL_TACTILE_AUDITORY_SPATIAL_OR_PERSONAL_INATTENTION = (
        "VISUAL_TACTILE_AUDITORY_SPATIAL_OR_PERSONAL_INATTENTION"
    )
    PROFOUND_HEMI_INATTENTION = "PROFOUND_HEMI_INATTENTION"


class CalcRequestNIHSS(BaseModel):
    consciousness: NIHSSConsciousness = Field(
        ...,
        title="Level of Consciousness",
        description="Eyes open spontaneously, to speech, to pain, etc. Separate from orientation.",
    )
    questions: NIHSSQuestions = Field(
        ...,
        title="LOC Questions",
        description="Separate from alertness. How does patient respond to orientation questions: What is your name, what month is it?",
    )
    commands: NIHSSCommands = Field(
        ..., title="LOC Commands", description="Does the patient follow commands?"
    )
    gaze: NIHSSGaze = Field(
        ..., title="Best Gaze", description="Assess horizontal extraocular movement"
    )
    visual: NIHSSVisualFields = Field(
        title="Visual",
        description="Options include: "
        "NO_VISUAL_LOSS;"
        "PARTIAL_HEMIANOPIA;"
        "COMPLETE_HEMIANOPIA;"
        "or "
        "BILATERAL_HEMIANOPIA",
    )
    facial_palsy: NIHSSFacialPalsy = Field(
        ...,
        title="Facial Palsy",
        description="Options include:"
        "Normal symmetry; "
        "Minor paralysis (flat nasolabial fold, smile asymmetry); "
        "Partial paralysis (lower face); "
        "Complete paralysis (upper/lower face), unilateral or bilatreral",
    )
    motor_arm_left: NIHSSMotorArm = Field(
        ...,
        title="Motor Arm - Left",
        description="Options include: "
        "NO_DRIFT. No drift for 10 seconds (normal);"
        "DRIFT. Drift but doesn't hit bed; "
        "SOME_EFFORT_AGAINST_GRAVITY;"
        "NO_EFFORT_AGAINST_GRAVITY;"
        "or "
        "NO_MOVEMENT",
    )
    motor_arm_right: NIHSSMotorArm = Field(
        ...,
        title="Motor Arm - Right",
        description="Options include: "
        "NO_DRIFT. No drift for 10 seconds (normal);"
        "DRIFT. Drift but doesn't hit bed; "
        "SOME_EFFORT_AGAINST_GRAVITY;"
        "NO_EFFORT_AGAINST_GRAVITY;"
        "or "
        "NO_MOVEMENT",
    )
    motor_leg_left: NIHSSMotorLeg = Field(
        ...,
        title="Motor Leg - Left",
        description="Options include: "
        "NO_DRIFT. No drift for 10 seconds (normal);"
        "DRIFT. Drift but doesn't hit bed; "
        "SOME_EFFORT_AGAINST_GRAVITY;"
        "NO_EFFORT_AGAINST_GRAVITY;"
        "or "
        "NO_MOVEMENT",
    )
    motor_leg_right: NIHSSMotorLeg = Field(
        ...,
        title="Motor Leg - Right",
        description="Options include: "
        "NO_DRIFT. No drift for 10 seconds (normal);"
        "DRIFT. Drift but doesn't hit bed; "
        "SOME_EFFORT_AGAINST_GRAVITY;"
        "NO_EFFORT_AGAINST_GRAVITY;"
        "or "
        "NO_MOVEMENT",
    )
    limb_ataxia: NIHSSAtaxia = Field(
        ...,
        title="Limb Ataxia",
        description="Does the patient have ataxia in none, one, or both limbs?",
    )
    sensory: NIHSSSensory = Field(
        ...,
        title="Sensory",
        description="Mild-moderate loss: less sharp/more dull, can sense being touched; "
        "Severe-to-total loss: cannot sense being touched at all",
    )
    language: NIHSSLanguage = Field(
        ...,
        title="Best Language",
        description="Mild-moderate aphasia: some obvious changes, without significant limitation; "
        "Severe aphasia: fragmentary expression, inference needed, cannot identify materials;"
        "Mute/global aphasia: no usable speech/auditory comprehension",
    )
    dysarthria: NIHSSDysarthria = Field(
        ...,
        title="Dysarthria",
        description="Mild-moderate dysarthria: slurring but can be understood; "
        "Severe dysarthria: unintelligible slurring or out of proportion to dysphasia",
    )
    extinction: NIHSSExtinction = Field(
        ...,
        title="Extinction and Inattention",
        description="Options include: No abnormality;"
        "Visual, tactile, auditory, spatial, or personal inattention; "
        "Profound hemi-inattention",
    )


# SOFA


class CalcRequestSOFA(BaseModel):
    pao2: float = Field(
        ...,
        title="PaO2",
        description="Partial pressure of oxygen, PaO₂ in mmHg",
        ge=0,
        le=1000,
        examples=[60, 80],
    )
    fio2: float = Field(
        ...,
        title="FiO2",
        description="FiO₂ of patient, as a percent 21% to 100%",
        ge=21,
        le=100,
        examples=[25, 80],
    )
    mechanical_ventilation: bool = Field(
        ...,
        title="Mechanical ventilation",
        description="Is the patient being mechanically ventilated? This includes CPAP, BiPAP, or intubation",
    )
    platelets: int = Field(
        ..., title="Platelets", description="Platelet count, ×10³/µL"
    )
    glasgow_coma_scale: int = Field(
        ..., title="Glasgow", description="Glasgow Coma Scale", ge=3, le=15
    )
    bilirubin: float = Field(..., title="Bilirubin", description="Bilirubin, mg/dL")
    map: float = Field(
        ..., title="MAP", description="Mean arterial pressure, mmHg", examples=[70, 80]
    )
    dopamine_dose: float = Field(
        ...,
        title="Dopamine dose",
        description="Dopamine dose in mcg/kg/min; note dopamine is also referrred to as 'intropin' or 'dopa'",
        ge=0,
        le=25,
        examples=[5, 15],
    )
    dobutamine_dose: float = Field(
        ...,
        title="Dobutamine dose",
        description="Dobutamine dose in mcg/kg/min; note that dobutamine is also referred to as 'dobutrex'",
        ge=0,
        le=25,
        examples=[5, 15],
    )
    epinephrine_dose: float = Field(
        ...,
        title="Epinephrine dose",
        description="Epinephrine dose in mcg/kg/min; note that epinephrine is also referred to as 'epi' or 'adrenaline'",
        ge=0,
        le=0.5,
        examples=[0.08, 0.12],
    )
    norepinephrine_dose: float = Field(
        ...,
        title="Norepinephrine dose",
        description="Norepinephrine dose in mcg/kg/min; note that norepinephrine is also referred to as 'levophed', 'levo', 'norepi', and 'noradrenaline'",
        ge=0,
        le=0.5,
        examples=[0.08, 0.12],
    )

    creatinine: float = Field(
        ...,
        title="Creatinine",
        description="Creatinine, mg/dL; should include one decimal place",
        ge=0,
        le=20,
        examples=[1.2, 3.5],
    )

    urine_output: float = Field(
        ...,
        title="Urine output",
        description="What is the patient's urine output in mL/day?",
        ge=0,
        le=8000,
        examples=[1000, 2000],
    )


# UberCalcRequests (hold requests)
# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒


class UberCalcRequestMeld(BaseModel):
    input_data: CalcRequestMeld


class UberCalcRequestMeldNa(BaseModel):
    input_data: CalcRequestMeldNa


class UberCalcRequestCapriniVte(BaseModel):
    input_data: CalcRequestCapriniVte


class UberCalcRequestWellsDvt(BaseModel):
    input_data: CalcRequestWellsDvt


class UberCalcRequestPsiPort(BaseModel):
    input_data: CalcRequestPsiPort


class UberCalcRequestAriscat(BaseModel):
    input_data: CalcRequestAriscat


class UberCalcRequestCCI(BaseModel):
    input_data: CalcRequestCCI


class UberCalcRequestGAD7(BaseModel):
    input_data: CalcRequestGAD7


class UberCalcRequestHASBLED(BaseModel):
    input_data: CalcRequestHASBLED


class UberCalcRequestNIHSS(BaseModel):
    input_data: CalcRequestNIHSS


class UberCalcRequestSOFA(BaseModel):
    input_data: CalcRequestSOFA


if __name__ == "__main__":
    print("you've reached this message in error 45342656")
