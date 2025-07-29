# Project:     open-med-calc
# File:        api/main.py
# Created by:  Alex Goodell
import os

# ============== Imports ==============

from fastapi import FastAPI, Request

from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
import numpy as np
from llm_calc.tools.openmedcalc.api_datamodel import *
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import markdown
from llm_calc.util import util
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import pandas as pd
from llm_calc.lib.experiment import ls_client, make_df
from llm_calc.lib.config import config
from llm_calc.lib.datamodel import Arm, ArmSlug, Model, ModelSlug
from llm_calc.lib.datacore import datacore
from os.path import join as path_join
from llm_calc.util import util

load_dotenv()


# ============== Functions ==============


def calc_docs(calculator_name: str):
    return Path(
        f"{util.ROOT_DIR}/llm_calc/tools/openmedcalc/calculator_docs/short_calculator_info/{calculator_name}.md"
    ).read_text()


def full_calculator_pages(calculator_name: str):
    md_text = Path(
        f"{util.ROOT_DIR}/llm_calc/tools/openmedcalc/calculator_docs/full_calculator_pages/{calculator_name}.md"
    ).read_text()
    return md_text


# ============== Content server ==============


app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=util.ROOT_DIR + "/llm_calc/tools/openmedcalc/static"),
    name="static",
)
templates = Jinja2Templates(
    directory=util.ROOT_DIR + "/llm_calc/tools/openmedcalc/templates"
)
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:7777",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import status


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


@app.get("/", response_class=HTMLResponse)
def read_main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
def read_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/contact", response_class=HTMLResponse)
def read_contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


def error_classification_analysis():
    import numpy as np
    from llm_calc.lib.experiment import ls_client, make_df
    from llm_calc.lib.config import config
    from llm_calc.lib.datamodel import Arm, ArmSlug, Model, ModelSlug
    from llm_calc.lib.datacore import datacore
    from os.path import join as path_join
    import plotly.graph_objects as go
    import plotly.express as px
    import pandas as pd
    from llm_calc.util import util

    filename = path_join(
        config.RESULTS_DATA_PATH, "annotation", f"all_error_class_runs_master.pkl"
    )
    loaded_df: pd.DataFrame = pd.read_pickle(filename)

    # Make a copy of the input dataframe
    dfu = loaded_df.copy()

    # Drop columns error_class_one, error_class_two, notes if they exist
    dfu.drop(
        columns=["error_class_one", "error_class_two", "notes"],
        inplace=True,
        errors="ignore",
    )

    # Get run IDs
    run_ids = dfu["id"].tolist()
    print(f"Querying LangSmith for info from {len(run_ids)} runs...")
    current_runs_df = make_df(ls_client.list_runs(run_ids=run_ids))
    print(f"Received data re {len(current_runs_df)} runs from LangSmith")

    # get the annotations for all runs in the database
    error_class_one_df = make_df(
        ls_client.list_feedback(run_ids=run_ids, feedback_key=["error classification"])
    )
    error_class_two_df = make_df(
        ls_client.list_feedback(
            run_ids=run_ids, feedback_key=["error classification second error"]
        )
    )
    notes_df = make_df(ls_client.list_feedback(run_ids=run_ids, feedback_key=["note"]))

    # Merge dfu with error_class_one_df to get the first error classification
    dfu = dfu.merge(
        error_class_one_df[["run_id", "value"]],
        left_on="id",
        right_on="run_id",
        how="left",
    )
    dfu.rename(columns={"value": "error_class_one"}, inplace=True)

    # Merge dfu with error_class_two_df to get the second error classification
    dfu = dfu.merge(
        error_class_two_df[["run_id", "value"]],
        left_on="id",
        right_on="run_id",
        how="left",
    )
    dfu.rename(columns={"value": "error_class_two"}, inplace=True)

    # Function to concatenate notes for each run
    def concatenate_notes(run_id):
        notes = notes_df[notes_df["run_id"] == run_id]["comment"]
        return "\n\n".join(notes)

    # Apply the function to get the concatenated notes for each run
    dfu["notes"] = dfu["id"].apply(concatenate_notes)

    # Drop the extra run_id columns from the merges
    dfu.drop(columns=["run_id_x", "run_id_y"], inplace=True)

    # mark the runs with an error_class_one as having an annotation_status of 'annotated'
    dfu.loc[dfu["error_class_one"].notnull(), "annotation_status"] = "annotated"

    # set url
    dfu["url"] = dfu.app_path.map(lambda x: "https://smith.langchain.com" + str(x))

    # export the dfu to a pkl file and csv file
    filename = path_join(
        config.RESULTS_DATA_PATH, "annotation", f"all_error_class_runs_master.pkl"
    )
    dfu.to_pickle(filename)
    print(f"{len(dfu)} rows written to {filename}")

    filename = path_join(
        config.RESULTS_DATA_PATH, "annotation", f"all_error_class_runs_master.csv"
    )
    dfu.to_pickle(filename)
    print(f"{len(dfu)} rows written to {filename}")

    df = dfu

    print(df[df.notes != ""].tail(1).notes.item())

    import plotly.express as px

    # Create a bar chart for annotation progress
    progress = (
        df.groupby(["assigned_to", "annotation_status"]).size().unstack().fillna(0)
    )
    fig = px.bar(
        progress.reset_index(),
        x="assigned_to",
        y=["annotated", "queued"],
        title="Annotation Progress by User",
        labels={"value": "Number of Annotations", "assigned_to": "User"},
        barmode="stack",
    )
    util.save_fig(fig, "annotation_progress")
    error_class_combined = (
        df["error_class_one"].fillna("NA").to_list()
        + df["error_class_two"].fillna("NA").to_list()
    )


