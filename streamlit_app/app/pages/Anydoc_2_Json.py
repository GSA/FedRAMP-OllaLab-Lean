# Anydoc_2_Json.py

app_version = "0.1"
app_title = "OllaLab - AnyDoc to JSON"
app_description = "Save unstructured documents to JSON"
app_icon = ":arrow_upper_right:"

import streamlit as st
import os
import json
import shutil
import datetime
import yaml
import sys

sys.path.append(os.path.abspath('..'))  # Adjust the path to locate the modules

# Import modules
from anydoc_2_json.modules.param_manager import ParamManager
from anydoc_2_json.modules.logger_manager import LoggerManager
from anydoc_2_json.modules.doc_preprocessor import DocPreprocessor
from anydoc_2_json.modules.doc_converter import DocConverter
from anydoc_2_json.modules.md_parser import MdParser
from anydoc_2_json.modules.table_processor import TableProcessor


def main():
    """
    Main function that orchestrates the Streamlit application steps.

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Upstream functions:
        - None (entry point)

    Downstream functions:
        - initialize_session_state()
        - handle_file_upload()
        - handle_parameter_file()
        - pre_conversion_processing()
        - convert_document()
        - display_markdown_content()
        - extract_structured_data()
        - process_tables()
    """
    # Set page title and layout
    st.set_page_config(page_title="AnyDoc to JSON", layout='wide')

    # Initialize session state
    initialize_session_state()

    st.title("AnyDoc to JSON")

    # Step 1: Initialization
    # File upload
    handle_file_upload()

    if st.session_state.get('file_uploaded', False):
        # Parameter file selection or creation
        handle_parameter_file()

    if st.session_state.get('param_file_selected', False):
        # Step 2: Pre-conversion processing
        pre_conversion_processing()

        # Once pre-processing is done, proceed to conversion
        if st.session_state.get('preprocessing_done', False):
            # Step 3: Convert document to Markdown
            convert_document()

            # Step 4: Display Markdown content
            display_markdown_content()

            # Step 5: Extract structured data
            extract_structured_data()

            # Step 6: Process and enrich tables
            process_tables()

def initialize_session_state():
    """
    Initializes Streamlit session state variables used in the application.

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Upstream functions:
        - Called by main()

    Downstream functions:
        None

    Dependencies:
        - Streamlit session_state object
    """
    # Initialize the required session state variables
    session_vars = [
        'uploaded_file', 'result_folder', 'param_file', 'param_manager', 'logger_manager',
        'preprocessing_done', 'param_file_selected', 'converted_markdown_path', 'markdown_content',
        'document_title', 'file_uploaded', 'preprocessing_steps_completed', 'json_data', 'enriched_json_data'
    ]
    for var in session_vars:
        if var not in st.session_state:
            st.session_state[var] = None

