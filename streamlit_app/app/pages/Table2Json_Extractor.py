# Table2Json_Extractor.py

import streamlit as st
import logging
import os
import tempfile
import shutil
import json
import re

# Import necessary modules and functions
from table2json_extractor.data_processing import parse_documents
from table2json_extractor.extraction_parameters import (
    ExtractionParameters,
    TableSelectionCriteria,
    FormattingRules,
    ErrorHandlingStrategy,
    ParserConfiguration,
    ResourceLimits,
    StructureInterpretationRules
)
from table2json_extractor.user_interface import (
    process_user_input,
    process_user_input_preview,
    process_documents,
    render_results,
    table_to_dataframe
)
from table2json_extractor.exceptions import (
    InvalidUserInputError,
    DataValidationError,
    ProcessingError,
    RenderingError,
    InvalidParameterError,
)
from typing import Dict, Any, List
import pandas as pd

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def main():
    st.set_page_config(page_title="Table to JSON Extractor", layout="wide")

    st.title("Table to JSON Extractor")
    st.write("Upload your MS Word (.docx) or PDF documents containing tables, specify your extraction parameters, and extract the tables in JSON format.")

    # Initialize session_state variables
    if 'documents' not in st.session_state:
        st.session_state['documents'] = []
    if 'extracted_tables' not in st.session_state:
        st.session_state['extracted_tables'] = []
    if 'selected_tables_indices' not in st.session_state:
        st.session_state['selected_tables_indices'] = []
    if 'user_inputs' not in st.session_state:
        st.session_state['user_inputs'] = {}
    if 'temp_dirs' not in st.session_state:
        st.session_state['temp_dirs'] = []
    if 'file_paths' not in st.session_state:
        st.session_state['file_paths'] = []
    if 'profiles' not in st.session_state:
        st.session_state['profiles'] = load_saved_profiles()

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose MS Word (.docx) or PDF files",
        type=['pdf', 'docx'],
        accept_multiple_files=True
    )

    # Display uploaded files
    if uploaded_files:
        st.write("Uploaded files:")
        for file in uploaded_files:
            st.write(f"- {file.name}")

        # Save uploaded files and populate file_paths
        #try:
        # Clean up previous temp directories if any
        for temp_dir in st.session_state['temp_dirs']:
            try:
                shutil.rmtree(temp_dir)
                logger.debug(f"Deleted temporary directory '{temp_dir}'.")
            except OSError as e:
                logger.warning(f"Error deleting temporary directory '{temp_dir}': {e}")
        st.session_state['temp_dirs'] = []
        st.session_state['file_paths'] = []

        for uploaded_file in uploaded_files:
            temp_dir = tempfile.mkdtemp()
            st.session_state['temp_dirs'].append(temp_dir)
            file_name = uploaded_file.name

            # Check if file extension is '.doc'
            if file_name.lower().endswith('.doc'):
                st.error(f"File '{file_name}' is a .doc file, which is not supported. Please convert it to .docx.")
                logger.error(f"File '{file_name}' is a .doc file, which is not supported.")
                continue  # Skip this file

            temp_file_path = os.path.join(temp_dir, file_name)

            with open(temp_file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            st.session_state['file_paths'].append(temp_file_path)
            logger.debug(f"Saved uploaded file '{uploaded_file.name}' to temporary file '{temp_file_path}'.")

        # Process the documents and extract tables for preview
        #try:
        # Parse the documents and extract tables
        documents, parse_errors = parse_documents(st.session_state['file_paths'])
        st.session_state['documents'] = documents
        logger.info(f"Parsed {len(documents)} documents.")

        if parse_errors:
            st.subheader("Errors during parsing:")
            for error in parse_errors:
                st.error(error)
            if not documents:
                st.error("No documents were successfully parsed. Please check the errors above.")
                st.stop()
        else:
            st.success(f"All {len(documents)} documents were successfully parsed.")

        all_tables = []
        document_table_mapping = []
        total_tables = 0
        for doc_index, document in enumerate(documents):
            # For preview, we'll select all tables initially
            selected_tables = document.tables
            total_tables += len(selected_tables)
            all_tables.extend(selected_tables)
            document_table_mapping.extend([(doc_index, tbl) for tbl in selected_tables])

        # Save extracted tables in session state
        st.session_state['extracted_tables'] = all_tables
        st.session_state['document_table_mapping'] = document_table_mapping

        # Display the number of detected tables
        st.subheader("Number of Detected Tables")
        st.write(f"Total number of tables detected in uploaded files: {total_tables}")

        if total_tables == 0:
            st.error("No tables were found in the uploaded documents.")
            st.stop()
        # Create preliminary user inputs
        st.session_state['user_inputs']['source_documents'] = st.session_state['file_paths']
        
        # Now that we have tables, we can set default indices for preview
        if 'table_selection' not in st.session_state['user_inputs']:
            st.session_state['user_inputs']['table_selection'] = {}
        if 'method' not in st.session_state['user_inputs']['table_selection']:
            st.session_state['user_inputs']['table_selection']['method'] = 'indexing'
        if 'indices' not in st.session_state['user_inputs']['table_selection']:
            # Default to all indices in the preview
            st.session_state['user_inputs']['table_selection']['indices'] = list(range(total_tables))
        
        # Process user inputs to create extraction parameters (without needing the full parameters yet)
        extraction_parameters = process_user_input_preview(st.session_state['user_inputs'])

        # Parse the documents and extract tables
        documents, parse_errors = parse_documents(st.session_state['file_paths'])
        st.session_state['documents'] = documents
        logger.info(f"Parsed {len(documents)} documents.")

        if parse_errors:
            st.subheader("Errors during parsing:")
            for error in parse_errors:
                st.error(error)
            if not documents:
                st.error("No documents were successfully parsed. Please check the errors above.")
                st.stop()
        else:
            st.success(f"All {len(documents)} documents were successfully parsed.")

        all_tables = []
        document_table_mapping = []
        total_tables = 0
        for doc_index, document in enumerate(documents):
            # For preview, we'll select all tables initially
            selected_tables = document.tables
            total_tables += len(selected_tables)
            all_tables.extend(selected_tables)
            document_table_mapping.extend([(doc_index, tbl) for tbl in selected_tables])

        # Save extracted tables in session state
        st.session_state['extracted_tables'] = all_tables
        st.session_state['document_table_mapping'] = document_table_mapping

        # Display the number of detected tables
        st.subheader("Number of Detected Tables")
        st.write(f"Total number of tables detected in uploaded files: {total_tables}")

        if total_tables == 0:
            st.error("No tables were found in the uploaded documents.")
            st.stop()

        #except Exception as e:
            #st.error(f"An error occurred during table extraction: {e}")
            #logger.exception(f"An error occurred during table extraction: {e}")
            #st.stop()

        #except Exception as e:
            #st.error(f"Error saving uploaded files: {e}")
            #logger.error(f"Error saving uploaded files: {e}")
            #st.stop()

    else:
        st.stop()  # Stop execution until files are uploaded

    # Load saved profiles
    st.header("Load Saved Profile")
    profiles = st.session_state['profiles']
    if profiles:
        selected_profile_name = st.selectbox("Select a saved profile", ["-- Select --"] + list(profiles.keys()))
        if selected_profile_name != "-- Select --":
            user_inputs = profiles[selected_profile_name]
                        # Ensure 'table_selection' exists
            if 'table_selection' not in user_inputs:
                st.warning("Loaded profile is missing 'table_selection'. Assigning default method 'indexing'.")
                user_inputs['table_selection'] = {'method': 'indexing'}
            else:
                # Ensure 'method' is set and valid
                method = user_inputs['table_selection'].get('method')
                if not method or method.lower() not in ['indexing', 'keyword', 'regex', 'criteria', 'saved_profile']:
                    st.warning(f"Loaded profile has invalid or missing 'method'. Assigning default method 'indexing'.")
                    user_inputs['table_selection']['method'] = 'indexing'

            st.session_state['user_inputs'] = user_inputs
            st.success(f"Loaded profile '{selected_profile_name}'")
        else:
            user_inputs = st.session_state['user_inputs']
    else:
        st.write("No saved profiles found.")
        user_inputs = st.session_state['user_inputs']

    # Extraction parameters
    st.header("Extraction Parameters")

    # Table Selection Criteria
    st.subheader("Table Selection Criteria")

    selection_methods = ['Indexing', 'Keyword', 'Regex', 'Criteria']
    method_index = selection_methods.index(user_inputs.get('table_selection', {}).get('method', 'Indexing').capitalize()) if 'table_selection' in user_inputs else 0

    selection_method = st.selectbox(
        "Select Table Selection Method",
        selection_methods,
        index=method_index
    )

    indices = None
    keywords = None
    regex_patterns = None
    row_conditions = None
    column_conditions = None

    # Retrieve values from user_inputs if they exist
    indices_input = user_inputs.get('indices_input', '1')
    keywords_input = user_inputs.get('keywords_input', '')
    regex_input = user_inputs.get('regex_input', '')

    if selection_method == 'Indexing':
        indices_input = st.text_input("Enter Table Indices (comma-separated)", value=indices_input)
        try:
            indices = [int(i.strip()) - 1 for i in indices_input.split(',') if i.strip()]  # Adjusted for zero-based index
        except ValueError:
            st.error("Indices must be integers separated by commas.")
            st.stop()
    elif selection_method == 'Keyword':
        keywords_input = st.text_input("Enter Keywords (comma-separated)", value=keywords_input)
        keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
    elif selection_method == 'Regex':
        regex_input = st.text_input("Enter Regular Expressions (comma-separated)", value=regex_input)
        regex_patterns = [r.strip() for r in regex_input.split(',') if r.strip()]
    elif selection_method == 'Criteria':
        st.info("Criteria-based selection is not implemented in this interface yet.")
        st.stop()

    # Save selection method parameters to user_inputs
    st.session_state['user_inputs']['table_selection'] = {
        'method': selection_method.lower(),
        'indices': indices,
        'keywords': keywords,
        'regex_patterns': regex_patterns,
        'row_conditions': row_conditions,
        'column_conditions': column_conditions
    }
    st.session_state['user_inputs']['indices_input'] = indices_input
    st.session_state['user_inputs']['keywords_input'] = keywords_input
    st.session_state['user_inputs']['regex_input'] = regex_input

    # Now re-select tables based on the selection criteria
    extraction_parameters = process_user_input_preview(st.session_state['user_inputs'])

    selected_tables = []
    selected_document_table_mapping = []
    if selection_method.lower() == 'indexing':
        # Handle Indexing
        for idx in indices:
            if idx >= 0 and idx < len(st.session_state['extracted_tables']):
                table = st.session_state['extracted_tables'][idx]
                doc_idx, _ = st.session_state['document_table_mapping'][idx]
                selected_tables.append(table)
                selected_document_table_mapping.append((doc_idx, table))
    else:
        # Other methods
        for idx, (doc_idx, table) in enumerate(st.session_state['document_table_mapping']):
            if select_table_by_criteria(table, extraction_parameters.table_selection):
                selected_tables.append(table)
                selected_document_table_mapping.append((doc_idx, table))

    if not selected_tables:
        st.error("No tables found according to the selection criteria.")
        st.stop()
    else:
        st.session_state['extracted_tables'] = selected_tables
        st.session_state['document_table_mapping'] = selected_document_table_mapping
        st.write(f"Number of tables selected based on criteria: {len(selected_tables)}")

    # Show the preview of the extracted tables
    st.subheader("Extracted Tables Preview")

    table_indices = []
    table_previews = []
    for idx, (doc_idx, table) in enumerate(st.session_state['document_table_mapping']):
        # Show a preview of the table
        st.write(f"Table {idx+1} from Document: {os.path.basename(st.session_state['documents'][doc_idx].file_path)}")
        df = table_to_dataframe(table)
        st.dataframe(df.head())  # Show first few rows
        table_indices.append(idx)
        table_previews.append(f"Document {os.path.basename(st.session_state['documents'][doc_idx].file_path)} - Table {idx+1}")
    # Allow the user to select which tables to include
    selected_tables_indices = st.multiselect(
        "Select Tables to Include in Extraction",
        options=table_indices,
        format_func=lambda x: table_previews[x],
        default=table_indices  # By default, select all tables
    )
    # Save the indices of selected tables
    st.session_state['selected_tables_indices'] = selected_tables_indices

    # Proceed to the rest of the extraction parameters

    # Formatting Rules
    st.subheader("Formatting Rules")

    preserve_styles = st.checkbox("Preserve Text Styles (e.g., bold, italic)", value=st.session_state['user_inputs'].get('preserve_styles', False))
    date_format = st.text_input("Date Format", value=st.session_state['user_inputs'].get('date_format', "%Y-%m-%d"))
    number_format = st.text_input("Number Format (e.g., {:.2f} for two decimal places)", value=st.session_state['user_inputs'].get('number_format', ''))
    encoding = st.text_input("Text Encoding", value=st.session_state['user_inputs'].get('encoding', 'utf-8'))
    placeholder_for_missing = st.text_input("Placeholder for Missing Data", value=st.session_state['user_inputs'].get('placeholder_for_missing', ''))
    header_rows = st.number_input("Number of Header Rows", min_value=0, value=st.session_state['user_inputs'].get('header_rows', 1))

    # Save formatting rules to user_inputs
    st.session_state['user_inputs']['extraction_parameters'] = {
        'formatting_rules': {
            'preserve_styles': preserve_styles,
            'date_format': date_format,
            'number_format': number_format if number_format else None,
            'encoding': encoding,
            'placeholder_for_missing': placeholder_for_missing if placeholder_for_missing else None,
            'header_rows': int(header_rows)
        }
    }

    # Error Handling Strategy
    st.subheader("Error Handling Strategy")

    on_parsing_error = st.selectbox(
        "On Parsing Error",
        ['Skip', 'Abort', 'Log'],
        index={'skip': 0, 'abort': 1, 'log': 2}.get(st.session_state['user_inputs'].get('on_parsing_error', 'log').lower(), 2)
    )
    on_validation_error = st.selectbox(
        "On Validation Error",
        ['Correct', 'Omit', 'Prompt', 'Abort'],
        index={'correct': 0, 'omit': 1, 'prompt': 2, 'abort': 3}.get(st.session_state['user_inputs'].get('on_validation_error', 'omit').lower(), 1)
    )

    st.session_state['user_inputs']['extraction_parameters']['error_handling'] = {
        'on_parsing_error': on_parsing_error.lower(),
        'on_validation_error': on_validation_error.lower(),
        'fallback_mechanisms': []  # Placeholder for potential fallback functions
    }

    # Parser Configuration
    st.subheader("Parser Configuration")

    ocr_enabled = st.checkbox("Enable OCR for Scanned PDFs", value=st.session_state['user_inputs'].get('ocr_enabled', False))
    language = st.text_input("Document Language", value=st.session_state['user_inputs'].get('language', 'en'))

    st.session_state['user_inputs']['extraction_parameters']['parser_config'] = {
        'ocr_enabled': ocr_enabled,
        'language': language,
        'resource_limits': {
            'max_memory': None,
            'max_time': None,
            'max_cpu_usage': None
        }
    }

    # Resource Limits
    st.subheader("Resource Limits")

    max_memory = st.number_input("Max Memory (MB)", min_value=0, value=st.session_state['user_inputs'].get('max_memory', 0))
    max_time = st.number_input("Max Time (seconds)", min_value=0, value=st.session_state['user_inputs'].get('max_time', 0))
    max_cpu_usage = st.number_input("Max CPU Usage (%)", min_value=0, max_value=100, value=st.session_state['user_inputs'].get('max_cpu_usage', 0))

    st.session_state['user_inputs']['extraction_parameters']['parser_config']['resource_limits'] = {
        'max_memory': int(max_memory) if max_memory > 0 else None,
        'max_time': int(max_time) if max_time > 0 else None,
        'max_cpu_usage': int(max_cpu_usage) if max_cpu_usage > 0 else None
    }

    # Save current settings as profile
    st.subheader("Save Current Settings as Profile")
    profile_name_input = st.text_input("Profile Name", value='')
    if st.button("Save Profile"):
        if profile_name_input:
            profile = st.session_state['user_inputs']
            save_profile(profile_name_input, profile)
            st.success(f"Profile '{profile_name_input}' saved successfully.")
            # Reload profiles
            st.session_state['profiles'] = load_saved_profiles()
        else:
            st.error("Please enter a profile name to save.")

    # Process Documents button
    if st.button("Process Documents"):
        if not st.session_state.get('extracted_tables'):
            st.error("Please extract and preview tables before processing.")
            st.stop()
        if not st.session_state.get('selected_tables_indices'):
            st.error("Please select at least one table to process.")
            st.stop()

        # Update user_inputs with current selections
        st.session_state['user_inputs']['selected_tables_indices'] = st.session_state['selected_tables_indices']
        user_inputs = st.session_state['user_inputs']

        # Process user inputs
        try:
            source_documents, extraction_parameters = process_user_input(user_inputs)
        except InvalidUserInputError as e:
            st.error(f"Invalid user input: {e}")
            logger.error(f"Invalid user input: {e}")
            st.stop()

        # Process the documents
        try:
            # Process only the selected tables
            extracted_data = process_documents(
                st.session_state['file_paths'],
                extraction_parameters,
                selected_tables=st.session_state['selected_tables_indices'],
                documents=st.session_state['documents'],
                extracted_tables=st.session_state['extracted_tables'],
                document_table_mapping=[st.session_state['document_table_mapping'][i] for i in st.session_state['selected_tables_indices']]
            )
        except ProcessingError as e:
            st.error(f"Error processing documents: {e}")
            logger.error(f"Error processing documents: {e}")
            st.stop()
        except Exception as e:
            st.error(f"An unexpected error occurred during document processing: {e}")
            logger.exception(f"An unexpected error occurred during document processing: {e}")
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
                data=rendered_data.encode('utf-8'),
                file_name='extracted_tables.json',
                mime='application/json'
            )

        except RenderingError as e:
            st.error(f"Error rendering results: {e}")
            logger.error(f"Error rendering results: {e}")
            st.stop()
        except Exception as e:
            st.error(f"An unexpected error occurred during rendering: {e}")
            logger.exception(f"An unexpected error occurred during rendering: {e}")
            st.stop()

        finally:
            # Clean up temporary files and directories
            for temp_dir in st.session_state['temp_dirs']:
                try:
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Deleted temporary directory '{temp_dir}'.")
                except OSError as e:
                    logger.warning(f"Error deleting temporary directory '{temp_dir}': {e}")
            st.session_state['temp_dirs'] = []
            st.session_state['file_paths'] = []
            st.session_state['documents'] = []
            st.session_state['extracted_tables'] = []
            st.session_state['selected_tables_indices'] = []

