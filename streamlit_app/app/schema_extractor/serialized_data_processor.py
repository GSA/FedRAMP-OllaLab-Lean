# serialized_data_processor.py

from io import BytesIO
import json
import yaml
import xml.etree.ElementTree as ET
import xmlschema
import pandas as pd
import streamlit as st
from jsonschema import validate as jsonschema_validate
from jsonschema import exceptions as jsonschema_exceptions
import genson
from genson import SchemaBuilder
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
import pickle
import msgpack
from schema_extractor.utils import detect_file_type

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
    else:
        st.error(f"Couldn't parse given data.")

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
        #try:
        if file_type == 'json':
            parsed_data[file_name] = json.loads(file_content)
        elif file_type in ['yaml', 'yml']:
            parsed_data[file_name] = yaml.safe_load(file_content)
        elif file_type == 'xml':
            # Parse XML content into ElementTree
            parsed_data[file_name] = ET.ElementTree(ET.fromstring(file_content))
        elif file_type == 'pickle':
            parsed_data[file_name] = pickle.loads(file_content)
        elif file_type == 'msgpack':
            parsed_data[file_name] = msgpack.unpackb(file_content)
        else:
            st.error(f"Unsupported file type: {file_type} for file {file_name}")
        #except Exception as e:
            #st.error(f"Error parsing file {file_name}: {e}")
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
                # For XML data, generate XSD
                xsd_schema = generate_xsd_from_xml(data,file_name)
                if xsd_schema:
                    extracted_schemas[file_name] = xsd_schema
                    st.write("Generated XML Schema (XSD):")
                    st.code(xsd_schema, language='xml')
            else:
                st.error(f"Unsupported data type for file {file_name}")
        except Exception as e:
            st.error(f"Error extracting schema for file {file_name}: {e}")
    return extracted_schemas

def generate_xsd_from_xml (xml_tree, file_name):
    """
    Generates an XML Schema (XSD) from an XML ElementTree

    **Note:** Automatically generating XSD from complex XML data is still a challenging problem and may need further improvements.

    Args:
        xml_tree (ET.ElementTree): Parsed XMl data.
        file_name (str): Name of the file being processed.

    Returns:
        str: The generated XSD as a string, or None if generation fails
    """

    root = xml_tree.getroot()
    xsd = construct_basic_xsd(root)
    return xsd

def construct_basic_xsd(root):
    """
    Construct a basic XSD schema string based on the XML root element

    Args:
        root (ET.Element): The root element of the XML.

    Returns:
        str: A basic XSD schema as a string.
    """

    xsd_template = '''<?xml version="1.0" encoding="UTF-8"?>
    <xs:schema xmlns:"http://www.w3.org/2001/XMLSchema">
        {elements}
    </xs:schema>
    '''
    elements = construct_xsd_elements(root, level=0)
    return xsd_template.format(elements=elements)

def construct_xsd_elements(element, level):
    """
    Recursively constructs XSD element definition.
    Args:
        element (ET.Element): The current XMl element.
        level (int): Current depth for indentation

    Returns:
        str: XSD elements as a string
    """
    indent = '  ' * (level+1)
    xsd = f"{indent}<xs:element name=\"{element.tag}\" type=\"{element.tag}Type\"/>\n"
    xsd += f"{indent}<xs:complexType name=\"{element.tag}Type\">\n"
    # check if the element has child elements
    children = list(element)
    if children:
        xsd += f"{indent}   <xs:sequence>\n"
        for child in children:
            xsd += construct_xsd_elements(child, level + 2)
        xsd += f"{indent}   </xs:sequnce>\n"
    else:
        # Define simple type based on text content
        if element.text and element.text.strip().isdigit():
            xsd += f"{indent}   <xs:simpleContent\n"
            xsd += f"{indent}       <xs:extension base\"xs:integer\" />\n"
            xsd += f"{indent}   <xs:simpleContent\n"
        else:
            xsd += f"{indent}   <xs:simpleContent\n"
            xsd += f"{indent}       <xs:extension base\"xs:string\" />\n"
            xsd += f"{indent}   <xs:simpleContent\n"
    xsd += f"{indent}</xs:complexType>\n"
    return xsd

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
                file_type = detect_file_type(file_name)
                if file_type == 'json':
                    jsonschema_validate(instance=data, schema=schema)
                elif file_type == 'yaml':
                    jsonschema_validate(instance=data, schema=schema)
                elif file_type == 'xml':
                    validate_xml_schema(data, schema, file_name)
                st.success(f"Data in {file_name} is **valid** against the extracted schema.")
            except jsonschema_exceptions.ValidationError as ve:
                st.error(f"Validation error in file {file_name}: {ve.message}")
            except Exception as e:
                st.error(f"Error during validation for file {file_name}: {e}")
        else:
            st.warning(f"No schema available for file {file_name}, skipping validation.")

def validate_xml_schema (xml_tree, xsd_schema_str, file_name):
    """
    Validates XML data against the provided XML Schema (XSD)

    Args:
        xml_tree (ET.ElementTree): The parsed XMl data
        xsd_schema_str (str): The XML Schema as a string
        file_name (str): Name of the file being validated
    """
    try:
        # write XSD to a temporary file-like object
        xsd_io = BytesIO(xsd_schema_str.encode('utf-8'))
        xsd = xmlschema.XMLSchema(xsd.io)

        # Validate XML tree against the schema
        valid = xsd.is_valid(xml_tree)
        if valid:
            st.success(f"XML data in {file_name} is **valid** against the generated XSD schema.")
        else:
            errors = xsd.validate(xml_tree, use_defaults=False)
            st.error(f"XML data in {file_name} is **invalid** against the generated XSD schema.")
            errors = xsd.iter_errors(xml_tree)
            for error in errors:
                st.error(f"Error: {error.message}")
    except xmlschema.XMLSchemaException as e:
        st.error(f"XML Schema validation error for file {file.name}: {e}")
    except Exception as e:
        st.error(f"Unexpected error during XML schema validation for the {file_name}: {e}")