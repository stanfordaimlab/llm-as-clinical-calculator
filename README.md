# Augmentation of ChatGPT with clinician-informed tools improves performance on medical calculation tasks
[![DOI](https://zenodo.org/badge/730459595.svg)](https://zenodo.org/doi/10.5281/zenodo.10360442)

**Abstract:** Prior work has shown that large language models (LLMs) have the ability to answer expert-level multiple choice questions in medicine, but are limited by both their tendency to hallucinate knowledge and their inherent inadequacy in performing basic mathematical operations. Unsurprisingly, early evidence suggests that LLMs perform poorly when asked to execute common clinical calculations. Recently, it has been demonstrated that LLMs have the capability of interacting with external programs and tools, presenting a possible remedy for this limitation. In this study, we explore the ability of ChatGPT (GPT-4, November 2023) to perform medical calculations, evaluating its performance across 48 diverse clinical calculation tasks. Our findings indicate that ChatGPT is an unreliable clinical calculator, delivering inaccurate responses in one-third of trials (n=212). To address this, we developed an open-source clinical calculation API (openmedcalc.org), which we then integrated with ChatGPT. We subsequently evaluated the performance of this augmented model by comparing it against standard ChatGPT using 75 clinical vignettes in three common clinical calculation tasks: Caprini VTE Risk, Wells DVT Criteria, and MELD-Na. The augmented model demonstrated a marked improvement in accuracy over unimproved ChatGPT. Our findings suggest that integration of machine-usable, clinician-informed tools can help alleviate the reliability limitations observed in medical LLMs.

Find our preprint on [medrXiv](https://www.medrxiv.org/content/10.1101/2023.12.13.23299881v1).

## Repo structure

```
├── LICENSE
├── README.md
└── results-data                       
    ├── calculators-list.csv            - list of calculators by calculator type
    ├── exploratory-analysis.csv        - results from exploratory analysis
    └── focused-analysis-results.csv    - results from focused analysis (MELD, 
                                          Caprini, Wells DVT)
```

