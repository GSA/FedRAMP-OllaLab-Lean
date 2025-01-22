# validation.py

"""
validation.py

Module containing validation functions for user inputs and extracted data.
"""

from exceptions import ValidationError, DataValidationError
from extraction_parameters import (
    ExtractionParameters,
    TableSelectionCriteria,
    FormattingRules,
    ErrorHandlingStrategy,
    ParserConfiguration,
    ResourceLimits,
)
from typing import Dict, Any, List, Type
import re
import datetime
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def validate_user_inputs(user_inputs: Dict[str, Any]) -> None:
    """
    Validates user inputs to ensure they meet required criteria.

    Parameters:
        user_inputs (Dict[str, Any]): 
            The inputs provided by the user.

    Returns:
        None

    Raises:
        ValidationError:
            If any of the inputs are invalid.

    Upstream functions:
        - Called by `process_user_input` in `user_interface.py`.

    Dependencies:
        - None
    """
    logger.debug("Validating user inputs.")

    # Required fields
    required_fields = ['source_documents', 'table_selection', 'extraction_parameters']
    for field in required_fields:
        if field not in user_inputs:
            logger.error(f"Missing required input: {field}")
            raise ValidationError(f"Missing required input: {field}")

    # Validate source_documents
    source_documents = user_inputs.get('source_documents')
    if not isinstance(source_documents, list) or not source_documents:
        logger.error("source_documents must be a non-empty list of file paths.")
        raise ValidationError("source_documents must be a non-empty list of file paths.")
    for file_path in source_documents:
        if not isinstance(file_path, str) or not file_path.strip():
            logger.error(f"Invalid file path: {file_path}")
            raise ValidationError(f"Invalid file path: {file_path}")

        # Note: Further validation of file existence should occur elsewhere

    # Validate table_selection
    table_selection = user_inputs.get('table_selection')
    if not isinstance(table_selection, dict):
        logger.error("table_selection must be a dictionary.")
        raise ValidationError("table_selection must be a dictionary.")
    validate_table_selection_criteria(table_selection)

    # Validate extraction_parameters
    extraction_parameters = user_inputs.get('extraction_parameters')
    if not isinstance(extraction_parameters, dict):
        logger.error("extraction_parameters must be a dictionary.")
        raise ValidationError("extraction_parameters must be a dictionary.")
    validate_extraction_parameters(extraction_parameters)

def validate_table_selection_criteria(criteria: Dict[str, Any]) -> None:
    """
    Validates the table selection criteria provided by the user.

    Parameters:
        criteria (Dict[str, Any]):
            The table selection criteria provided by the user.

    Returns:
        None

    Raises:
        ValidationError:
            If any of the criteria are invalid.
    """
    logger.debug("Validating table selection criteria.")

    valid_methods = ['indexing', 'keyword', 'regex', 'criteria']
    method = criteria.get('method')
    if method not in valid_methods:
        logger.error(f"Invalid table selection method '{method}'. Valid methods are {valid_methods}")
        raise ValidationError(f"Invalid table selection method '{method}'. Valid methods are {valid_methods}")

    if method == 'indexing':
        indices = criteria.get('indices')
        if not isinstance(indices, list) or not indices:
            logger.error("Indices must be a non-empty list of integers when method is 'indexing'.")
            raise ValidationError("Indices must be a non-empty list of integers when method is 'indexing'.")
        if not all(isinstance(i, int) and i >= 0 for i in indices):
            logger.error("All indices must be non-negative integers.")
            raise ValidationError("All indices must be non-negative integers.")
    elif method == 'keyword':
        keywords = criteria.get('keywords')
        if not isinstance(keywords, list) or not keywords:
            logger.error("Keywords must be a non-empty list of strings when method is 'keyword'.")
            raise ValidationError("Keywords must be a non-empty list of strings when method is 'keyword'.")
        if not all(isinstance(k, str) for k in keywords):
            logger.error("All keywords must be strings.")
            raise ValidationError("All keywords must be strings.")
    elif method == 'regex':
        regex_patterns = criteria.get('regex_patterns')
        if not isinstance(regex_patterns, list) or not regex_patterns:
            logger.error("Regex patterns must be a non-empty list of strings when method is 'regex'.")
            raise ValidationError("Regex patterns must be a non-empty list of strings when method is 'regex'.")
        for pattern in regex_patterns:
            try:
                re.compile(pattern)
            except re.error as e:
                logger.error(f"Invalid regex pattern '{pattern}': {e}")
                raise ValidationError(f"Invalid regex pattern '{pattern}': {e}")
    elif method == 'criteria':
        row_conditions = criteria.get('row_conditions')
        column_conditions = criteria.get('column_conditions')
        if not row_conditions and not column_conditions:
            logger.error("At least one of row_conditions or column_conditions must be provided when method is 'criteria'.")
            raise ValidationError("At least one of row_conditions or column_conditions must be provided when method is 'criteria'.")
    else:
        logger.error(f"Invalid table selection method '{method}'.")
        raise ValidationError(f"Invalid table selection method '{method}'.")

