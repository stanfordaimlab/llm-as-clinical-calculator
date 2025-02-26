# PECARN Pediatric Head Injury/Trauma Algorithm

## INPUTS

+-----------------------------------+-----------------------------------+
| Age                               | **Options:**                      |
|                                   |                                   |
|                                   | -   \<2 Years                     |
|                                   | -   ≥2 Years                      |
+-----------------------------------+-----------------------------------+
| GCS ≤14, palpable skull fracture  | **Options:**                      |
| or signs of AMS                   |                                   |
|                                   | -   No                            |
| *AMS: Agitation, somnolence,      | -   Yes                           |
| repetitive questioning, or slow   |                                   |
| response to verbal communication* |                                   |
+-----------------------------------+-----------------------------------+
| GCS ≤14 or signs of basilar skull | **Options:**                      |
| fracture or signs of AMS          |                                   |
|                                   | -   No                            |
| *AMS: Agitation, somnolence,      | -   Yes                           |
| repetitive questioning, or slow   |                                   |
| response to verbal communication* |                                   |
+-----------------------------------+-----------------------------------+
| Occipital, parietal or temporal   | **Options:**                      |
| scalp hematoma; history of LOC ≥5 |                                   |
| sec; not acting normally per      | -   No                            |
| parent or severe mechanism of     | -   Yes                           |
| injury?                           |                                   |
|                                   |                                   |
| *Severe mechanism: MVC with       |                                   |
| patient ejection, death of        |                                   |
| another passenger, rollover;      |                                   |
| pedestrian or bicyclist w/o       |                                   |
| helmet struck by motorized        |                                   |
| vehicle; fall from \>0.9m or 3ft; |                                   |
| head struck by high-impact        |                                   |
| object*                           |                                   |
+-----------------------------------+-----------------------------------+
| History of LOC or history of      | **Options:**                      |
| vomiting or severe headache or    |                                   |
| severe mechanism of injury        | -   No                            |
|                                   | -   Yes                           |
| *Motor vehicle crash with patient |                                   |
| ejection, death of another        |                                   |
| passenger, or rollover;           |                                   |
| pedestrian or bicyclist without   |                                   |
| helmet struck by a motorized      |                                   |
| vehicle; falls of more than       |                                   |
| 1.5m/5ft; head struck by a        |                                   |
| high-impact object*               |                                   |
+-----------------------------------+-----------------------------------+

## FORMULA

Prediction tree using a series of dichotomous Yes/No questions.

Use A if \<2 years old and B if ≥2 years old.

