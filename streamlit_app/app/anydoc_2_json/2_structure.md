# FedRAMP OllaLab - AnyDoc to JSON

Below is a suggested modular breakdown of the application that balances clarity with maintainability. Each module targets specific requirements from the “Program Requirements” and “Program Steps.” The structure avoids over-segmentation while still separating major concerns.

## 1. HIGH-LEVEL FOLDER STRUCTURE
```
app/
│
├── main.py                       # The main entry point for the Streamlit web interface
├── pages/
│   ├── Anydoc_2_Json.py          # The Streamlit page for AnyDoc-to-JSON functionality
│   └── ...                       # Other pages
├── app_data/
│   ├── anydoc_2_json/            # Storing uploaded files and result folders
│   └── ...
└── anydoc_2_json/
    ├── modules/
    │   ├── param_manager.py
    │   ├── doc_preprocessor.py
    │   ├── doc_converter.py
    │   ├── md_parser.py
    │   ├── table_processor.py
    │   ├── data_enricher.py
    │   ├── logger_manager.py
    │   └── __init__.py
    ├── parameters/
    │   └── default.yaml          # Default parameter file
    ├── logs/
    │   ├── error.log             # Error log file
    │   ├── events.log            # Main events log file
    │   └── ...
    ├── tests/
    │   ├── test_param_manager.py
    │   ├── test_doc_preprocessor.py
    │   ├── test_doc_converter.py
    │   ├── test_md_parser.py
    │   ├── test_table_processor.py
    │   ├── test_data_enricher.py
    │   └── ...
    ├── requirements.txt          # Required packages and dependencies
    ├── README.md                 # Documentation for setup and usage
    └── anydoc2json_cli.py        # CLI entry point
```

## 2. MODULES INSIDE “anydoc_2_json/modules/”

Below are key modules, each with its own Python file. This helps map program steps to maintainable components.

### (1) param_manager.py
- Purpose:  
  - Handle reading, validation, and defaulting of parameter files (.yaml).  
  - Manage optional parameters, default values, and parameter error handling.  
- Key Responsibilities:  
  - Load YAML from either CLI-specified file or default.yaml.  
  - Validate mandatory and optional parameters (e.g., “–target” is required).  
  - Provide application-wide access to parameters.  
  - Return user-friendly or CLI-friendly error messages if parameters are invalid.  
- Related Requirements:  
  - “Program Steps” → Step 1, especially setting parameter file & defaults.  
  - “5. Logging, Monitoring, Alerting” (logs parameter load successes/failures).  
  - “8. Data Quality and Validation” (validates parameter correctness).

### (2) doc_preprocessor.py
- Purpose:  
  - Execute all pre-conversion text transformations: form-control replacement, removing text between markers, find/replace text, anonymization, and date shifting.  
- Key Responsibilities:  
  - “replaceFormControls”: Replace interactive form controls (checkboxes, radio buttons) with the appropriate text tokens ({{checked box}}, etc.).  
  - “removeTexts”: Remove text between specified start/end markers (including “end of line” when specified).  
  - “replaceText”: Find and replace strings with user-defined mapping rules.  
  - “anonymization”: Detect emails, names, organizations; anonymize with chosen method (redact, jibberish, realistic).  
  - “adjustDates”: Shift all date occurrences by specified rules (add/subtract days or set them relative to “now”).  
  - Maintain interim or partial results in memory or disk.  
- Related Requirements:  
  - “Program Steps” → Step 2 (Pre-conversion processing).  
  - “Data Processing and Management” (structured data extraction starts here).  
  - “Logging and Error Handling”: Log partial or failing transformations.

### (3) doc_converter.py
- Purpose:  
  - Convert docx/PDF files into Markdown using Docling. Handle doc → docx conversion if needed and place results into the designated result folder.  
- Key Responsibilities:  
  - Convert PDF to docx (if needed).  
  - Convert doc (not docx) to docx.  
  - Leverage Docling to transform docx into Markdown.  
  - Insert a top-level “# (Document Title)” heading if missing or if multiple H1 headings are encountered.  
  - Output the final .md file to the result folder.  
- Related Requirements:  
  - “Program Steps” → Step 3 (Convert document to MarkDown using Docling).  
  - “Large File Processing” and resilience (test docling with large inputs).  
  - Ensures correct logging for conversion successes/failures.

### (4) md_parser.py
- Purpose:  
  - Parse raw Markdown content into a JSON structure according to the “Markdown to JSON” schema provided.  
