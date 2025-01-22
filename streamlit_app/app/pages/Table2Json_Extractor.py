# streamlit_app/app/pages/Table2Json_Extractor.py

"""
Table2Json_Extractor.py

Streamlit page handling user interactions and displaying results for the Table to JSON Extractor app.

This module provides the user interface for uploading documents, specifying extraction parameters,
processing the documents, and displaying the extracted tables in JSON format.

It relies on other modules for processing, including:
- data_processing.py
- extraction_parameters.py
- structure_interpretation.py
- user_interface.py
- validation.py
- logging_handlers.py
"""

import streamlit as st
import logging

# Import necessary modules and functions
from data_processing import parse_documents
from extraction_parameters import (
    ExtractionParameters,
    TableSelectionCriteria,
    FormattingRules,
    ErrorHandlingStrategy,
    ParserConfiguration,
    ResourceLimits,
)
from structure_interpretation import interpret_table_structure
from user_interface import process_user_input, process_documents, render_results
from validation import validate_user_inputs, validate_extracted_data
from locale_manager import load_locale
from exceptions import (
    InvalidUserInputError,
    DataValidationError,
    ProcessingError,
    RenderingError,
    InvalidParameterError,
)

# Initialize logging
logger = logging.getLogger(__name__)

# Set up logging configurations (assuming setup_logging from logging_config.py has been called in main.py)

# Load locale (for internationalization)
locale = load_locale('en')  # For simplicity, using English locale

