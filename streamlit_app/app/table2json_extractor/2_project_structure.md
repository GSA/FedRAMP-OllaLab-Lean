# FedRAMP OllaLab - Table to Json Extractor
The following sub-sections describe the project's structure.

## Detailed Doc-Strings for Functions/Classes

---

### **Module: document_parser.py**

---

#### **Function: `parse_document(filepath)`**

```python
def parse_document(filepath):
    """
    Parses a document (MS Word or PDF) and extracts raw tables.

    Parameters:
        filepath (str): 
            - The file path to the document to parse.

    Returns:
        tables (list of Table): 
            - A list of raw Table objects extracted from the document.

    Raises:
        FileNotFoundError: 
            - If the specified file does not exist.
        UnsupportedFileTypeError: 
            - If the file type is neither .docx nor .pdf.
        DocumentParseError: 
            - If there is an error parsing the document.

    Upstream functions:
        - Called by the main application flow when a document needs to be parsed.
        - Called by the Streamlit app upon user document upload.

    Downstream functions:
        - `_parse_ms_word(filepath)`: Parses MS Word documents.
        - `_parse_pdf(filepath)`: Parses PDF documents.

    Dependencies:
        - Requires 'python-docx' library for MS Word parsing.
        - Requires 'pdfplumber' library for PDF parsing.
        - File system access to read the document.
    """
    pass
```

#### **Function: `_parse_ms_word(filepath)`**

```python
def _parse_ms_word(filepath):
    """
    Parses an MS Word document and extracts raw tables.

    Parameters:
        filepath (str): 
            - The file path to the MS Word document to parse.

    Returns:
        tables (list of Table): 
            - A list of raw Table objects extracted from the MS Word document.

    Raises:
        DocumentParseError: 
            - If there is an error parsing the MS Word document.

    Upstream functions:
        - `parse_document(filepath)`

    Downstream functions:
        - None.

    Dependencies:
        - Requires 'python-docx' library.
        - Properly formatted MS Word (.docx) document.
    """
    pass
```

#### **Function: `_parse_pdf(filepath)`**

```python
def _parse_pdf(filepath):
    """
    Parses a PDF document and extracts raw tables.

    Parameters:
        filepath (str): 
            - The file path to the PDF document to parse.

    Returns:
        tables (list of Table): 
            - A list of raw Table objects extracted from the PDF document.

    Raises:
        DocumentParseError: 
            - If there is an error parsing the PDF document.

    Upstream functions:
        - `parse_document(filepath)`

    Downstream functions:
        - None.

    Dependencies:
        - Requires 'pdfplumber' library.
        - The PDF must be accessible and not corrupted.
    """
    pass
```

---

### **Module: table_selector.py**

---

#### **Function: `list_tables(tables)`**

```python
def list_tables(tables):
    """
    Generates a list of tables with indices and summaries for selection.

    Parameters:
        tables (list of Table): 
            - The list of Table objects extracted from the document.

    Returns:
        table_summaries (list of dict): 
            - A list containing summaries of each table, including index and preview.

    Raises:
        ValueError: 
            - If the input tables list is empty.

    Upstream functions:
        - Called after parsing the document to prepare for table selection.

    Downstream functions:
        - Used by the user interface to display table options.

    Dependencies:
        - None.
    """
    pass
```

#### **Function: `select_tables(tables, selection_criteria)`**

```python
def select_tables(tables, selection_criteria):
    """
    Selects tables based on provided selection criteria.

    Parameters:
        tables (list of Table): 
            - The list of Table objects extracted from the document.
        selection_criteria (dict): 
            - Criteria provided by the user for selecting tables.
            - Can include 'indices', 'keywords', 'row_conditions', 'column_conditions'.

    Returns:
        selected_tables (list of Table): 
            - The list of tables that meet the selection criteria.

    Raises:
        SelectionError: 
            - If no tables match the selection criteria.
        InvalidCriteriaError: 
            - If the selection criteria are improperly formatted.

    Upstream functions:
        - Called by the user interface after user specifies selection criteria.

    Downstream functions:
        - Feeds into the table extraction process.

    Dependencies:
        - Relies on accurate parsing of tables.
        - Requires that the selection criteria are validated prior to use.
    """
    pass
```

