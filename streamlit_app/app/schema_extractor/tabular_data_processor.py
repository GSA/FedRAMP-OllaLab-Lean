# schema_extractor/tabular_data_processor.py

import io
import pandas as pd
import streamlit as st
import pandera as pa
from pandera import DataFrameSchema
from ydata_profiling import ProfileReport

def process_tabular_data(sanitized_data):
    """
    Processes tabular data files.

    Performs EDA, schema extraction, and validation.

    Args:
        sanitized_data (dict): Dictionary containing sanitized data.
                               Keys are filenames, values are file-like objects.
    """
    # Load data into DataFrames
    data_frames = load_tabular_data(sanitized_data)

    # Check if data_frames is empty
    if not data_frames:
        st.error("No valid tabular data files were loaded.")
        return

    # Perform Exploratory Data Analysis
    perform_eda(data_frames)

    # Data Schema Extraction
    schemas = extract_schema(data_frames)

    # Data Schema Validation
    validate_schema(data_frames, schemas)

def load_tabular_data(sanitized_data):
    """
    Loads tabular data into data frames.

    Args:
        sanitized_data (dict): Sanitized data.
                               Keys are filenames, values are file-like objects.

    Returns:
        dict: Dictionary of pandas DataFrame objects with filenames as keys.
    """
    data_frames = {}
    for filename, file_content in sanitized_data.items():
        try:
            # Reset the file pointer to the beginning
            file_content.seek(0)

            # Determine file extension and load accordingly
            if filename.endswith('.csv'):
                df = pd.read_csv(file_content)
            elif filename.endswith('.tsv'):
                df = pd.read_csv(file_content, sep='\t')
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(file_content)
            elif filename.endswith('.parquet'):
                df = pd.read_parquet(file_content)
            elif filename.endswith('.feather'):
                df = pd.read_feather(file_content)
            elif filename.endswith('.h5') or filename.endswith('.hdf5'):
                df = pd.read_hdf(file_content)
            else:
                st.warning(f"Unsupported file format for file {filename}")
                continue

            # Store the DataFrame with the filename as the key
            data_frames[filename] = df
        except Exception as e:
            st.error(f"Error loading file {filename}: {e}")
    return data_frames

def perform_eda(data_frames):
    """
    Performs Exploratory Data Analysis on data frames.

    Generates and displays profiling reports.

    Args:
        data_frames (dict): Dictionary of pandas DataFrame objects.
    """
    for filename, df in data_frames.items():
        st.write(f"## Exploratory Data Analysis for {filename}")

        # Generate profiling report using ydata_profiling
        profile = ProfileReport(df, title=f"Profiling Report for {filename}", explorative=True)

        # Display the profiling report in Streamlit
        st_profile_report(profile)

def st_profile_report(profile):
    """
    Displays the profiling report in the Streamlit app.

    Args:
        profile (ProfileReport): The profiling report object.
    """
    # Convert the report to HTML and embed it in the Streamlit app
    st.components.v1.html(profile.to_html(), height=1000, scrolling=True)

def extract_schema(data_frames):
    """
    Extracts schema from data frames using pandera.

    Args:
        data_frames (dict): Dictionary of pandas DataFrame objects.

    Returns:
        dict: Dictionary of DataFrameSchema objects with filenames as keys.
    """
    schemas = {}
    for filename, df in data_frames.items():
        st.write(f"## Extracting Schema for {filename}")

        # Infer schema using pandera
        schema = infer_schema(df)

        # Store the schema with the filename as the key
        schemas[filename] = schema

        # Display the schema
        st.write(schema)
    return schemas

def infer_schema(df):
    """
    Infers a pandera schema from the dataframe.

    Args:
        df (pd.DataFrame): The dataframe to infer schema from.

    Returns:
        DataFrameSchema: The inferred schema.
    """
    # Use pandera's infer_schema function
    schema = pa.infer_schema(df)

    return schema

def validate_schema(data_frames, schemas):
    """
    Validates data frames against the extracted schema.

    Args:
        data_frames (dict): Dictionary of pandas DataFrame objects.
        schemas (dict): Dictionary of DataFrameSchema objects.
    """
    for filename in data_frames:
        st.write(f"## Validating Data for {filename}")
        df = data_frames[filename]
        schema = schemas[filename]
        try:
            # Validate the dataframe against the schema
            validated_df = schema.validate(df)

            # If validation is successful
            st.success(f"{filename} is valid against the schema.")
        except pa.errors.SchemaErrors as e:
            # If validation fails, display the error messages
            st.error(f"Schema validation errors for {filename}:")
            st.dataframe(e.failure_cases)