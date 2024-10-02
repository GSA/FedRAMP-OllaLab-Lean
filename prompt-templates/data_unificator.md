# Data Unificator Prompt Template
This document will guide you through the steps of working with LLMs to build a professional and secure "Data Unificator" Project. The goal is to help you jump start your project and you may need to add more steps and prompts. We hope you'll find this document useful and contribute your prompts to improve it.

## Step 1 - Define and Refine The Project's Problem Statement
Prompt for the project's refined problem statement
```
I have the following problem statement: data intakes are being supported by multiple google forms, there is a problem with unifying and normalizing gathered data from multiple data source files with potential overlaps among them.
Give me an improved problem statement considering the following guiding questions:
What are the key components and aspects of the problem statement?
What potential ambiguities or unclear elements exist in the current problem statement?
What should be included in the scope of the problem, and what elements should be explicitly excluded?
What assumptions are we making about the problem that might need to be challenged or verified?
How can we make the problem statement more specific and actionable?
```

The result will be saved to **{{refined problem statement}}**

## Step 2 - Identifying Project's Functional and Non-functional Requirements
The prompt is:

>
>{{refinedproblem statement}}
>
>List the key functional and non-functional requirements for a python application that will address the mentioned problem, key challenges, and objectives. Please be consise yet as comprehensive as possible.


You can read the result and modify/add more requirements as needed.

The final result will be saved to **{{requirements}}**

## Step 3 - Define The Project Architecture
The prompt is:
>
>{{refinedproblem statement}}
>
>{{requirements}}
>
>Outline a system architecture for this project, including main components, their interactions, and any external systems or APIs.


The results will be saved to **{{architecture}}**

## Step 4 - Pre Project-Generation
At this point, we concatenate **{{refinedproblem statement}} {{requirements}} {{architecture}}**. It is always a good idea to review these information and make modification/addition as needed. The below is the collaborative result of LLM's generated text and my addition/improvement based on my experience.