@app.get("/error_classification", response_class=HTMLResponse)
def error_classification(request: Request):
    return templates.TemplateResponse("errors.html", {"request": request})


@app.get("/download_error_classification")
def read_error_classification(request: Request):

    # Perform the error classification analysis
    error_classification_analysis()
    # Path to the CSV file
    csv_file_path = path_join(
        config.RESULTS_DATA_PATH, "annotation", "all_error_class_runs_master.xlsx"
    )

    # Return the CSV file as a response
    return FileResponse(
        csv_file_path,
        media_type="text/xlsx",
        filename="all_error_class_runs_master.xlsx",
    )


# -------------------------------------------- redirects --------------------------------------------

redirects = [
    {"from": "/meld", "to": "/meld-na"},
    {"from": "/chatbot", "to": "/chat"},
    {"from": "/bot", "to": "/chat"},
    {"from": "/chat", "to": "https://chat.openai.com/g/g-mtNkUsX41-openmedcalc"},
    {
        "from": "/paper",
        "to": "https://www.medrxiv.org/content/10.1101/2023.12.13.23299881v1",
    },
    {
        "from": "/preprint",
        "to": "https://www.medrxiv.org/content/10.1101/2023.12.13.23299881v1",
    },
]

for redirect in redirects:
    app.add_api_route(redirect["from"], lambda: RedirectResponse(url=redirect["to"]))


# ------------------------------------ about calculator pages -------------------------------------


def read_full_calculator_page(request: Request):
    # get route
    route_last = str(request.url).split("/")[-1]
    content = markdown.markdown(full_calculator_pages(route_last))
    return templates.TemplateResponse(
        "blank.html", {"request": request, "content": content}
    )


# for each file in calculator_docs/full_calculator_pages, add a route
for file in Path("openmedcalc/calculator_docs/full_calculator_pages").glob("*.md"):
    app.add_route(f"/{file.stem}", read_full_calculator_page)

# ============== API ==============

if os.environ.get("IS_LOCAL_ENV"):
    openapi_url = "/api/openapi.json"
    api_root = "http://localhost:7777/api"
else:
    openapi_url = "https://api.openmedcalc.org/openapi.json"
    api_root = "https://api.openmedcalc.org/"


api = FastAPI(
    swagger_ui_parameters={"url": openapi_url, "openapi_url": openapi_url},
    title="OpenMedCalc API",
    description="OpenMedCalc API helps you calculate medical scores and indices.",
    summary="The open source medical calculator",
    terms_of_service="http://openmedcalc.org/about",
    contact={
        "name": "OpenMedCalc",
        "url": "http://openmedcalc.org/contact",
        "email": "info@openmedcalc.org",
    },
    servers=[{"url": api_root, "description": "primary SSL endpoint"}],
    root_path="/api",
    root_path_in_servers=False,
)
app.mount("/api", api)

import logging

logger = logging.getLogger("api")

# uvicorn.run(app, log_config=log_config)


# 404
@app.api_route("/{path_name:path}", methods=["GET"], response_class=HTMLResponse)
def catch_all(request: Request, path_name: str):
    return templates.TemplateResponse("index.html", {"request": request})


# ================= API Routes ==================


@api.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


# ----------------- Welcome -----------------
@api.get("/", summary="Welcome")
def welcome():
    return {
        "message": "Welcome to the open-med-calc API. Please see the documentation at /docs for more information"
    }


# ------------- Original MELD -----------------


@api.post(
    "/meld",
    summary="Calculate Original MELD Score",
    response_model=CalcResponse,
    description=calc_docs("meld"),
)
def calculate_meld(calc: CalcRequestMeld):
    additional_info = calc_docs("meld")
    # (0.957 * ln(Serum Cr) + 0.378 * ln(Serum Bilirubin) + 1.120 * ln(INR) + 0.643 ) * 10
    if calc.is_on_dialysis:
        calc.creatinine = 4.0
    meld_score = (
        0.957 * np.log(calc.creatinine)
        + 0.378 * np.log(calc.bilirubin)
        + 1.120 * np.log(calc.inr)
        + 0.643
    ) * 10
    meld_score = int(np.round(meld_score, 0))
    # Estimated 3-Month Mortality By MELD Score
    # ≤9 1.9%
    # 10–19 6.0%
    # 20–29 19.6%
    # 30–39 52.6%
    # ≥40 71.3%

    three_month_mortality = 0
    if meld_score <= 9:
        three_month_mortality = 1.9
    elif meld_score <= 19:
        three_month_mortality = 6.0
    elif meld_score <= 29:
        three_month_mortality = 19.6
    elif meld_score <= 39:
        three_month_mortality = 52.6
    else:
        three_month_mortality = 71.3
    message = (
        "The patient's MELD score is "
        + str(meld_score)
        + ". The estimated 3-month mortality is "
        + str(three_month_mortality)
        + "%."
    )
    response = CalcResponse(
        success=True, score=meld_score, message=message, additional_info=additional_info
    )
    return response


# -------------- MELD-Na -----------------


