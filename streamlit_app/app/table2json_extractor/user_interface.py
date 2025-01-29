# user_interface.py

"""
user_interface.py

Module containing functions that process user inputs and orchestrate the extraction and rendering of tables from documents.

Includes functions for:
- Processing user inputs from the web or command-line interface.
- Orchestrating the document processing based on user parameters.
- Rendering the extracted data in the desired format.

"""

import datetime
import logging
from typing import Dict, Any, List, Tuple
import pandas as pd

from .exceptions import (
    InvalidUserInputError,
    ProcessingError,
    RenderingError,
    ValidationError,
    DataValidationError
)
from .extraction_parameters import (
    ExtractionParameters,
    TableSelectionCriteria,
    FormattingRules,
    ErrorHandlingStrategy,
    ParserConfiguration,
    ResourceLimits,
    StructureInterpretationRules
)
from .validation import validate_user_inputs, validate_extracted_data
from .data_processing import parse_documents, Table, Cell, ParsedDocument
from .structure_interpretation import interpret_table_structure
import json
import re

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def process_user_input(user_inputs: Dict[str, Any]) -> Tuple[List[str], ExtractionParameters]:
    """
    Processes user inputs from the web or command-line interface.

    Parameters:
        user_inputs (Dict[str, Any]):
            A dictionary containing inputs provided by the user.

    Returns:
        Tuple[List[str], ExtractionParameters]:
            A tuple containing the list of source documents and an object containing validated extraction parameters.

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

        # Extract source documents
        source_documents = user_inputs.get('source_documents', [])
        logger.debug(f"Source documents: {source_documents}")

        # Extract parameters from user_inputs
        table_selection_input = user_inputs.get('table_selection', {})
        pages = table_selection_input.get('pages') # get the pages where the tables will be extracted
        table_selection = TableSelectionCriteria(
            method=table_selection_input.get('method'),
            indices=table_selection_input.get('indices'),
            keywords=table_selection_input.get('keywords'),
            regex_patterns=table_selection_input.get('regex_patterns'),
            row_conditions=table_selection_input.get('row_conditions'),
            column_conditions=table_selection_input.get('column_conditions'),
            saved_profile=table_selection_input.get('saved_profile'),
            pages=pages
        )

        # Extract extraction parameters
        extraction_parameters_input = user_inputs.get('extraction_parameters', {})

        # Extract StructureInterpretationRules
        structure_interpretation_input = extraction_parameters_input.get('structure_interpretation', {})
        structure_interpretation = StructureInterpretationRules(
            handle_merged_cells=structure_interpretation_input.get('handle_merged_cells', True),
            handle_nested_tables=structure_interpretation_input.get('handle_nested_tables', True),
            handle_irregular_structures=structure_interpretation_input.get('handle_irregular_structures', True)
        )

        # Extract FormattingRules
        formatting_rules_input = extraction_parameters_input.get('formatting_rules', {})
        formatting_rules = FormattingRules(
            preserve_styles=formatting_rules_input.get('preserve_styles', False),
            date_format=formatting_rules_input.get('date_format', "%Y-%m-%d"),
            number_format=formatting_rules_input.get('number_format', None),
            encoding=formatting_rules_input.get('encoding', 'utf-8'),
            placeholder_for_missing=formatting_rules_input.get('placeholder_for_missing', None),
            header_rows=formatting_rules_input.get('header_rows', 0)
        )

        # Convert data type strings to actual Python types
        data_types_input = extraction_parameters_input.get('data_types', {})
        valid_types_map = {'int': int, 'float': float, 'str': str, 'bool': bool, 'date': datetime.datetime}
        data_types = {}
        for column, type_str in data_types_input.items():
            if type_str in valid_types_map:
                data_types[column] = valid_types_map[type_str]
            else:
                raise InvalidUserInputError(f"Invalid data type '{type_str}' for column '{column}'.")

        # Extract ErrorHandlingStrategy
        error_handling_input = extraction_parameters_input.get('error_handling', {})
        error_handling = ErrorHandlingStrategy(
            on_parsing_error=error_handling_input.get('on_parsing_error', 'log'),
            on_validation_error=error_handling_input.get('on_validation_error', 'omit'),
            fallback_mechanisms=error_handling_input.get('fallback_mechanisms', [])
        )

        # Extract ParserConfiguration
        resource_limits_input = extraction_parameters_input.get('parser_config', {}).get('resource_limits', {})
        resource_limits = ResourceLimits(
            max_memory=resource_limits_input.get('max_memory'),
            max_time=resource_limits_input.get('max_time'),
            max_cpu_usage=resource_limits_input.get('max_cpu_usage')
        )

        parser_config_input = extraction_parameters_input.get('parser_config', {})
        parser_config = ParserConfiguration(
            ocr_enabled=parser_config_input.get('ocr_enabled', False),
            language=parser_config_input.get('language', 'en'),
            resource_limits=resource_limits
        )

        # Create ExtractionParameters instance
        extraction_parameters = ExtractionParameters(
            table_selection=table_selection,
            formatting_rules=formatting_rules,
            data_types=data_types,
            error_handling=error_handling,
            parser_config=parser_config,
            structure_interpretation=structure_interpretation
        )

        # Validate extraction parameters
        extraction_parameters.validate_parameters()

        logger.info("Extraction parameters have been successfully created and validated.")

        return source_documents, extraction_parameters

    except ValidationError as e:
        logger.error(f"User inputs failed validation: {e}")
        raise InvalidUserInputError(f"User inputs failed validation: {e}")
    except Exception as e:
        logger.exception(f"An error occurred while processing user input: {e}")
        raise InvalidUserInputError(f"An error occurred while processing user input: {e}")


def process_documents(
    file_paths: List[str],
    parameters: ExtractionParameters,
    selected_tables: List[int],
    documents: List[ParsedDocument],
    extracted_tables: List[Table],
    document_table_mapping: List[Tuple[int, Table]]
) -> List[Dict]:
    """
    Orchestrates the processing of selected tables from documents based on user parameters.

    Parameters:
        file_paths (List[str]):
            List of file paths to the documents (provided for compatibility).
        parameters (ExtractionParameters):
            Parameters guiding the extraction process.
        selected_tables (List[int]):
            Indices of the tables selected by the user.
        documents (List[ParsedDocument]):
            Parsed documents.
        extracted_tables (List[Table]):
            List of all extracted tables.
        document_table_mapping (List[Tuple[int, Table]]):
            Mapping of document indices to tables.

    Returns:
        List[Dict]:
            A list of dictionaries representing the extracted data in JSON format.

    Raises:
        ProcessingError:
            If an error occurs during document processing.
    """
    try:
        extracted_data = []
        for idx in selected_tables:
            doc_idx, table = document_table_mapping[idx]
            logger.info(f"Processing Table {idx+1} from Document {os.path.basename(documents[doc_idx].file_path)}")
            if doc_idx is not None:
                document_name = os.path.basename(documents[doc_idx].file_path)
                logger.info(f"Processing Table {idx+1} from Document {document_name}")
            else:
                document_name = "Appended Tables"
                logger.info(f"Processing Table {idx+1} from {document_name}")
            # Interpret the table structure
            interpreted_table = interpret_table_structure(table, parameters)

            # Convert the table to a JSON-friendly format
            table_data = table_to_dict(interpreted_table, parameters)

            # Validate the extracted data
            try:
                validate_extracted_data(table_data['data'], parameters)
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
                    table_data = correct_data(table_data, parameters)
                elif action == 'prompt':
                    # Implement prompt logic (not applicable in backend code)
                    logger.warning("Prompt action not supported in this context.")
                    pass
            else:
                # If validation passes, proceed
                extracted_data.append(table_data)

        logger.info("Table processing completed successfully.")

        return extracted_data

    except Exception as e:
        logger.exception(f"An error occurred during table processing: {e}")
        raise ProcessingError(f"An error occurred during table processing: {e}")


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
            rendered_output = json.dumps(data, indent=4, default=str)
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


def select_table_by_criteria(table: Table, selection_criteria: TableSelectionCriteria) -> bool:
    """
    Determines if a table should be selected based on the given selection criteria.
    """
    if selection_criteria.pages:
        page_number = table.metadata.get('page_number')
        if page_number and page_number not in selection_criteria.pages:
            return False
    if selection_criteria.method == 'keyword':
        return table_contains_keywords(table, selection_criteria.keywords)
    elif selection_criteria.method == 'regex':
        return table_matches_regex(table, selection_criteria.regex_patterns)
    elif selection_criteria.method == 'criteria':
        return table_matches_conditions(table, selection_criteria.row_conditions, selection_criteria.column_conditions)
    else:
        # Other methods handled separately (e.g., indexing)
        return False


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
            Conditions based on the data within rows.
        column_conditions (Dict[str, Any]):
            Conditions based on the data within columns.

    Returns:
        bool:
            True if the table meets the conditions, False otherwise.
    """
    logger.debug("Evaluating table against row and column conditions.")
    if row_conditions:
        # Evaluate row count conditions
        if 'min_rows' in row_conditions:
            min_rows = row_conditions['min_rows']
            if len(table.data) < min_rows:
                return False
        if 'max_rows' in row_conditions:
            max_rows = row_conditions['max_rows']
            if len(table.data) > max_rows:
                return False
        # Evaluate content conditions
        if 'contains_value' in row_conditions:
            value = row_conditions['contains_value']
            found = any(value in str(cell.content) for row in table.data for cell in row)
            if not found:
                return False
        if 'contains_regex' in row_conditions:
            pattern = row_conditions['contains_regex']
            regex = re.compile(pattern)
            found = any(regex.search(str(cell.content)) for row in table.data for cell in row)
            if not found:
                return False

    if column_conditions:
        # Evaluate column count conditions
        max_columns = max(len(row) for row in table.data)
        if 'min_columns' in column_conditions:
            min_columns = column_conditions['min_columns']
            if max_columns < min_columns:
                return False
        if 'max_columns' in column_conditions:
            max_columns_condition = column_conditions['max_columns']
            if max_columns > max_columns_condition:
                return False
        # Evaluate content conditions
        if 'contains_value' in column_conditions:
            value = column_conditions['contains_value']
            found = any(value in str(cell.content) for row in table.data for cell in row)
            if not found:
                return False
        if 'contains_regex' in column_conditions:
            pattern = column_conditions['contains_regex']
            regex = re.compile(pattern)
            found = any(regex.search(str(cell.content)) for row in table.data for cell in row)
            if not found:
                return False

    return True  # Return True if all conditions are met


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
    header_rows = parameters.formatting_rules.header_rows

    # Extract header names if header_rows > 0
    headers = []
    if header_rows > 0:
        for h_idx in range(header_rows):
            if h_idx >= len(table.data):
                logger.warning(f"Header row index {h_idx} is out of range.")
                continue
            row = table.data[h_idx]
            headers.append([str(cell.content) for cell in row])
        column_names = merge_headers(headers)
    else:
        # If no headers are specified, use default column names
        max_cols = max(len(row) for row in table.data)
        column_names = [f"Column_{i+1}" for i in range(max_cols)]

    for row_idx in range(header_rows, len(table.data)):
        row_data = {}
        row = table.data[row_idx]
        for col_idx, cell in enumerate(row):
            cell_content = cell.content
            # Apply data types if specified
            column_name = column_names[col_idx] if col_idx < len(column_names) else f"Column_{col_idx+1}"
            if parameters.data_types and column_name in parameters.data_types:
                expected_type = parameters.data_types[column_name]
                try:
                    if expected_type == datetime.datetime:
                        # Handle date conversion
                        date_format = parameters.formatting_rules.date_format
                        cell_content = datetime.datetime.strptime(cell_content, date_format)
                    else:
                        cell_content = expected_type(cell_content)
                except ValueError:
                    logger.warning(f"Failed to convert cell content '{cell_content}' to {expected_type}")
                    # Optionally assign placeholder or continue based on error handling strategy

            if parameters.formatting_rules.placeholder_for_missing is not None and (cell_content is None or cell_content == ''):
                cell_content = parameters.formatting_rules.placeholder_for_missing

            row_data[column_name] = cell_content

        data.append(row_data)

    table_dict['data'] = data
    table_dict['metadata'] = table.metadata
    return table_dict