![](https://cdn-web-img.mdcalc.com/pecarn-algorithm.png){style="max-width: 100%;"}

Figure from [Kuppermann
2009](https://www.ncbi.nlm.nih.gov/pubmed/19758692){target="_blank"
rel="noopener"}. 

## FACTS & FIGURES

Definition of **clinically-important traumatic brain injury (ciTBI)**
(any of the following satisfy definition):

-   Death from traumatic brain injury (TBI)
-   Neurosurgical intervention for traumatic brain injury
    -   Intracranial pressure monitoring
    -   Elevation of depressed skull fracture
    -   Ventriculostomy
    -   Hematoma evacuation
    -   Lobectomy
    -   Tissue debridement
    -   Dura repair
    -   Other
-   Intubation of more than 24 hours for TBI
-   Hospital admission of 2 nights or more for the TBI in association
    with TBI on CT
    -   Hospital admission for TBI defined by admission for persistent
        neurological symptoms or signs such as persistent alteration in
        mental status, recurrent emesis due to head injury, persistent
        severe headache or ongoing seizure management

Definition of **traumatic brain injury on CT** (any of the following
satisfy definition):

-   Intracranial hemorrhage or contusion
-   Cerebral edema
-   Traumatic infarction
-   Diffuse axonal injury
-   Shearing injury
-   Sigmoid sinus thrombosis
-   Midline shift of intracranial contents or signs of brain herniation
-   Diastasis of the skull
-   Pneumocephalus
-   Skull fracture depressed by at least the width of the table of the
    skull

## EVIDENCE APPRAISAL

-   The original PECARN trial included 42,412 children \<18 years old
    presenting to 1 of 25 North American PECARN-affiliated emergency
    departments with 33,785 in derivation cohort (8,502 \<2 years old)
    and 8,627 in the validation cohort (2,216 \<2 years old).
-   CT scans were performed at the physician's discretion in 35.3% while
    medical records, telephone surveys, and county morgue records were
    used to assess for cases of missed ciTBI in those discharged without
    imaging.
    -   Potential for CT reduction quoted above is likely underestimated
        given that CT utilization in this study (35.3%) was
        significantly lower than the estimated average in North American
        EDs (50%).
-   TBI, as defined in the "More Info" header occurred in 5.2% of
    patients.
-   9% of patients were admitted to the hospital.
-   ciTBI occurred in **0.9%** of the cohort, neurosurgery was performed
    in **0.1%** of the overall cohort, and zero patients died.
-   In patients \<2 years of age that were negative for any PECARN risk
    factor, the aid was **100%** sensitive (95% CI 86.3-100) with NPV of
    **100%** (95% CI 99.7-1000) for ruling out ciTBI in the validation
    cohort.
-   In patient \>2 years of age that were negative for any PECARN risk
    factor, the aid was **96.8%** sensitive (95% CI 89.0-99.6) with NPV
    of **99.95%** (95% CI 99.8-99.99) for ruling out ciTBI in the
    validation cohort External validation studies have demonstrated
    sensitivity of 100% for ciTBI and any injury requiring neurosurgery.
    -   The algorithm has reasonable specificity (53%-60%) considering
        its extremely high sensitivity.
        -   60 (15.9%) of 376 patients with ciTBI underwent
            neurosurgery, 8 (2.1%) with ciTBI were intubated \>24 Hours,
            and 0 patients died.
        -   As a result of the infrequency of ciTBI, the lower bounds of
            the confidence intervals of sensitivity started at 86 and
            89%, respectively, for the \<2 and \>2 years of age cohorts.
        -   The NPV confidence intervals were very tightly approximating
            100%.
-   PECARN has now been externally validated in 2 separate studies.
    -   One trial of 2439 children in 2 North American and Italian
        centers found PECARN to be **100%** sensitive for ruling out
        ciTBI in both age cohorts.
    -   The rates of ciTBI at 0.8% (19/2439) and those requiring
        neurosurgery 0.08% (2/2439) were similar to the PECARN trial.
    -   A second trial at a single US emergency department of 1009
        patients under 18 years of age prospectively compared PECARN to
        two other pediatric head CT decision aids (CHALICE and CATCH) as
        well as to physician estimate and physician practice.
    -   2% (21/1009) had ciTBI and neurosurgery was needed in 0.4%
        (4/1009) of this sample.
    -   Again PECARN was found to be **100%** sensitive for identifying
        ciTBI.
    -   PECARN outperformed both the CHALICE and CATCH decision aids
        (91% and 84% sensitive for ciTBI, respectively).
-   Although the goal was to Rule-Out those with very low risk of ciTBI,
    the prediction rule also performed well to Rule-Out TBI on Head CT.
-   In those \<2 years old, sensitivity and NPV were 100% for TBI on CT
    with narrow confidence intervals.
-   In those \>2 years old, sensitivity was 98.4% and NPV 94% for TBI on
    CT with relatively narrow confidence intervals.
-   2 recent PECARN subgroup analyses attempted to further risk-stratify
    patients with single predictors (e.g., Isolated scalp hematoma in
    patients \<2years old).
    -   ciTBI was too uncommon to apply age, hematoma size, or hematoma
        location predictors.
    -   There were several non-statistically significant trends for
        higher rates or TBI on Head CT that may affect imaging
        tendencies (e.g., \<3 months of age, Non-frontal hematoma +
        Large size).
-   Another sub-analysis of those with isolated vomiting (i.g., no other
    PECARN predictors) reiterated the parent study results.
-   In the \>2 year old cohort, there was a low rate of TBI on Head CT
    (3.2%, 26/806) and an even lower rate of ciTBI (0.7%, 10/1,501) so
    observation rather than emergent imaging is indicated in the
    majority of these patients.
-   Number of vomiting episodes and timing of episodes was not helpful
    in predicting ciTBI or TBI on Head CT, as there was a
    non-statistically significant counterintuitive trend towards less
    ciTBI/TBI on CT with more episodes.
