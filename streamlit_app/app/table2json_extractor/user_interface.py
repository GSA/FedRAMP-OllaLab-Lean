# user_interface.py

"""
user_interface.py

Module containing functions that process user inputs and orchestrate the extraction and rendering of tables from documents.

Includes functions for:
- Processing user inputs from the web or command-line interface.
- Orchestrating the document processing based on user parameters.
- Rendering the extracted data in the desired format.

"""

import logging
from typing import Dict, Any, List

from exceptions import InvalidUserInputError, ProcessingError, RenderingError, ValidationError, DataValidationError
from extraction_parameters import (
    ExtractionParameters,
    TableSelectionCriteria,
    FormattingRules,
    ErrorHandlingStrategy,
    ParserConfiguration,
    ResourceLimits
)
from validation import validate_user_inputs, validate_extracted_data
from data_processing import parse_documents, Table, Cell, Document
from structure_interpretation import interpret_table_structure
import json
import re

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def process_user_input(user_inputs: Dict[str, Any]) -> ExtractionParameters:
    """
    Processes user inputs from the web or command-line interface.

    Parameters:
        user_inputs (Dict[str, Any]): 
            A dictionary containing inputs provided by the user.

    Returns:
        ExtractionParameters:
            An object containing validated extraction parameters.

    Raises:
        InvalidUserInputError:
            If the user inputs fail validation checks.

    Dependencies:
        - Requires the `validation` module for input validation.
    """
    try:
        # Validate user inputs
        validate_user_inputs(user_inputs)
        logger.info("User inputs passed validation.")

        # Extract parameters from user_inputs
        table_selection = TableSelectionCriteria(
            method=user_inputs.get('table_selection', {}).get('selection_method'),
            indices=user_inputs.get('table_selection', {}).get('indices'),
            keywords=user_inputs.get('table_selection', {}).get('keywords'),
            regex_patterns=user_inputs.get('table_selection', {}).get('regex_patterns'),
            row_conditions=user_inputs.get('table_selection', {}).get('row_conditions'),
            column_conditions=user_inputs.get('table_selection', {}).get('column_conditions')
        )

        # Extract FormattingRules
        formatting_rules = FormattingRules(
            preserve_styles=user_inputs.get('preserve_styles', False),
            date_format=user_inputs.get('date_format', "%Y-%m-%d"),
            number_format=user_inputs.get('number_format', None),
            encoding=user_inputs.get('encoding', 'utf-8'),
            placeholder_for_missing=user_inputs.get('placeholder_for_missing', None)
        )

        # Convert data type strings to actual Python types
        data_types_input = user_inputs.get('data_types', {})
        valid_types_map = {'int': int, 'float': float, 'str': str, 'bool': bool, 'date': 'date'}
        data_types = {}
        for column, type_str in data_types_input.items():
            if type_str in valid_types_map:
                data_types[column] = valid_types_map[type_str]
            else:
                raise InvalidUserInputError(f"Invalid data type '{type_str}' for column '{column}'.")

        # Extract ErrorHandlingStrategy
        error_handling = ErrorHandlingStrategy(
            on_parsing_error=user_inputs.get('on_parsing_error', 'log'),
            on_validation_error=user_inputs.get('on_validation_error', 'omit'),
            fallback_mechanisms=user_inputs.get('fallback_mechanisms', [])
        )

        # Extract ParserConfiguration
        resource_limits = ResourceLimits(
            max_memory=user_inputs.get('max_memory'),
            max_time=user_inputs.get('max_time'),
            max_cpu_usage=user_inputs.get('max_cpu_usage')
        )

        parser_config = ParserConfiguration(
            ocr_enabled=user_inputs.get('ocr_enabled', False),
            language=user_inputs.get('language', 'en'),
            resource_limits=resource_limits
        )

        # Create ExtractionParameters instance
        extraction_parameters = ExtractionParameters(
            table_selection=table_selection,
            formatting_rules=formatting_rules,
            data_types=data_types,
            error_handling=error_handling,
            parser_config=parser_config
        )

        # Validate extraction parameters
        extraction_parameters.validate_parameters()

        logger.info("Extraction parameters have been successfully created and validated.")

        return extraction_parameters

    except ValidationError as e:
        logger.error(f"User inputs failed validation: {e}")
        raise InvalidUserInputError(f"User inputs failed validation: {e}")
    except Exception as e:
        logger.exception(f"An error occurred while processing user input: {e}")
        raise InvalidUserInputError(f"An error occurred while processing user input: {e}")

