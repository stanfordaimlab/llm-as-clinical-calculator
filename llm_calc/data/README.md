# overview of data organization
- build_database: all the initial input data that was used to build the inputs for the model 
  - excel_as_csvs: remote input data from https://alx.gd/llm-calc-view-database that was converted to CSV format and stored here
  - cases: vignettes for the model
  - reference_material: reference material from MDCalc used for RAG
  - vignettes_templates: vignettes (YAML) for each calculator with template codes for specifics of the fictionalized patient
  - vignettes_templates_json: same as `vignettes_templates` but in JSON format
- database: contains two databases, both with duckDB format
  - inputs_database: contains the input data for the model, downloaded from https://alx.gd/llm-calc-view-database and formatted for the model
  - experiments_database: contains the metadata and vignettes for the experiments
- omc_api_definition: contains the OMC API definition in JSON and YAML formats to OpenAPI 3.0.0 specifications