# schema_extractor/schema_builder.py

"""
Module: schema_builder.py

This module provides functions to build data schemas from various types of data
and to validate data against these schemas.

Functions:
- build_schema(data, data_type, user_inputs=None)
- validate_data_against_schema(data, schema, data_type)
"""

import json
import pandas as pd
import jsonschema
from jsonschema import validate as json_validate
from genson import SchemaBuilder  # For JSON schema generation
import pandera as pa  # For schema inference from pandas DataFrames
from pandera import Column, Check, DataFrameSchema
import re

# For unstructured data processing, you might need NLP libraries
# Uncomment and install as needed
# import spacy

def build_schema(data, data_type, user_inputs=None):
    """
    Builds a data schema based on the provided data and type.

    Args:
        data (any): The data from which to build the schema.
        data_type (str): The type of data ('serialized', 'tabular', 'unstructured').
        user_inputs (dict, optional): Additional user inputs for schema customization.

    Returns:
        any: The constructed schema. The type depends on data_type:
            - For 'serialized': Returns a dict representing the JSON schema.
            - For 'tabular': Returns a pandera.DataFrameSchema object.
            - For 'unstructured': Returns a dict representing the schema.

    Raises:
        ValueError: If the data_type is unsupported.
    """
    if data_type == 'serialized':
        return build_schema_from_serialized_data(data, user_inputs)
    elif data_type == 'tabular':
        return build_schema_from_tabular_data(data, user_inputs)
    elif data_type == 'unstructured':
        return build_schema_from_unstructured_data(user_inputs)
    else:
        raise ValueError(f"Unsupported data type: {data_type}")

def build_schema_from_serialized_data(data, user_inputs=None):
    """
    Builds a schema from serialized data (e.g., JSON, XML).

    Args:
        data (dict): The parsed serialized data (e.g., JSON object).
        user_inputs (dict, optional): User inputs for schema customization.

    Returns:
        dict: The constructed schema.

    Notes:
        - Uses genson to generate a JSON schema from JSON data.
        - Applies user constraints if provided.
    """
    builder = SchemaBuilder()
    builder.add_object(data)
    schema = builder.to_schema()

    # Apply user constraints if any
    if user_inputs:
        schema = apply_user_constraints_to_json_schema(schema, user_inputs)

    return schema

def apply_user_constraints_to_json_schema(schema, user_inputs):
    """
    Modifies the JSON schema based on user inputs, such as constraints.

    Args:
        schema (dict): The JSON schema to modify.
        user_inputs (dict): The user inputs specifying constraints.

    Returns:
        dict: The modified schema.
    """
    # Example user_inputs:
    # {
    #   'required_fields': ['name', 'age'],
    #   'field_constraints': {
    #       'name': {'maxLength': 50},
    #       'age': {'minimum': 0, 'maximum': 100},
    #       'gender': {'enum': ['Male', 'Female', 'Other']}
    #    }
    # }

    if 'required_fields' in user_inputs:
        schema['required'] = user_inputs['required_fields']

    if 'field_constraints' in user_inputs:
        properties = schema.get('properties', {})
        for field, constraints in user_inputs['field_constraints'].items():
            if field in properties:
                properties[field].update(constraints)
            else:
                properties[field] = constraints
        schema['properties'] = properties

    return schema

def build_schema_from_tabular_data(data_frame, user_inputs=None):
    """
    Builds a schema from tabular data (pandas DataFrame).

    Args:
        data_frame (pd.DataFrame): The tabular data.
        user_inputs (dict, optional): User inputs for schema customization.

    Returns:
        pa.DataFrameSchema: The constructed schema.

    Notes:
        - Uses pandera to infer a schema from the DataFrame.
        - Applies user constraints if provided.
    """
    inferred_schema = pa.infer_schema(data_frame)

    # Apply user inputs if any
    if user_inputs:
        inferred_schema = apply_user_constraints_to_pandera_schema(inferred_schema, user_inputs)

    return inferred_schema