```
We are experiencing difficulties in unifying and normalizing data collected through multiple sources. This hinders our ability to perform accurate data analysis and affects decision-making processes. We need to develop the "Data Unificator" application to effectively merge the data from all local source files, eliminate overlaps, normalize and standardize the data to ensure consistency and reliability in our data reporting.

Key Technical Requirements
    Use Streamlit for the Graphical User Interface.
    Use st.empty() for dynamic organization of contents including error messages.
    Use @st.fragment decorator (https://docs.streamlit.io/develop/concepts/architecture/fragments) to allow individual fragment run and rerun without rerun the whole app. 
    Back-end Python functions can all be wrapped in an API.
    Parallelism/concurencies should be used. User can choose how many source files to be processed at the same time.
    Batch processing for large datasets
    Codes, rules, and other important components should be modular and can be updated independently
    Keep detailed logs of all important details (i.e. errors, exception, conflicts, data merge)
    Maintain audit trails
    Logs and audit trails should be properly stored and protected.
    Use Autogluon or better solution for AutoML.
    Use Autoviz or better for automatic Exploratory Data Analysis (EDA) and visualization of data.
    Use PostgreSQL for relational database if needed.
    The entire process including programmed actions and user manual actions are recorded and can be repeated later in command line with python.

The Data Unificator program must satisfy the following requirements:

Functional Requirements

    Data Import
        The application shall import data from multiple offline data sources such as JSON, CSVs, TSVs, XML, Excel, parquet.
        Through a graphical user interface (GUI), users should be able to point the application to a local folder storing those files.
        Before importing, the application must make sure the application can parse and process the files and inform the user via the GUI of the files that cannot be processed.
        While importing, the application should ensure consistency in character encoding and other data encoding standards.
        While importing, the application should avoid importing data that may lead code execution, memory overflow, and other cybersecurity issues.
        While importing, the application should remove duplicated data entries in each source file.
        Before finalizing the import of a source file, inform the user via GUI about any discrepancies and how to reconcile them. The user can either fix the discrepancies in the file and instruct the application to rerun the Data Import or accept the discrepancies and move on.
        Before finalizing the import of a source, the application allows the user to input data for missing data fields or select one among predefined strategies for handling missing data and null data for affected fields
        Sample strategies for handling missing or null data are statistical imputation, predictive model, deletion, manual input by user.
        Before finalizing the import of a source file, inform the user via GUI about any personal identifiable data entries and how to reconcile them.
        After successful import of each source, Exploratory Data Analysis (EDA) is performed for each source file and results are displayed. The results must at least include sample rows, column names and data types, basic statics, unique value counts, and visualization of data distributions. The results for each source file must be colisrael lapsible.
    
    Data Mapping
        The application reads each imported data source and extract a list of all data fields.
        Get metadata for each field including data types, units, descriptions and available constraints.
        Identify overlapping fields based on names.
        Allow user to establish source hierachy based on data reliability and accuracy.
        All sources are assigned default weights and allow user to adjust weights.
        Align data structures and hierarchies across source files.
        Identify conflicts in data, formats, types, key pairs, and data structure.
        Display identified conflicts to user
        Conflict resolution strategies were stored in configuration files or  databases
        Display and explain conflict resolution strategies such as manual, time-based (lastest or earliest data win), hierachy-based, weight-based and so on.
        Allow user to select conflict resolution strategy to resolve conflict
        Allow the user to create a mapping dictionary that links original field names to standardized names.
        Allow the users to save the mapping dictionary, load and modify it as needed.
        Allow dictionary versioning.
        Verify that fields mapped together have compatible data types and inform the user of incompatible data types.
        Detect mapping ambiguities and other problems and propose solutions for user approval.
        Allow the users via GUI to convert data types of user selected fields.

    Data Normalization
        The application shall standardize data formats (e.g., dates, numbers, text casing) to ensure consistency.
        It shall handle different data types and convert them into a unified format.
        Standardize units of measurement such as time, currency, etc.
        Detect extreme outliers and ask user for selecting action such as capping, removal, or transformation.
        Allow user to select fields and apply a common scale (ie. 0-1 range, z-score normalization).
        Allow user to aggregate new fields from existing fields.
        Allow user to remove fields.
        Standardize text encoding.

    Data Deduplication and Consolidation
        The application shall merge data from multiple source files into a single, unified dataset.
        It shall maintain data integrity during the consolidation process.
        Allow the user to develop/configure criteria for determining what constitutes a duplication in the combined dataset.
        Support common duplicate detection criteria such as Exact Match, Fuzzy Match, Composite Key Matching, demographic information, geographic information, business-specific identifiers, biometric data, document numbers, digital footprints, transactional data, communication pattern, behavioral pattern, textual similiarity, meta data, network analysis, probabilistic matching, domain-specific rules, cross-reference checks.
        The application shall detect and eliminate duplicate entries based on the selected criteria.
        

    Data Validation
        The application shall validate data for completeness, correctness, and consistency.
        It shall flag or handle missing or inconsistent data entries.
        Ensure foreign key relationships are maintained across merged datasets.
        Ensure logical consistency across different attributes.
        Ensure that time-series data is consistent and complete.
        Ensure metadata is consistent and actually reflects the actual data.
        Recalculate derived fields to ensure accuracy.
        Double check for impossible values and report to user for action.
        Double check for duplciated records and remove them.
        Ensure data formats are consistent and valid.
        Ensure that strings follow expected patterns.
        Verify that audit trails and logs are complete and consistent.
        Allow the user to perform manual review of sample records.
        Perform Exploratory Data Analysis (EDA) on the whole dataset and the results must at least include sample rows, column names and data types, basic statics, unique value counts, and visualization of data distributions. The results must be colapsible.
        Perform statistical analysis to identify anomalies or unexpected patterns.
        Allow the use of business rules to validate data.


    Error Handling
        The application shall provide meaningful error messages and logging for any data inconsistencies or processing errors.
        It shall handle exceptions without terminating the entire process unexpectedly.
        Use try-except blocks.
        Handle API and database connection errors explicitly.
        Use st.warning() for non-critical issues.
        Use st.error() to display clear and meaningful error messages to users without revealing information that may compromise system security.
        Log full error messages and traces to error logs.
        Use st.exception for full traceback.
        Implement custom error handling as needed for specific scenarios.
        Use st.stop() to control Streamlit execution flow.
        Implement global error handling to catch any unhandled exceptions.

    User Interface
        The application shall offer user-friendly interfaces, via both command-line and Streamlit graphical interface, for configuration and operation.
        It shall provide clear instructions and prompts for user inputs.
        Streamlit interface should allow user to make all necessary configuration, and customization. It should also allow the user to view samples of end results in each step of the data pipeline.

    Other Functional Requirements
        The application shall generate reports or export the consolidated data in commonly used formats (e.g., JSON, CSV, Excel).
        It shall support exporting data to databases if required. In such case, the application will offer users via GUI the option to input database connection information.
        The application shall support scheduled execution to automate data consolidation at defined intervals, running separated from the Streamlit GUI.
        It shall allow users to set up and modify the schedules easily.
        The application shall securely handle authentication tokens and personal data.
        It shall comply with relevant data protection regulations (e.g., GDPR).
        The application shall allow users to save and load configuration settings for data mappings, normalization rules, and deduplication criteria.
        It shall support easy updates to configurations as forms change over time.

Non-Functional Requirements

    Performance
        The application shall process large datasets efficiently without significant delays.
        It shall optimize resource usage to prevent excessive memory or CPU consumption.

    Scalability
        The application shall be able to handle an increasing number of source files and larger volumes of data with minimal performance degradation.

    Reliability
        The application shall perform its functions consistently and accurately over time.
        It shall have mechanisms to recover from failures without data loss.

    Usability
        The application shall be intuitive and easy to use for users with varying technical expertise.
        It shall include comprehensive documentation and help resources.

    Maintainability
        The application's codebase shall be well-documented and modular to facilitate future enhancements and bug fixes.
        It shall follow best coding practices and standards.

    Compatibility
        The application shall be compatible with the required versions of Python and any third-party libraries.
        It shall run on the operating systems used by the organization (e.g., Windows, macOS, Linux).

    Security
        The application shall implement security best practices to protect data during processing and storage.
        It shall handle all credentials and sensitive information securely, avoiding hard-coded secrets.

    Logging and Monitoring
        The application shall provide detailed logging to assist in monitoring its operations and troubleshooting issues.
        It shall log significant events without exposing sensitive data.

    Extensibility
        The application shall be designed to allow new features or integrations to be added with minimal changes to the existing codebase.
        It shall support plugin or module systems if applicable.

    Legal and Ethical Compliance
        The application shall comply with all relevant laws and ethical guidelines related to data processing and user privacy.
        It shall include options to anonymize or pseudonymize personal data if necessary.

Produce all necessary folders/files/codes/tests to implement the project. Generate comprehensive and full implementation logic for each file. Make sure not to miss any files. 
```