@api.post(
    "/meld-na",
    summary="Calculate MELD-Na Score",
    response_model=CalcResponse,
    description=calc_docs("meld-na"),
)
def calculate_meld_na(calc: CalcRequestMeldNa):
    additional_info = calc_docs("meld-na")

    # All values in US units (Cr and bilirubin in mg/dL, Na in mEq/L, and INR unitless).
    # If bilirubin, Cr, or INR is <1.0, use 1.0.
    if calc.creatinine < 1:
        calc.creatinine = 1
    if calc.bilirubin < 1:
        calc.bilirubin = 1
    if calc.inr < 1:
        calc.inr = 1

    # If any of the following is true, use Cr 4.0:
    # Cr >4.0.
    # ≥2 dialysis treatments within the prior 7 days.
    # 24 hours of continuous veno-venous hemodialysis (CVVHD) within the prior 7 days.
    if calc.creatinine > 4:
        calc.creatinine = 4
    if calc.is_on_dialysis == 1:
        calc.creatinine = 4

    # If Na <125 mmol/L, use 125. If Na >137 mmol/L, use 137.
    if calc.sodium < 125:
        calc.sodium = 125
    if calc.sodium > 137:
        calc.sodium = 137

    # first calculate the MELD(i) = 0.957 × ln(Cr) + 0.378 × ln(bilirubin) + 1.120 × ln(INR) + 0.643
    # Then, round to the tenth decimal place and multiply by 10.
    # confirmed:  np.log is natural log
    meld_i = (
        0.957 * np.log(calc.creatinine)
        + 0.378 * np.log(calc.bilirubin)
        + 1.12 * np.log(calc.inr)
        + 0.643
    )
    meld_i = np.round(meld_i, 2) * 10.0

    # If MELD(i) > 11, perform additional MELD calculation as follows:
    # MELD = MELD(i) + 1.32 × (137 – Na) –  [ 0.033 × MELD(i) × (137 – Na) ]
    if meld_i > 11:
        meld_na = (
            meld_i + 1.32 * (137 - calc.sodium) - (0.033 * meld_i * (137 - calc.sodium))
        )
    else:
        meld_na = meld_i

    # cannot be higher than 40
    if meld_na > 40:
        meld_na = 40

    # round to nearest integer
    meld_na = np.round(meld_na, 0)

    three_month_mortality = 0
    if meld_na <= 9:
        three_month_mortality = 1.9
    elif meld_na <= 19:
        three_month_mortality = 6.0
    elif meld_na <= 29:
        three_month_mortality = 19.6
    elif meld_na <= 39:
        three_month_mortality = 52.6
    else:
        three_month_mortality = 71.3
    message = (
        "The patient's MELD-Na score is "
        + str(meld_na)
        + ". The estimated 3-month mortality is "
        + str(three_month_mortality)
        + "%."
    )
    response = CalcResponse(
        success=True, score=meld_na, message=message, additional_info=additional_info
    )
    return response


# -------------- Caprini VTE -----------------