def process_documents(file_paths: List[str], parameters: ExtractionParameters) -> List[Dict]:
    """
    Orchestrates the processing of documents based on user parameters.

    Parameters:
        file_paths (List[str]): 
            List of file paths to the documents to be processed.
        parameters (ExtractionParameters): 
            Parameters guiding the extraction process.

    Returns:
        List[Dict]:
            A list of dictionaries representing the extracted data in JSON format.

    Raises:
        ProcessingError:
            If an error occurs during document processing.

    Dependencies:
        - Depends on several modules for parsing, interpreting, and validating data.
    """
    try:
        # Parse the documents to extract raw tables
        documents = parse_documents(file_paths)
        logger.info(f"Parsed {len(documents)} documents.")

        extracted_data = []

        for document in documents:
            logger.info(f"Processing document: {document.file_path}")

            # Filter tables based on selection criteria in parameters.table_selection
            selected_tables = select_tables(document.tables, parameters.table_selection)

            logger.info(f"Selected {len(selected_tables)} tables from document.")

            for table in selected_tables:
                # Interpret the table structure
                interpreted_table = interpret_table_structure(table, parameters)

                # Convert the table to a JSON-friendly format
                table_data = table_to_dict(interpreted_table, parameters)

                # Validate the extracted data
                try:
                    validate_extracted_data(table_data, parameters)
                except DataValidationError as e:
                    # Handle invalid data as per error_handling rules
                    action = parameters.error_handling.on_validation_error
                    if action == 'omit':
                        logger.warning(f"Omitting invalid data for table due to validation error: {e}")
                        continue
                    elif action == 'abort':
                        logger.error(f"Aborting processing due to validation error: {e}")
                        raise ProcessingError(f"Aborting processing due to validation error: {e}")
                    elif action == 'correct':
                        # Implement error correction logic if applicable
                        logger.info("Attempting to correct invalid data.")
                        table_data = correct_data(table_data)
                    elif action == 'prompt':
                        # Implement prompt logic (not applicable in backend code)
                        logger.warning("Prompt action not supported in this context.")
                        pass
                else:
                    # If validation passes, proceed
                    extracted_data.append(table_data)

        logger.info("Document processing completed successfully.")

        return extracted_data

    except Exception as e:
        logger.exception(f"An error occurred during document processing: {e}")
        raise ProcessingError(f"An error occurred during document processing: {e}")

def render_results(data: List[Dict], output_format: str) -> str:
    """
    Renders the extracted data in the desired output format (e.g., JSON, Markdown).

    Parameters:
        data (List[Dict]): 
            The data extracted from the documents.
        output_format (str): 
            The format in which to render the results ('json', 'markdown').

    Returns:
        str:
            The rendered data as a string in the specified format.

    Raises:
        RenderingError:
            If an error occurs during data rendering.

    Dependencies:
        - May use json library for JSON output.
        - May use markdown library or custom code for Markdown output.
    """
    try:
        if output_format.lower() == 'json':
            rendered_output = json.dumps(data, indent=4)
        elif output_format.lower() == 'markdown':
            rendered_output = convert_to_markdown(data)
        else:
            logger.error(f"Unsupported output format: {output_format}")
            raise RenderingError(f"Unsupported output format: {output_format}")

        logger.info(f"Data rendered successfully in {output_format} format.")
        return rendered_output

    except Exception as e:
        logger.exception(f"An error occurred during data rendering: {e}")
        raise RenderingError(f"An error occurred during data rendering: {e}")

def select_tables(tables: List[Table], selection_criteria: TableSelectionCriteria) -> List[Table]:
    """
    Selects tables from the list based on the provided selection criteria.

    Parameters:
        tables (List[Table]): 
            List of Table objects extracted from the document.
        selection_criteria (TableSelectionCriteria): 
            Criteria for selecting which tables to extract.

    Returns:
        List[Table]:
            List of tables that match the selection criteria.
    """
    selected_tables = []
    logger.debug(f"Selecting tables using method: {selection_criteria.method}")

    if selection_criteria.method == 'indexing':
        indices = selection_criteria.indices or []
        for index in indices:
            if index < 0 or index >= len(tables):
                logger.warning(f"Table index {index} is out of range.")
                continue
            selected_tables.append(tables[index])
    elif selection_criteria.method == 'keyword':
        keywords = selection_criteria.keywords or []
        for table in tables:
            if table_contains_keywords(table, keywords):
                selected_tables.append(table)
    elif selection_criteria.method == 'regex':
        patterns = selection_criteria.regex_patterns or []
        for table in tables:
            if table_matches_regex(table, patterns):
                selected_tables.append(table)
    elif selection_criteria.method == 'criteria':
        for table in tables:
            if table_matches_conditions(table, selection_criteria.row_conditions, selection_criteria.column_conditions):
                selected_tables.append(table)
    else:
        logger.warning(f"Unknown selection method: {selection_criteria.method}")

    return selected_tables