## Step 5 - Project Generation
At this step, we generate the bulk of the project folders and files. The prompt template is:

>
>{{refinedproblem statement}} {{requirements}} {{architecture}}
>
>{{last minute requirements}}
>
>Produce all necessary folders/files/codes/tests to implement the project. For graphical web interface, please use Streamlit. The main programming language must be Python. Make sure not to miss any files. 
>

The {{last minute requirements}} can be something like:
```
We need to fit these files and folders into an existing streamlit app as its component. The existing streamlit app already has main.py in the "app" folder. In the current "app" folder, there's a "pages" folder. First, create a "data-unificator" folder in the "pages" folder and put all the project folders and files in it. Create "data_unificator.py" as the project Streamlit app and place it in the "pages" folder.
```

## Step 6+ - Section Code Optimization
In this step, we provide additional prompts to further improve, iterate, and optimize section codes.

The promt template is:

> Double check and improve the {{section files}} and related files to make sure they satisfy the following requirements for {{section}}:
>
>{{core requirements}}
>
>{{section requirements}}
>

{{section}} is one of the application main sections such as "data import"

{{section files}} are the implementation of the section such as data_import.py and import_ui.py

{{core requirements}} =
```
    Use Streamlit for the Graphical User Interface.
    Use st.empty() for dynamic organization of contents including error messages.
    Use @st.fragment decorator (https://docs.streamlit.io/develop/concepts/architecture/fragments) to allow individual fragment run and rerun without rerun the whole app. 
    Parallelism/concurencies should be used. User can choose how many source files to be processed at the same time.
    Batch processing for large datasets
    Keep detailed logs of all important details (i.e. errors, exception, conflicts, data merge)
    Maintain audit trails
    Logs and audit trails should be properly stored and protected.
    Use Autogluon or better solution for AutoML.
    Use Autoviz or better for automatic Exploratory Data Analysis (EDA) and visualization of data.
    Use PostgreSQL for relational database if needed.
    The entire process including programmed actions and user manual actions are recorded and can be repeated later in command line with python.
    The application shall provide meaningful error messages and logging for any data inconsistencies or processing errors.
    It shall handle exceptions without terminating the entire process unexpectedly.
    Use try-except blocks.
    Handle API and database connection errors explicitly.
    Use st.warning() for non-critical issues.
    Use st.error() to display clear and meaningful error messages to users without revealing information that may compromise system security.
    Log full error messages and traces to error logs.
    Use st.exception for full traceback.
    Implement custom error handling as needed for specific scenarios.
    Use st.stop() to control Streamlit execution flow.
    Implement global error handling to catch any unhandled exceptions.
    The application shall offer user-friendly interfaces, via both command-line and Streamlit graphical interface, for configuration and operation.
    It shall provide clear instructions and prompts for user inputs.
    Streamlit interface should allow user to make all necessary configuration, and customization. It should also allow the user to view samples of end results in each step of the data pipeline.
```

{{section requirements}} is the requirements specific to a section such as
```
    Data Normalization
        The application shall standardize data formats (e.g., dates, numbers, text casing) to ensure consistency.
        It shall handle different data types and convert them into a unified format.
        Standardize units of measurement such as time, currency, etc.
        Detect extreme outliers and ask user for selecting action such as capping, removal, or transformation.
        Allow user to select fields and apply a common scale (ie. 0-1 range, z-score normalization).
        Allow user to aggregate new fields from existing fields.
        Allow user to remove fields.
        Standardize text encoding.
```

## Step 7 - Final Check Prompt
In the final step, we run the following prompt to allow the LLM to double check its work.

> Double check all files make sure they are all consistent and free of programming errors nor logic errors. 
