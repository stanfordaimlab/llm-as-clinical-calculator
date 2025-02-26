# PSI/PORT Score: Pneumonia Severity Index for CAP

## INPUTS

+-----------------------------------+-----------------------------------+
| Age                               | **Options:**                      |
+-----------------------------------+-----------------------------------+
| Sex                               | **Options:**                      |
|                                   |                                   |
|                                   | -   Female (-10)                  |
|                                   | -   Male (0)                      |
+-----------------------------------+-----------------------------------+
| Nursing home resident             | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (10)                      |
+-----------------------------------+-----------------------------------+
| Neoplastic disease                | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (30)                      |
+-----------------------------------+-----------------------------------+
| Liver disease history             | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (20)                      |
+-----------------------------------+-----------------------------------+
| CHF history                       | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (10)                      |
+-----------------------------------+-----------------------------------+
| Cerebrovascular disease history   | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (10)                      |
+-----------------------------------+-----------------------------------+
| Renal disease history             | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (10)                      |
+-----------------------------------+-----------------------------------+
| Altered mental status             | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (20)                      |
+-----------------------------------+-----------------------------------+
| Respiratory rate ≥30 breaths/min  | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (20)                      |
+-----------------------------------+-----------------------------------+
| Systolic blood pressure \<90 mmHg | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (20)                      |
+-----------------------------------+-----------------------------------+
| Temperature \<35°C (95°F) or      | **Options:**                      |
| \>39.9°C (103.8°F)                |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (15)                      |
+-----------------------------------+-----------------------------------+
| Pulse ≥125 beats/min              | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (10)                      |
+-----------------------------------+-----------------------------------+
| pH \<7.35                         | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (30)                      |
+-----------------------------------+-----------------------------------+
| BUN ≥30 mg/dL or ≥11 mmol/L       | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (20)                      |
+-----------------------------------+-----------------------------------+
| Sodium \<130 mmol/L               | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (20)                      |
+-----------------------------------+-----------------------------------+
| Glucose ≥250 mg/dL or ≥14 mmol/L  | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (10)                      |
+-----------------------------------+-----------------------------------+
| Hematocrit \<30%                  | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (10)                      |
+-----------------------------------+-----------------------------------+
| Partial pressure of oxygen \<60   | **Options:**                      |
| mmHg or \<8 kPa                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (10)                      |
+-----------------------------------+-----------------------------------+
| Pleural effusion on x-ray         | **Options:**                      |
|                                   |                                   |
|                                   | -   No (0)                        |
|                                   | -   Yes (10)                      |
+-----------------------------------+-----------------------------------+

## FORMULA

Addition of selected points, as above.

## FACTS & FIGURES

**Score interpretation:**

::: table-responsive
  ------------ ---------- -------------------------------------------------------
  Risk Class   Risk       Point Value
  I            Low        None from Comorbidities, PE findings, or Lab findings
  II           Low        ≤70 points
  III          Low        71-90
  IV           Moderate   91-130
  V            High       \>130 total points
  ------------ ---------- -------------------------------------------------------
:::

## EVIDENCE APPRAISAL

The original study created a five-tier risk stratification based on
14199 inpatients with community acquired pneumonia. This was then
validated on 38039 inpatients and additionally another 2287 inpatients
and outpatients. Points are assigned based on age, co-morbid disease,
abnormal physical findings, and abnormal laboratory results.

In comparison to the PSI score, CURB-65 offers equal sensitivity of
mortality prediction due to community acquired pneumonia. Notably,
CURB-65 (74.6%) has a higher specificity than PSI (52.2%). However,
CURB-65 had a lower sensitivity than PSI in predicting ICU admission.
