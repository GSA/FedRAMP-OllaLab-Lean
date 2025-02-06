# FedRAMP OllaLab – AnyDoc to JSON

## Overview

Organizations often store essential structured data within unstructured files (e.g., DOCX and PDF). However, manual extraction is time-consuming and error-prone. This project provides an automated, scalable, and modular solution to extract data from file documents and convert it into structured JSON. By handling complex table structures, multiple processing rules (such as form control replacement, text removals, find and replace, anonymization, and date adjustments) and robust logging with error recovery, this solution supports compliance and rapid data accessibility in FedRAMP environments.

## Key Features

- **Modular Architecture:** Each major functionality (file preprocessing, conversion, markdown parsing, table processing, and data enrichment) is implemented as a distinct module.
- **Multiple Interfaces:** 
  - **Streamlit Web Interface:** A user-friendly browser-based interface.
  - **Command Line Interface (CLI):** For batch processing and integration with existing workflows.
- **Robust Data Processing:** 
  - Extraction and enrichment of content for DOCX and PDF files.
  - Advanced Markdown conversion using Docling.
  - Detailed parsing to match a comprehensive JSON schema (document title, paragraphs, lists, sections, tables, and nested subsections).
- **Table Handling:** Resolve cell spanning issues, merge multi-page tables, and transform tables into key-value representation.
- **Extensive Logging & Error Handling:** A dedicated logging module provides event, error, and exception logs including stack traces.
- **Configurable Pre-Processing:** Via YAML parameter files allowing custom rules for replacing form controls, removing text between markers, find/replace operations, anonymization of personal data, and date adjustments.

## System Architecture & Folder Structure

The application uses a clear separation of concerns. A typical folder structure is as follows:

```
app/
│
├── main.py                       # Entry point for FedRAMP OllaLab Streamlit apps
├── app_data/
│   ├── anydoc_2_json/            # Folder storing enriched JSON results
│   └── ...
├── pages/
│   ├── Anydoc_2_Json.py          # Main page for the AnyDoc to JSON conversion app
│   └── ...
└── anydoc_2_json/
    ├── parameters/               # YAML parameter files
    ├── requirements.txt          # Required Python packages
    ├── README.md                 # (This file)
    ├── logs/                     # Log files for errors, events, and audits
    ├── tests/                    # Unit and integration tests
    ├── modules/                  # Core logic for document preprocessing, conversion, parsing, table processing, and data enrichment
    └── ...
```

## Installation

1. **Clone the repository:**

   Run the following command to clone the repository:
   > git clone https://your.repo.url/FedRAMP-OllaLab-Anydoc2json.git

2. **Create and activate a virtual environment (recommended):**

   > python -m venv venv  
   > (Windows) venv\Scripts\activate  
   > (Unix/macOS) source venv/bin/activate  

3. **Install required packages:**

   Install dependencies using the provided `requirements.txt`:
   > pip install -r app/anydoc_2_json/requirements.txt

4. **Additional Dependencies:**

   Ensure that extra libraries (such as `python-docx`, `PyPDF2`, `datefinder`, and Docling’s document converter) are installed as required by the modules.

## Configuration

Parameters are maintained in YAML files stored under the `parameters/` folder. Key parameters include:

- **target:** (Mandatory) The path of the DOCX or PDF file.
- **replaceFormControls:** Use `yes` (default) or `no` to control form controls replacement.
- **removeTexts:** A list of rules with `start` and `end` markers to remove unwanted text.
- **replaceText:** A list of find/replace rules.
- **anonymization:** Dictionary rules for replacing emails, person names, and organizations (methods: redact, jibberish, realistic).
- **adjustDates:** Dictionary specifying how dates should be modified (e.g., add, subtract, daysBefore, daysAfter).

Parameter validation ensures that mandatory entries (like the `target` file) are present. In CLI mode, if no parameter file is provided, the system will either require a default template or exit gracefully with instructions.

## Usage

### Streamlit Web Interface

Launch the web interface by running the main Streamlit app from the `app/` directory (ensure you have Streamlit installed):

> streamlit run main.py

The interface allows users to upload documents, select or create parameter files, and follow guided steps through file pre-processing, conversion, Markdown processing, and final JSON enrichment.

### Command-Line Interface (CLI)

The solution is also accessible from the terminal. For example:

> python anydoc_2_json/your_cli_module.py --target "/path/to/document.pdf" --param "/path/to/parameter.yaml"

Additionally, the data enrichment process can be invoked via the provided `data_enricher.py` script:

> python anydoc_2_json/modules/data_enricher.py --md_file "/path/to/converted.md" --output_folder "/path/to/output" --log_file "/path/to/data_enricher.log"

CLI arguments are validated at startup, with clear error messages for missing or invalid parameters.

## Module Overview

- **logger_manager.py:**  
  Provides a configurable logging solution (file and console handlers) to record application events, errors, and stack traces.

- **param_manager.py:**  
  Manages loading, updating, validating, and saving YAML parameter files. Ensures that required parameters are provided and confirms structure for optional rules.

- **doc_preprocessor.py:**  
  Executes a series of pre-processing steps on DOCX/PDF files. These steps include replacing form controls, removing specified text blocks, performing find/replace operations, anonymizing content, and adjusting date values.

- **doc_converter.py:**  
  Converts DOCX/PDF files to Markdown using the Docling library, adjusts heading levels to ensure a single document title (H1), and saves the adjusted Markdown file.

- **md_parser.py:**  
  Parses the Markdown content into a JSON structure following a well-defined schema. It handles parsing of document title, content splits, various headings, paragraphs, lists, and tables.

- **table_processor.py:**  
  Processes Markdown table content to solve spanning cell issues, merge multi-page tables, and transform table data into key-value pairs.

- **data_enricher.py:**  
  Coordinates the enrichment of JSON data by invoking the Markdown parser and table processor. It saves both the raw JSON and the enriched JSON with updated table information.

## Testing and Stress Workloads

- **Automated Testing:**  
  Unit and integration tests are provided in the `tests/` directory. These tests include parameter validation, conversion benchmarks, and concurrency simulation for large file uploads.

- **Performance Monitoring:**  
  The system logs performance metrics and processing delays. It also supports simulations for concurrent user uploads via automated tools such as Locust or JMeter.

## Logging and Alerts

The logging mechanism captures all significant events (file uploads, parameter changes, errors, retries) and logs them to the `logs/` folder. In the event of failures (e.g., corrupted files or partial conversion), detailed error messages including error type, timestamp, and stack trace are saved. Critical issues are also printed as user-friendly messages in the Streamlit interface and CLI output.

## Contributing

Contributions and improvements are welcome. Please:
- Follow coding standards and document your changes.
- Ensure unit tests pass before committing.
- Use Git for version control and consider implementing code reviews.

## License

Same as OllaLab license.