def validate_extraction_parameters(params: Dict[str, Any]) -> None:
    """
    Validates the extraction parameters provided by the user.

    Parameters:
        params (Dict[str, Any]):
            The extraction parameters provided by the user.

    Returns:
        None

    Raises:
        ValidationError:
            If any of the parameters are invalid.
    """
    logger.debug("Validating extraction parameters.")

    # Validate formatting_rules
    formatting_rules = params.get('formatting_rules')
    if formatting_rules:
        if not isinstance(formatting_rules, dict):
            logger.error("formatting_rules must be a dictionary.")
            raise ValidationError("formatting_rules must be a dictionary.")
        date_format = formatting_rules.get('date_format')
        if date_format:
            try:
                datetime.datetime.now().strftime(date_format)
            except Exception as e:
                logger.error(f"Invalid date format '{date_format}': {e}")
                raise ValidationError(f"Invalid date format '{date_format}': {e}")
        number_format = formatting_rules.get('number_format')
        if number_format:
            if not isinstance(number_format, str):
                logger.error("number_format must be a string.")
                raise ValidationError("number_format must be a string.")
        encoding = formatting_rules.get('encoding')
        if encoding:
            try:
                ''.encode(encoding)
            except LookupError:
                logger.error(f"Invalid encoding '{encoding}'.")
                raise ValidationError(f"Invalid encoding '{encoding}'.")

    # Validate data_types
    data_types = params.get('data_types')
    if data_types:
        if not isinstance(data_types, dict):
            logger.error("data_types must be a dictionary.")
            raise ValidationError("data_types must be a dictionary.")
        valid_type_strings = {'int', 'float', 'str', 'bool', 'date'}
        for column, dtype in data_types.items():
            if not isinstance(column, str):
                logger.error(f"Column names in data_types must be strings, got {type(column)}")
                raise ValidationError(f"Column names in data_types must be strings, got {type(column)}")
            if not isinstance(dtype, str) or dtype not in valid_type_strings:
                logger.error(f"Invalid data type '{dtype}' for column '{column}'. Valid types are {valid_type_strings}")
                raise ValidationError(f"Invalid data type '{dtype}' for column '{column}'. Valid types are {valid_type_strings}")

    # Validate parser_config
    parser_config = params.get('parser_config')
    if parser_config:
        if not isinstance(parser_config, dict):
            logger.error("parser_config must be a dictionary.")
            raise ValidationError("parser_config must be a dictionary.")
        ocr_enabled = parser_config.get('ocr_enabled')
        if ocr_enabled is not None and not isinstance(ocr_enabled, bool):
            logger.error("ocr_enabled must be a boolean.")
            raise ValidationError("ocr_enabled must be a boolean.")
        language = parser_config.get('language')
        if language and not isinstance(language, str):
            logger.error("language must be a string.")
            raise ValidationError("language must be a string.")
        # Validate resource_limits if present
        resource_limits = parser_config.get('resource_limits')
        if resource_limits:
            if not isinstance(resource_limits, dict):
                logger.error("resource_limits must be a dictionary.")
                raise ValidationError("resource_limits must be a dictionary.")
            validate_resource_limits(resource_limits)

def validate_resource_limits(limits: Dict[str, Any]) -> None:
    """
    Validates resource limits provided in the parser configuration.

    Parameters:
        limits (Dict[str, Any]):
            The resource limits provided by the user.

    Returns:
        None

    Raises:
        ValidationError:
            If any of the resource limits are invalid.
    """
    logger.debug("Validating resource limits.")

    max_memory = limits.get('max_memory')
    if max_memory is not None:
        if not isinstance(max_memory, int) or max_memory <= 0:
            logger.error("max_memory must be a positive integer.")
            raise ValidationError("max_memory must be a positive integer.")
    max_time = limits.get('max_time')
    if max_time is not None:
        if not isinstance(max_time, int) or max_time <= 0:
            logger.error("max_time must be a positive integer.")
            raise ValidationError("max_time must be a positive integer.")
    max_cpu_usage = limits.get('max_cpu_usage')
    if max_cpu_usage is not None:
        if not isinstance(max_cpu_usage, int) or not (0 < max_cpu_usage <= 100):
            logger.error("max_cpu_usage must be an integer between 1 and 100.")
            raise ValidationError("max_cpu_usage must be an integer between 1 and 100.")

def validate_extracted_data(data: List[Dict[str, Any]], parameters: ExtractionParameters) -> None:
    """
    Validates the extracted data against the specified parameters.

    Parameters:
        data (List[Dict[str, Any]]): 
            The data extracted from the documents.
        parameters (ExtractionParameters): 
            Parameters that guide the validation process.

    Returns:
        None

    Raises:
        DataValidationError:
            If the data fails validation checks.

    Dependencies:
        - Depends on `ExtractionParameters` for validation rules.
    """
    logger.debug("Validating extracted data.")

    data_types = parameters.data_types
    for row_idx, row in enumerate(data):
        for column, expected_type in data_types.items():
            value = row.get(column)
            if value is None:
                # Handle missing values according to placeholder_for_missing
                continue  # Assuming missing values are allowed
            if not validate_value_type(value, expected_type):
                logger.error(
                    f"Invalid data type for column '{column}' in row {row_idx}. "
                    f"Expected {expected_type.__name__ if hasattr(expected_type, '__name__') else expected_type}, "
                    f"got {type(value).__name__}."
                )
                raise DataValidationError(
                    f"Invalid data type for column '{column}' in row {row_idx}. "
                    f"Expected {expected_type.__name__ if hasattr(expected_type, '__name__') else expected_type}, "
                    f"got {type(value).__name__}."
                )

def validate_value_type(value: Any, expected_type: Any) -> bool:
    """
    Validates that the value is of the expected type.

    Parameters:
        value (Any):
            The value to validate.
        expected_type (Any):
            The expected data type, can be a type or a special string like 'date'.

    Returns:
        bool:
            True if the value is of the expected type, False otherwise.
    """
    if expected_type == 'date':
        return isinstance(value, (datetime.date, datetime.datetime))
    else:
        return isinstance(value, expected_type)