@api.post(
    "/caprini-vte",
    summary="Calculate the Caprini Score for Venous Thromboembolism",
    response_model=CalcResponse,
    description=calc_docs("caprini-vte"),
)
def calculate_caprini(calc: CalcRequestCapriniVte):
    additional_info = calc_docs("caprini-vte")

    caprini_vte_score = 0

    # age
    if calc.age < 41:
        caprini_vte_score += 0
    if calc.age >= 41 and calc.age <= 60:
        caprini_vte_score += 1
    if calc.age >= 61 and calc.age <= 74:
        caprini_vte_score += 2
    if calc.age >= 75:
        caprini_vte_score += 3

    # sex has no impact on score
    if calc.sex == calc.sex.male:
        caprini_vte_score += 0
    elif calc.sex == calc.sex.male:
        caprini_vte_score += 0

    # type of surgery
    if calc.type_of_surgery == calc.type_of_surgery.none:
        caprini_vte_score += 0
    elif calc.type_of_surgery == calc.type_of_surgery.minor:
        caprini_vte_score += 1
    elif calc.type_of_surgery == calc.type_of_surgery.major:
        caprini_vte_score += 2
    elif calc.type_of_surgery == calc.type_of_surgery.major_lower_extremity:
        caprini_vte_score += 5

    # mobility
    if calc.mobility == calc.mobility.ambulatory:
        caprini_vte_score += 0
    elif calc.mobility == calc.mobility.bedrest:
        caprini_vte_score += 1
    elif calc.mobility == calc.mobility.confined:
        caprini_vte_score += 2

    # BMI
    if calc.bmi <= 25:
        caprini_vte_score += 0
    elif calc.bmi > 25:
        caprini_vte_score += 1

    if calc.recent_major_surgery:
        caprini_vte_score += 1
    if calc.recent_chf:
        caprini_vte_score += 1
    if calc.recent_sepsis:
        caprini_vte_score += 1
    if calc.recent_pna:
        caprini_vte_score += 1
    if calc.recent_preg:
        caprini_vte_score += 1

    if calc.recent_cast:
        caprini_vte_score += 2

    if calc.recent_lower_extremity_or_hip_or_pelvis_fracture:
        caprini_vte_score += 5
    if calc.recent_stroke:
        caprini_vte_score += 5
    if calc.recent_trauma:
        caprini_vte_score += 5
    if calc.recent_spinal_cord_injury:
        caprini_vte_score += 5

    if calc.varicose_veins:
        caprini_vte_score += 1
    if calc.current_swollen_legs:
        caprini_vte_score += 1

    if calc.current_central_venous_access:
        caprini_vte_score += 2

    if calc.history_of_dvt_pe:
        caprini_vte_score += 3
    if calc.family_history_of_thrombosis:
        caprini_vte_score += 3
    if calc.positive_factor_v_leiden:
        caprini_vte_score += 3
    if calc.positive_prothrombin_20210a:
        caprini_vte_score += 3
    if calc.elevated_serum_homocysteine:
        caprini_vte_score += 3
    if calc.positive_lupus_anticoagulant:
        caprini_vte_score += 3
    if calc.elevated_anticardiolipin_antibody:
        caprini_vte_score += 3
    if calc.heparin_induced_thrombocytopenia:
        caprini_vte_score += 3
    if calc.other_congenital_or_acquired_thrombophilia:
        caprini_vte_score += 3

    if calc.history_of_inflammatory_bowel_disease:
        caprini_vte_score += 1
    if calc.acute_mi:
        caprini_vte_score += 1
    if calc.copd:
        caprini_vte_score += 1
    if calc.present_or_previous_malignancy:
        caprini_vte_score += 2
    if calc.other_risk_factors:
        caprini_vte_score += 1

    # risk category
    if caprini_vte_score == 0:
        risk_category = "Lowest"
        risk_percent = "minimal"
    elif 1 <= caprini_vte_score <= 2:
        risk_category = "low"
        risk_percent = "minimal"
    elif 3 <= caprini_vte_score <= 4:
        risk_category = "moderate"
        risk_percent = "0.7%"
    elif 5 <= caprini_vte_score <= 6:
        risk_category = "high"
        risk_percent = "1.8%"
    elif 7 <= caprini_vte_score <= 8:
        risk_category = "high"
        risk_percent = "4.0%"
    elif caprini_vte_score >= 9:
        risk_category = "highest"
        risk_percent = "10.7%"

    #
    # | Caprini Score | Risk category | Risk percent* | Recommended prophylaxis** | Duration of chemoprophylaxis |
    # | 0 | Lowest | Minimal | Early frequent ambulation only, OR at discretion of surgical team: Pneumatic compression devices OR graduated compression stockings | During hospitalization |
    # | 1–2 | Low | Minimal | Pneumatic compression devices ± graduated compression stockings | During hospitalization |
    # | 3–4 | Moderate | 0.7% | Pneumatic compression devices ± graduated compression stockings | During hospitalization |
    # | 5–6 | High | 1.8% | Pneumatic compression devices AND low dose heparin OR low molecular weight heparin | 7–10 days total |
    # | 7-8 | High | 4.0% | Pneumatic compression devices AND low dose heparin OR low molecular weight heparin | 7–10 days total |
    # | ≥9 | Highest | 10.7% | Pneumatic compression devices AND low dose heparin OR low molecular weight heparin | 30 days total |

    message = f"The patient's Caprini VTE risk score is {caprini_vte_score}. This correlates to a {risk_category} risk category and a {risk_percent} risk of VTE during a hospital admission."
    response = CalcResponse(
        success=True,
        score=caprini_vte_score,
        message=message,
        additional_info=additional_info,
    )
    return response


# -------------- Wells DVT -----------------


@api.post(
    "/wells-dvt",
    summary="Calculate Wells Criteria for DVT",
    response_model=CalcResponse,
    description=calc_docs("wells-dvt"),
)
def calculate_wells_dvt(calc: CalcRequestWellsDvt):
    additional_info = calc_docs("wells-dvt")

    wells_dvt_score = 0
    if calc.active_cancer:
        wells_dvt_score += 1
    if calc.bedridden_or_major_surgery_recently:
        wells_dvt_score += 1
    if calc.calf_swelling:
        wells_dvt_score += 1
    if calc.collateral_veins:
        wells_dvt_score += 1
    if calc.entire_leg_swollen:
        wells_dvt_score += 1
    if calc.localized_tenderness:
        wells_dvt_score += 1
    if calc.pitting_edema:
        wells_dvt_score += 1
    if calc.paralysis_paresis_or_plaster:
        wells_dvt_score += 1
    if calc.previous_dvt:
        wells_dvt_score += 1
    if calc.alternative_diagnosis_as_likely:
        wells_dvt_score += -2

    if wells_dvt_score == 0:
        risk_category = "low/unlikely"
        prevalence_of_dvt = "5%"
    if wells_dvt_score == 1 or wells_dvt_score == 2:
        risk_category = "moderate"
        prevalence_of_dvt = "17%"
    if wells_dvt_score >= 3:
        risk_category = "high/likely"
        prevalence_of_dvt = "17-53%"

    message = (
        f"The patient's Wells Criteria for DVT score is {wells_dvt_score}. This corresponds to a {risk_category}"
        f" risk category; individuals in this group had a {prevalence_of_dvt} prevalence of deep vein thrombosis."
    )
    response = CalcResponse(
        success=True,
        score=wells_dvt_score,
        message=message,
        additional_info=additional_info,
    )
    return response