---

### **Module: table_extractor.py**

---

#### **Function: `extract_table(raw_table, extraction_parameters)`**

```python
def extract_table(raw_table, extraction_parameters):
    """
    Extracts and formats a single table based on extraction parameters.

    Parameters:
        raw_table (Table): 
            - The raw Table object to be processed.
        extraction_parameters (dict): 
            - Parameters defining how the extraction should be performed.
            - May include 'header_rows', 'data_types', 'formatting_rules', 'error_handling'.

    Returns:
        extracted_table (Table): 
            - The processed Table object ready for structure interpretation.

    Raises:
        ExtractionError: 
            - If there is an error during the extraction process.
        InvalidParameterError: 
            - If extraction parameters are invalid.

    Upstream functions:
        - Invoked for each selected table after selection.

    Downstream functions:
        - Passes the extracted table to the structure interpreter.

    Dependencies:
        - Accurate raw_table data from the parser.
        - Correctly specified extraction_parameters.
    """
    pass
```

---

### **Module: structure_interpreter.py**

---

#### **Function: `interpret_structure(table, structure_guidelines)`**

```python
def interpret_structure(table, structure_guidelines):
    """
    Interprets the structure of a table based on guidelines for complex table features.

    Parameters:
        table (Table): 
            - The Table object to interpret.
        structure_guidelines (dict): 
            - Guidelines specifying how to handle complex structures.
            - Includes handling of merged cells, nested tables, irregularities.

    Returns:
        interpreted_table (Table): 
            - The Table object with structures interpreted and ready for validation.

    Raises:
        StructureInterpretationError: 
            - If the table's structure cannot be interpreted as per guidelines.

    Upstream functions:
        - Receives the extracted table from the extraction process.

    Downstream functions:
        - Passes the interpreted table to the data validator.

    Dependencies:
        - Accurate extraction of the table.
        - Comprehensive structure guidelines.
    """
    pass
```

#### **Function: `handle_merged_cells(table)`**

```python
def handle_merged_cells(table):
    """
    Handles merged cells within a table by appropriately redistributing or representation.

    Parameters:
        table (Table): 
            - The Table object that may contain merged cells.

    Returns:
        table (Table): 
            - The Table object with merged cells handled.

    Raises:
        MergedCellHandlingError: 
            - If merged cells cannot be handled according to specified rules.

    Upstream functions:
        - Called within `interpret_structure` if merged cells are detected.

    Downstream functions:
        - May be followed by handling nested tables or irregular structures.

    Dependencies:
        - Accurate detection of merged cells.
    """
    pass
```

#### **Function: `handle_nested_tables(table)`**

```python
def handle_nested_tables(table):
    """
    Processes nested tables within the main table, representing them appropriately.

    Parameters:
        table (Table): 
            - The Table object that may contain nested tables.

    Returns:
        table (Table): 
            - The Table object with nested tables processed.

    Raises:
        NestedTableHandlingError: 
            - If nested tables cannot be processed correctly.

    Upstream functions:
        - Invoked within `interpret_structure` when nested tables are present.

    Downstream functions:
        - Continues to further structure interpretation steps.

    Dependencies:
        - Ability to detect nested tables.
        - Rules for representing nested structures.
    """
    pass
```

#### **Function: `handle_irregular_structures(table)`**

```python
def handle_irregular_structures(table):
    """
    Manages irregular table structures by normalizing or documenting inconsistencies.

    Parameters:
        table (Table): 
            - The Table object with potential irregularities.

    Returns:
        table (Table): 
            - The normalized Table object.

    Raises:
        IrregularStructureError: 
            - If the table cannot be normalized.

    Upstream functions:
        - Called within `interpret_structure` when irregularities are found.

    Downstream functions:
        - May proceed to data validation after handling irregularities.

    Dependencies:
        - Methods for detecting and correcting irregular structures.
    """
    pass
```