def merge_headers(headers: List[List[str]]) -> List[str]:
    column_names = []
    max_length = max(len(h) for h in headers)
    for col_idx in range(max_length):
        col_name_parts = []
        for header_row in headers:
            if col_idx < len(header_row):
                col_name_parts.append(str(header_row[col_idx]).strip())
            else:
                col_name_parts.append("")
        col_name = ' '.join(part for part in col_name_parts if part)
        if not col_name:
            col_name = f"Column_{col_idx+1}"
        column_names.append(col_name)
    return column_names


def correct_data(data: Dict, parameters: ExtractionParameters) -> Dict:
    """
    Attempts to correct invalid data by coercing values to the expected types where possible.

    Parameters:
        data (Dict):
            The data to be corrected.
        parameters (ExtractionParameters):
            The extraction parameters containing type information.

    Returns:
        Dict:
            The corrected data.

    Notes:
        This function assumes that data is a dictionary with a 'data' key containing a list of dictionaries (rows).
    """
    corrected_data = []
    data_types = parameters.data_types
    for row in data['data']:
        corrected_row = {}
        for column, value in row.items():
            expected_type = data_types.get(column)
            if expected_type:
                try:
                    if expected_type == datetime.datetime:
                        # Try to parse the date with the specified format
                        date_format = parameters.formatting_rules.date_format
                        if isinstance(value, str):
                            corrected_value = datetime.datetime.strptime(value, date_format)
                        else:
                            corrected_value = value  # Assume it's already datetime
                    else:
                        corrected_value = expected_type(value)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert value '{value}' to type {expected_type}. Using placeholder.")
                    placeholder = parameters.formatting_rules.placeholder_for_missing or None
                    corrected_value = placeholder
            else:
                corrected_value = value
            corrected_row[column] = corrected_value
        corrected_data.append(corrected_row)
    data['data'] = corrected_data
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