# -------------- PSI/PORT -----------------
@api.post(
    "/psi-port",
    summary="Calculate the PSI/PORT Score Pneumonia Severity Index for CAP",
    response_model=CalcResponse,
    description=calc_docs("psi-port"),
)
def calculate_psi_port(calc: CalcRequestPsiPort):
    additional_info = calc_docs("psi-port")

    psi_port_score = 0

    # demographic: age & gender
    psi_port_score += calc.age
    if calc.sex == calc.sex.female:
        psi_port_score -= 10

    # nursing home resident
    if calc.nursing_home_resident:
        psi_port_score += 10

    # Coexisting illnesses
    if calc.neoplastic_disease:
        psi_port_score += 30
    if calc.liver_disease:
        psi_port_score += 20
    if calc.congestive_heart_failure:
        psi_port_score += 10
    if calc.cerebrovascular_disease:
        psi_port_score += 10
    if calc.renal_disease:
        psi_port_score += 10

    # physical examination
    if calc.altered_mental_status:
        psi_port_score += 20
    if calc.respiratory_rate >= 30:
        psi_port_score += 20
    if calc.systolic_bp < 90:
        psi_port_score += 20
    if calc.pulse >= 125:
        psi_port_score += 10
    if calc.temperature < 35 or calc.temperature > 39.9:
        psi_port_score += 15

    # lab and radiographic findings
    if calc.ph < 7.35:
        psi_port_score += 30
    if calc.bun >= 30:
        psi_port_score += 20
    if calc.sodium_mmol_L < 130:
        psi_port_score += 20
    # glucose mg/dL
    if calc.glucose >= 250:
        psi_port_score += 10

    if calc.hematocrit < 30:
        psi_port_score += 10
    if calc.pao2 < 60:
        psi_port_score += 10
    if calc.pleural_effusion:
        psi_port_score += 10

    # risk category
    if psi_port_score <= 50:
        risk_category = "low"
        risk_class = "I"
    elif 50 <= psi_port_score <= 70:
        risk_category = "low"
        risk_class = "II"
    elif 71 <= psi_port_score <= 90:
        risk_category = "moderate"
        risk_class = "III"
    elif 91 <= psi_port_score <= 130:
        risk_category = "high"
        risk_class = "IV"
    elif psi_port_score >= 130:
        risk_category = "high"
        risk_class = "V"
    if psi_port_score < 50 & calc.age >= 50:
        risk_category = "low"
        risk_class = "II"

    # | PSI/PORT Score | Risk class | Risk category | Recommended disposition |
    # | <=50 | I | Low risk | Outpatient care |
    # | <= 70 | II | Low risk | Outpatient care |
    # | 71-90 | III | Low risk | Outpatient vs. Observation admission |
    # | 91-130 | IV | Medium risk | Inpatient admission |
    # | >=130 | V | High risk | Inpatient admission |

    message = f"The patient's PSI/PORT score is {psi_port_score}. This correlates to a risk class {risk_class} with {risk_category} risk mortality for patients with community-acquired pneumonia."
    response = CalcResponse(
        success=True,
        score=psi_port_score,
        message=message,
        additional_info=additional_info,
    )
    return response


# ARISCAT Score
@api.post(
    "/ariscat",
    summary="Calculate the ARISCAT Score for Postoperative Pulmonary Complications",
    response_model=CalcResponse,
    description=calc_docs("ariscat"),
)
def calculate_ariscat(calc: CalcRequestAriscat):
    additional_info = calc_docs("ariscat")

    ariscat_score = 0

    # Age
    if 51 <= calc.age <= 80:
        ariscat_score += 3
    elif calc.age > 80:
        ariscat_score += 16

    # Preoperative SpO2
    if 91 <= calc.preoperative_spo2 <= 95:
        ariscat_score += 8
    elif calc.preoperative_spo2 <= 90:
        ariscat_score += 24

    # Respiratory infection in the last month
    if calc.respiratory_infection_with_fever_and_antibiotics:
        ariscat_score += 17

    # Preoperative anemia
    if calc.preoperative_anemia:
        ariscat_score += 11

    # Surgical incision
    if calc.surgical_incision == SurgicalIncision.upper_abdominal:
        ariscat_score += 15
    elif calc.surgical_incision == SurgicalIncision.intrathoracic:
        ariscat_score += 24

    # Duration of surgery
    if 2 <= calc.duration_of_surgery <= 3:
        ariscat_score += 16
    elif calc.duration_of_surgery > 3:
        ariscat_score += 23

    # Emergency procedure
    if calc.emergency_procedure:
        ariscat_score += 8

    # Risk category
    if ariscat_score < 26:
        risk_category = "Low"
        risk_percentage = "1.6%"
    elif 26 <= ariscat_score <= 44:
        risk_category = "Intermediate"
        risk_percentage = "13.3%"
    else:
        risk_category = "High"
        risk_percentage = "42.1%"

    message = f"The patient's ARISCAT score is {ariscat_score}. This correlates to a {risk_category} risk category with a {risk_percentage} risk of postoperative pulmonary complications."
    response = CalcResponse(
        success=True,
        score=ariscat_score,
        message=message,
        additional_info=additional_info,
    )
    return response


