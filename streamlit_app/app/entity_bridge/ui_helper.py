# streamlit_app/app/entity_bridge/ui_helper.py

"""
UI Helper Module

This module contains helper functions to build and manage the Streamlit UI components.
"""

import streamlit as st
import pandas as pd

def display_file_upload():
    """
    Display file upload widgets and return the uploaded files.

    Returns:
        list: List of UploadedFile objects.

    Side Effects:
        Renders file upload widgets in the Streamlit UI.
    """
    st.header("Upload Data Files")
    st.write("You can upload one or more data files (CSV, TSV, or Excel formats).")
    uploaded_files = st.file_uploader(
        "Upload one or more data files",
        type=['csv', 'tsv', 'xls', 'xlsx'],
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.warning("Please upload at least two files to proceed.")
    else:
        st.info(f"{len(uploaded_files)} files were uploaded.")
    return uploaded_files

def display_missing_data_options(idx, file_name):
    """
    Display options for handling missing data and return the user's choice.

    Args:
        idx (int): Index of the file, used for unique Streamlit widget keys.
        file_name (str): Name of the file being processed.

    Returns:
        tuple: A tuple containing the selected strategy, default value (if applicable), and missing threshold (if applicable).

    Side Effects:
        Renders widgets in the Streamlit UI.
    """
    st.subheader(f"Handling Missing Data for {file_name}")
    options = ['Remove rows with missing values',
               'Fill missing values with defaults',
               'Skip processing fields with excessive missing data']
    choice = st.selectbox(
        f"Select how to handle missing data in {file_name}:",
        options,
        key=f'strategy_{idx}'
    )

    strategy_mapping = {
        'Remove rows with missing values': 'remove',
        'Fill missing values with defaults': 'fill',
        'Skip processing fields with excessive missing data': 'skip'
    }
    strategy = strategy_mapping.get(choice, 'remove')

    default_value = None
    missing_threshold = None

    if strategy == 'fill':
        default_value = st.text_input(
            f"Enter default value to fill missing data in {file_name}:",
            value='',
            key=f'default_value_{idx}'
        )
    elif strategy == 'skip':
        missing_threshold = st.slider(
            f"Select missing data threshold to drop columns in {file_name}:",
            min_value=0.0, max_value=1.0, value=0.5, step=0.05, key=f'missing_threshold_{idx}'
        )

    return strategy, default_value, missing_threshold

def display_enriched_data(enriched_data_frames):
    """
    Display the enriched data frames in the Streamlit UI.

    Args:
        enriched_data_frames (list): List of enriched DataFrames to display.

    Side Effects:
        Renders data frames and relevant information in the Streamlit UI.
    """
    st.header("Enriched Data Frames")
    for idx, df in enumerate(enriched_data_frames):
        st.subheader(f"Enriched DataFrame {idx + 1}")
        st.dataframe(df.head(20))  # Display first 20 rows

def download_enriched_data(enriched_data_frames):
    """
    Provide options to download the enriched data frames.

    Args:
        enriched_data_frames (list): List of enriched DataFrames to download.

    Side Effects:
        Adds download buttons to the Streamlit UI.
    """
    st.header("Download Enriched Data Frames")
    for idx, df in enumerate(enriched_data_frames):
        st.subheader(f"Download Enriched DataFrame {idx + 1}")
        # Provide options to select file format
        file_format = st.selectbox(
            f"Select file format for DataFrame {idx + 1}:",
            options=['CSV', 'Excel'],
            key=f'file_format_{idx}'
        )

        if file_format == 'CSV':
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"enriched_data_{idx + 1}.csv",
                mime='text/csv',
                key=f'download_csv_{idx}'
            )
        elif file_format == 'Excel':
            excel_buffer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')
            df.to_excel(excel_buffer, index=False)
            excel_buffer.save()
            excel_buffer.seek(0)
            excel_data = excel_buffer.read()
            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name=f"enriched_data_{idx + 1}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                key=f'download_excel_{idx}'
            )

def display_similarity_threshold_setting(entity_type='parent', default_threshold=0.9):
    """
    Display a slider to adjust the similarity threshold.

    Args:
        entity_type (str): The type of entity ('parent' or 'child').
        default_threshold (float): Default value for the similarity threshold.

    Returns:
        float: The user-selected similarity threshold.

    Side Effects:
        Renders a slider in the Streamlit UI.
    """
    st.subheader(f"Set Similarity Threshold for {entity_type.capitalize()} Entity Matching")
    threshold = st.slider(
        f"Set similarity threshold for {entity_type} entity matching:",
        min_value=0.0,
        max_value=1.0,
        value=default_threshold,
        step=0.01,
        key=f'similarity_threshold_{entity_type}'
    )
    return threshold

def display_confirmation_dialog(message, key):
    """
    Display a confirmation dialog with Yes/No options.

    Args:
        message (str): The message to display to the user.
        key (str): Unique key for the Streamlit widget.

    Returns:
        bool: True if the user selects 'Yes', False if 'No'.

    Side Effects:
        Renders radio buttons in the Streamlit UI.
    """
    st.write(message)
    response = st.radio(
        "Select an option:",
        options=['Yes', 'No'],
        key=key
    )
    return response == 'Yes'

def display_field_selection(df, file_name, idx):
    """
    Allow the user to select fields from the DataFrame.

    Args:
        df (DataFrame): The DataFrame to select fields from.
        file_name (str): Name of the file for display purposes.
        idx (int): Index of the file, used for unique Streamlit widget keys.

    Returns:
        dict: A dictionary with selected field names.

    Side Effects:
        Displays Streamlit widgets for field selection.
    """
    st.subheader(f"Field Selection for {file_name}")
    columns = df.columns.tolist()

    if not columns:
        st.error(f"No columns found in {file_name}.")
        return {}

    # Mandatory fields: Parent ID and Parent Name
    parent_id_field = st.selectbox(
        f"Select Parent ID Field for {file_name}:",
        options=['None'] + columns,
        key=f'parent_id_{idx}'
    )

    if parent_id_field == 'None':
        parent_id_field = None
        
    parent_name_field = st.selectbox(
        f"Select Parent Name Field for {file_name}:",
        options=columns,
        key=f'parent_name_{idx}'
    )

    # Validate that Parent ID and Parent Name fields are not the same
    if parent_id_field == parent_name_field:
        st.error("Parent ID Field and Parent Name Field cannot be the same.")
        st.stop()

    # Optional fields: Child ID and Child Name
    child_id_field = st.selectbox(
        f"Select Child ID Field for {file_name} (optional):",
        options=['None'] + columns,
        index=0,
        key=f'child_id_{idx}'
    )

    if child_id_field == 'None':
        child_id_field = None

    child_name_field = st.selectbox(
        f"Select Child Name Field for {file_name} (optional):",
        options=['None'] + columns,
        index=0,
        key=f'child_name_{idx}'
    )

    if child_name_field == 'None':
        child_name_field = None

    selected_fields = {
        'parent_id': parent_id_field,
        'parent_name': parent_name_field,
        'child_id': child_id_field,
        'child_name': child_name_field
    }

    return selected_fields

def display_progress(message, progress_value):
    """
    Display a progress bar with the given message and progress value.

    Args:
        message (str): Message to display above the progress bar.
        progress_value (float): Progress value between 0.0 and 1.0.

    Side Effects:
        Renders a progress bar in the Streamlit UI.
    """
    st.write(message)
    st.progress(progress_value)