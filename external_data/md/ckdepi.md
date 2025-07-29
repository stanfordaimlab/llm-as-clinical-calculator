# CKD-EPI Equations for Glomerular Filtration Rate (GFR)

## INPUTS

+-----------------------------------+-----------------------------------+
| Equation                          | **Options:**                      |
|                                   |                                   |
|                                   | -   2021 CKD-EPI Creatinine       |
|                                   | -   2021 CKD-EPI                  |
|                                   |     Creatinine-Cystatin C         |
|                                   | -   2009 CKD-EPI Creatinine       |
|                                   | -   2012 CKD-EPI Cystatin C       |
|                                   | -   2012 CKD-EPI                  |
|                                   |     Creatinine--Cystatin C        |
+-----------------------------------+-----------------------------------+
| Sex                               | **Options:**                      |
|                                   |                                   |
|                                   | -   Female                        |
|                                   | -   Male                          |
+-----------------------------------+-----------------------------------+
| Age                               | **Options:**                      |
+-----------------------------------+-----------------------------------+
| Serum creatinine                  | **Options:**                      |
+-----------------------------------+-----------------------------------+
| Serum cystatin C                  | **Options:**                      |
+-----------------------------------+-----------------------------------+
| Race                              | **Options:**                      |
|                                   |                                   |
| *Race may/may not provide better  | -   Black                         |
| estimates of GFR; optional*       | -   Non-black                     |
+-----------------------------------+-----------------------------------+

## FORMULA

