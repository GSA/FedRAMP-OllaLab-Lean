# serialized_data_processor.py

import json
import yaml
import pandas as pd
import streamlit as st
import xml.etree.ElementTree as ET
import genson
import jsonschema
from ydata_profiling import ProfileReport
from io import StringIO

# Import custom modules
from schema_extractor import ui_components, utils

def process_serialized_data(sanitized_data):
    """
    Processes serialized data files.

    Performs EDA, schema extraction, and validation.

    Args:
        sanitized_data (dict): Dictionary containing sanitized data.
    """
    # Parse the serialized data
    parsed_data = parse_serialized_data(sanitized_data)

    if not parsed_data:
        st.error("No data could be parsed from the serialized files.")
        return

    # Perform Exploratory Data Analysis
    perform_eda(parsed_data)

    # Data Schema Extraction
    extracted_schemas = extract_schema(parsed_data)

    # Data Schema Validation
    validate_schema(parsed_data, extracted_schemas)

def parse_serialized_data(sanitized_data):
    """
    Parses serialized data from sanitized data.

    Args:
        sanitized_data (dict): Sanitized data.

    Returns:
        dict: Parsed data structures.
    """
    parsed_data = {}
    for file_name, content in sanitized_data.items():
        try:
            # Detect file format based on file extension
            file_extension = file_name.split('.')[-1].lower()
            if file_extension == 'json':
                data = json.loads(content)
                parsed_data[file_name] = {'data': data, 'type': 'json'}
            elif file_extension in ['yaml', 'yml']:
                data = yaml.safe_load(content)
                parsed_data[file_name] = {'data': data, 'type': 'yaml'}
            elif file_extension == 'xml':
                data = ET.fromstring(content)
                parsed_data[file_name] = {'data': data, 'type': 'xml'}
            else:
                st.warning(f"File format of {file_name} not recognized or not supported for serialization parsing.")
        except Exception as e:
            st.error(f"Error parsing file {file_name}: {str(e)}")
    return parsed_data

def perform_eda(parsed_data):
    """
    Performs Exploratory Data Analysis on parsed data.

    Args:
        parsed_data (dict): Parsed data structures.
    """
    st.header("Exploratory Data Analysis (EDA)")
    for file_name, data_info in parsed_data.items():
        st.subheader(f"EDA for {file_name}")
        data_type = data_info['type']
        data = data_info['data']
        if data_type in ['json', 'yaml']:
            # Flatten the data into a DataFrame for EDA
            df = pd.json_normalize(data)
            if not df.empty:
                # Generate EDA report using ydata-profiling
                profile = ProfileReport(df, title=f"EDA Report for {file_name}", explorative=True)
                utils.st_profile_report(profile)
            else:
                st.warning(f"No tabular data extracted from {file_name} for EDA.")
        elif data_type == 'xml':
            # Convert XML to DataFrame
            df = xml_to_dataframe(data_info['data'])
            if not df.empty:
                profile = ProfileReport(df, title=f"EDA Report for {file_name}", explorative=True)
                utils.st_profile_report(profile)
            else:
                st.warning(f"No tabular data extracted from {file_name} for EDA.")
        else:
            st.warning(f"EDA not implemented for data type {data_type}.")

def extract_schema(parsed_data):
    """
    Extracts schema from parsed data.

    Args:
        parsed_data (dict): Parsed data structures.

    Returns:
        dict: Extracted schemas.
    """
    st.header("Data Schema Extraction")
    extracted_schemas = {}
    for file_name, data_info in parsed_data.items():
        st.subheader(f"Schema Extraction for {file_name}")
        data_type = data_info['type']
        data = data_info['data']
        try:
            if data_type in ['json', 'yaml']:
                # Use genson to build JSON schema
                builder = genson.SchemaBuilder()
                builder.add_object(data)
                schema = builder.to_schema()
                # Allow user to customize the schema
                schema = ui_components.customize_json_schema(schema)
                extracted_schemas[file_name] = {'schema': schema, 'type': 'json'}
                st.write("Extracted and customized schema:")
                st.json(schema)
            elif data_type == 'xml':
                # Inform the user that automatic schema extraction is not implemented
                st.warning("Automatic XML schema extraction is not implemented. Please provide an XML schema or use an external tool.")
            else:
                st.warning(f"Schema extraction not implemented for data type {data_type}.")
        except Exception as e:
            st.error(f"Error extracting schema from {file_name}: {str(e)}")
    return extracted_schemas

def validate_schema(parsed_data, extracted_schemas):
    """
    Validates the parsed data against the extracted schema.

    Args:
        parsed_data (dict): Parsed data structures.
        extracted_schemas (dict): Extracted schemas.
    """
    st.header("Data Schema Validation")
    for file_name in parsed_data:
        if file_name in extracted_schemas:
            data_info = parsed_data[file_name]
            schema_info = extracted_schemas[file_name]
            data_type = data_info['type']
            data = data_info['data']
            schema = schema_info['schema']
            st.subheader(f"Schema Validation for {file_name}")
            try:
                if data_type == 'json':
                    jsonschema.validate(instance=data, schema=schema)
                    st.success(f"Data in {file_name} is valid against the extracted JSON schema.")
                elif data_type == 'yaml':
                    # Use the same schema as JSON
                    jsonschema.validate(instance=data, schema=schema)
                    st.success(f"Data in {file_name} is valid against the extracted schema.")
                elif data_type == 'xml':
                    # Inform the user that XML schema validation is not implemented
                    st.warning("XML schema validation is not implemented in this application.")
                else:
                    st.warning(f"Schema validation not implemented for data type {data_type}.")
            except jsonschema.exceptions.ValidationError as ve:
                st.error(f"Validation error in {file_name}: {str(ve)}")
            except Exception as e:
                st.error(f"Error during schema validation for {file_name}: {str(e)}")
        else:
            st.warning(f"No extracted schema available for {file_name}, skipping validation.")

def xml_to_dataframe(root_element):
    """
    Converts an XML ElementTree to a pandas DataFrame.

    Args:
        root_element (Element): Root element of the XML tree.

    Returns:
        DataFrame: A pandas DataFrame representing the XML data.
    """
    all_records = []
    # Iterate over child elements (records)
    for record in root_element:
        record_data = {}
        for elem in record:
            record_data[elem.tag] = elem.text
        if record_data:
            all_records.append(record_data)
    if all_records:
        df = pd.DataFrame(all_records)
        return df
    else:
        return pd.DataFrame()