def load_saved_profiles():
    # Implement code to load saved profiles
    # For simplicity, we can store profiles as JSON files in a 'profiles' directory
    profiles = {}
    profiles_dir = 'profiles'
    if not os.path.exists(profiles_dir):
        os.makedirs(profiles_dir)
    for file_name in os.listdir(profiles_dir):
        file_path = os.path.join(profiles_dir, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.json'):
            with open(file_path, 'r') as f:
                profile = json.load(f)
                profile_name = os.path.splitext(file_name)[0]
                profiles[profile_name] = profile
    return profiles

def save_profile(profile_name, profile_data):
    profiles_dir = 'profiles'
    if not os.path.exists(profiles_dir):
        os.makedirs(profiles_dir)

    # Ensure 'table_selection' exists
    if 'table_selection' not in profile_data:
        profile_data['table_selection'] = {'method': 'indexing'}
    else:
        # Ensure 'method' is set and valid
        method = profile_data['table_selection'].get('method')
        if not method or method.lower() not in ['indexing', 'keyword', 'regex', 'criteria', 'saved_profile']:
            profile_data['table_selection']['method'] = 'indexing'

    file_path = os.path.join(profiles_dir, f"{profile_name}.json")
    with open(file_path, 'w') as f:
        json.dump(profile_data, f)

def select_table_by_criteria(table, selection_criteria: TableSelectionCriteria) -> bool:
    """
    Determines if a table should be selected based on the given selection criteria.
    """
    if selection_criteria.method == 'indexing':
        # Indexing method is handled separately
        return False
    elif selection_criteria.method == 'keyword':
        return table_contains_keywords(table, selection_criteria.keywords)
    elif selection_criteria.method == 'regex':
        return table_matches_regex(table, selection_criteria.regex_patterns)
    else:
        return False  # Other methods not implemented

def table_contains_keywords(table, keywords: List[str]) -> bool:
    for row in table.data:
        for cell in row:
            if any(keyword.lower() in str(cell.content).lower() for keyword in keywords):
                return True
    return False

def table_matches_regex(table, patterns: List[str]) -> bool:
    for pattern in patterns:
        regex = re.compile(pattern)
        for row in table.data:
            for cell in row:
                if regex.search(str(cell.content)):
                    return True
    return False

if __name__ == '__main__':
    main()