# Charlson Comorbidity Index (CCI)
@api.post(
    "/cci",
    summary="Calculate the Charlson Comorbidity Index",
    response_model=CalcResponse,
    description=calc_docs("cci"),
)
def calculate_cci(calc: CalcRequestCCI):

    additional_info = calc_docs("cci")

    cci_score = 0

    # Age score
    if calc.age < 50:
        cci_score += 0
    elif 50 <= calc.age <= 59:
        cci_score += 1
    elif 60 <= calc.age <= 69:
        cci_score += 2
    elif 70 <= calc.age <= 79:
        cci_score += 3
    else:
        cci_score += 4

    # Comorbidity scores
    if calc.myocardial_infarction:
        cci_score += 1
    if calc.congestive_heart_failure:
        cci_score += 1
    if calc.peripheral_vascular_disease:
        cci_score += 1
    if calc.cerebrovascular_disease:
        cci_score += 1
    if calc.dementia:
        cci_score += 1
    if calc.chronic_pulmonary_disease:
        cci_score += 1
    if calc.rheumatic_disease:
        cci_score += 1
    if calc.peptic_ulcer_disease:
        cci_score += 1
    if calc.liver_disease == CCILiverDisease.YES_MILD:
        cci_score += 1
    if calc.liver_disease == CCILiverDisease.YES_MODERATE_SEVERE:
        cci_score += 3
    if calc.diabetes == CCIDiabetesType.UNCOMPLICATED:
        cci_score += 1
    if calc.diabetes == CCIDiabetesType.END_ORGAN_DAMAGE:
        cci_score += 2
    if calc.hemiplegia_or_paraplegia:
        cci_score += 2
    if calc.renal_disease:
        cci_score += 2
    if calc.solid_tumor == CCISolidTumor.YES_LOCALIZED:
        cci_score += 2
    if calc.solid_tumor == CCISolidTumor.YES_WITH_METASTASIS:
        cci_score += 6
    if calc.aids_hiv:
        cci_score += 6
    if calc.leukemia:
        cci_score += 2
    if calc.lymphoma:
        cci_score += 2

    # Calculate 10-year survival
    ten_year_survival = round(0.983 ** (2.71828 ** (cci_score * 0.9)) * 100, 0)

    message = f"The patient's Charlson Comorbidity Index (CCI) score is {cci_score}. The estimated 10-year survival is {ten_year_survival}%."

    response = CalcResponse(
        success=True,
        score=cci_score,
        message=message,
        additional_info=additional_info,
    )
    return response


# GAD-7 (General Anxiety Disorder-7)
@api.post(
    "/gad7",
    summary="Calculate the GAD-7 (General Anxiety Disorder-7) Score",
    response_model=CalcResponse,
    description=calc_docs("gad7"),
)
def calculate_gad7(calc: CalcRequestGAD7):
    additional_info = calc_docs("gad7")

    # make a map of the values
    gad_freq_map = {
        GAD7Frequency.NOT_AT_ALL: 0,
        GAD7Frequency.SEVERAL_DAYS: 1,
        GAD7Frequency.MORE_THAN_HALF_THE_DAYS: 2,
        GAD7Frequency.NEARLY_EVERY_DAY: 3,
    }

    gad7_score = (
        gad_freq_map[calc.feeling_nervous]
        + gad_freq_map[calc.cant_stop_worrying]
        + gad_freq_map[calc.worrying_too_much]
        + gad_freq_map[calc.trouble_relaxing]
        + gad_freq_map[calc.restlessness]
        + gad_freq_map[calc.easily_annoyed]
        + gad_freq_map[calc.feeling_afraid]
    )

    if gad7_score < 5:
        severity = "minimal anxiety"
    elif 5 <= gad7_score < 10:
        severity = "mild anxiety"
    elif 10 <= gad7_score < 15:
        severity = "moderate anxiety"
    else:
        severity = "severe anxiety"

    message = f"The GAD-7 score is {gad7_score}, indicating {severity}. "
    message += f"The patient reports that these problems have made it {calc.difficulty.value} to do work, take care of things at home, or get along with other people."

    response = CalcResponse(
        success=True,
        score=gad7_score,
        message=message,
        additional_info=additional_info,
    )
    return response


@api.post(
    "/hasbled",
    summary="Calculate the HAS-BLED Score for Major Bleeding Risk",
    response_model=CalcResponse,
    description=calc_docs("hasbled"),
)
def calculate_hasbled(calc: CalcRequestHASBLED):
    additional_info = calc_docs("hasbled")

    hasbled_score = sum(
        [
            calc.hypertension,
            calc.severe_renal_disease,
            calc.severe_liver_disease,
            calc.stroke_history,
            calc.prior_major_bleeding,
            calc.labile_inr,
            calc.drugs,
            calc.alcohol,
        ]
    )

    if calc.age >= 65:
        hasbled_score += 1

    if hasbled_score <= 1:
        risk_group = "Low"
        bleeding_risk = "0.9-3.4%"
        recommendation = "Anticoagulation should be considered"
    elif hasbled_score == 2:
        risk_group = "Moderate"
        bleeding_risk = "4.1%"
        recommendation = "Anticoagulation can be considered"
    elif hasbled_score == 3:
        risk_group = "High"
        bleeding_risk = "5.8%"
        recommendation = "Alternatives to anticoagulation should be considered"
    else:
        risk_group = "Very High"
        bleeding_risk = "8.9-9.1% or higher"
        recommendation = "Alternatives to anticoagulation should be strongly considered"

    message = f"The HAS-BLED score is {hasbled_score}, indicating a {risk_group} risk of major bleeding. The estimated risk of major bleeding is {bleeding_risk}. {recommendation}."

    response = CalcResponse(
        success=True,
        score=hasbled_score,
        message=message,
        additional_info=additional_info,
    )
    return response


# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  NIHSS


