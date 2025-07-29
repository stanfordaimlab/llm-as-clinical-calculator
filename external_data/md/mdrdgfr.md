# MDRD GFR Equation

## INPUTS

+-----------------------------------+-----------------------------------+
| Sex                               | **Options:**                      |
|                                   |                                   |
|                                   | -   Female                        |
|                                   | -   Male                          |
+-----------------------------------+-----------------------------------+
| Age                               | **Options:**                      |
+-----------------------------------+-----------------------------------+
| Creatinine                        | **Options:**                      |
+-----------------------------------+-----------------------------------+
| Black race                        | **Options:**                      |
|                                   |                                   |
| *Race may/may not provide better  | -   No                            |
| estimates of GFR; optional*       | -   Yes                           |
+-----------------------------------+-----------------------------------+

## FORMULA

GFR = 175 × Serum Cr^-1.154^× age^-0.203^ × 1.212 (if patient is
black\*) × 0.742 (if female)

Use serum Cr in mg/dL for this formula.

From [Levey
2006](https://pubmed.ncbi.nlm.nih.gov/16908915/){target="_blank"
rel="noopener"
stringify-link="https://pubmed.ncbi.nlm.nih.gov/16908915/"
sk="tooltip_parent"}.

[Note: the original MDRD study equation used a constant of 186, which
the authors later revised to 175 to accommodate for standardization of
creatinine assays over IDMS. The evidence doesn\'t seem to strongly
suggest that the revised version is demonstrably better than the
original (furthermore, the same authors of MDRD also developed the newer
[CKD-EPI
equations](https://www.mdcalc.com/ckd-epi-equations-glomerular-filtration-rate-gfr){target="_blank"
rel="noopener"}, which are more accurate at a broader range of estimated
GFR than the MDRD equations).
]{#docs-internal-guid-b5935790-7fff-0870-f853-90677e5ed110}

\*Race may/may not provide better estimates of GFR; optional. [See
here](https://www.mdcalc.com/race){target="_blank" rel="noopener"
stringify-link="https://www.mdcalc.com/race" sk="tooltip_parent"} for
more on our approach to addressing race and bias on MDCalc.

## FACTS & FIGURES

::: authorimage
![creatinine clearance
table](https://cdn-web-img.mdcalc.com/content/creatinine-clearance-table.png){.alignnone
.size-full .wp-image-1839 style="max-width: 100%;"}
:::

From: [KDIGO 2012 Clinical Practice
Guideline.](https://kdigo.org/wp-content/uploads/2017/02/KDIGO_2012_CKD_GL.pdf){target="_blank"
rel="noopener"}

## EVIDENCE APPRAISAL

Derived and validated in patients from the Modification of Diet in Renal
Disease (MDRD) cohort by [Levey et al in
1999](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2763564/){target="_blank"
rel="noopener"}. The derivation cohort included 1070 patients and the
validation cohort 558 patients. The equation has since been validated
more extensively in a variety of populations, though it remains useful
primarily for patients with impaired kidney function (eGFR \< 60
ml/min/1.73m). The equation has not been validated in patients greater
than 70 years old, though it is still applied in these patients.
Additional modifications exist for use in certain populations,
[including East Asian
populations](https://pubmed.ncbi.nlm.nih.gov/18037093/){target="_blank"
rel="noopener"}.

[]{#docs-internal-guid-faf22306-7fff-fe96-54c5-d9b3c5eb44a1}

Debate has arisen regarding the use of the adjustment coefficient for
black patients. The extent to which self-reported race may be considered
a variable in physiologic calculations is currently being scrutinized,
and several large health systems have now removed the race coefficient
from eGFR calculations.
