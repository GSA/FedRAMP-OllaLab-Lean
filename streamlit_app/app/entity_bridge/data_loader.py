# streamlit_app/app/entity_bridge/data_loader.py

"""
Data Loader Module

This module provides functions to load and handle data files, including
file I/O operations, handling missing data, and field selection for processing.
"""

import pandas as pd
import streamlit as st
import os

def load_data(file):
    """
    Load data from an uploaded file into a pandas DataFrame.

    Args:
        file (UploadedFile): The file uploaded by the user.

    Returns:
        DataFrame: A pandas DataFrame containing the data from the file.

    Raises:
        ValueError: If the file format is unsupported or an error occurs during loading.
    """
    try:
        filename = file.name
        file_extension = os.path.splitext(filename)[1].lower()

        # Determine the file type and use the appropriate pandas function
        if file_extension == '.csv':
            df = pd.read_csv(file)
        elif file_extension == '.tsv':
            df = pd.read_csv(file, delimiter='\t')
        elif file_extension in ['.xls', '.xlsx']:
            df = pd.read_excel(file)
        else:
            # Raise an error if the file format is unsupported
            raise ValueError(f"Unsupported file format: {file_extension}")
        return df

    except Exception as e:
        # Raise an error if loading fails for any reason
        raise ValueError(f"Error loading file {file.name}: {e}")

def handle_missing_data(df, strategy, default_value=None, missing_threshold=0.5):
    """
    Handle missing data in the DataFrame based on the specified strategy.

    Args:
        df (DataFrame): The DataFrame to process.
        strategy (str): The strategy to handle missing data ('remove', 'fill', 'skip').
        default_value (any, optional): The default value to fill in if strategy is 'fill'.
        missing_threshold (float, optional): Threshold for missing data in 'skip' strategy (between 0 and 1).

    Returns:
        DataFrame: The DataFrame after handling missing data.

    Raises:
        ValueError: If the strategy is unsupported.
    """
    if strategy == 'remove':
        # Remove rows with any missing values
        df = df.dropna()
    elif strategy == 'fill':
        # Fill missing values with the specified default value
        if default_value is None:
            default_value = ''
        df = df.fillna(default_value)
    elif strategy == 'skip':
        # Remove columns with missing data exceeding the threshold
        missing_percent = df.isnull().mean()
        columns_to_keep = missing_percent[missing_percent <= missing_threshold].index
        df = df[columns_to_keep]
    else:
        # Raise an error if the strategy is unsupported
        raise ValueError(f"Unsupported missing data handling strategy: {strategy}")
    return df

def select_fields(df, file_name, idx):
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
        options=columns,
        key=f'parent_id_{idx}'
    )

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
        key=f'child_id_{idx}'
    )

    if child_id_field == 'None':
        child_id_field = None

    child_name_field = st.selectbox(
        f"Select Child Name Field for {file_name} (optional):",
        options=['None'] + columns,
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

def load_and_preprocess_files(uploaded_files):
    """
    Load and preprocess multiple uploaded files.

    Args:
        uploaded_files (list): List of files uploaded by the user.

    Returns:
        list: List of tuples (DataFrame, selected_fields).

    Side Effects:
        Displays options and messages in the Streamlit UI.
    """
    data_frames = []
    if not uploaded_files:
        st.warning("No files uploaded.")
        return data_frames

    for idx, file in enumerate(uploaded_files):
        st.header(f"Processing file: {file.name}")
        try:
            # Load the data
            df = load_data(file)
            st.success(f"Successfully loaded {file.name}")

            # Display the first few rows of the data
            st.write("First few rows:")
            st.dataframe(df.head())

            # Ask user how to handle missing data for this file
            st.subheader(f"Handling missing data for {file.name}")
            strategy = st.selectbox(
                f"Select how to handle missing data in {file.name}:",
                ('Remove rows with missing values', 'Fill missing values with defaults', 'Skip processing fields with excessive missing data'),
                key=f'strategy_{idx}'
            )

            # Apply the selected missing data handling strategy
            if strategy == 'Remove rows with missing values':
                df = handle_missing_data(df, 'remove')
            elif strategy == 'Fill missing values with defaults':
                default_value = st.text_input(
                    f"Enter default value to fill missing data in {file.name}:",
                    value='', key=f'default_value_{idx}'
                )
                df = handle_missing_data(df, 'fill', default_value=default_value)
            elif strategy == 'Skip processing fields with excessive missing data':
                st.write("Columns with missing data exceeding the threshold will be dropped.")
                missing_threshold = st.slider(
                    f"Select missing data threshold to drop columns in {file.name}:",
                    min_value=0.0, max_value=1.0, value=0.5, key=f'missing_threshold_{idx}'
                )
                df = handle_missing_data(df, 'skip', missing_threshold=missing_threshold)
            else:
                st.error("Unknown strategy selected.")
                continue  # Skip this file if strategy is invalid

            # Allow user to select fields for processing
            selected_fields = select_fields(df, file.name, idx)

            # Save the selected columns (columns with selected fields)
            # Extract only the selected columns
            required_columns = [col for col in selected_fields.values() if col]
            df_selected = df[required_columns].copy()

            # Append the DataFrame and selected fields to the list
            data_frames.append((df_selected, selected_fields))

        except ValueError as e:
            st.error(f"Error processing file {file.name}: {e}")

    return data_frames