@api.post(
    "/nihss",
    summary="Calculate the NIH Stroke Scale/Score (NIHSS)",
    response_model=CalcResponse,
    description=calc_docs("nihss"),
)
def calculate_nihss(calc: CalcRequestNIHSS):
    additional_info = calc_docs("nihss")

    # Mapping dictionaries for each NIHSS component
    consciousness_map = {
        NIHSSConsciousness.ALERT: 0,
        NIHSSConsciousness.NOT_ALERT: 1,
        NIHSSConsciousness.OBTUNDED: 2,
        NIHSSConsciousness.COMA: 3,
    }

    questions_map = {
        NIHSSQuestions.ANSWERS_BOTH: 0,
        NIHSSQuestions.ANSWERS_ONE: 1,
        NIHSSQuestions.ANSWERS_NEITHER: 2,
    }

    commands_map = {
        NIHSSCommands.PERFORMS_BOTH: 0,
        NIHSSCommands.PERFORMS_ONE: 1,
        NIHSSCommands.PERFORMS_NEITHER: 2,
    }

    gaze_map = {
        NIHSSGaze.NORMAL: 0,
        NIHSSGaze.PARTIAL_GAZE_PALSY: 1,
        NIHSSGaze.FORCED_DEVIATION: 2,
    }

    visual_map = {
        NIHSSVisualFields.NO_VISUAL_LOSS: 0,
        NIHSSVisualFields.PARTIAL_HEMIANOPIA: 1,
        NIHSSVisualFields.COMPLETE_HEMIANOPIA: 2,
        NIHSSVisualFields.BILATERAL_HEMIANOPIA: 3,
    }

    facial_palsy_map = {
        NIHSSFacialPalsy.NORMAL: 0,
        NIHSSFacialPalsy.MINOR: 1,
        NIHSSFacialPalsy.PARTIAL: 2,
        NIHSSFacialPalsy.COMPLETE: 3,
    }

    motor_arm_map = {
        NIHSSMotorArm.NO_DRIFT: 0,
        NIHSSMotorArm.DRIFT: 1,
        NIHSSMotorArm.SOME_EFFORT_AGAINST_GRAVITY: 2,
        NIHSSMotorArm.NO_EFFORT_AGAINST_GRAVITY: 3,
        NIHSSMotorArm.NO_MOVEMENT: 4,
    }

    motor_leg_map = {
        NIHSSMotorLeg.NO_DRIFT: 0,
        NIHSSMotorLeg.DRIFT: 1,
        NIHSSMotorLeg.SOME_EFFORT_AGAINST_GRAVITY: 2,
        NIHSSMotorLeg.NO_EFFORT_AGAINST_GRAVITY: 3,
        NIHSSMotorLeg.NO_MOVEMENT: 4,
    }

    ataxia_map = {
        NIHSSAtaxia.ABSENT: 0,
        NIHSSAtaxia.PRESENT_IN_ONE_LIMB: 1,
        NIHSSAtaxia.PRESENT_IN_TWO_LIMBS: 2,
    }

    sensory_map = {
        NIHSSSensory.NORMAL: 0,
        NIHSSSensory.MILD_TO_MODERATE_LOSS: 1,
        NIHSSSensory.SEVERE_TO_TOTAL_LOSS: 2,
    }

    language_map = {
        NIHSSLanguage.NO_APHASIA: 0,
        NIHSSLanguage.MILD_TO_MODERATE_APHASIA: 1,
        NIHSSLanguage.SEVERE_APHASIA: 2,
        NIHSSLanguage.MUTE: 3,
    }

    dysarthria_map = {
        NIHSSDysarthria.NORMAL: 0,
        NIHSSDysarthria.MILD_TO_MODERATE: 1,
        NIHSSDysarthria.SEVERE: 2,
    }

    extinction_map = {
        NIHSSExtinction.NO_ABNORMALITY: 0,
        NIHSSExtinction.VISUAL_TACTILE_AUDITORY_SPATIAL_OR_PERSONAL_INATTENTION: 1,
        NIHSSExtinction.PROFOUND_HEMI_INATTENTION: 2,
    }

    nihss_score = (
        consciousness_map[calc.consciousness]
        + questions_map[calc.questions]
        + commands_map[calc.commands]
        + gaze_map[calc.gaze]
        + visual_map[calc.visual]
        + facial_palsy_map[calc.facial_palsy]
        + motor_arm_map[calc.motor_arm_left]
        + motor_arm_map[calc.motor_arm_right]
        + motor_leg_map[calc.motor_leg_left]
        + motor_leg_map[calc.motor_leg_right]
        + ataxia_map[calc.limb_ataxia]
        + sensory_map[calc.sensory]
        + language_map[calc.language]
        + dysarthria_map[calc.dysarthria]
        + extinction_map[calc.extinction]
    )

    severity = ""
    if nihss_score == 0:
        severity = "No stroke symptoms"
    elif 1 <= nihss_score <= 4:
        severity = "Minor stroke"
    elif 5 <= nihss_score <= 15:
        severity = "Moderate stroke"
    elif 16 <= nihss_score <= 20:
        severity = "Moderate to severe stroke"
    elif 21 <= nihss_score <= 42:
        severity = "Severe stroke"

    message = f"The NIHSS score is {nihss_score}, indicating a {severity}."

    response = CalcResponse(
        success=True,
        score=nihss_score,
        message=message,
        additional_info=additional_info,
    )
    return response