def handle_file_upload():
    """
    Handles file upload and saves the uploaded file to the result folder.

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Upstream functions:
        - Called by main()

    Downstream functions:
        - Saves the uploaded file to the result folder
        - Initializes logger_manager

    Dependencies:
        - Streamlit file_uploader
        - os, shutil, datetime modules
        - LoggerManager
    """
    st.header("1. Upload Document")
    uploaded_file = st.file_uploader("Choose a DOCX or PDF file", type=["docx", "pdf", "doc"])
    if uploaded_file is not None:
        st.session_state['uploaded_file'] = uploaded_file
        # Create result folder
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H") # only use the hour
        file_name = os.path.splitext(uploaded_file.name)[0]
        result_folder_name = f"{file_name}_{timestamp}"
        result_folder = os.path.join('app_data', 'anydoc_2_json', result_folder_name)
        os.makedirs(result_folder, exist_ok=True)
        st.session_state['result_folder'] = result_folder
        # Save uploaded file to result folder
        file_path = os.path.join(result_folder, uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        st.write(f"File saved to {file_path}")
        # Initialize logger manager
        log_file_path = os.path.join(result_folder, 'processing.log')
        logger_manager = LoggerManager(log_file_path=log_file_path)
        st.session_state['logger_manager'] = logger_manager
        st.session_state['file_uploaded'] = True
        st.success("File uploaded and saved successfully.")

def handle_parameter_file():
    """
    Handles parameter file selection or creation.

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Upstream functions:
        - Called by main()

    Downstream functions:
        - Initializes param_manager

    Dependencies:
        - Streamlit inputs
        - ParamManager
        - yaml module
        - os module
    """
    st.header("2. Select or Create Parameter File")
    parameters_dir = os.path.join('anydoc_2_json', 'parameters')
    os.makedirs(parameters_dir, exist_ok=True)  # Ensure the parameters directory exists
    param_files = [f for f in os.listdir(parameters_dir) if f.endswith('.yaml')]
    if param_files:
        param_file_option = st.radio("Choose parameter file option", ['Select existing parameter file', 'Create new parameter file'])
    else:
        st.info("No existing parameter files found. Please create a new parameter file.")
        param_file_option = 'Create new parameter file'

    if param_file_option == 'Select existing parameter file':
        if not param_files:
            st.warning("No parameter files found. Please create a new parameter file.")
        else:
            selected_param_file = st.selectbox("Select a parameter file", param_files)
            if st.button("Use this parameter file", key="use_existing_param_file"):
                param_file_path = os.path.join(parameters_dir, selected_param_file)
                param_manager = ParamManager(param_file_path=param_file_path)
                st.session_state['param_file'] = param_file_path
                st.session_state['param_manager'] = param_manager
                st.session_state['param_file_selected'] = True
                st.success(f"Parameter file '{selected_param_file}' selected.")
    else:
        new_param_file_name = st.text_input("Enter new parameter file name (without extension)")
        if st.button("Create and use this parameter file", key="create_new_param_file"):
            if new_param_file_name:
                param_file_path = os.path.join(parameters_dir, new_param_file_name + '.yaml')
                if os.path.exists(param_file_path):
                    st.error("Parameter file already exists. Please choose a different name.")
                else:
                    # Create empty parameter file
                    with open(param_file_path, 'w') as f:
                        yaml.dump({}, f)
                    param_manager = ParamManager(param_file_path=param_file_path)
                    st.session_state['param_file'] = param_file_path
                    st.session_state['param_manager'] = param_manager
                    st.session_state['param_file_selected'] = True
                    st.success(f"Parameter file '{new_param_file_name}.yaml' created and selected.")
            else:
                st.error("Please enter a parameter file name.")

def pre_conversion_processing():
    """
    Handles pre-conversion processing steps:
    - Replace interactive form controls
    - Remove texts between markers
    - Find and replace texts
    - Anonymize texts
    - Adjust dates

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Upstream functions:
        - Called by main()

    Downstream functions:
        - Calls functions for each pre-processing step
        - Updates param_manager

    Dependencies:
        - Streamlit inputs
        - ParamManager
        - DocPreprocessor
    """
    st.header("3. Pre-conversion Processing")
    st.write("You can skip any of the following steps or proceed to the next one.")

    # Initialize a list to keep track of completed steps
    if 'preprocessing_steps_completed' not in st.session_state:
        st.session_state['preprocessing_steps_completed'] = []

    replace_form_controls_step()
    remove_texts_step()
    find_and_replace_texts_step()
    anonymize_texts_step()
    adjust_dates_step()

    # Run the pre-processing steps
    if st.button("Run Pre-processing"):
        try:
            param_manager = st.session_state['param_manager']
            input_file_path = os.path.join(st.session_state['result_folder'], st.session_state['uploaded_file'].name)
            output_folder = st.session_state['result_folder']
            doc_preprocessor = DocPreprocessor(input_file=input_file_path,
                                               output_folder=output_folder,
                                               param_manager=param_manager,
                                               logger_manager=st.session_state['logger_manager'])
            doc_preprocessor.process_document()
            st.session_state['preprocessing_done'] = True
            st.success("Pre-processing completed successfully.")
        except Exception as e:
            st.error(f"Error during pre-processing: {e}")
            st.session_state['logger_manager'].log_exception(e, "Error during pre-processing", input_file_path)

def replace_form_controls_step():
    """
    Handles the Replace Form Controls pre-processing step.

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Upstream functions:
        - Called by pre_conversion_processing()

    Downstream functions:
        - Updates param_manager

    Dependencies:
        - Streamlit inputs
        - ParamManager
    """
    st.subheader("3.1 Replace Interactive Form Controls")
    replace_form_controls = st.radio("Replace interactive form controls?", options=["yes", "no"], index=0)
    st.session_state['param_manager'].set_parameter('replaceFormControls', replace_form_controls)
    st.session_state['param_manager'].save_parameters()
    if replace_form_controls == 'yes':
        st.write("The program will replace interactive form controls with text strings.")
    else:
        st.write("The program will skip replacing interactive form controls.")

def remove_texts_step():
    """
    Handles the Remove Texts Between Markers pre-processing step.

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Upstream functions:
        - Called by pre_conversion_processing()

    Downstream functions:
        - Updates param_manager

    Dependencies:
        - Streamlit inputs
        - ParamManager
    """
    st.subheader("3.2 Remove Texts Between Markers")
    remove_text_option = st.radio("Do you want to remove texts between markers?", options=["Skip this step", "Add text removal rule"], key="remove_text_option")
    if remove_text_option == "Add text removal rule":
        remove_texts = []
        num_rules = st.number_input("How many text removal rules do you want to add?", min_value=1, step=1, key="remove_text_num_rules")
        for i in range(num_rules):
            st.write(f"Rule {i+1}")
            col1, col2 = st.columns(2)
            with col1:
                start_marker = st.text_input("Start marker", key=f"remove_text_start_{i}")
            with col2:
                end_marker = st.text_input("End marker", key=f"remove_text_end_{i}")
            if start_marker and end_marker:
                remove_texts.append({'start': start_marker, 'end': end_marker})
        st.session_state['param_manager'].set_parameter('removeTexts', remove_texts)
        st.session_state['param_manager'].save_parameters()
        st.success("Text removal rules added.")
    else:
        st.write("Skipping removing texts between markers.")

def find_and_replace_texts_step():
    """
    Handles the Find and Replace Texts pre-processing step.

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Upstream functions:
        - Called by pre_conversion_processing()

    Downstream functions:
        - Updates param_manager

    Dependencies:
        - Streamlit inputs
        - ParamManager
    """
    st.subheader("3.3 Find and Replace Texts")
    replace_text_option = st.radio("Do you want to find and replace texts?", options=["Skip this step", "Add text replacement rule"], key="replace_text_option")
    if replace_text_option == "Add text replacement rule":
        replace_texts = []
        num_rules = st.number_input("How many text replacement rules do you want to add?", min_value=1, step=1, key="replace_text_num_rules")
        for i in range(num_rules):
            st.write(f"Rule {i+1}")
            col1, col2 = st.columns(2)
            with col1:
                find_text = st.text_input("Find", key=f"replace_text_find_{i}")
            with col2:
                replace_with = st.text_input("Replace", key=f"replace_text_replace_{i}")
            if find_text is not None:
                replace_texts.append({'from': find_text, 'to': replace_with})
        st.session_state['param_manager'].set_parameter('replaceText', replace_texts)
        st.session_state['param_manager'].save_parameters()
        st.success("Text replacement rules added.")
    else:
        st.write("Skipping find and replace texts.")

def anonymize_texts_step():
    """
    Handles the Anonymize Texts pre-processing step.

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Upstream functions:
        - Called by pre_conversion_processing()

    Downstream functions:
        - Updates param_manager

    Dependencies:
        - Streamlit inputs
        - ParamManager
    """
    st.subheader("3.4 Anonymize Texts")
    anonymize_option = st.radio("Do you want to anonymize texts?", options=["Skip this step", "Add anonymization rule"], key="anonymize_option")
    if anonymize_option == "Add anonymization rule":
        anonymization = {}
        categories = ['email', 'person name', 'organization']
        methods = ['redact', 'jibberish', 'realistic']
        for category in categories:
            st.write(f"Anonymization for {category}:")
            method = st.selectbox(f"Select method", methods, key=f"anonymize_{category}")
            anonymization[category] = method
        st.session_state['param_manager'].set_parameter('anonymization', anonymization)
        st.session_state['param_manager'].save_parameters()
        st.success("Anonymization rules added.")
    else:
        st.write("Skipping anonymization.")

def adjust_dates_step():
    """
    Handles the Adjust Dates pre-processing step.

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Upstream functions:
        - Called by pre_conversion_processing()

    Downstream functions:
        - Updates param_manager

    Dependencies:
        - Streamlit inputs
        - ParamManager
    """
    st.subheader("3.5 Adjust Dates")
    adjust_dates_option = st.radio("Do you want to adjust dates?", options=["Skip this step", "Add date adjustment rule"], key="adjust_dates_option")
    if adjust_dates_option == "Add date adjustment rule":
        methods = {'Add days': 'add', 'Subtract days': 'subtract', 'Days before now': 'daysBefore', 'Days after now': 'daysAfter'}
        method_option = st.selectbox("Select adjustment method", list(methods.keys()), key="adjust_dates_method")
        days_value = st.number_input("Number of days", min_value=1, step=1, key="adjust_dates_days")
        if days_value:
            adjust_dates = {methods[method_option]: int(days_value)}
            st.session_state['param_manager'].set_parameter('adjustDates', adjust_dates)
            st.session_state['param_manager'].save_parameters()
            st.success("Date adjustment rule added.")
    else:
        st.write("Skipping adjust dates.")

def convert_document():
    """
    Converts the document to Markdown using DocConverter and handles heading adjustments.

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Upstream functions:
        - Called by main()

    Downstream functions:
        - Updates session_state with converted_markdown_path and markdown_content

    Dependencies:
        - DocConverter
        - ParamManager
        - LoggerManager
        - os module
    """
    st.header("4. Convert Document to Markdown")
    if st.button("Convert Document"):
        try:
            param_manager = st.session_state['param_manager']
            # Update target file in parameters (in case of pre-processed file)
            input_file_path = os.path.join(st.session_state['result_folder'], st.session_state['uploaded_file'].name)
            # If pre-processing was done, use the processed file
            if st.session_state.get('preprocessing_done', False):
                processed_file_path = os.path.join(st.session_state['result_folder'], st.session_state['uploaded_file'].name)
                param_manager.set_parameter('target', processed_file_path)
            else:
                param_manager.set_parameter('target', input_file_path)
            st.write("Converting document...")
            # Ask for document title
            default_title = os.path.splitext(st.session_state['uploaded_file'].name)[0]
            document_title = st.text_input("Enter document title", value=default_title)
            if document_title:
                param_manager.set_parameter('document_title', document_title)
                st.session_state['document_title'] = document_title
            else:
                st.error("Please enter a document title.")
                return
            doc_converter = DocConverter(logger_manager=st.session_state['logger_manager'], param_manager=param_manager)
            markdown_file_path = doc_converter.convert_document(input_file=param_manager.get_parameter('target'),
                                                                output_folder=st.session_state['result_folder'])
            st.session_state['converted_markdown_path'] = markdown_file_path
            # Read markdown content
            with open(markdown_file_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            st.session_state['markdown_content'] = markdown_content
            st.success("Document converted to Markdown successfully.")
        except Exception as e:
            st.error(f"Error during document conversion: {e}")
            st.session_state['logger_manager'].log_exception(e, "Error during document conversion")

def display_markdown_content():
    """
    Displays the converted Markdown content in a collapsible expander.

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Upstream functions:
        - Called by main()

    Downstream functions:
        None

    Dependencies:
        - Streamlit expander
    """
    st.header("5. Display Markdown Content")
    if st.session_state.get('markdown_content'):
        with st.expander("Show Markdown Content"):
            st.code(st.session_state['markdown_content'], language='markdown')
    else:
        st.info("No markdown content available. Please convert the document first.")

def extract_structured_data():
    """
    Extracts structured data from the Markdown content using MdParser.

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Upstream functions:
        - Called by main()

    Downstream functions:
        - Updates session_state with json_data

    Dependencies:
        - MdParser
        - LoggerManager
    """
    st.header("6. Extract Structured Data")
    if st.button("Extract Structured Data"):
        try:
            markdown_file_path = st.session_state.get('converted_markdown_path')
            if markdown_file_path:
                md_parser = MdParser(md_file_path=markdown_file_path,
                                     output_folder=st.session_state['result_folder'],
                                     logger=st.session_state['logger_manager'])
                json_data = md_parser.parse_markdown()
                st.session_state['json_data'] = json_data
                # Save raw JSON data
                base_file_name = os.path.splitext(os.path.basename(markdown_file_path))[0]
                json_output_file = os.path.join(st.session_state['result_folder'], f"{base_file_name}_raw.json")
                with open(json_output_file, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2)
                st.success(f"Structured data extracted and saved to '{json_output_file}'")
            else:
                st.error("Markdown file not found. Please convert the document first.")
        except Exception as e:
            st.error(f"Error during structured data extraction: {e}")
            st.session_state['logger_manager'].log_exception(e, "Error during structured data extraction")

def process_tables():
    """
    Processes tables in the JSON data, enriches them, and updates the JSON data.

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Upstream functions:
        - Called by main()

    Downstream functions:
        - Updates session_state with enriched_json_data

    Dependencies:
        - TableProcessor
        - LoggerManager
    """
    st.header("7. Process and Enrich Tables")
    if st.button("Process Tables"):
        try:
            json_data = st.session_state.get('json_data')
            if json_data:
                table_processor = TableProcessor(json_data=json_data,
                                                 output_folder=st.session_state['result_folder'],
                                                 logger=st.session_state['logger_manager'])
                table_processor.process_tables()
                # Save enriched JSON data
                base_file_name = os.path.splitext(os.path.basename(st.session_state['converted_markdown_path']))[0]
                table_processor.save_updated_json(base_file_name)
                st.success(f"Tables processed and enriched JSON data saved.")
                # Update session state
                st.session_state['enriched_json_data'] = table_processor.json_data
            else:
                st.error("JSON data not found. Please extract structured data first.")
        except Exception as e:
            st.error(f"Error during table processing: {e}")
            st.session_state['logger_manager'].log_exception(e, "Error during table processing")

if __name__ == '__main__':
    main()