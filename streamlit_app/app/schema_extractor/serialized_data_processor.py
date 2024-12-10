# serialized_data_processor.py

import json
import yaml
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st
from jsonschema import validate as jsonschema_validate
from jsonschema import exceptions as jsonschema_exceptions
import genson
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report

def process_serialized_data(sanitized_data):
    """
    Processes serialized data files.

    Performs EDA, schema extraction, and validation.

    Args:
        sanitized_data (dict): Dictionary with file names as keys and sanitized data as values.
            Each value is a dict containing 'content' and 'file_type'.
    """
    # Parsing the serialized data
    parsed_data = parse_serialized_data(sanitized_data)
    if parsed_data:
        # Perform Exploratory Data Analysis
        perform_eda(parsed_data)
        # Extract Data Schemas
        extracted_schemas = extract_schema(parsed_data)
        # Validate Data Against Schemas
        validate_schema(parsed_data, extracted_schemas)

def parse_serialized_data(sanitized_data):
    """
    Parses serialized data from sanitized data.

    Args:
        sanitized_data (dict): Dictionary with file names as keys and sanitized data as values.
            Each value is a dict containing 'content' and 'file_type'.

    Returns:
        dict: Dictionary containing parsed data structures with file names as keys.
    """
    parsed_data = {}
    for file_name, data_info in sanitized_data.items():
        file_content = data_info.get('content')
        file_type = data_info.get('file_type').lower()
        st.write(f"Parsing file **{file_name}** of type **{file_type}**")
        try:
            if file_type == 'json':
                parsed_data[file_name] = json.loads(file_content)
            elif file_type in ['yaml', 'yml']:
                parsed_data[file_name] = yaml.safe_load(file_content)
            elif file_type == 'xml':
                # Parse XML content into ElementTree
                parsed_data[file_name] = ET.ElementTree(ET.fromstring(file_content))
            else:
                st.error(f"Unsupported file type: {file_type} for file {file_name}")
        except Exception as e:
            st.error(f"Error parsing file {file_name}: {e}")
    return parsed_data

def perform_eda(parsed_data):
    """
    Performs Exploratory Data Analysis on parsed data.

    Args:
        parsed_data (dict): Dictionary containing parsed data structures with file names as keys.
    """
    for file_name, data in parsed_data.items():
        st.write(f"### Performing EDA on file: **{file_name}**")
        try:
            # Flatten data into a DataFrame
            df = flatten_data_to_df(data)
            if df is not None and not df.empty:
                # Generate EDA report
                profile = ProfileReport(df, title=f"EDA Report for {file_name}", explorative=True)
                # Display the report in Streamlit
                st_profile_report(profile)
            else:
                st.warning(f"No tabular data found in file {file_name} for EDA.")
        except Exception as e:
            st.error(f"Error during EDA for file {file_name}: {e}")

def flatten_data_to_df(data):
    """
    Flattens the parsed data into a pandas DataFrame.

    Args:
        data (any): Parsed data (dict, list, or ElementTree) to be flattened into DataFrame.

    Returns:
        pd.DataFrame: Flattened data as DataFrame.
    """
    if isinstance(data, dict):
        # Data is a dict; normalize it
        df = pd.json_normalize(data)
    elif isinstance(data, list):
        # Data is a list of dicts
        df = pd.json_normalize(data)
    elif isinstance(data, ET.ElementTree):
        # For XML data
        df = xml_to_dataframe(data)
    else:
        df = pd.DataFrame()

    return df

def xml_to_dataframe(tree):
    """
    Converts an XML ElementTree into a pandas DataFrame.

    Args:
        tree (ET.ElementTree): Parsed XML data.

    Returns:
        pd.DataFrame: Data extracted from XML as DataFrame.
    """
    root = tree.getroot()
    all_records = []

    # Traverse the XML tree and extract data
    for elem in root.iter():
        record = {}
        # Include element's tag and text
        record[elem.tag] = elem.text
        # Include attributes
        for attr, value in elem.attrib.items():
            record[f"{elem.tag}_{attr}"] = value
        all_records.append(record)

    if all_records:
        df = pd.DataFrame(all_records)
        return df
    else:
        return pd.DataFrame()

def extract_schema(parsed_data):
    """
    Extracts schema from parsed data.

    Args:
        parsed_data (dict): Dictionary containing parsed data structures with file names as keys.

    Returns:
        dict: Dictionary containing schemas with file names as keys.
    """
    extracted_schemas = {}
    for file_name, data in parsed_data.items():
        st.write(f"### Extracting schema for file: **{file_name}**")
        try:
            if isinstance(data, (dict, list)):
                # Assume JSON/YAML data
                builder = genson.SchemaBuilder()
                builder.add_object(data)
                schema = builder.to_schema()
                extracted_schemas[file_name] = schema
                st.write("Extracted Schema:")
                st.json(schema)
            elif isinstance(data, ET.ElementTree):
                # For XML data, inform the user
                st.warning(f"Automatic schema extraction for XML is not currently supported in this tool.")
                extracted_schemas[file_name] = None
            else:
                st.error(f"Unsupported data type for file {file_name}")
        except Exception as e:
            st.error(f"Error extracting schema for file {file_name}: {e}")
    return extracted_schemas

def validate_schema(parsed_data, extracted_schemas):
    """
    Validates the parsed data against the extracted schemas.

    Args:
        parsed_data (dict): Dictionary containing parsed data structures with file names as keys.
        extracted_schemas (dict): Dictionary containing schemas with file names as keys.
    """
    for file_name in parsed_data.keys():
        st.write(f"### Validating data against schema for file: **{file_name}**")
        data = parsed_data[file_name]
        schema = extracted_schemas.get(file_name)
        if schema:
            try:
                jsonschema_validate(instance=data, schema=schema)
                st.success(f"Data in {file_name} is **valid** against the extracted schema.")
            except jsonschema_exceptions.ValidationError as ve:
                st.error(f"Validation error in file {file_name}: {ve.message}")
            except Exception as e:
                st.error(f"Error during validation for file {file_name}: {e}")
        else:
            st.warning(f"No schema available for file {file_name}, skipping validation.")