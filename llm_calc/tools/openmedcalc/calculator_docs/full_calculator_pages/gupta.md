# Gupta Perioperative Risk for Myocardial Infarction or Cardiac Arrest (MICA)

## INPUTS

+-----------------------------------+-----------------------------------+
| Age                               | **Options:**                      |
+-----------------------------------+-----------------------------------+
| Functional status                 | **Options:**                      |
|                                   |                                   |
|                                   | -   Independent                   |
|                                   | -   Partially dependent           |
|                                   | -   Totally dependent             |
+-----------------------------------+-----------------------------------+
| ASA class                         | **Options:**                      |
|                                   |                                   |
|                                   | -   1: normal healthy patient     |
|                                   | -   2: mild systemic disease      |
|                                   | -   3: severe systemic disease    |
|                                   | -   4: severe systemic disease    |
|                                   |     that is a constant threat to  |
|                                   |     life (i.e., patient could die |
|                                   |     acutely without intervention) |
|                                   | -   5: moribund, not expected to  |
|                                   |     survive without surgery       |
+-----------------------------------+-----------------------------------+
| Creatinine                        | **Options:**                      |
|                                   |                                   |
|                                   | -   Normal (≤1.5 mg/dL, 133       |
|                                   |     µmol/L)                       |
|                                   | -   Elevated (\>1.5 mg/dL, 133    |
|                                   |     µmol/L)                       |
|                                   | -   Unknown                       |
+-----------------------------------+-----------------------------------+
| Type of procedure                 | **Options:**                      |
|                                   |                                   |
|                                   | -   Anorectal                     |
|                                   | -   Aortic                        |
|                                   | -   Bariatric                     |
|                                   | -   Brain                         |
|                                   | -   Breast                        |
|                                   | -   Cardiac                       |
|                                   | -   ENT (except                   |
|                                   |     thyroid/parathyroid)          |
|                                   | -   Foregut (esophagus, stomach)  |
|                                   |     or hepatopancreatobiliary     |
|                                   | -   Gallbladder, appendix,        |
|                                   |     adrenals, or spleen           |
|                                   | -   Hernia (ventral, inguinal,    |
|                                   |     femoral)                      |
|                                   | -   Intestinal                    |
|                                   | -   Neck (thyroid/parathyroid)    |
|                                   | -   Obstetric/gynecologic         |
|                                   | -   Orthopedic and non-vascular   |
|                                   |     extremity                     |
|                                   | -   Other abdominal               |
|                                   | -   Peripheral vascular           |
|                                   | -   Skin                          |
|                                   | -   Spine                         |
|                                   | -   Non-esophageal thoracic       |
|                                   |     (lung, mediastinum, etc)      |
|                                   | -   Vein                          |
|                                   | -   Urology                       |
+-----------------------------------+-----------------------------------+

## FORMULA

Cardiac risk, % = e^*x*^ / (1 + e^*x*^)

Where x = −5.25 + sum of the values of the selected variables.

  -------------------------- ---------------------------------------------------------------- ------------
  **Variable**               **Options**                                                      **Value**
  Age per year of increase                                                                    Age x 0.02
  Functional status          Independent                                                      0
                             Partially dependent                                              0.65
                             Totally dependent                                                1.03
  ASA class                  1: normal healthy patient                                        −5.17
                             2: mild systemic disease                                         −3.29
                             3: severe systemic disease                                       −1.92
                             4: severe systemic disease that is a constant threat to life\*   −0.95
                             5: moribund, not expected to survive without surgery             0
  Creatinine                 Normal (≤1.5 mg/dL, 133 µmol/L)                                  0
                             Elevated (\>1.5 mg/dL, 133 µmol/L)                               0.61
                             Unknown                                                          −0.10
  Type of procedure          Anorectal                                                        −0.16
                             Aortic                                                           1.60
                             Bariatric                                                        −0.25
                             Brain                                                            1.40
                             Breast                                                           −1.61
                             Cardiac                                                          1.01
                             ENT (except thyroid/parathyroid)                                 0.71
                             Foregut or hepatopancreatobiliary                                1.39
                             Gallbladder, appendix, adrenals, or spleen                       0.59
                             Hernia (ventral, inguinal, femoral)                              0
                             Intestinal                                                       1.14
                             Neck (thyroid/parathyroid)                                       0.18
                             Obstetric/gynecologic                                            0.76
                             Orthopedic and non-vascular extremity                            0.80
                             Other abdominal                                                  1.13
                             Peripheral vascular\*\*                                          0.86
                             Skin                                                             0.54
                             Spine                                                            0.21
                             Non-esophageal thoracic                                          0.40
                             Vein                                                             −1.09
                             Urology                                                          −0.26
  -------------------------- ---------------------------------------------------------------- ------------

\*i.e., patient could die acutely without intervention.

\*\*Non-aortic, non-vein vascular surgeries.

## FACTS & FIGURES

## EVIDENCE APPRAISAL

[Gupta et al
(2011)](https://circ.ahajournals.org/content/124/4/381#xref-fn-9-1){target="_blank"
rel="noopener"} used the NSQIP database to identify risk factors
associated with intra- or postoperative MI or cardiac arrest in over
200,000 patients. Compared with other risk calculators, the Gupta
Perioperative Risk Score (also sometimes called the MICA or Myocardial
Infarction/Cardiac Arrest Score) factors in higher usage of minimally
invasive surgery and differentiates between organ system and type of
surgery. However, this score was only validated retrospectively, and
therefore likely underestimates myocardial ischemia. Further, stress
test results and beta-blocker therapy status were not a part of the
NSQIP database data used to derive this score.

[Like the Gupta Score, the ACS NSQIP Surgical Risk Calculator predicts
either myocardial infarction or cardiac arrest within 30 days of
surgery, and has been shown to perform well in patients undergoing
low-risk procedures or those with a shorter duration length of stay. The
Gupta Score selects fewer patients as elevated risk compared to the ACS
NSQIP Surgical Risk Calculator or the RCRI. RCRI tends to overestimate
risk in lower risk patients; therefore, it is suggested to use ACS NSQIP
or Gupta Score calculators for that group of patients ([Cohn
2018](https://www.ncbi.nlm.nih.gov/pubmed/29126584){target="_blank"
rel="noopener"}).]{#docs-internal-guid-38287305-7fff-d3a6-fced-73408fff9761}