---

### **Module: data_validator.py**

---

#### **Function: `validate_table(table, validation_rules)`**

```python
def validate_table(table, validation_rules):
    """
    Validates the data within a table according to specified validation rules.

    Parameters:
        table (Table): 
            - The Table object to validate.
        validation_rules (dict): 
            - Rules specifying how to validate data, e.g., data types, constraints.

    Returns:
        is_valid (bool): 
            - True if the table data passes all validation rules.
        errors (list of str): 
            - List of validation errors encountered.

    Raises:
        ValidationError: 
            - If validation process fails unexpectedly.

    Upstream functions:
        - Receives the table from the structure interpreter.

    Downstream functions:
        - If valid, passes the table to the converter.

    Dependencies:
        - Accurate and comprehensive validation rules.
    """
    pass
```

---

### **Module: converter.py**

---

#### **Function: `convert_table_to_json(table)`**

```python
def convert_table_to_json(table):
    """
    Converts a Table object to a structured JSON format.

    Parameters:
        table (Table): 
            - The validated Table object to convert.

    Returns:
        json_output (str): 
            - A JSON-formatted string representing the table.

    Raises:
        ConversionError: 
            - If the table cannot be converted to JSON.

    Upstream functions:
        - Called after data validation confirms table is valid.

    Downstream functions:
        - The output is used for storage or further processing.

    Dependencies:
        - Properly formatted and validated Table object.
        - 'json' standard library module.
    """
    pass
```

#### **Function: `convert_table_to_markdown(table, markdown_style='default')`**

```python
def convert_table_to_markdown(table, markdown_style='default'):
    """
    Converts a Table object to a Markdown formatted string.

    Parameters:
        table (Table): 
            - The validated Table object to convert.
        markdown_style (str, optional): 
            - The style or flavor of Markdown to use (e.g., 'GitHub', 'MultiMarkdown').
            - Default is 'default'.

    Returns:
        markdown_output (str): 
            - A Markdown-formatted string representing the table.

    Raises:
        ConversionError: 
            - If the table cannot be converted to Markdown.

    Upstream functions:
        - Called after data validation confirms table is valid.

    Downstream functions:
        - The output is used for display or documentation purposes.

    Dependencies:
        - Correctly formatted and validated Table object.
        - Any necessary Markdown libraries if custom styles are used.
    """
    pass
```

---

### **Module: logging_setup.py**

---

#### **Function: `setup_logging()`**

```python
def setup_logging():
    """
    Sets up logging configuration for the application.

    Parameters:
        None.

    Returns:
        logger (logging.Logger): 
            - Configured logger for the application.

    Raises:
        LoggingConfigurationError: 
            - If there is an error configuring the logger.

    Upstream functions:
        - Called at the start of the application to initialize logging.

    Downstream functions:
        - Provides logging capabilities to all other modules.

    Dependencies:
        - Python 'logging' standard library.
        - Access to logging configuration settings.
    """
    pass
```

---

## Proposed Folder Structure and Files

```
streamlit_app/
└── app/
    ├── main.py
    ├── pages/
    │   └── Table2Json_Extractor.py
    ├── table2json_extractor/
    │   ├── __init__.py
    │   ├── document_parser.py
    │   ├── table_selector.py
    │   ├── table_extractor.py
    │   ├── structure_interpreter.py
    │   ├── data_validator.py
    │   ├── converter.py
    │   ├── logging_setup.py
    │   ├── utils.py
    │   └── tests/
    │       ├── __init__.py
    │       ├── test_document_parser.py
    │       ├── test_table_selector.py
    │       ├── test_table_extractor.py
    │       ├── test_structure_interpreter.py
    │       ├── test_data_validator.py
    │       └── test_converter.py
```

