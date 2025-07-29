# Large Language Model Agents Can Use Tools to Perform Clinical Calculation

> Data from this project has be released as **Aʙᴀᴄᴜs-212** (49 calculation tasks, 212 vignettes) and **Aʙᴀᴄᴜs-409** (10 calculation tasks, 10,000 vignettes). The cleaned datasets are available in the `datasets` directory. The other code here is the experimental code for our paper. A clean repository for the web tool component of OpenMedCalc is available [in a separate OpenMedCalc repository](https://github.com/alexgoodell/open-med-calc). Note that some of the data in this repository is not covered by the MIT license of this repository (see "external data" section below).

See our paper in NPJ Digital Medicine, available here: [Large Language Model Agents Can Use Tools to Perform Clinical Calculation](https://doi.org/10.1038/s41746-025-01475-8).

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

1. **Installation**: You will need to have uv installed. Clone the repository and install the required dependencies, build package using: `uv sync`. This will install a command line application called `llmcalc` in the UV environment.
2. **Configuration**: Set up the environment variables and configuration files as needed. See `sameple_env.txt` for reference. You will need an account with OpenAI and OpenRouter. Some functionality will require a LangChain API key as wel.
3. **External data:** Review the "external data" section below and copy files as needed.
4. **Execution**: Use the command-line interface to interact with the application and perform calculations. To run the full workflow, you will need to run the following commands:

```bash
uv run llmcalc rebuild-database
```

This takes the vignette data, calculators, arms, etc and places it into a database.

```bash
uv run llmcalc experiment rebuild
```

This prepares the system to run an experiment. After, you can start an experiment with the following line. Note that "number of cases" is on a per-calculator per-arm basis, so depending on configuration, can be many cases.

```bash
uv run llmcalc experiment new  --description "Evaluating 10 vignettes" --number-of-cases 1
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

## External data

Evaluation of the model (RAG arm) included usage of published written material owned by MDCalc Ltd (New York, NY); used and reproduced here with their permission. MDCalc reserves all rights to said material. For this reason, it is stored in the `external_data` directory. This data is not included in the MIT license.

To re-run the original experiments, you are required to move the data from the `external_data` directory, which can be accomplished by running the following from the root directory:

```bash
mkdir llm_calc/data/build_database/reference_material
cp -r external_data/* llm_calc/data/build_database/reference_material
```

If you have any other difficulties getting the code running, please reach out to us (using email in our paper).

## License

Apart from the copyrighted material found in the `external_data` directory (see "External data" section above) and relevant transitory requirements (in table below), this software is licensed under the MIT license.

This Software contains python dependencies which are not property of the authors. Please see the following table of dependencies and their licenses (built with licensecheck).

| Package                                  | License(s)                                | Compatible |
| ---------------------------------------- | ----------------------------------------- | :--------: |
| certifi                                  | MOZILLA PUBLIC LICENSE 2.0 _MPL 2.0_      |     ✖      |
| pathspec                                 | MOZILLA PUBLIC LICENSE 2.0 _MPL 2.0_      |     ✖      |
| fqdn                                     | MOZILLA PUBLIC LICENSE 2.0 _MPL 2.0_      |     ✖      |
| ---------------------------------------- | ----------------------------------------- | :--------: |
| adjusttext                               | MIT                                       |     ✔      |
| aiofiles                                 | APACHE SOFTWARE LICENSE                   |     ✔      |
| aiohappyeyeballs                         | PYTHON SOFTWARE FOUNDATION LICENSE        |     ✔      |
| aiohttp                                  | APACHE-2.0                                |     ✔      |
| aiosignal                                | APACHE SOFTWARE LICENSE                   |     ✔      |
| airportsdata                             | MIT LICENSE                               |     ✔      |
| annotated-types                          | MIT LICENSE                               |     ✔      |
| anthropic                                | MIT LICENSE                               |     ✔      |
| anyio                                    | MIT LICENSE                               |     ✔      |
| appnope                                  | BSD LICENSE                               |     ✔      |
| argon2-cffi                              | MIT                                       |     ✔      |
| argon2-cffi-bindings                     | MIT LICENSE                               |     ✔      |
| arrow                                    | APACHE SOFTWARE LICENSE                   |     ✔      |
| asttokens                                | APACHE 2.0                                |     ✔      |
| async-lru                                | MIT LICENSE                               |     ✔      |
| asyncstdlib-fw                           | MIT LICENSE                               |     ✔      |
| atpublic                                 | APACHE SOFTWARE LICENSE                   |     ✔      |
| attrs                                    | MIT LICENSE                               |     ✔      |
| babel                                    | BSD LICENSE                               |     ✔      |
| backoff                                  | MIT LICENSE                               |     ✔      |
| bcrypt                                   | APACHE SOFTWARE LICENSE                   |     ✔      |
| beautifulsoup4                           | MIT LICENSE                               |     ✔      |
| betterproto-fw                           | MIT LICENSE                               |     ✔      |
| bioinfokit                               | MIT LICENSE                               |     ✔      |
| black                                    | MIT LICENSE                               |     ✔      |
| bleach                                   | APACHE SOFTWARE LICENSE                   |     ✔      |
| build                                    | MIT LICENSE                               |     ✔      |
| cachetools                               | MIT LICENSE                               |     ✔      |
| cffi                                     | MIT LICENSE                               |     ✔      |
| charset-normalizer                       | MIT LICENSE                               |     ✔      |
| chart-studio                             | MIT                                       |     ✔      |
| chromadb                                 | APACHE SOFTWARE LICENSE                   |     ✔      |
| click                                    | BSD-3-CLAUSE                              |     ✔      |
| click-default-group                      | PUBLIC DOMAIN                             |     ✔      |
| cloudpickle                              | BSD LICENSE                               |     ✔      |
| coloredlogs                              | MIT LICENSE                               |     ✔      |
| comm                                     | BSD LICENSE                               |     ✔      |
| command-runner                           | BSD LICENSE                               |     ✔      |
| condense-json                            | APACHE-2.0                                |     ✔      |
| contourpy                                | BSD LICENSE                               |     ✔      |
| cryptography                             | APACHE-2.0;; BSD-3-CLAUSE                 |     ✔      |
| cycler                                   | BSD LICENSE                               |     ✔      |
| dataclasses-json                         | MIT LICENSE                               |     ✔      |
| debugpy                                  | MIT LICENSE                               |     ✔      |
| decorator                                | BSD LICENSE                               |     ✔      |
| defusedxml                               | PYTHON SOFTWARE FOUNDATION LICENSE        |     ✔      |
| dill                                     | BSD LICENSE                               |     ✔      |
| dirtyjson                                | ACADEMIC FREE LICENSE _AFL_;; MIT LICENSE |     ✔      |
| diskcache                                | APACHE SOFTWARE LICENSE                   |     ✔      |
| distro                                   | APACHE SOFTWARE LICENSE                   |     ✔      |
| dnspython                                | ISC LICENSE _ISCL_                        |     ✔      |
| duckdb                                   | MIT LICENSE                               |     ✔      |
| duckdb-engine                            | MIT LICENSE                               |     ✔      |
| durationpy                               | MIT                                       |     ✔      |
| e2b                                      | MIT LICENSE                               |     ✔      |
| e2b-code-interpreter                     | MIT LICENSE                               |     ✔      |
| email-validator                          | THE UNLICENSE _UNLICENSE_                 |     ✔      |
| emoji                                    | BSD LICENSE                               |     ✔      |
| et-xmlfile                               | MIT LICENSE                               |     ✔      |
| executing                                | MIT LICENSE                               |     ✔      |
| faker                                    | MIT LICENSE                               |     ✔      |
| fastapi                                  | MIT LICENSE                               |     ✔      |
| fastapi-cli                              | MIT LICENSE                               |     ✔      |
| fastapi-cloud-cli                        | MIT LICENSE                               |     ✔      |
| fastjsonschema                           | BSD LICENSE                               |     ✔      |
| filelock                                 | UNLICENSE                                 |     ✔      |
| filetype                                 | MIT LICENSE                               |     ✔      |
| fireworks-ai                             | MIT LICENSE                               |     ✔      |
| flatbuffers                              | APACHE SOFTWARE LICENSE                   |     ✔      |
| fonttools                                | MIT                                       |     ✔      |
| frozenlist                               | APACHE-2.0                                |     ✔      |
| fsspec                                   | BSD LICENSE                               |     ✔      |
| genson                                   | MIT LICENSE                               |     ✔      |
| google-auth                              | APACHE SOFTWARE LICENSE                   |     ✔      |
| google-auth-oauthlib                     | APACHE SOFTWARE LICENSE                   |     ✔      |
| google-search-results                    | MIT LICENSE                               |     ✔      |
| googleapis-common-protos                 | APACHE SOFTWARE LICENSE                   |     ✔      |
| groq                                     | APACHE SOFTWARE LICENSE                   |     ✔      |
| grpcio                                   | APACHE SOFTWARE LICENSE                   |     ✔      |
| grpclib                                  | BSD LICENSE                               |     ✔      |
| gspread                                  | MIT LICENSE                               |     ✔      |
| gspread-dataframe                        | MIT LICENSE                               |     ✔      |
| h11                                      | MIT LICENSE                               |     ✔      |
| h2                                       | MIT LICENSE                               |     ✔      |
| hf-xet                                   | APACHE-2.0                                |     ✔      |
| hpack                                    | MIT LICENSE                               |     ✔      |
| html5lib                                 | MIT LICENSE                               |     ✔      |
| httpcore                                 | BSD-3-CLAUSE                              |     ✔      |
| httptools                                | MIT LICENSE                               |     ✔      |
| httpx                                    | BSD LICENSE                               |     ✔      |
| httpx-sse                                | MIT                                       |     ✔      |
| httpx-ws                                 | MIT LICENSE                               |     ✔      |
| huggingface-hub                          | APACHE SOFTWARE LICENSE                   |     ✔      |
| humanfriendly                            | MIT LICENSE                               |     ✔      |
| hyperframe                               | MIT LICENSE                               |     ✔      |
| ibis-framework                           | APACHE SOFTWARE LICENSE                   |     ✔      |
| idna                                     | BSD LICENSE                               |     ✔      |
| importlib-metadata                       | APACHE SOFTWARE LICENSE                   |     ✔      |
| importlib-resources                      | APACHE SOFTWARE LICENSE                   |     ✔      |
| iniconfig                                | MIT                                       |     ✔      |
| inquirerpy                               | MIT LICENSE                               |     ✔      |
| interegular                              | MIT LICENSE                               |     ✔      |
| invoke                                   | BSD LICENSE                               |     ✔      |
| ipaddress                                | PYTHON SOFTWARE FOUNDATION LICENSE        |     ✔      |
| ipykernel                                | BSD 3-CLAUSE LICENSE                      |     ✔      |
| ipython                                  | BSD LICENSE                               |     ✔      |
| ipython-genutils                         | BSD LICENSE                               |     ✔      |
| ipywidgets                               | BSD LICENSE                               |     ✔      |
| iso3166                                  | MIT LICENSE                               |     ✔      |
| isoduration                              | ISC LICENSE _ISCL_                        |     ✔      |
| jedi                                     | MIT LICENSE                               |     ✔      |
| jinja2                                   | BSD LICENSE                               |     ✔      |
| jiter                                    | MIT LICENSE                               |     ✔      |
| joblib                                   | BSD LICENSE                               |     ✔      |
| json5                                    | APACHE SOFTWARE LICENSE                   |     ✔      |
| jsonpatch                                | BSD LICENSE                               |     ✔      |
| jsonpointer                              | BSD LICENSE                               |     ✔      |
| jsonschema                               | MIT                                       |     ✔      |
| jsonschema-specifications                | MIT                                       |     ✔      |
| jupysql                                  | APACHE SOFTWARE LICENSE                   |     ✔      |
| jupysql-plugin                           | BSD LICENSE                               |     ✔      |
| jupyter                                  | BSD LICENSE                               |     ✔      |
| jupyter-client                           | BSD LICENSE                               |     ✔      |
| jupyter-console                          | BSD LICENSE                               |     ✔      |
| jupyter-core                             | BSD-3-CLAUSE                              |     ✔      |
| jupyter-events                           | BSD LICENSE                               |     ✔      |
| jupyter-lsp                              | BSD LICENSE                               |     ✔      |
| jupyter-server                           | BSD LICENSE                               |     ✔      |
| jupyter-server-terminals                 | BSD LICENSE                               |     ✔      |
| jupyterlab                               | BSD LICENSE                               |     ✔      |
| jupyterlab-pygments                      | BSD LICENSE                               |     ✔      |
| jupyterlab-server                        | BSD LICENSE                               |     ✔      |
| jupyterlab-widgets                       | BSD LICENSE                               |     ✔      |
| kaleido                                  | MIT                                       |     ✔      |
| kiwisolver                               | BSD LICENSE                               |     ✔      |
| kubernetes                               | APACHE SOFTWARE LICENSE                   |     ✔      |
| langchain                                | MIT                                       |     ✔      |
| langchain-anthropic                      | MIT                                       |     ✔      |
| langchain-chroma                         | MIT                                       |     ✔      |
| langchain-community                      | MIT                                       |     ✔      |
| langchain-core                           | MIT                                       |     ✔      |
| langchain-experimental                   | MIT LICENSE                               |     ✔      |
| langchain-fireworks                      | MIT                                       |     ✔      |
| langchain-groq                           | MIT                                       |     ✔      |
| langchain-huggingface                    | MIT                                       |     ✔      |
| langchain-openai                         | MIT                                       |     ✔      |
| langchain-text-splitters                 | MIT                                       |     ✔      |
| langchain-together                       | MIT LICENSE                               |     ✔      |
| langchainhub                             | MIT LICENSE                               |     ✔      |
| langdetect                               | APACHE SOFTWARE LICENSE                   |     ✔      |
| langgraph                                | MIT                                       |     ✔      |
| langgraph-checkpoint                     | MIT                                       |     ✔      |
| langgraph-prebuilt                       | MIT                                       |     ✔      |
| langgraph-sdk                            | MIT                                       |     ✔      |
| langsmith                                | MIT LICENSE                               |     ✔      |
| lark                                     | MIT LICENSE                               |     ✔      |
| llamaapi                                 | MIT LICENSE                               |     ✔      |
| llm                                      | APACHE-2.0                                |     ✔      |
| llm-anthropic                            | APACHE SOFTWARE LICENSE                   |     ✔      |
| llm-claude-3                             | APACHE SOFTWARE LICENSE                   |     ✔      |
| load-dotenv                              | APACHE SOFTWARE LICENSE                   |     ✔      |
| lxml                                     | BSD LICENSE                               |     ✔      |
| markdown                                 | BSD-3-CLAUSE                              |     ✔      |
| markdown-it-py                           | MIT LICENSE                               |     ✔      |
| markupsafe                               | BSD LICENSE                               |     ✔      |
| marshmallow                              | MIT LICENSE                               |     ✔      |
| matplotlib                               | PYTHON SOFTWARE FOUNDATION LICENSE        |     ✔      |
| matplotlib-inline                        | BSD LICENSE                               |     ✔      |
| matplotlib-venn                          | MIT LICENSE                               |     ✔      |
| mdurl                                    | MIT LICENSE                               |     ✔      |
| mistune                                  | BSD LICENSE                               |     ✔      |
| mmh3                                     | MIT LICENSE                               |     ✔      |
| mpmath                                   | BSD LICENSE                               |     ✔      |
| multidict                                | APACHE LICENSE 2.0                        |     ✔      |
| multiprocess                             | BSD LICENSE                               |     ✔      |
| mypy-extensions                          | MIT LICENSE                               |     ✔      |
| nbclient                                 | BSD LICENSE                               |     ✔      |
| nbconvert                                | BSD LICENSE                               |     ✔      |
| nbformat                                 | BSD LICENSE                               |     ✔      |
| nest-asyncio                             | BSD LICENSE                               |     ✔      |
| networkx                                 | BSD LICENSE                               |     ✔      |
| nltk                                     | APACHE SOFTWARE LICENSE                   |     ✔      |
| notebook                                 | BSD LICENSE                               |     ✔      |
| notebook-shim                            | BSD LICENSE                               |     ✔      |
| numexpr                                  | MIT LICENSE                               |     ✔      |
| numpy                                    | BSD LICENSE                               |     ✔      |
| oauthlib                                 | BSD-3-CLAUSE                              |     ✔      |
| ofunctions                               | BSD LICENSE                               |     ✔      |
| olefile                                  | BSD LICENSE                               |     ✔      |
| onnxruntime                              | MIT LICENSE                               |     ✔      |
| openai                                   | APACHE SOFTWARE LICENSE                   |     ✔      |
| openpyxl                                 | MIT LICENSE                               |     ✔      |
| opentelemetry-api                        | APACHE-2.0                                |     ✔      |
| opentelemetry-exporter-otlp-proto-common | APACHE-2.0                                |     ✔      |
| opentelemetry-exporter-otlp-proto-grpc   | APACHE-2.0                                |     ✔      |
| opentelemetry-proto                      | APACHE-2.0                                |     ✔      |
| opentelemetry-sdk                        | APACHE-2.0                                |     ✔      |
| opentelemetry-semantic-conventions       | APACHE-2.0                                |     ✔      |
| orjson                                   | APACHE SOFTWARE LICENSE;; MIT LICENSE     |     ✔      |
| ormsgpack                                | APACHE SOFTWARE LICENSE;; MIT LICENSE     |     ✔      |
| outlines                                 | APACHE-2.0                                |     ✔      |
| outlines-core                            | APACHE-2.0                                |     ✔      |
| overrides                                | APACHE LICENSE\_ VERSION 2.0              |     ✔      |
| packaging                                | APACHE SOFTWARE LICENSE;; BSD LICENSE     |     ✔      |
| pandantic                                | MIT LICENSE                               |     ✔      |
| pandas                                   | BSD LICENSE                               |     ✔      |
| pandas-stubs                             | BSD LICENSE                               |     ✔      |
| pandocfilters                            | BSD LICENSE                               |     ✔      |
| parso                                    | MIT LICENSE                               |     ✔      |
| parsy                                    | MIT LICENSE                               |     ✔      |
| patsy                                    | BSD LICENSE                               |     ✔      |
| pexpect                                  | ISC LICENSE _ISCL_                        |     ✔      |
| pfzy                                     | MIT LICENSE                               |     ✔      |
| pillow                                   | MIT-CMU                                   |     ✔      |
| pip                                      | MIT LICENSE                               |     ✔      |
| platformdirs                             | MIT LICENSE                               |     ✔      |
| ploomber-core                            | APACHE SOFTWARE LICENSE                   |     ✔      |
| plotly                                   | MIT LICENSE                               |     ✔      |
| pluggy                                   | MIT LICENSE                               |     ✔      |
| posthog                                  | MIT LICENSE                               |     ✔      |
| prettytable                              | BSD-3-CLAUSE                              |     ✔      |
| prometheus-client                        | APACHE-2.0;; BSD-2-CLAUSE                 |     ✔      |
| prompt-toolkit                           | BSD LICENSE                               |     ✔      |
| propcache                                | APACHE SOFTWARE LICENSE                   |     ✔      |
| protobuf                                 | 3-CLAUSE BSD LICENSE                      |     ✔      |
| psutil                                   | BSD LICENSE                               |     ✔      |
| ptyprocess                               | ISC LICENSE _ISCL_                        |     ✔      |
| pure-eval                                | MIT LICENSE                               |     ✔      |
| puremagic                                | MIT LICENSE                               |     ✔      |
| pyarrow                                  | APACHE SOFTWARE LICENSE                   |     ✔      |
| pyarrow-hotfix                           | APACHE LICENSE\_ VERSION 2.0              |     ✔      |
| pyasn1                                   | BSD LICENSE                               |     ✔      |
| pyasn1-modules                           | BSD LICENSE                               |     ✔      |
| pybase64                                 | BSD LICENSE                               |     ✔      |
| pycparser                                | BSD LICENSE                               |     ✔      |
| pydantic                                 | MIT                                       |     ✔      |
| pydantic-core                            | MIT LICENSE                               |     ✔      |
| pydantic-settings                        | MIT                                       |     ✔      |
| pygments                                 | BSD LICENSE                               |     ✔      |
| pymysql                                  | MIT LICENSE                               |     ✔      |
| pypandoc-binary                          | MIT LICENSE                               |     ✔      |
| pyparsing                                | MIT LICENSE                               |     ✔      |
| pypdf                                    | BSD-3-CLAUSE                              |     ✔      |
| pypika                                   | APACHE SOFTWARE LICENSE                   |     ✔      |
| pyproject-hooks                          | MIT LICENSE                               |     ✔      |
| pytest                                   | MIT LICENSE                               |     ✔      |
| python-dateutil                          | APACHE SOFTWARE LICENSE;; BSD LICENSE     |     ✔      |
| python-dotenv                            | BSD LICENSE                               |     ✔      |
| python-iso639                            | APACHE SOFTWARE LICENSE                   |     ✔      |
| python-json-logger                       | BSD LICENSE                               |     ✔      |
| python-magic                             | MIT LICENSE                               |     ✔      |
| python-multipart                         | APACHE SOFTWARE LICENSE                   |     ✔      |
| python-oxmsg                             | MIT LICENSE                               |     ✔      |
| python-ulid                              | MIT LICENSE                               |     ✔      |
| pytz                                     | MIT LICENSE                               |     ✔      |
| pyyaml                                   | MIT LICENSE                               |     ✔      |
| pyzmq                                    | BSD LICENSE                               |     ✔      |
| rapidfuzz                                | MIT                                       |     ✔      |
| referencing                              | MIT                                       |     ✔      |
| regex                                    | APACHE SOFTWARE LICENSE                   |     ✔      |
| requests                                 | APACHE SOFTWARE LICENSE                   |     ✔      |
| requests-oauthlib                        | BSD LICENSE                               |     ✔      |
| requests-toolbelt                        | APACHE SOFTWARE LICENSE                   |     ✔      |
| retrying                                 | APACHE SOFTWARE LICENSE                   |     ✔      |
| rfc3339-validator                        | MIT LICENSE                               |     ✔      |
| rfc3986-validator                        | MIT LICENSE                               |     ✔      |
| rfc3987-syntax                           | MIT                                       |     ✔      |
| rich                                     | MIT LICENSE                               |     ✔      |
| rich-toolkit                             | MIT                                       |     ✔      |
| rignore                                  | MIT                                       |     ✔      |
| rpds-py                                  | MIT                                       |     ✔      |
| rsa                                      | APACHE SOFTWARE LICENSE                   |     ✔      |
| ruff                                     | MIT LICENSE                               |     ✔      |
| safetensors                              | APACHE SOFTWARE LICENSE                   |     ✔      |
| scikit-learn                             | BSD-3-CLAUSE                              |     ✔      |
| scipy                                    | BSD LICENSE                               |     ✔      |
| seaborn                                  | BSD LICENSE                               |     ✔      |
| send2trash                               | BSD LICENSE                               |     ✔      |
| sentencepiece                            | APACHE SOFTWARE LICENSE                   |     ✔      |
| sentry-sdk                               | BSD LICENSE                               |     ✔      |
| setuptools                               | MIT                                       |     ✔      |
| shellingham                              | ISC LICENSE _ISCL_                        |     ✔      |
| six                                      | MIT LICENSE                               |     ✔      |
| sniffio                                  | APACHE SOFTWARE LICENSE;; MIT LICENSE     |     ✔      |
| soupsieve                                | MIT                                       |     ✔      |
| sqlalchemy                               | MIT                                       |     ✔      |
| sqlglot                                  | MIT LICENSE                               |     ✔      |
| sqlite-fts4                              | APACHE LICENSE\_ VERSION 2.0              |     ✔      |
| sqlite-migrate                           | APACHE-2.0                                |     ✔      |
| sqlite-utils                             | APACHE SOFTWARE LICENSE                   |     ✔      |
| sqlparse                                 | BSD LICENSE                               |     ✔      |
| stack-data                               | MIT LICENSE                               |     ✔      |
| starlette                                | BSD-3-CLAUSE                              |     ✔      |
| statsmodels                              | BSD LICENSE                               |     ✔      |
| sympy                                    | BSD LICENSE                               |     ✔      |
| tabulate                                 | MIT LICENSE                               |     ✔      |
| tenacity                                 | APACHE SOFTWARE LICENSE                   |     ✔      |
| terminado                                | BSD LICENSE                               |     ✔      |
| text-generation                          | APACHE SOFTWARE LICENSE                   |     ✔      |
| textwrap3                                | PYTHON SOFTWARE FOUNDATION LICENSE        |     ✔      |
| threadpoolctl                            | BSD LICENSE                               |     ✔      |
| tiktoken                                 | MIT LICENSE                               |     ✔      |
| tinycss2                                 | BSD LICENSE                               |     ✔      |
| tokenizers                               | APACHE SOFTWARE LICENSE                   |     ✔      |
| toml                                     | MIT LICENSE                               |     ✔      |
| toolz                                    | BSD LICENSE                               |     ✔      |
| torch                                    | BSD LICENSE                               |     ✔      |
| tornado                                  | APACHE SOFTWARE LICENSE                   |     ✔      |
| tqdm                                     | MIT LICENSE;; MOZILLA PUBLIC LICENSE 2.0  |     ✔      |
| traitlets                                | BSD LICENSE                               |     ✔      |
| transformers                             | APACHE SOFTWARE LICENSE                   |     ✔      |
| typer                                    | MIT LICENSE                               |     ✔      |
| types-python-dateutil                    | APACHE-2.0                                |     ✔      |
| types-pytz                               | APACHE-2.0                                |     ✔      |
| types-requests                           | APACHE-2.0                                |     ✔      |
| typing                                   | PYTHON SOFTWARE FOUNDATION LICENSE        |     ✔      |
| typing-extensions                        | PSF-2.0                                   |     ✔      |
| typing-inspect                           | MIT LICENSE                               |     ✔      |
| typing-inspection                        | MIT                                       |     ✔      |
| tzdata                                   | APACHE SOFTWARE LICENSE                   |     ✔      |
| unstructured                             | APACHE SOFTWARE LICENSE                   |     ✔      |
| unstructured-client                      | MIT LICENSE                               |     ✔      |
| uri-template                             | MIT LICENSE                               |     ✔      |
| urllib3                                  | MIT                                       |     ✔      |
| uvicorn                                  | BSD-3-CLAUSE                              |     ✔      |
| uvloop                                   | APACHE SOFTWARE LICENSE;; MIT LICENSE     |     ✔      |
| watchfiles                               | MIT LICENSE                               |     ✔      |
| wcwidth                                  | MIT LICENSE                               |     ✔      |
| webcolors                                | BSD LICENSE                               |     ✔      |
| webencodings                             | BSD LICENSE                               |     ✔      |
| websocket-client                         | APACHE SOFTWARE LICENSE                   |     ✔      |
| websockets                               | BSD LICENSE                               |     ✔      |
| widgetsnbextension                       | BSD LICENSE                               |     ✔      |
| wonderwords                              | MIT LICENSE                               |     ✔      |
| wrapt                                    | BSD LICENSE                               |     ✔      |
| wsproto                                  | MIT LICENSE                               |     ✔      |
| xarray                                   | APACHE SOFTWARE LICENSE                   |     ✔      |
| xxhash                                   | BSD LICENSE                               |     ✔      |
| yarl                                     | APACHE SOFTWARE LICENSE                   |     ✔      |
| zipp                                     | MIT                                       |     ✔      |
| zstandard                                | BSD LICENSE                               |     ✔      |

If there are any questions about usage or licensing, please reach out over email in the email listed for the corresponding author in our article PDF.