def table_contains_keywords(table: Table, keywords: List[str]) -> bool:
    """
    Checks if the table contains any of the specified keywords.

    Parameters:
        table (Table):
            The table to check.
        keywords (List[str]):
            List of keywords to look for.

    Returns:
        bool:
            True if any keyword is found in the table, False otherwise.
    """
    for row in table.data:
        for cell in row:
            if any(keyword.lower() in str(cell.content).lower() for keyword in keywords):
                return True
    return False

def table_matches_regex(table: Table, patterns: List[str]) -> bool:
    """
    Checks if the table content matches any of the specified regex patterns.

    Parameters:
        table (Table):
            The table to check.
        patterns (List[str]):
            List of regex patterns.

    Returns:
        bool:
            True if any pattern matches, False otherwise.
    """
    for pattern in patterns:
        regex = re.compile(pattern)
        for row in table.data:
            for cell in row:
                if regex.search(str(cell.content)):
                    return True
    return False

def table_matches_conditions(table: Table, row_conditions: Dict[str, Any], column_conditions: Dict[str, Any]) -> bool:
    """
    Checks if the table meets the specified row and column conditions.

    Parameters:
        table (Table):
            The table to check.
        row_conditions (Dict[str, Any]):
            Conditions based on row data.
        column_conditions (Dict[str, Any]):
            Conditions based on column data.

    Returns:
        bool:
            True if the table meets the conditions, False otherwise.
    """
    # Placeholder implementation
    # Actual implementation should evaluate the conditions specified
    return True  # For demonstration purposes

def table_to_dict(table: Table, parameters: ExtractionParameters) -> Dict:
    """
    Converts a Table object into a dictionary representation.

    Parameters:
        table (Table):
            The Table object to convert.
        parameters (ExtractionParameters):
            Parameters guiding the extraction process.

    Returns:
        Dict:
            A dictionary representing the table data.
    """
    table_dict = {}
    data = []

    # Identify header rows if specified
    header_rows = parameters.formatting_rules.header_rows if hasattr(parameters.formatting_rules, 'header_rows') else 0

    for row_idx, row in enumerate(table.data):
        row_data = {}
        for col_idx, cell in enumerate(row):
            cell_content = cell.content
            # Apply data types if specified
            column_name = f"Column_{col_idx+1}"
            if parameters.data_types and column_name in parameters.data_types:
                expected_type = parameters.data_types[column_name]
                try:
                    if expected_type == 'date':
                        # Handle date conversion if necessary
                        pass  # Placeholder for date parsing
                    else:
                        cell_content = expected_type(cell_content)
                except ValueError:
                    logger.warning(f"Failed to convert cell content '{cell_content}' to {expected_type}")

            if parameters.formatting_rules.placeholder_for_missing is not None and (cell_content is None or cell_content == ''):
                cell_content = parameters.formatting_rules.placeholder_for_missing

            row_data[column_name] = cell_content

        data.append(row_data)

    table_dict['data'] = data
    table_dict['metadata'] = table.metadata
    return table_dict

def correct_data(data: Dict) -> Dict:
    """
    Attempts to correct invalid data.

    Parameters:
        data (Dict):
            The data to be corrected.

    Returns:
        Dict:
            The corrected data.
    """
    # Implement error correction logic as needed
    # Placeholder implementation
    return data

def convert_to_markdown(data: List[Dict]) -> str:
    """
    Converts the extracted data into Markdown formatted tables.

    Parameters:
        data (List[Dict]):
            The data extracted from the documents.

    Returns:
        str:
            A string containing the data formatted as Markdown tables.
    """
    markdown_output = ''
    for idx, table in enumerate(data):
        markdown_table = ''
        table_data = table.get('data', [])
        if not table_data:
            continue  # Skip empty tables

        # Generate the header
        headers = list(table_data[0].keys())
        header_line = '| ' + ' | '.join(headers) + ' |'
        separator_line = '| ' + ' | '.join('---' for _ in headers) + ' |'

        markdown_table += header_line + '\n' + separator_line + '\n'

        # Generate the body
        for row in table_data:
            row_line = '| ' + ' | '.join(str(row.get(header, '')) for header in headers) + ' |'
            markdown_table += row_line + '\n'

        markdown_output += markdown_table + '\n\n'

    return markdown_output