- **main.py**: The main entry point of the parent Streamlit application that provides navigation to apps like the FedRAMP OllaLab - Table to Json Extractor.
- **pages/Table2Json_Extractor.py**: The Streamlit page for this app, handling user interactions and displaying results.
- **table2json_extractor/**: Package containing modules for the Table to JSON Extractor app.
  - **__init__.py**: Initializes the package.
  - **document_parser.py**: Module for parsing MS Word and PDF documents to extract raw tables.
  - **table_selector.py**: Module that provides functionalities for listing and selecting tables based on user criteria.
  - **table_extractor.py**: Module that handles the extraction of tables with user-defined parameters.
  - **structure_interpreter.py**: Module that interprets complex table structures (merged cells, nested tables, irregular structures).
  - **data_validator.py**: Module that validates the extracted data according to specified rules.
  - **converter.py**: Module that converts tables into JSON and Markdown formats.
  - **logging_setup.py**: Module that sets up logging for the application.
  - **utils.py**: Utility functions and helper methods.
  - **tests/**: Contains all test files for the app.
    - **__init__.py**: Initializes the test package.
    - **test_document_parser.py**: Unit tests for document_parser.py.
    - **test_table_selector.py**: Unit tests for table_selector.py.
    - **test_table_extractor.py**: Unit tests for table_extractor.py.
    - **test_structure_interpreter.py**: Unit tests for structure_interpreter.py.
    - **test_data_validator.py**: Unit tests for data_validator.py.
    - **test_converter.py**: Unit tests for converter.py.

## Proposed Content of Each Files**

---

### **File: streamlit_app/app/main.py**

```python
# main.py

import streamlit as st

def main():
    """
    Main function to run the parent Streamlit application.
    Provides navigation to different apps including the Table to JSON Extractor.
    """
    st.title("OllaLab Application Suite")
    st.sidebar.title("Navigation")
    # Navigation options to different apps
    app_selection = st.sidebar.selectbox("Select an App", ["Table to JSON Extractor"])

    if app_selection == "Table to JSON Extractor":
        # Navigate to the Table2Json_Extractor page
        from pages import Table2Json_Extractor
        Table2Json_Extractor.run()

if __name__ == "__main__":
    main()
```

---

### **File: streamlit_app/app/pages/Table2Json_Extractor.py**

```python
# Table2Json_Extractor.py

import streamlit as st
from table2json_extractor import document_parser, table_selector, table_extractor
from table2json_extractor import structure_interpreter, data_validator, converter, logging_setup

def run():
    """
    Streamlit page function for the Table to JSON Extractor app.
    Handles user interactions and displays results.
    """
    st.title("FedRAMP OllaLab - Table to JSON Extractor")

    # Setup logging
    logger = logging_setup.setup_logging()

    # File upload
    uploaded_file = st.file_uploader("Upload a document (MS Word or PDF)", type=["docx", "pdf"])
    if uploaded_file is not None:
        # Save uploaded file to a temporary location
        with open("temp_uploaded_file", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Parse document
        try:
            tables = document_parser.parse_document("temp_uploaded_file")
            st.success(f"Found {len(tables)} tables in the document.")
        except Exception as e:
            st.error(f"Error parsing document: {e}")
            return

        # List tables and allow selection
        table_summaries = table_selector.list_tables(tables)
        # Display table summaries and get user selection
        # ...

        # Get user input for extraction parameters
        # extraction_parameters = ...

        # Extract and process selected tables
        # for table in selected_tables:
            # extracted_table = table_extractor.extract_table(table, extraction_parameters)
            # interpreted_table = structure_interpreter.interpret_structure(extracted_table, structure_guidelines)
            # is_valid, errors = data_validator.validate_table(interpreted_table, validation_rules)
            # if is_valid:
                # json_output = converter.convert_table_to_json(interpreted_table)
                # Display or download json_output
            # else:
                # Display validation errors

        # Clean up temporary files
        # ...

if __name__ == "__main__":
    run()
```

---

### **File: streamlit_app/app/table2json_extractor/__init__.py**

```python
# __init__.py

"""
Package initialization for table2json_extractor.
"""

__all__ = [
    "document_parser",
    "table_selector",
    "table_extractor",
    "structure_interpreter",
    "data_validator",
    "converter",
    "logging_setup",
    "utils"
]
```

---

### **File: streamlit_app/app/table2json_extractor/document_parser.py**

```python
# document_parser.py

"""
Module for parsing MS Word and PDF documents to extract raw tables.
"""

def parse_document(filepath):
    # Doc-string as previously defined
    pass

def _parse_ms_word(filepath):
    # Doc-string as previously defined
    pass

def _parse_pdf(filepath):
    # Doc-string as previously defined
    pass

# Additional helper functions if needed
```

---

### **File: streamlit_app/app/table2json_extractor/table_selector.py**

```python
# table_selector.py

"""
Module providing functionalities for listing and selecting tables.
"""

def list_tables(tables):
    # Doc-string as previously defined
    pass

def select_tables(tables, selection_criteria):
    # Doc-string as previously defined
    pass

# Additional helper functions
```

---

### **File: streamlit_app/app/table2json_extractor/table_extractor.py**

```python
# table_extractor.py

"""
Module handling the extraction of tables with user-defined parameters.
"""

def extract_table(raw_table, extraction_parameters):
    # Doc-string as previously defined
    pass

# Additional helper functions
```

---

### **File: streamlit_app/app/table2json_extractor/structure_interpreter.py**

```python
# structure_interpreter.py

"""
Module that interprets complex table structures.
"""

def interpret_structure(table, structure_guidelines):
    # Doc-string as previously defined
    pass

def handle_merged_cells(table):
    # Doc-string as previously defined
    pass

def handle_nested_tables(table):
    # Doc-string as previously defined
    pass

def handle_irregular_structures(table):
    # Doc-string as previously defined
    pass

# Additional helper functions
```

---

### **File: streamlit_app/app/table2json_extractor/data_validator.py**

```python
# data_validator.py

"""
Module that validates the extracted data according to specified rules.
"""

def validate_table(table, validation_rules):
    # Doc-string as previously defined
    pass

# Additional helper functions
```

---

### **File: streamlit_app/app/table2json_extractor/converter.py**

```python
# converter.py

"""
Module that converts tables into JSON and Markdown formats.
"""

def convert_table_to_json(table):
    # Doc-string as previously defined
    pass

def convert_table_to_markdown(table, markdown_style='default'):
    # Doc-string as previously defined
    pass

# Additional helper functions
```

---

### **File: streamlit_app/app/table2json_extractor/logging_setup.py**

```python
# logging_setup.py

"""
Module that sets up logging for the application.
"""

import logging

def setup_logging():
    # Doc-string as previously defined
    pass

# Additional helper functions
```

---

### **File: streamlit_app/app/table2json_extractor/utils.py**

```python
# utils.py

"""
Utility functions and helpers for the application.
"""

def check_file_type(filepath):
    """
    Checks the file type of the given filepath.

    Parameters:
        filepath (str): 
            - The file path to check.

    Returns:
        file_type (str): 
            - The type of the file ('docx', 'pdf', etc.)

    Raises:
        UnsupportedFileTypeError: 
            - If the file type is unsupported.
    """
    pass

# Additional utility functions
```

---

### **Files in streamlit_app/app/table2json_extractor/tests/**

Each test file (e.g., `test_document_parser.py`) will contain unit tests for its corresponding module.

Example content for `test_document_parser.py`:

```python
# test_document_parser.py

import unittest
from table2json_extractor import document_parser

class TestDocumentParser(unittest.TestCase):
    def test_parse_document_with_docx(self):
        # Test parsing a valid .docx file
        pass

    def test_parse_document_with_pdf(self):
        # Test parsing a valid .pdf file
        pass

    def test_parse_document_with_invalid_file(self):
        # Test handling of invalid file types
        pass

    # Additional test methods

if __name__ == '__main__':
    unittest.main()
```

---