- Key Responsibilities:  
  - Read the .md file line by line, detect headings (#, ##, ###, ####).  
  - Extract paragraphs, lists, and tables into the appropriate fields (content_text1, sections, sub-sections, etc.).  
  - Build an in-memory JSON object matching the schema’s structure.  
  - Handle “content_text2” for content after the last “##” heading.  
- Related Requirements:  
  - “Program Steps” → Step 4.  
  - “Data Processing and Management” (Structured Data Extraction).  
  - “Markdown to JSON Schema” compliance.

### (5) table_processor.py
- Purpose:  
  - Correctly handle spanning cells and multi-page table merges within Markdown tables prior to final JSON encoding.  
- Key Responsibilities:  
  - Detect and fix repeated content from Docling’s cell spanning approach.  
  - For two-row table headers, merge row1 and row2 headers if the second row is truly part of the header.  
  - Merge multi-page tables if they have identical headers.  
  - Return cleaned-up table representations ready for the final JSON.  
- Related Requirements:  
  - “Program Steps” → Step 5 (Process MarkDown tables).  
  - “5. Logging…” (record table merge anomalies).  
  - Provides output that “data_enricher.py” can further interpret.

### (6) data_enricher.py
- Purpose:  
  - Translate cleaned Markdown tables into finer key-value structures per the enrichment rules.  
  - Integrate the final enriched data into the JSON.  
- Key Responsibilities:  
  - Apply the custom logic for single-column or multi-column table transformations.  
  - Create sub-keys or “item” arrays from table rows.  
  - Insert enriched table data back into the main JSON structure (replacing the raw table text).  
  - Save the final “_raw” and “_enriched” JSON files to disk.  
- Related Requirements:  
  - “Program Steps” → Step 6 (Enrich the JSON data).  
  - “Data Quality and Validation” (ensure the transformations preserve or clarify meaning).  

### (7) logger_manager.py
- Purpose:  
  - Provide centralized logging, monitoring, and error-handling hooks.  
- Key Responsibilities:  
  - Maintain logs (error.log, events.log).  
  - Implement try/catch wrappers that record file name, stack trace, and timestamp.  
  - Provide standard ways to raise alerts for performance thresholds or critical errors.  
- Related Requirements:  
  - “5. Logging, Monitoring, and Alerting.”  
  - “6. Development and Deployment Practices” (record performance metrics, concurrency issues).

## 3. OTHER IMPORTANT FILES
### (1) anydoc2json_cli.py
- Purpose:  
  - Command-line interface entry point for the AnyDoc-to-JSON functionality.  
  - Exposes parameters “–target / -t”, “–param / -p”, etc.  
  - Invokes modules (param_manager, doc_preprocessor, doc_converter, etc.) in the correct sequence.  
  - Logs outputs and errors to console and logs/ folder.  
### (2) README.md
- Purpose:  
  - Provides high-level overview of how to install and use the application (both CLI and GUI).  
  - Documents dependencies, environment setups, usage examples.
### (3) requirements.txt
- Purpose:  
  - Tracks necessary Python packages (e.g., pyyaml, docling, PyPDF2, Streamlit, etc.).  
  - Ensures consistent reproducible environments.
### (4) parameters/default.yaml
- Purpose:  
  - Supplies a reference parameter file containing all valid keys (replaceFormControls, removeTexts, replaceText, anonymization, adjustDates, etc.).  
  - Serves as a fallback if no parameter file is provided in CLI mode.
### (5) tests/ (multiple test files)
- Purpose:  
  - Unit tests and integration tests for each module (test_param_manager.py, test_doc_preprocessor.py, etc.).  
  - Automated QA checks for concurrency, large file handling, partial extraction, and error handling.  

## 4. SUGGESTIONS FOR FURTHER IMPROVEMENT OF THE PROPOSED STRUCTURE
- Create a “file_manager” or “storage_manager” Layer (Optional)  
  - Why: While “doc_converter” and “doc_preprocessor” might handle file I/O, you may find repeated logic around copying, naming, or archiving files. A small utility module (e.g., file_manager.py) could unify these operations—especially for the creation of the “result folder,” copying or moving the original file, and so on.  
   - Benefit: Helps keep reading/writing logic consistent and makes the main modules (doc_converter, doc_preprocessor) focus on their core tasks—conversion and pre-processing rather than file housekeeping.  
- Consider Splitting Out “cli_app” Logic (Optional)  
   - Rationale: You already propose anydoc2json_cli.py as the CLI entry point. This is good; just ensure it remains a thin wrapper. If the CLI logic ever grows (e.g., multi-stage user prompts, advanced command chaining), separating out the heavier CLI logic into a dedicated “cli_app” or “cli_controller” module could improve readability.  
- Potential Single “logging_config.py” for Logging Configuration (Optional)  
   - Why: logger_manager.py as planned is excellent if it truly centralizes logging across the entire application. In some Python applications, the configuration for handling log formatters, streams, rotating file handlers, etc. sits in a separate logging_config.py or logging.yaml. You can keep everything inside logger_manager.py, but if logging becomes more complex (rotating logs, sending logs to multiple endpoints), you might want to break out the configuration from the actual “manager” code.  
- Distinguish “Utilities” vs. “Core Modules” (Optional)  
   - Explanation: If smaller utility/helper functions are common across modules (e.g., string normalization, date parsing, custom exceptions, etc.), consider a “utils/” subfolder. This prevents duplication and keeps each module more streamlined.  
   - This is purely optional and depends on project size.  