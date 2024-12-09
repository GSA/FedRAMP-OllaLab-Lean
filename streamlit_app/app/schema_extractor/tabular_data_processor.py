# schema_extractor/tabular_data_processor.py

import pandas as pd
import streamlit as st
from typing import List, Dict, Any
import pandera as pa
from pandera import Column, DataFrameSchema
from pandera import Check
from schema_extractor.utils import detect_file_type, backup_data
from schema_extractor.schema_builder import build_schema, validate_data_against_schema
from schema_extractor.ui_components import display_eda_results, schema_builder_interface, display_validation_results
from schema_extractor.utils import load_tabular_file

def process_tabular_data(sanitized_data: Dict[str, Any]) -> None:
    """
    Processes tabular data files by performing EDA, schema extraction, and validation.

    Args:
        sanitized_data (dict): Dictionary containing sanitized data with file names as keys.
    """
    st.header("Process Tabular Data")

    data_frames = load_tabular_data(sanitized_data)

    if not data_frames:
        st.error("No valid tabular data found to process.")
        return

    # Perform Exploratory Data Analysis
    eda_results = perform_eda(data_frames)
    display_eda_results(eda_results)

    # Data Schema Extraction
    st.subheader("Data Schema Extraction")
    inferred_schema = extract_schema(data_frames)
    st.write("### Inferred Schema")
    st.json(inferred_schema.dict())

    # Schema Builder Interface
    st.subheader("Customize Schema")
    user_defined_schema = schema_builder_interface(inferred_schema)

    # Data Schema Validation
    st.subheader("Schema Validation")
    is_valid = validate_data_against_schema(data_frames, user_defined_schema)
    display_validation_results(is_valid)

def load_tabular_data(sanitized_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    """
    Loads sanitized tabular data into pandas DataFrames.

    Args:
        sanitized_data (dict): Dictionary containing sanitized data with file names as keys.

    Returns:
        dict: Dictionary with file names as keys and pandas DataFrames as values.
    """
    data_frames = {}
    for file_name, content in sanitized_data.items():
        try:
            df = load_tabular_file(content, file_name)
            data_frames[file_name] = df
            st.success(f"Loaded {file_name} successfully.")
        except Exception as e:
            st.error(f"Failed to load {file_name}: {e}")
    return data_frames

def perform_eda(data_frames: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Performs Exploratory Data Analysis on loaded DataFrames.

    Args:
        data_frames (dict): Dictionary with file names as keys and pandas DataFrames as values.

    Returns:
        dict: Dictionary containing EDA reports for each DataFrame.
    """
    eda_reports = {}
    for file_name, df in data_frames.items():
        st.subheader(f"EDA for {file_name}")
        st.write("Generating EDA Report...")
        try:
            profile = generate_eda_report(df)
            eda_reports[file_name] = profile
            # Display EDA report in Streamlit
            st.profile_report(profile)
        except Exception as e:
            st.error(f"Failed to generate EDA for {file_name}: {e}")
    return eda_reports

def generate_eda_report(df: pd.DataFrame) -> Any:
    """
    Generates an EDA report using Pandas Profiling.

    Args:
        df (pd.DataFrame): The DataFrame to analyze.

    Returns:
        Any: The EDA report object.
    """
    import pandas_profiling
    profile = pandas_profiling.ProfileReport(df, explorative=True)
    return profile

def extract_schema(data_frames: Dict[str, pd.DataFrame]) -> pa.DataFrameSchema:
    """
    Extracts schema from DataFrames using Pandera.

    Args:
        data_frames (dict): Dictionary with file names as keys and pandas DataFrames as values.

    Returns:
        pa.DataFrameSchema: The inferred schema.
    """
    # For simplicity, process the first DataFrame
    # Extend as needed to handle multiple DataFrames
    first_file = next(iter(data_frames))
    df = data_frames[first_file]
    st.write(f"Inferring schema for {first_file}")

    schema = infer_schema_with_pandera(df)
    return schema

def infer_schema_with_pandera(df: pd.DataFrame) -> pa.DataFrameSchema:
    """
    Infers a schema for a DataFrame using Pandera.

    Args:
        df (pd.DataFrame): The DataFrame to infer the schema from.

    Returns:
        pa.DataFrameSchema: The inferred schema.
    """
    schema_dict = {}
    for column in df.columns:
        dtype = df[column].dtype
        if pd.api.types.is_integer_dtype(dtype):
            pa_type = pa.Int
        elif pd.api.types.is_float_dtype(dtype):
            pa_type = pa.Float
        elif pd.api.types.is_bool_dtype(dtype):
            pa_type = pa.Bool
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            pa_type = pa.DateTime
        else:
            pa_type = pa.String
        schema_dict[column] = Column(pa_type, nullable=df[column].isnull().any())
    schema = pa.DataFrameSchema(schema_dict)
    return schema

def validate_schema(data_frames: Dict[str, pd.DataFrame], schema: pa.DataFrameSchema) -> bool:
    """
    Validates DataFrames against the provided schema.

    Args:
        data_frames (dict): Dictionary with file names as keys and pandas DataFrames as values.
        schema (pa.DataFrameSchema): The schema to validate against.

    Returns:
        bool: True if all DataFrames are valid, False otherwise.
    """
    all_valid = True
    for file_name, df in data_frames.items():
        st.write(f"Validating schema for {file_name}")
        try:
            schema.validate(df, lazy=True)
            st.success(f"Schema validation passed for {file_name}.")
        except pa.errors.SchemaError as e:
            st.error(f"Schema validation failed for {file_name}: {e}")
            all_valid = False
    return all_valid