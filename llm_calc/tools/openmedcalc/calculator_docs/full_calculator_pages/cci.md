# Charlson Comorbidity Index (CCI)

## INPUTS

+-----------------------------------+-----------------------------------+
| Age                               | **Options:**                      |
|                                   |                                   |
|                                   | -   \<50 years (0)                |
|                                   | -   50--59 years (1)              |
|                                   | -   60--69 years (2)              |
|                                   | -   70--79 years (3)              |
|                                   | -   ≥80 years (4)                 |
+-----------------------------------+-----------------------------------+
| Myocardial infarction             | **Options:**                      |
|                                   |                                   |
| *History of definite or probable  | -   No (0)                        |
| MI (EKG changes and/or enzyme     | -   Yes (1)                       |
| changes)*                         |                                   |
+-----------------------------------+-----------------------------------+
| CHF                               | **Options:**                      |
|                                   |                                   |
| *Exertional or paroxysmal         | -   No (0)                        |
| nocturnal dyspnea and has         | -   Yes (1)                       |
| responded to digitalis,           |                                   |
| diuretics, or afterload reducing  |                                   |
| agents*                           |                                   |
+-----------------------------------+-----------------------------------+
| Peripheral vascular disease       | **Options:**                      |
|                                   |                                   |
| *Intermittent claudication or     | -   No (0)                        |
| past bypass for chronic arterial  | -   Yes (1)                       |
| insufficiency, history of         |                                   |
| gangrene or acute arterial        |                                   |
| insufficiency, or untreated       |                                   |
| thoracic or abdominal aneurysm    |                                   |
| (≥6 cm)*                          |                                   |
+-----------------------------------+-----------------------------------+
| CVA or TIA                        | **Options:**                      |
|                                   |                                   |
| *History of a cerebrovascular     | -   No (0)                        |
| accident with minor or no residua | -   Yes (1)                       |
| and transient ischemic attacks*   |                                   |
+-----------------------------------+-----------------------------------+
| Dementia                          | **Options:**                      |
|                                   |                                   |
| *Chronic cognitive deficit*       | -   No (0)                        |
|                                   | -   Yes (1)                       |
+-----------------------------------+-----------------------------------+
| COPD                              | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (1)                       |
+-----------------------------------+-----------------------------------+
| Connective tissue disease         | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (1)                       |
+-----------------------------------+-----------------------------------+
| Peptic ulcer disease              | **Options:**                      |
|                                   |                                   |
| *Any history of treatment for     | -   No (0)                        |
| ulcer disease or history of ulcer | -   Yes (1)                       |
| bleeding*                         |                                   |
+-----------------------------------+-----------------------------------+
| Liver disease                     | **Options:**                      |
|                                   |                                   |
| *Severe = cirrhosis and portal    | -   None (0)                      |
| hypertension with variceal        | -   Mild (1)                      |
| bleeding history, moderate =      | -   Moderate to severe (3)        |
| cirrhosis and portal hypertension |                                   |
| but no variceal bleeding history, |                                   |
| mild = chronic hepatitis (or      |                                   |
| cirrhosis without portal          |                                   |
| hypertension)*                    |                                   |
+-----------------------------------+-----------------------------------+
| Diabetes mellitus                 | **Options:**                      |
|                                   |                                   |
|                                   | -   None or diet-controlled (0)   |
|                                   | -   Uncomplicated (1)             |
|                                   | -   End-organ damage (2)          |
+-----------------------------------+-----------------------------------+
| Hemiplegia                        | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (2)                       |
+-----------------------------------+-----------------------------------+
| Moderate to severe CKD            | **Options:**                      |
|                                   |                                   |
| *Severe = on dialysis, status     | -   No (0)                        |
| post kidney transplant, uremia,   | -   Yes (2)                       |
| moderate = creatinine \>3 mg/dL   |                                   |
| (0.27 mmol/L)*                    |                                   |
+-----------------------------------+-----------------------------------+
| Solid tumor                       | **Options:**                      |
|                                   |                                   |
|                                   | -   None (0)                      |
|                                   | -   Localized (2)                 |
|                                   | -   Metastatic (6)                |
+-----------------------------------+-----------------------------------+
| Leukemia                          | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (2)                       |
+-----------------------------------+-----------------------------------+
| Lymphoma                          | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (2)                       |
+-----------------------------------+-----------------------------------+
| AIDS                              | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (6)                       |
+-----------------------------------+-----------------------------------+

## FORMULA

Addition of the selected points:

  ------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ------------
  **Variable**                                            **Definition**                                                                                                                                                                          **Points**
  Myocardial infarction                                   History of definite or probable MI (EKG changes and/or enzyme changes)                                                                                                                  1
  Congestive heart failure                                Exertional or paroxysmal nocturnal dyspnea and has responded to digitalis, diuretics, or afterload reducing agents                                                                      1
  Peripheral vascular disease                             Intermittent claudication or past bypass for chronic arterial insufficiency, history of gangrene or acute arterial insufficiency, or untreated thoracic or abdominal aneurysm (≥6 cm)   1
  Cerebrovascular accident or transient ischemic attack   History of a cerebrovascular accident with minor or no residua and transient ischemic attacks                                                                                           1
  Dementia                                                Chronic cognitive deficit                                                                                                                                                               1
  Chronic obstructive pulmonary disease                   \-                                                                                                                                                                                      1
  Connective tissue disease                               \-                                                                                                                                                                                      1
  Peptic ulcer disease                                    Any history of treatment for ulcer disease or history of ulcer bleeding                                                                                                                 1
  Mild liver disease                                      Mild = chronic hepatitis (or cirrhosis without portal hypertension)                                                                                                                     1
  Uncomplicated diabetes                                  \-                                                                                                                                                                                      1
  Hemiplegia                                              \-                                                                                                                                                                                      2
  Moderate to severe chronic kidney disease               Severe = on dialysis, status post kidney transplant, uremia, moderate = creatinine \>3 mg/dL (0.27 mmol/L)                                                                              2
  Diabetes with end-organ damage                          \-                                                                                                                                                                                      2
  Localized solid tumor                                   \-                                                                                                                                                                                      2
  Leukemia                                                \-                                                                                                                                                                                      2
  Lymphoma                                                \-                                                                                                                                                                                      2
  Moderate to severe liver disease                        Severe = cirrhosis and portal hypertension with variceal bleeding history, moderate = cirrhosis and portal hypertension but no variceal bleeding history                                3
  Metastatic solid tumor                                  \-                                                                                                                                                                                      6
  AIDS\*                                                  \-                                                                                                                                                                                      6
  ------------------------------------------------------- --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- ------------

Plus 1 point for every decade age 50 years and over, maximum 4 points.

Note: liver disease and diabetes inputs are mutually exclusive (e.g. do
not give points for both \"mild liver disease\" and \"moderate or severe
liver disease\").

\*This data is from the original Charlson study in 1987, before
the widespread availability of effective antiretroviral therapy. We are
not aware of any re-evaluations of the CCI using more recent data.

## FACTS & FIGURES

10-year survival = 0.983^exp(CCI\*0.9)^, where CCI = Charlson
Comorbidity Index.

## EVIDENCE APPRAISAL