def main():
    st.set_page_config(page_title="Table to JSON Extractor", layout="wide")

    st.title("Table to JSON Extractor")
    st.write("Upload your MS Word or PDF documents containing tables, specify your extraction parameters, and extract the tables in JSON format.")

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose MS Word or PDF files",
        type=['pdf', 'docx', 'doc'],
        accept_multiple_files=True
    )

    # Display uploaded files
    if uploaded_files:
        st.write("Uploaded files:")
        for file in uploaded_files:
            st.write(f"- {file.name}")

    # Extraction parameters
    st.header("Extraction Parameters")

    # Table Selection Criteria
    st.subheader("Table Selection Criteria")

    selection_method = st.selectbox(
        "Select Table Selection Method",
        ['Indexing', 'Keyword', 'Regex', 'Criteria']
    )

    indices = None
    keywords = None
    regex_patterns = None
    row_conditions = None
    column_conditions = None

    if selection_method == 'Indexing':
        indices_input = st.text_input("Enter Table Indices (comma-separated)", value="1")
        try:
            indices = [int(i.strip()) - 1 for i in indices_input.split(',')]  # Adjusted to zero-based index
        except ValueError:
            st.error("Indices must be integers separated by commas.")
            st.stop()
    elif selection_method == 'Keyword':
        keywords_input = st.text_input("Enter Keywords (comma-separated)")
        keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
    elif selection_method == 'Regex':
        regex_input = st.text_input("Enter Regular Expressions (comma-separated)")
        regex_patterns = [r.strip() for r in regex_input.split(',') if r.strip()]
    elif selection_method == 'Criteria':
        st.info("Criteria-based selection is not implemented in this interface yet.")
        st.stop()

    # Formatting Rules
    st.subheader("Formatting Rules")

    preserve_styles = st.checkbox("Preserve Text Styles (e.g., bold, italic)")
    date_format = st.text_input("Date Format", value="%Y-%m-%d")
    number_format = st.text_input("Number Format (e.g., {:.2f} for two decimal places)", value="")
    encoding = st.text_input("Text Encoding", value="utf-8")
    placeholder_for_missing = st.text_input("Placeholder for Missing Data", value="")

    # Error Handling Strategy
    st.subheader("Error Handling Strategy")

    on_parsing_error = st.selectbox(
        "On Parsing Error",
        ['Skip', 'Abort', 'Log'],
        index=2  # Default to 'Log'
    )
    on_validation_error = st.selectbox(
        "On Validation Error",
        ['Correct', 'Omit', 'Prompt', 'Abort'],
        index=1  # Default to 'Omit'
    )

    # Parser Configuration
    st.subheader("Parser Configuration")

    ocr_enabled = st.checkbox("Enable OCR for Scanned PDFs")
    language = st.text_input("Document Language", value="en")

    # Resource Limits
    st.subheader("Resource Limits")

    max_memory = st.number_input("Max Memory (MB)", min_value=0, value=0)
    max_time = st.number_input("Max Time (seconds)", min_value=0, value=0)
    max_cpu_usage = st.number_input("Max CPU Usage (%)", min_value=0, max_value=100, value=0)

    # Process Button
    if st.button("Process Documents"):
        if not uploaded_files:
            st.error("Please upload at least one document.")
            st.stop()

        # Collect user inputs
        user_inputs = {
            'table_selection': {
                'method': selection_method.lower(),
                'indices': indices,
                'keywords': keywords,
                'regex_patterns': regex_patterns,
                'row_conditions': row_conditions,
                'column_conditions': column_conditions
            },
            'formatting_rules': {
                'preserve_styles': preserve_styles,
                'date_format': date_format,
                'number_format': number_format if number_format else None,
                'encoding': encoding,
                'placeholder_for_missing': placeholder_for_missing if placeholder_for_missing else None
            },
            'error_handling': {
                'on_parsing_error': on_parsing_error.lower(),
                'on_validation_error': on_validation_error.lower(),
                'fallback_mechanisms': []  # Placeholder
            },
            'parser_config': {
                'ocr_enabled': ocr_enabled,
                'language': language,
                'resource_limits': {
                    'max_memory': int(max_memory) if max_memory > 0 else None,
                    'max_time': int(max_time) if max_time > 0 else None,
                    'max_cpu_usage': int(max_cpu_usage) if max_cpu_usage > 0 else None
                }
            },
            'data_types': {}  # Could be expanded to accept user inputs
        }

        # Process user inputs
        try:
            extraction_parameters = process_user_input(user_inputs)
        except InvalidUserInputError as e:
            st.error(f"Invalid user input: {e}")
            logger.error(f"Invalid user input: {e}")
            st.stop()

        # Convert uploaded_files into file paths
        import tempfile
        import shutil

        file_paths = []
        temp_dirs = []

        try:
            for uploaded_file in uploaded_files:
                # Save uploaded file to a temporary directory
                temp_dir = tempfile.mkdtemp()
                temp_dirs.append(temp_dir)
                file_name = uploaded_file.name
                temp_file_path = os.path.join(temp_dir, file_name)

                with open(temp_file_path, 'wb') as f:
                    f.write(uploaded_file.read())

                file_paths.append(temp_file_path)
                logger.debug(f"Saved uploaded file '{uploaded_file.name}' to temporary file '{temp_file_path}'.")

            # Process the documents
            try:
                extracted_data = process_documents(file_paths, extraction_parameters)
            except ProcessingError as e:
                st.error(f"Error processing documents: {e}")
                logger.error(f"Error processing documents: {e}")
                st.stop()

            # Render results
            try:
                output_format = 'json'  # Currently supporting JSON output
                rendered_data = render_results(extracted_data, output_format)
                st.success("Documents processed successfully!")
                st.subheader("Extracted Tables in JSON Format")
                st.code(rendered_data, language='json')

                # Provide a download button
                st.download_button(
                    label="Download JSON",
                    data=rendered_data,
                    file_name='extracted_tables.json',
                    mime='application/json'
                )

            except RenderingError as e:
                st.error(f"Error rendering results: {e}")
                logger.error(f"Error rendering results: {e}")
                st.stop()

        finally:
            # Clean up temporary files and directories
            for temp_dir in temp_dirs:
                try:
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Deleted temporary directory '{temp_dir}'.")
                except OSError as e:
                    logger.warning(f"Error deleting temporary directory '{temp_dir}': {e}")

if __name__ == '__main__':
    main()