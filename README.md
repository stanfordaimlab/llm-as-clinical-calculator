                                                                                                            
# Large Language Model Agents Can Use Tools to Perform Clinical Calculation

> Data from this project has be released as **Aʙᴀᴄᴜs-212** (49 calculation tasks, 212 vignettes) and **Aʙᴀᴄᴜs-409** (10 calculation tasks, 10,000 vignettes). The cleaned datasets are available in the `datasets` directory. Please see the usage page in that directory for more details.

See our paper (in press), available here [Large Language Model Agents Can Use Tools to Perform Clinical Calculation](https://doi.org/10.1038/s41746-025-01475-8)

## Abstract

Large language models (LLMs) can answer expert-level questions in medicine but are prone to hallucinations and arithmetic errors. Early evidence suggests LLMs cannot reliably perform clinical calculations, limiting their potential integration into clinical workﬂows. We evaluated ChatGPT’s performance across 48 medical calculation tasks, ﬁnding incorrect responses in one-third of trials (n = 212). We then assessed three forms of agentic augmentation: retrieval-augmented generation, a code interpreter tool, and a set of task-speciﬁc calculation tools (OpenMedCalc) across 10,000 trials. Models with access to task-speciﬁc tools showed the greatest improvement, with LLaMa and GPT- based models demonstrating a 5.5-fold (88% vs 16%) and 13-fold (64% vs 4.8%) reduction in incorrect responses, respectively, compared to the unimproved model. Our ﬁndings suggest that integration of machine-readable, task-speciﬁc tools may help overcome LLMs’ limitations in medical calculations.


## Overview

This project explores the augmentation of large language models (LLMs) like ChatGPT with clinician-informed tools to improve performance on medical calculation tasks. The project addresses the limitations of LLMs in performing basic mathematical operations and their tendency to hallucinate knowledge. By integrating an open-source clinical calculation API, OpenMedCalc, with ChatGPT, the project demonstrates significant improvements in accuracy for clinical calculations. This integration allows for the execution of common clinical calculations with enhanced reliability, aiming to revolutionize medical practice by automating routine tasks and providing accurate, evidence-based calculations to clinicians.

Large language models (LLMs) such as ChatGPT have shown the ability to answer expert-level multiple-choice questions in medicine but are limited by their tendency to hallucinate knowledge and inadequacy in performing basic mathematical operations. This project explores the ability of ChatGPT to perform medical calculations, evaluating its performance across diverse clinical calculation tasks. Initial findings indicated that ChatGPT is an unreliable clinical calculator, delivering inaccurate responses in a significant number of trials.

### Objectives

To address the limitations of LLMs, the project developed an open-source clinical calculation API, OpenMedCalc, which was integrated with ChatGPT. The augmented model was evaluated against standard ChatGPT using clinical vignettes in common clinical calculation tasks. The goal was to enhance the accuracy and reliability of medical calculations performed by LLMs.

### Key Findings

- The integration of OpenMedCalc with ChatGPT significantly improved the accuracy of clinical calculations.
- The augmented model demonstrated a marked improvement in accuracy over unimproved ChatGPT.
- The project highlights the potential of integrating machine-usable, clinician-informed tools to alleviate the reliability limitations observed in medical LLMs.

LLM Calc is a comprehensive tool designed to facilitate medical calculations using large language models (LLMs). It integrates various clinical calculators and provides a user-friendly interface for performing complex medical computations. The project aims to enhance the accuracy and efficiency of medical calculations by leveraging the power of LLMs.

### Additional Models and Calculators

In this revision, we have expanded the range of models and calculators used in the project:

#### Models:
- gpt4o
- llama3_1 (provided by OpenRouter)
- 
#### Calculators:
- psiport
- ariscat
- cci
- caprini
- gad7
- sofa
- meldna
- hasbled
- wellsdvt

## Features

- **Interactive Menu**: Navigate through the application using a simple command-line interface.
- **Database Management**: Easily rebuild and manage the database of medical calculators.
- **Vignette Generation**: Automatically generate clinical vignettes for testing and demonstration purposes.
- **Configuration Viewing**: View and customize the configuration settings of the application.
- **Testing Suite**: Run comprehensive tests to ensure the reliability and accuracy of the calculations.

## Usage

To use LLM Calc, you can execute the following commands:

```
Usage: llmcalc [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion          Install completion for the current shell.
  --show-completion             Show completion for the current shell, to copy it or customize the installation.
  --help                        Show this message and exit.

Commands:
  interpreter        Start an iPython interpreter in the current context.
  rebuild-database   Rebuild the database.
  test               Run tests.
  view-config        View config page 
  vignettes          Build the vignettes.
  experiment         Manage and run experiments.
```

## Getting Started

1. **Installation**: Clone the repository and install the required dependencies using `poetry install`. This will install a command line application called `llmcalc`.
2. **Configuration**: Set up the environment variables and configuration files as needed. See `sameple_env.txt` for reference. You will need an account with OpenAI and OpenRouter. Some functionality will require a LangChain API key as wel. 
3. **Execution**: Use the command-line interface to interact with the application and perform calculations. To run the full workflow, you will need to run the following commands:
```shell
llmcalc rebuild-database
```

This takes the vignette data, calculators, arms, etc and places it into a database.

```shell
llmcalc experiment rebuild
```

This prepares the system to run an experiment. After, you can start an experiment with the following line. Note that "number of cases" is on a per-calculator per-arm basis, so depending on configuration, can be many cases.

```shell
llmcalc experiment new  --description "Evaluating 10 vignettes" --number-of-cases 1
```
This builds the experiment, including the actual vignettes/cases. A file called cases.json will be output into the `data/build_database` folder after this step; this contains the synthetic patients information. It will also start the experiement, running the vignettes against the calculators listed in the `llmcalc/lib/config.py` file. That file contains the following lines, where one can specify the configuration of the experiement.

```python

# Calculators
self.DEFAULT_SELECTED_CALCULATORS_SLUGS = [
CalculatorSlug.nihss,
CalculatorSlug.hasbled,
CalculatorSlug.meldna,
CalculatorSlug.gad7,
CalculatorSlug.sofa,
CalculatorSlug.psiport,
CalculatorSlug.wellsdvt,
CalculatorSlug.caprini,
CalculatorSlug.cci,
CalculatorSlug.ariscat,
]

# arms
self.DEFAULT_SELECTED_ARM_SLUGS = [
ArmSlug.llama_base,
ArmSlug.llama_ci,
ArmSlug.llama_rag,
ArmSlug.llama_rag_ci,
ArmSlug.llama_omc,
ArmSlug.gpt4_base,
ArmSlug.gpt4_ci,
ArmSlug.gpt4_rag,
ArmSlug.gpt4_rag_ci,
ArmSlug.gpt4_omc,
]

```

## Contributing

We welcome contributions from the community. Please feel free to submit issues, fork the repository, and make pull requests.

## Citation

Works citing this study should cite:

```bibtex
@article{goodell2025,
  title         = {Large Language Model Agents Can Use Tools to Perform Clinical Calculations},
  author        = {Goodell, Alex J. and Chu, Simon N and Rouholiman, Dara and Chu, Larry F},
  year          = {2025},
  month         = {Feb},
  journal       = {NPJ Digital Medicine},
  doi           = {10.1038/s41746-025-01475-8},
}
```

## License
The Datasets are released under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0).