def process_user_input_preview(user_inputs: Dict[str, Any]) -> ExtractionParameters:
    """
    Processes user inputs for the preview phase.

    Parameters:
        user_inputs (Dict[str, Any]):
            A dictionary containing inputs provided by the user.

    Returns:
        ExtractionParameters:
            An object containing validated extraction parameters for preview.

    Raises:
        InvalidUserInputError:
            If the user inputs fail validation checks.

    """
    # Similar to process_user_input but with minimal parameters required for preview
    try:
        # Retrieve the method, defaulting to 'indexing' if not provided
        method = user_inputs.get('table_selection', {}).get('method') or 'append tables'

        # Validate and create TableSelectionCriteria
        table_selection = TableSelectionCriteria(
            method=method.lower(),  # Ensure it's lowercase to match valid methods
            indices=user_inputs.get('table_selection', {}).get('indices'),
            keywords=user_inputs.get('table_selection', {}).get('keywords'),
            regex_patterns=user_inputs.get('table_selection', {}).get('regex_patterns'),
            row_conditions=user_inputs.get('table_selection', {}).get('row_conditions'),
            column_conditions=user_inputs.get('table_selection', {}).get('column_conditions'),
            saved_profile=user_inputs.get('table_selection', {}).get('saved_profile')
        )
        table_selection.validate()

        # Create minimal ExtractionParameters
        extraction_parameters = ExtractionParameters(
            table_selection=table_selection,
            formatting_rules=FormattingRules(),
            data_types={},
            error_handling=ErrorHandlingStrategy(),
            parser_config=ParserConfiguration(),
            structure_interpretation=StructureInterpretationRules()
        )

        return extraction_parameters
    except ValidationError as e:
        logger.error(f"User inputs failed validation: {e}")
        raise InvalidUserInputError(f"User inputs failed validation: {e}")
    except Exception as e:
        logger.exception(f"An error occurred while processing user input: {e}")
        raise InvalidUserInputError(f"An error occurred while processing user input: {e}")


def table_to_dataframe(table: Table) -> pd.DataFrame:
    """
    Converts a Table object into a Pandas DataFrame for preview.

    Parameters:
        table (Table):
            The Table object to convert.

    Returns:
        pd.DataFrame:
            The DataFrame representation of the table.
    """
    data = []
    for row in table.data:
        row_data = [cell.content for cell in row]
        data.append(row_data)
    df = pd.DataFrame(data)
    return df