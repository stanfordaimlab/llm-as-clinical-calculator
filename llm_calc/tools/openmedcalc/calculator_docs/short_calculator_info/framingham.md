# Framingham Risk Score for Hard Coronary Heart Disease

## INPUTS

+-----------------------------------+-----------------------------------+
| Age                               | **Options:**                      |
+-----------------------------------+-----------------------------------+
| Sex                               | **Options:**                      |
|                                   |                                   |
|                                   | -   Female                        |
|                                   | -   Male                          |
+-----------------------------------+-----------------------------------+
| Smoker                            | **Options:**                      |
|                                   |                                   |
|                                   | -   No                            |
|                                   | -   Yes                           |
+-----------------------------------+-----------------------------------+
| Total cholesterol                 | **Options:**                      |
+-----------------------------------+-----------------------------------+
| HDL cholesterol                   | **Options:**                      |
+-----------------------------------+-----------------------------------+
| Systolic BP                       | **Options:**                      |
+-----------------------------------+-----------------------------------+
| Blood pressure being treated with | **Options:**                      |
| medicines                         |                                   |
|                                   | -   No                            |
|                                   | -   Yes                           |
+-----------------------------------+-----------------------------------+

## FORMULA

Equations as follows (β coefficients listed in table below):

**Men:**

L~Men~ = β x ln(Age) + β x ln(Total cholesterol) + β x ln(HDL
cholesterol) + β x ln(Systolic BP) + β x Treated for blood pressure + β
x Smoker + β x ln(Age) x ln(Total cholesterol) + β x ln(Age) x Smoker +
β x ln(Age) x ln(Age) - 172.300168

P~Men~ = 1 - 0.9402\^exp(L~Men~)

**Women:**

L~Women~ = β x ln(Age) + β x ln(Total cholesterol) + β x ln(HDL
cholesterol) + β x ln(Systolic BP) + β x Treated for blood pressure + β
x Smoker + β x ln(Age) x ln(Total cholesterol) + β x ln(Age) x Smoker -
146.5933061

P~Women~ = 1 - 0.98767\^exp(L~Women~)

::: {dir="ltr"}
  --------------------------------- --------------------- -----------
  **Variable**                      **Coefficient (β)**   
                                    **Men**               **Women**
  ln(Age)                           52.00961              31.764001
  ln(Total cholesterol)             20.014077             22.465206
  ln(HDL cholesterol)               -0.905964             -1.187731
  ln(Systolic BP)                   1.305784              2.552905
  Treated for blood pressure\*      0.241549              0.420251
  Smoker\*                          12.096316             13.07543
  ln(Age) x ln(Total cholesterol)   -4.605038             -5.060998
  ln(Age) x Smoker\*\*              -2.84367              -2.996945
  ln(Age) x ln(Age)                 -2.93323              \-
  --------------------------------- --------------------- -----------
:::

\*Yes = 1, No = 0.

\*\*Men: if age \>70, use ln(70) x Smoker. Women: if age \>78, use
ln(78) x Smoker.

[ ]{style="font-size: 10pt; font-family: Arial; color: #0000ff; background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;"}

## FACTS & FIGURES

Interpretation:

::: {dir="ltr"}
+-------------+-------------+-------------+-------------+-------------+
| **Age,      | **Average   |             | **Low\*\*   |             |
| years**     | 10 year     |             | 10 year CHD |             |
|             | hard\* CHD  |             | risk in the |             |
|             | risk in     |             | average     |             |
|             | this        |             | patient**   |             |
|             | patient**   |             |             |             |
+-------------+-------------+-------------+-------------+-------------+
|             | **Women**   | **Men**     | **Women**   | **Men**     |
+-------------+-------------+-------------+-------------+-------------+
| 30-34       | \<1%        | 1%          | \<1%        | 2%          |
+-------------+-------------+-------------+-------------+-------------+
| 35-39       | \<1%        | 4%          | 1%          | 3%          |
+-------------+-------------+-------------+-------------+-------------+
| 40-44       | 1%          | 4%          | 2%          | 4%          |
+-------------+-------------+-------------+-------------+-------------+
| 45-49       | 2%          | 8%          | 3%          | 4%          |
+-------------+-------------+-------------+-------------+-------------+
| 50-54       | 3%          | 10%         | 5%          | 6%          |
+-------------+-------------+-------------+-------------+-------------+
| 55-59       | 7%          | 13%         | 7%          | 7%          |
+-------------+-------------+-------------+-------------+-------------+
| 60-64       | 8%          | 20%         | 8%          | 9%          |
+-------------+-------------+-------------+-------------+-------------+
| 65-69       | 8%          | 22%         | 8%          | 11%         |
+-------------+-------------+-------------+-------------+-------------+
| 70-74       | 11%         | 25%         | 8%          | 14%         |
+-------------+-------------+-------------+-------------+-------------+
| 74-79       | Data not    | Data not    | Data not    | Data not    |
|             | available   | available   | available   | available   |
+-------------+-------------+-------------+-------------+-------------+
:::

\*Excluding angina pectoris.

\*\*Low risk was calculated for a person the same age, optimal blood
pressure, LDL-C 100-129 mg/dL or cholesterol 160-199 mg/dL, HDL-C 45
mg/dL for men or 55 mg/dL for women, non-smoker, no diabetes.

[ ]{style="font-size: 10pt; font-family: Arial; color: #0000ff; background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;"}

## EVIDENCE APPRAISAL
