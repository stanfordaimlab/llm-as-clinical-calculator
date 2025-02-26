# Sequential Organ Failure Assessment (SOFA) Score

## INPUTS

+-----------------------------------+-----------------------------------+
| PaO₂                              | **Options:**                      |
+-----------------------------------+-----------------------------------+
| FiO₂                              | **Options:**                      |
|                                   |                                   |
| *See [Evidence](#evidence) for    |                                   |
| estimating FiO₂ from oxygen       |                                   |
| flow/delivery rates*              |                                   |
+-----------------------------------+-----------------------------------+
| On mechanical ventilation         | **Options:**                      |
|                                   |                                   |
| *Including CPAP*                  | -   No                            |
|                                   | -   Yes                           |
+-----------------------------------+-----------------------------------+
| Platelets, ×10³/µL                | **Options:**                      |
|                                   |                                   |
|                                   | -   ≥150 (0)                      |
|                                   | -   100-149 (1)                   |
|                                   | -   50-99 (2)                     |
|                                   | -   20-49 (3)                     |
|                                   | -   \<20 (4)                      |
+-----------------------------------+-----------------------------------+
| Glasgow Coma Scale                | **Options:**                      |
|                                   |                                   |
| *If on sedatives, estimate        | -   15 (0)                        |
| assumed GCS off sedatives*        | -   13-14 (1)                     |
|                                   | -   10-12 (2)                     |
|                                   | -   6-9 (3)                       |
|                                   | -   \<6 (4)                       |
+-----------------------------------+-----------------------------------+
| Bilirubin, mg/dL (μmol/L)         | **Options:**                      |
|                                   |                                   |
|                                   | -   \<1.2 (\<20) (0)              |
|                                   | -   1.2--1.9 (20-32) (1)          |
|                                   | -   2.0--5.9 (33-101) (2)         |
|                                   | -   6.0--11.9 (102-204) (3)       |
|                                   | -   ≥12.0 (\>204) (4)             |
+-----------------------------------+-----------------------------------+
| Mean arterial pressure OR         | **Options:**                      |
| administration of vasoactive      |                                   |
| agents required                   | -   No hypotension (0)            |
|                                   | -   MAP \<70 mmHg (1)             |
| *Listed doses are in units of     | -   DOPamine ≤5 or DOBUTamine     |
| mcg/kg/min*                       |     (any dose) (2)                |
|                                   | -   DOPamine \>5, EPINEPHrine     |
|                                   |     ≤0.1, or norEPINEPHrine ≤0.1  |
|                                   |     (3)                           |
|                                   | -   DOPamine \>15, EPINEPHrine    |
|                                   |     \>0.1, or norEPINEPHrine      |
|                                   |     \>0.1 (4)                     |
+-----------------------------------+-----------------------------------+
| Creatinine, mg/dL (μmol/L) (or    | **Options:**                      |
| urine output)                     |                                   |
|                                   | -   \<1.2 (\<110) (0)             |
|                                   | -   1.2--1.9 (110-170) (1)        |
|                                   | -   2.0--3.4 (171-299) (2)        |
|                                   | -   3.5--4.9 (300-440) or UOP     |
|                                   |     \<500 mL/day (3)              |
|                                   | -   ≥5.0 (\>440) or UOP \<200     |
|                                   |     mL/day (4)                    |
+-----------------------------------+-----------------------------------+

## FORMULA

Addition of the selected points:

:::: {dir="ltr"}
  ---------------------------------------------------------------------------------------------------------------------- ------------
  **Variable**                                                                                                           **Points**
  **PaO~2~/FiO~2~\*, mmHg**                                                                                              
  ≥400                                                                                                                   0
  300-399                                                                                                                +1
  200-299                                                                                                                +2
  ≤199 and NOT mechanically ventilated                                                                                   +2
  100-199 and mechanically ventilated                                                                                    +3
  \<100 and mechanically ventilated                                                                                      +4
  **Platelets, ×10^3^/µL**                                                                                               
  ≥150                                                                                                                   0
  100-149                                                                                                                +1
  50-99                                                                                                                  +2
  20-49                                                                                                                  +3
  \<20                                                                                                                   +4
  **Glasgow Coma Scale**                                                                                                 
  15                                                                                                                     0
  13--14                                                                                                                 +1
  10--12                                                                                                                 +2
  6--9                                                                                                                   +3
  \<6                                                                                                                    +4
  **Bilirubin, mg/dL (μmol/L)**                                                                                          
  \<1.2 (\<20)                                                                                                           0
  1.2--1.9 (20-32)                                                                                                       +1
  2.0--5.9 (33-101)                                                                                                      +2
  6.0--11.9 (102-204)                                                                                                    +3
  ≥12.0 (\>204)                                                                                                          +4
  **Mean arterial pressure OR administration of vasoactive agents required (listed doses are in units of mcg/kg/min)**   
  No hypotension                                                                                                         0
  MAP \<70 mmHg                                                                                                          +1
  DOPamine ≤5 or DOBUTamine (any dose)                                                                                   +2
  DOPamine \>5, EPINEPHrine ≤0.1, or norEPINEPHrine ≤0.1                                                                 +3
  DOPamine \>15, EPINEPHrine \>0.1, or norEPINEPHrine \>0.1                                                              +4
  **Creatinine, mg/dL (μmol/L) (or urine output)**                                                                       
  \<1.2 (\<110)                                                                                                          0
  1.2--1.9 (110-170)                                                                                                     +1
  2.0--3.4 (171-299)                                                                                                     +2
  3.5--4.9 (300-440) or UOP \<500 mL/day)                                                                                +3
  ≥5.0 (\>440) or UOP \<200 mL/day                                                                                       +4
  ---------------------------------------------------------------------------------------------------------------------- ------------

 