def apply_user_constraints_to_pandera_schema(schema, user_inputs):
    """
    Modifies the Pandera DataFrameSchema based on user inputs.

    Args:
        schema (pa.DataFrameSchema): The schema to modify.
        user_inputs (dict): The user inputs specifying constraints.

    Returns:
        pa.DataFrameSchema: The modified schema.
    """
    # Example user_inputs:
    # {
    #   'columns': {
    #       'age': {
    #           'dtype': 'int',
    #           'nullable': False,
    #           'checks': {
    #               'greater_than_or_equal_to': 0,
    #               'less_than_or_equal_to': 100
    #           }
    #       },
    #       'name': {
    #           'dtype': 'string',
    #           'nullable': False,
    #           'checks': {
    #               'str_length': {'min_value': 1, 'max_value': 50}
    #           }
    #       }
    #   }
    # }

    columns = schema.columns.copy()

    for col_name, col_constraints in user_inputs.get('columns', {}).items():
        if col_name in columns:
            column = columns[col_name]
            # Update data type if specified
            if 'dtype' in col_constraints:
                column.dtype = col_constraints['dtype']
            # Update nullable
            if 'nullable' in col_constraints:
                column.nullable = col_constraints['nullable']
            # Add checks
            if 'checks' in col_constraints:
                for check_name, check_value in col_constraints['checks'].items():
                    # Define mapping between check names and Pandera Check methods
                    if check_name == 'greater_than_or_equal_to':
                        column.checks.append(Check.ge(check_value))
                    elif check_name == 'less_than_or_equal_to':
                        column.checks.append(Check.le(check_value))
                    elif check_name == 'str_length':
                        min_value = check_value.get('min_value')
                        max_value = check_value.get('max_value')
                        column.checks.append(Check.str_length(min_value=min_value, max_value=max_value))
                    elif check_name == 'isin':
                        column.checks.append(Check.isin(check_value))
                    # Add other checks as needed
            columns[col_name] = column
        else:
            # Add new column
            checks = []
            if 'checks' in col_constraints:
                for check_name, check_value in col_constraints['checks'].items():
                    if check_name == 'greater_than_or_equal_to':
                        checks.append(Check.ge(check_value))
                    elif check_name == 'less_than_or_equal_to':
                        checks.append(Check.le(check_value))
                    elif check_name == 'str_length':
                        min_value = check_value.get('min_value')
                        max_value = check_value.get('max_value')
                        checks.append(Check.str_length(min_value=min_value, max_value=max_value))
                    elif check_name == 'isin':
                        checks.append(Check.isin(check_value))
                    # Add other checks as needed
            new_column = Column(
                dtype=col_constraints.get('dtype', 'object'),
                nullable=col_constraints.get('nullable', True),
                checks=checks
            )
            columns[col_name] = new_column

    schema = DataFrameSchema(columns=columns)
    return schema

def build_schema_from_unstructured_data(user_inputs):
    """
    Builds a schema from unstructured text data based on user inputs.

    Args:
        user_inputs (dict): User-defined schema elements.

    Returns:
        dict: The constructed schema.

    Notes:
        - Since unstructured data schema design is user-driven, we construct the schema based on user inputs.
    """
    # Expected user_inputs format:
    # {
    #     'title': 'Your Schema Title',
    #     'description': 'A description of your schema.',
    #     'type': 'object',
    #     'properties': {
    #         'field_name': {
    #             'type': 'string',
    #             'description': 'Description of the field.'
    #         },
    #         ...
    #     },
    #     'required': ['field_name', ...]
    # }
    schema = user_inputs
    return schema

def validate_data_against_schema(data, schema, data_type):
    """
    Validates data against the provided schema.

    Args:
        data (any): The data to validate.
        schema (any): The schema to validate against.
        data_type (str): The type of data ('serialized', 'tabular', 'unstructured').

    Returns:
        bool: True if data is valid, False otherwise.

    Raises:
        ValueError: If the data_type is unsupported.
    """
    if data_type == 'serialized':
        return validate_serialized_data_against_schema(data, schema)
    elif data_type == 'tabular':
        return validate_tabular_data_against_schema(data, schema)
    elif data_type == 'unstructured':
        return validate_unstructured_data_against_schema(data, schema)
    else:
        raise ValueError(f"Unsupported data type: {data_type}")

def validate_serialized_data_against_schema(data, schema):
    """
    Validates serialized data (e.g., JSON) against the schema.

    Args:
        data (dict): The data to validate.
        schema (dict): The JSON schema.

    Returns:
        bool: True if data is valid, False otherwise.
    """
    try:
        json_validate(instance=data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        # Handle validation error, log or re-raise as needed
        print(f"Validation error: {e.message}")
        return False

def validate_tabular_data_against_schema(data_frame, schema):
    """
    Validates tabular data (DataFrame) against the schema.

    Args:
        data_frame (pd.DataFrame): The data to validate.
        schema (pa.DataFrameSchema): The schema.

    Returns:
        bool: True if data is valid, False otherwise.
    """
    try:
        schema.validate(data_frame)
        return True
    except pa.errors.SchemaErrors as e:
        # Handle validation errors, log or re-raise as needed
        print(f"Validation errors:\n{e.failure_cases}")
        return False

def validate_unstructured_data_against_schema(text_data, schema):
    """
    Validates unstructured data against the schema.

    Args:
        text_data (str): The unstructured text data.
        schema (dict): The schema designed to extract data.

    Returns:
        bool: True if data can be successfully extracted using the schema, False otherwise.
    """
    # For unstructured data, we need to attempt to extract data using the schema
    # This might involve parsing the text and checking if we can extract the required fields

    # Placeholder implementation using regex (for illustration purposes)
    extracted_data = extract_data_from_text(text_data, schema)

    if extracted_data:
        return True
    else:
        return False

def extract_data_from_text(text_data, schema):
    """
    Extracts structured data from unstructured text using the provided schema.

    Args:
        text_data (str): The text data.
        schema (dict): The schema defining what to extract.

    Returns:
        dict: Extracted data if successful, None otherwise.
    """
    # Implement extraction logic based on schema
    # Placeholder example using regex

    extracted_data = {}
    for field, details in schema.get('properties', {}).items():
        field_type = details.get('type', 'string')
        # Define simple regex patterns for example purposes
        if field_type == 'string':
            pattern = details.get('pattern', fr'(?P<{field}>.+)')
        elif field_type == 'number':
            pattern = fr'(?P<{field}>\d+(\.\d+)?)'
        else:
            pattern = fr'(?P<{field}>.+)'

        match = re.search(pattern, text_data)
        if match:
            extracted_data[field] = match.group(field)
        else:
            # If required fields are missing, return None
            if field in schema.get('required', []):
                return None

    return extracted_data