@api.post(
    "/sofa",
    summary="Calculate the Sequential Organ Failure Assessment (SOFA) Score",
    response_model=CalcResponse,
    description=calc_docs("sofa"),
)
def calculate_sofa(calc: CalcRequestSOFA):
    additional_info = calc_docs("sofa")

    sofa_score = 0
    # hypotension_and_or_pressors: SOFAVasopressors = Field(
    # ...,
    # title="Hypotension and/or vasopressor use",
    # description="Measure of hypotension. Listed doses are in units of mcg/kg/min. Valid responses include: "
    # "-'No hypotension' (mean arterial pressure is 70 or above),"
    # "- 'MAP <70 mmHg' (hypotension without dopamine, dobutamine, epi, or norepi administation), "
    # "- 'DOPamine ≤5 or DOBUTamine (any dose)' if they are on 5 or less of dopamine or any dose of dobutamine,"
    # "- 'DOPamine >5, EPINEPHrine ≤0.1, or norEPINEPHrine ≤0.1' if 5-15 of dopamine or ≤0.1 of epi or norepi,"
    # " OR "
    # "- 'DOPamine >15, EPINEPHrine >0.1, or norEPINEPHrine >0.1' if they are on more than 15 of dopamine or more than 0.1 of epi or norepi.",

    # Cardiovascular
    cv_sofa_score = 0
    if (
        calc.dopamine_dose > 15
        or calc.epinephrine_dose > 0.1
        or calc.norepinephrine_dose > 0.1
    ):  # 4
        cv_sofa_score += 4
    elif (
        calc.dopamine_dose > 5
        or calc.epinephrine_dose > 0
        or calc.norepinephrine_dose > 0
    ):  # 3
        cv_sofa_score += 3
    elif calc.dopamine_dose > 0 or calc.dobutamine_dose > 0:  # 2
        cv_sofa_score += 2
    elif calc.map < 70:  # 1
        cv_sofa_score += 1
    elif calc.map >= 70:  # 0
        cv_sofa_score += 0
    # print(f"cv_sofa_score: {cv_sofa_score}")

    # PaO2/FiO2*, mmHg
    # ≥400
    # 0
    # 300-399
    # +1
    # 200-299
    # +2
    # ≤199 and NOT mechanically ventilated
    # +2
    # 100-199 and mechanically ventilated
    # +3
    # <100 and mechanically (ventilated
    # +4

    # Respiratory system
    resp_sof_score = 0
    pao2_fio2_ratio = calc.pao2 / (calc.fio2 / 100.0)
    if calc.mechanical_ventilation:
        if pao2_fio2_ratio < 100:
            resp_sof_score += 4
        elif pao2_fio2_ratio < 200:
            resp_sof_score += 3
    else:
        if pao2_fio2_ratio < 300:
            resp_sof_score += 2
        elif pao2_fio2_ratio < 400:
            resp_sof_score += 1
    # print(f"resp_sof_score: {resp_sof_score}")

    # Coagulation
    coag_sofa_score = 0
    if calc.platelets < 20:
        coag_sofa_score += 4
    elif calc.platelets < 50:
        coag_sofa_score += 3
    elif calc.platelets < 100:
        coag_sofa_score += 2
    elif calc.platelets < 150:
        coag_sofa_score += 1
    # print(f"coag_sofa_score: {coag_sofa_score}")

    # Liver
    liver_sofa_score = 0
    if calc.bilirubin >= 12.0:
        liver_sofa_score += 4
    elif calc.bilirubin >= 6.0:
        liver_sofa_score += 3
    elif calc.bilirubin >= 2.0:
        liver_sofa_score += 2
    elif calc.bilirubin >= 1.2:
        liver_sofa_score += 1
    # print(f"liver_sofa_score: {liver_sofa_score}")

    # Central nervous system
    cns_sofa_score = 0
    if calc.glasgow_coma_scale < 6:
        cns_sofa_score += 4
    elif calc.glasgow_coma_scale < 10:
        cns_sofa_score += 3
    elif calc.glasgow_coma_scale < 13:
        cns_sofa_score += 2
    elif calc.glasgow_coma_scale < 15:
        cns_sofa_score += 1
    # print(f"cns_sofa_score: {cns_sofa_score}")

    # Renal
    renal_sofa_score = 0
    if calc.creatinine >= 5.0 or calc.urine_output < 200:
        renal_sofa_score += 4
    elif calc.creatinine >= 3.5 or calc.urine_output < 500:
        renal_sofa_score += 3
    elif calc.creatinine >= 2.0:
        renal_sofa_score += 2
    elif calc.creatinine >= 1.2:
        renal_sofa_score += 1
    # print(f"renal_sofa_score: {renal_sofa_score}")

    sofa_score = (
        cv_sofa_score
        + resp_sof_score
        + coag_sofa_score
        + liver_sofa_score
        + cns_sofa_score
        + renal_sofa_score
    )

    # Interpret the score
    if sofa_score <= 1:
        mortality = "0.0%"
    elif sofa_score <= 3:
        mortality = "6.4%"
    elif sofa_score <= 5:
        mortality = "20.2%"
    elif sofa_score <= 7:
        mortality = "21.5%"
    elif sofa_score <= 9:
        mortality = "33.3%"
    elif sofa_score <= 11:
        mortality = "50.0%"
    elif sofa_score <= 14:
        mortality = "95.2%"
    else:
        mortality = "95.2%"

    message = f"The patient's SOFA score is {sofa_score}. This corresponds to an estimated mortality of {mortality} if this is the initial score."

    response = CalcResponse(
        success=True,
        score=sofa_score,
        message=message,
        additional_info=additional_info,
    )
    return response