\*Estimating FiO₂ from oxygen flow/delivery rates:

::: {dir="ltr" align="left"}
+-----------------------+-----------------------+-----------------------+
| **Type of O₂          | **Flow rates, L/min** | **FiO₂**              |
| delivery**            |                       |                       |
+-----------------------+-----------------------+-----------------------+
| Nasal cannula         | 1-6                   | \~4% FiO₂ added above |
|                       |                       | room air\* per 1      |
|                       |                       | L/min                 |
|                       |                       |                       |
|                       |                       | -   Room air = 21%    |
|                       |                       |                       |
|                       |                       | -   1 L/min = 25%     |
|                       |                       |                       |
|                       |                       | -   2 L/min = 29%     |
|                       |                       |                       |
|                       |                       | -   3 L/min = 33%     |
|                       |                       |                       |
|                       |                       | -   4 L/min = 37%     |
|                       |                       |                       |
|                       |                       | -   5 L/min = 41%     |
|                       |                       |                       |
|                       |                       | -   6 L/min = 45%     |
+-----------------------+-----------------------+-----------------------+
| Simple face mask      | \~6-12                | 35-60%\*              |
+-----------------------+-----------------------+-----------------------+
| Non-rebreather mask   | 10-15                 | \~70-90%              |
+-----------------------+-----------------------+-----------------------+
| High-flow nasal       | Up to 60              | 30-100%               |
| cannula               |                       |                       |
+-----------------------+-----------------------+-----------------------+
:::

\*Varies based on respiratory rate and minute ventilation.
::::

## FACTS & FIGURES

Interpretation:

<div>

::: {dir="ltr"}
  ---------------- -------------------------------- --------------------------------
  **SOFA Score**   **Mortality if initial score**   **Mortality if highest score**
  0-1              0.0%                             0.0%
  2-3              6.4%                             1.5%
  4-5              20.2%                            6.7%
  6-7              21.5%                            18.2%
  8-9              33.3%                            26.3%
  10-11            50.0%                            45.8%
  12-14            95.2%                            80.0%
  \>14             95.2%                            89.7%
  ---------------- -------------------------------- --------------------------------
:::

::: {dir="ltr"}
  --------------------- ---------------
  **Mean SOFA Score**   **Mortality**
  0-1.0                 1.2%
  1.1-2.0               5.4%
  2.1-3.0               20.0%
  3.1-4.0               36.1%
  4.1-5.0               73.1%
  \>5.1                 84.4%
  --------------------- ---------------
:::

From [Ferreira
2001](https://www.ncbi.nlm.nih.gov/pubmed/11594901){target="_blank"
rel="noopener"}.

</div>

## EVIDENCE APPRAISAL

-   [This
    paper](https://www.ncbi.nlm.nih.gov/pubmed/8844239){target="_blank"
    rel="noopener"} describes how the European Society of Intensive Care
    Medicine selected the SOFA score variables.
-   In [this validation
    study](https://www.ncbi.nlm.nih.gov/pubmed/9824069){target="_blank"
    rel="noopener"}, 1,449 patients were enrolled over a period of one
    month in forty intensive care units (ICUs) in 16 countries. The SOFA
    score was found to have a good correlation of organ
    dysfunction/failure in critically ill patients.
-   [This prospective, observational cohort
    study](https://www.ncbi.nlm.nih.gov/pubmed/11594901){target="_blank"
    rel="noopener"} was performed at a university hospital in Belgium
    and recruited 352 patients. The SOFA score was again found to be a
    good indicator of prognosis.