**2021  CKD-EPI Creatinine **= 142 x (Scr/*A*)*^B^* x 0.9938^age ^x
(1.012 if female), where *A* and *B* are the following:

+-----------------+-----------------+-----------------+-----------------+
| **Female**      |                 | **Male**        |                 |
+-----------------+-----------------+-----------------+-----------------+
| **Scr ≤0.7**    | *A* = 0.7       | **Scr ≤0.9**    | *A* = 0.9       |
|                 |                 |                 |                 |
|                 | *B* = -0.241    |                 | *B* = -0.302    |
+-----------------+-----------------+-----------------+-----------------+
| **Scr \>0.7**   | A = 0.7         | **Scr \>0.9**   | *A* = 0.9       |
|                 |                 |                 |                 |
|                 | B = -1.2        |                 | *B* = -1.2      |
+-----------------+-----------------+-----------------+-----------------+

**2021 CKD-EPI Creatinine-Cystatin C **= 135 x (Scr/*A*)*^B^* x
(Scys/*C*)*^D^* x 0.9961^age^ x (0.963 if female), where *A*, *B*, *C*,
and *D* are the following:

Female:

+-----------------------+-----------------------+-----------------------+
|                       | **Scr ≤0.7**          | **Scr \>0.7**         |
+-----------------------+-----------------------+-----------------------+
| **Scys ≤0.8**         | *A* = 0.7             | *A* = 0.7             |
|                       |                       |                       |
|                       | *B* = -0.219          | *B* = -0.544          |
|                       |                       |                       |
|                       | *C* = 0.8             | *C* = 0.8             |
|                       |                       |                       |
|                       | *D* = -0.323          | *D* = -0.323          |
+-----------------------+-----------------------+-----------------------+
| **Scys \>0.8**        | *A* = 0.7             | *A* = 0.7             |
|                       |                       |                       |
|                       | *B* = -0.219          | *B* = -0.544          |
|                       |                       |                       |
|                       | *C* = 0.8             | *C* = 0.8             |
|                       |                       |                       |
|                       | *D* = -0.778          | *D* = -0.778          |
+-----------------------+-----------------------+-----------------------+

Male:

+-----------------------+-----------------------+-----------------------+
|                       | **Scr ≤0.9**          | **Scr \>0.9**         |
+-----------------------+-----------------------+-----------------------+
| **Scys ≤0.8**         | *A* = 0.9             | *A* = 0.9             |
|                       |                       |                       |
|                       | *B* = -0.144          | *B* = -0.544          |
|                       |                       |                       |
|                       | *C* = 0.8             | *C* = 0.8             |
|                       |                       |                       |
|                       | *D* = -0.323          | *D* = -0.323          |
+-----------------------+-----------------------+-----------------------+
| **Scys \>0.8**        | *A* = 0.9             | *A* = 0.9             |
|                       |                       |                       |
|                       | *B* = -0.144          | *B* = -0.544          |
|                       |                       |                       |
|                       | *C* = 0.8             | *C* = 0.8             |
|                       |                       |                       |
|                       | *D* = -0.778          | *D* = -0.778          |
+-----------------------+-----------------------+-----------------------+

**2009** **CKD-EPI Creatinine** = *A* × (Scr/*B*)^*C*^ × 0.993^age^ ×
(1.159 if black\*), where *A,* *B*, and *C* are the following:

+-----------------+-----------------+-----------------+-----------------+
| **Female**      |                 | **Male**        |                 |
+-----------------+-----------------+-----------------+-----------------+
| **Scr ≤0.7**    | *A* = 144       | **Scr ≤0.9**    | *A* = 141       |
|                 |                 |                 |                 |
|                 | *B* = 0.7       |                 | *B* = 0.9       |
|                 |                 |                 |                 |
|                 | *C* = -0.329    |                 | *C* = -0.411    |
+-----------------+-----------------+-----------------+-----------------+
| **Scr \>0.7**   | *A* = 144       | **Scr \>0.9**   | *A* = 141       |
|                 |                 |                 |                 |
|                 | *B* = 0.7       |                 | *B* = 0.9       |
|                 |                 |                 |                 |
|                 | *C* = -1.209    |                 | *C* = -1.209    |
+-----------------+-----------------+-----------------+-----------------+

 

**2012 CKD-EPI Cystatin C** = 133 × (Scys/0.8)^*A*^ × 0.996^age^ × *B,*
where *A* and *B* are the following:

+-----------------------+-----------------------+-----------------------+
|                       | **Female**            | **Male**              |
+-----------------------+-----------------------+-----------------------+
| **Scys ≤0.8**         | *A* = -0.499          | *A* = -0.499          |
|                       |                       |                       |
|                       | *B* = 0.932           | *B* = 1               |
+-----------------------+-----------------------+-----------------------+
| **Scys \>0.8**        | *A* = -1.328          | *A* = -1.328          |
|                       |                       |                       |
|                       | *B* = 0.932           | *B* = 1               |
+-----------------------+-----------------------+-----------------------+

 

**2012 CKD-EPI Creatinine-Cystatin C** = *A* × (Scr/*B)*^*C*^ ×
(Scys/0.8)^*D*^ × 0.995^age^ × (1.08 if black\*), where *A, B, C,* and
*D* are the following:**\
**

**Female:**

+-----------------------+-----------------------+-----------------------+
|                       | **Scr ≤0.7**          | **Scr \>0.7**         |
+-----------------------+-----------------------+-----------------------+
| **Scys ≤0.8**         | *A* = 130             | *A* = 130             |
|                       |                       |                       |
|                       | *B* = 0.7             | *B* = 0.7             |
|                       |                       |                       |
|                       | *C* = -0.248          | *C* = -0.601          |
|                       |                       |                       |
|                       | *D* = -0.375          | *D* = -0.375          |
+-----------------------+-----------------------+-----------------------+
| **Scys \>0.8**        | *A* = 130             | *A* = 130             |
|                       |                       |                       |
|                       | *B* = 0.7             | *B* = 0.7             |
|                       |                       |                       |
|                       | *C* = -0.248          | *C* = -0.601          |
|                       |                       |                       |
|                       | *D* = -0.711          | *D* = -0.711          |
+-----------------------+-----------------------+-----------------------+

**Male:**

+-----------------------+-----------------------+-----------------------+
|                       | **Scr ≤0.9**          | **Scr \>0.9**         |
+-----------------------+-----------------------+-----------------------+
| **Scys ≤0.8**         | *A* = 135             | *A* = 135             |
|                       |                       |                       |
|                       | *B* = 0.9             | *B* = 0.9             |
|                       |                       |                       |
|                       | *C* = -0.207          | *C* = -0.601          |
|                       |                       |                       |
|                       | *D* = -0.375          | *D* = -0.375          |
+-----------------------+-----------------------+-----------------------+
| **Scys \>0.8**        | *A* = 135             | *A* = 135             |
|                       |                       |                       |
|                       | *B* = 0.9             | *B* = 0.9             |
|                       |                       |                       |
|                       | *C* = -0.207          | *C* = -0.601          |
|                       |                       |                       |
|                       | *D* = -0.711          | *D* = -0.711          |
+-----------------------+-----------------------+-----------------------+

Scr, serum creatinine, mg/dL. Scys, serum cystatin C, mg/L.

\*Race may/may not provide better estimates of GFR; optional. [See
here](https://www.mdcalc.com/race){target="_blank"
stringify-link="https://www.mdcalc.com/race" delay="150"
sk="tooltip_parent" rel="noopener noreferrer"} for more on our approach
to addressing race and bias on MDCalc.

## FACTS & FIGURES

::: authorimage
![creatinine clearance
table](https://cdn-web-img.mdcalc.com/content/creatinine-clearance-table.png){.alignnone
.size-full .wp-image-1839 style="max-width: 100%;"}
:::

From [KDIGO 2012 Clinical Practice
Guideline](https://kdigo.org/wp-content/uploads/2017/02/KDIGO_2012_CKD_GL.pdf){target="_blank"
rel="noopener"}.

## EVIDENCE APPRAISAL

The CKD-EPI (creatinine) was developed by [Levey et al in
2009](https://www.ncbi.nlm.nih.gov/pubmed/19414839){target="_blank"
rel="noopener"}, who measured GFR of 8,254 participants using clearance
of iothalamate (the most recent recommended gold standard). Linear
regression was used to estimate the logarithm of measured GFR from
standardized creatinine levels, sex, race, and age.

The equation was validated by [Inker et al
(2012)](https://www.ncbi.nlm.nih.gov/pubmed/22762315){target="_blank"
rel="noopener"} and found to be more accurate than the MDRD
Equation (percentage of estimated GFR within 30% of measured GFR was
84.1% vs. 80.6%). The sensitivity and specificity of estimated GFR \<60
mL/min/1.73 m^2^ were 91% and 87%, respectively, using the CKD-EPI
equation and 95% and 82%, respectively, using the MDRD Equation.

Debate has arisen regarding the use of the adjustment coefficient for
black patients. Because of this, [Inker et al
(2021)](https://pubmed.ncbi.nlm.nih.gov/34554658/){target="_blank"
rel="noopener"} updated the CKD-EPI formulae to redevelop the equation
so that the race component was removed from the equation.
