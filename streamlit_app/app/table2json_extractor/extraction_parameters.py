# extraction_parameters.py

"""
extraction_parameters.py

Module defining the parameters and criteria for extracting tables from documents.
"""

from typing import List, Dict, Any, Callable, Type, Optional
import re
import datetime
from .exceptions import InvalidParameterError

class StructureInterpretationRules:
    def __init__(
        self,
        handle_merged_cells: bool = True,
        handle_nested_tables: bool = True,
        handle_irregular_structures: bool = True
    ):
        self.handle_merged_cells = handle_merged_cells
        self.handle_nested_tables = handle_nested_tables
        self.handle_irregular_structures = handle_irregular_structures

    def validate(self):
        if not isinstance(self.handle_merged_cells, bool):
            raise InvalidParameterError("handle_merged_cells must be a boolean.")
        if not isinstance(self.handle_nested_tables, bool):
            raise InvalidParameterError("handle_nested_tables must be a boolean.")
        if not isinstance(self.handle_irregular_structures, bool):
            raise InvalidParameterError("handle_irregular_structures must be a boolean.")

class ExtractionParameters:
    """
    Defines the parameters and criteria for extracting tables from documents.

    Attributes:
        table_selection (TableSelectionCriteria): 
            Criteria for selecting which tables to extract.
        formatting_rules (FormattingRules): 
            Rules for formatting the extracted data.
        data_types (Dict[str, Type]): 
            Expected data types for table columns.
        error_handling (ErrorHandlingStrategy): 
            Strategy for handling errors during extraction.
        parser_config (ParserConfiguration): 
            Configurations for the parsing engine.

    Methods:
        validate_parameters()
    """

    def __init__(
        self, 
        table_selection: 'TableSelectionCriteria', 
        formatting_rules: 'FormattingRules', 
        data_types: Dict[str, Type], 
        error_handling: 'ErrorHandlingStrategy', 
        parser_config: 'ParserConfiguration',
        structure_interpretation: 'StructureInterpretationRules'
    ):
        """
        Initializes the ExtractionParameters object.

        Parameters:
            table_selection (TableSelectionCriteria): 
                Criteria for selecting which tables to extract.
            formatting_rules (FormattingRules): 
                Rules for formatting the extracted data.
            data_types (Dict[str, Type]): 
                Expected data types for table columns.
            error_handling (ErrorHandlingStrategy): 
                Strategy for handling errors during extraction.
            parser_config (ParserConfiguration): 
                Configurations for the parsing engine.
        """
        self.table_selection = table_selection
        self.formatting_rules = formatting_rules
        self.data_types = data_types
        self.error_handling = error_handling
        self.parser_config = parser_config
        self.structure_interpretation = structure_interpretation

        self.validate_parameters()

    def validate_parameters(self):
        """
        Validates the extraction parameters to ensure they are correctly specified.

        Raises:
            InvalidParameterError:
                If any of the parameters are invalid.
        """
        self.table_selection.validate()
        self.formatting_rules.validate()
        self._validate_data_types()
        self.error_handling.validate()
        self.parser_config.validate()
        self.structure_interpretation.validate()

    def _validate_data_types(self):
        """
        Validates the data_types dictionary.

        Raises:
            InvalidParameterError:
                If data_types is invalid.
        """
        if not isinstance(self.data_types, dict):
            raise InvalidParameterError("Data types must be provided as a dictionary.")

        for column, dtype in self.data_types.items():
            if not isinstance(column, str):
                raise InvalidParameterError(f"Column names must be strings. Invalid column: {column}")
            if not isinstance(dtype, type):
                raise InvalidParameterError(f"Data type for column '{column}' must be a type, got {type(dtype)} ({dtype})")


# extraction_parameters.py

class TableSelectionCriteria:
    VALID_METHODS = ['append tables', 'indexing', 'keyword', 'regex', 'criteria', 'saved_profile']

    def __init__(
        self, 
        method: str,
        indices: Optional[List[int]] = None,
        keywords: Optional[List[str]] = None,
        regex_patterns: Optional[List[str]] = None,
        row_conditions: Optional[Dict[str, Any]] = None,
        column_conditions: Optional[Dict[str, Any]] = None,
        saved_profile: Optional[str] = None,
        pages: Optional[List[int]] = None,
    ):
        self.method = method
        self.indices = indices
        self.keywords = keywords
        self.regex_patterns = regex_patterns
        self.row_conditions = row_conditions
        self.column_conditions = column_conditions
        self.saved_profile = saved_profile
        self.pages = pages

    def validate(self):
        if self.method not in self.VALID_METHODS:
            raise InvalidParameterError(
                f"Invalid selection method '{self.method}'. Valid methods are {self.VALID_METHODS}."
            )

        if self.method == 'append tables':
            pass  # No additional validation needed
        elif self.method == 'indexing':
            self._validate_indices()
        elif self.method == 'keyword':
            self._validate_keywords()
        elif self.method == 'regex':
            self._validate_regex_patterns()
        elif self.method == 'criteria':
            self._validate_criteria()
        elif self.method == 'saved_profile':
            self._validate_saved_profile()
        else:
            raise InvalidParameterError(f"Unrecognized method '{self.method}'.")
        
        # Validate pages
        self._validate_pages()

    # Include the validation methods for each case
    def _validate_indices(self):
        if not self.indices or not isinstance(self.indices, list):
            raise InvalidParameterError(
                "Indices must be provided as a list of integers when method is 'indexing'."
            )
        if not all(isinstance(i, int) and i >= 0 for i in self.indices):
            raise InvalidParameterError("All indices must be non-negative integers.")

    def _validate_keywords(self):
        if not self.keywords or not isinstance(self.keywords, list):
            raise InvalidParameterError(
                "Keywords must be provided as a list of strings when method is 'keyword'."
            )
        if not all(isinstance(k, str) for k in self.keywords):
            raise InvalidParameterError("All keywords must be strings.")

    def _validate_regex_patterns(self):
        if not self.regex_patterns or not isinstance(self.regex_patterns, list):
            raise InvalidParameterError(
                "Regex patterns must be provided as a list of strings when method is 'regex'."
            )
        for pattern in self.regex_patterns:
            try:
                re.compile(pattern)
            except re.error as e:
                raise InvalidParameterError(f"Invalid regex pattern '{pattern}': {e}")

    def _validate_criteria(self):
        if not self.row_conditions and not self.column_conditions:
            raise InvalidParameterError(
                "At least one of row_conditions or column_conditions must be provided when method is 'criteria'."
            )

    def _validate_saved_profile(self):
        if not self.saved_profile or not isinstance(self.saved_profile, str):
            raise InvalidParameterError(
                "A saved profile name must be provided as a string when method is 'saved_profile'."
            )
    
    def _validate_pages(self):
        if self.pages is not None:
            if not isinstance(self.pages, list):
                raise InvalidParameterError("Pages must be provided as a list of integers.")
            if not all(isinstance(p, int) and p >= 1 for p in self.pages):
                raise InvalidParameterError("All page numbers must be positive integers.")

class FormattingRules:
    """
    Defines rules for formatting extracted data.

    Attributes:
        preserve_styles (bool): 
            Indicates whether to preserve text styles like bold or italic.
        date_format (str): 
            Specifies the date format to use.
        number_format (str): 
            Specifies the numerical format to use.
        encoding (str): 
            Character encoding to use for text data.
        placeholder_for_missing (Any): 
            Value to use for missing data.

    Methods:
        validate()
    """

    def __init__(
        self, 
        preserve_styles: bool = False,
        date_format: str = "%Y-%m-%d",  # ISO 8601 format
        number_format: Optional[str] = None,  # Optional format string
        encoding: str = "utf-8",
        placeholder_for_missing: Any = None,
        header_rows: int = 0
    ):
        """
        Initializes the FormattingRules object.

        Parameters:
            preserve_styles (bool): 
                Indicates whether to preserve text styles like bold or italic.
            date_format (str): 
                Specifies the date format to use.
            number_format (Optional[str]): 
                Specifies the numerical format to use.
            encoding (str): 
                Character encoding to use for text data.
            placeholder_for_missing (Any): 
                Value to use for missing data.
        """
        self.preserve_styles = preserve_styles
        self.date_format = date_format
        self.number_format = number_format
        self.encoding = encoding
        self.placeholder_for_missing = placeholder_for_missing
        self.header_rows = header_rows

    def validate(self):
        if not isinstance(self.preserve_styles, bool):
            raise InvalidParameterError("preserve_styles must be a boolean.")

        # Validate date_format
        try:
            datetime.datetime.now().strftime(self.date_format)
        except Exception as e:
            raise InvalidParameterError(f"Invalid date format '{self.date_format}': {e}")

        # Validate number_format
        if self.number_format is not None:
            if not isinstance(self.number_format, str):
                raise InvalidParameterError("number_format must be a string.")
            # Test formatting with a sample number
            try:
                (1234567890.12345).__format__(self.number_format)
            except ValueError as e:
                raise InvalidParameterError(f"Invalid number format '{self.number_format}': {e}")

        if not isinstance(self.encoding, str):
            raise InvalidParameterError("encoding must be a string.")
        if not isinstance(self.header_rows, int) or self.header_rows < 0:
            raise InvalidParameterError("header_rows must be a non-negative integer.")


class ErrorHandlingStrategy:
    """
    Specifies how errors should be handled during data extraction.

    Attributes:
        on_parsing_error (str): 
            Action to take on parsing errors ('skip', 'abort', 'log').
        on_validation_error (str): 
            Action to take on validation errors ('correct', 'omit', 'prompt', 'abort').
        fallback_mechanisms (Optional[List[Callable]]): 
            List of fallback functions to call on error.

    Methods:
        validate()
    """
    VALID_PARSING_ACTIONS = ['skip', 'abort', 'log']
    VALID_VALIDATION_ACTIONS = ['correct', 'omit', 'prompt', 'abort']

    def __init__(
        self, 
        on_parsing_error: str = 'log',
        on_validation_error: str = 'omit',
        fallback_mechanisms: Optional[List[Callable]] = None,
    ):
        """
        Initializes the ErrorHandlingStrategy object.

        Parameters:
            on_parsing_error (str): 
                Action to take on parsing errors ('skip', 'abort', 'log').
            on_validation_error (str): 
                Action to take on validation errors ('correct', 'omit', 'prompt', 'abort').
            fallback_mechanisms (Optional[List[Callable]]): 
                List of fallback functions to call on error.
        """
        self.on_parsing_error = on_parsing_error
        self.on_validation_error = on_validation_error
        self.fallback_mechanisms = fallback_mechanisms or []

    def validate(self):
        """
        Validates the error handling strategy to ensure it is correctly specified.

        Raises:
            InvalidParameterError:
                If any of the error handling strategies are invalid.
        """
        if self.on_parsing_error not in self.VALID_PARSING_ACTIONS:
            raise InvalidParameterError(
                f"Invalid on_parsing_error action '{self.on_parsing_error}'. Valid actions are {self.VALID_PARSING_ACTIONS}."
            )

        if self.on_validation_error not in self.VALID_VALIDATION_ACTIONS:
            raise InvalidParameterError(
                f"Invalid on_validation_error action '{self.on_validation_error}'. Valid actions are {self.VALID_VALIDATION_ACTIONS}."
            )

        if not isinstance(self.fallback_mechanisms, list):
            raise InvalidParameterError("fallback_mechanisms must be a list of callables.")

        for func in self.fallback_mechanisms:
            if not callable(func):
                raise InvalidParameterError("All fallback mechanisms must be callable.")


class ParserConfiguration:
    """
    Configurations for the parsing engine.

    Attributes:
        ocr_enabled (bool): 
            Whether to use OCR for scanned PDFs.
        language (str): 
            Language of the documents to assist parsing.
        resource_limits (ResourceLimits): 
            Limits on system resources for parsing.

    Methods:
        validate()
    """

    def __init__(
        self,
        ocr_enabled: bool = False,
        language: str = 'en',
        resource_limits: Optional['ResourceLimits'] = None
    ):
        """
        Initializes the ParserConfiguration object.

        Parameters:
            ocr_enabled (bool): 
                Whether to use OCR for scanned PDFs.
            language (str): 
                Language of the documents to assist parsing.
            resource_limits (ResourceLimits): 
                Limits on system resources for parsing.
        """
        self.ocr_enabled = ocr_enabled
        self.language = language
        self.resource_limits = resource_limits or ResourceLimits()

    def validate(self):
        """
        Validates the parser configuration to ensure it is correctly specified.

        Raises:
            InvalidParameterError:
                If any of the parser configurations are invalid.
        """
        if not isinstance(self.ocr_enabled, bool):
            raise InvalidParameterError("ocr_enabled must be a boolean.")

        if not isinstance(self.language, str):
            raise InvalidParameterError("language must be a string.")

        self.resource_limits.validate()


class ResourceLimits:
    """
    Limits on system resources for the extraction process.

    Attributes:
        max_memory (Optional[int]): 
            Maximum memory (in MB) to use.
        max_time (Optional[int]): 
            Maximum time (in seconds) allowed for extraction.
        max_cpu_usage (Optional[int]): 
            Maximum CPU percentage to use.

    Methods:
        validate()
    """

    def __init__(
        self,
        max_memory: Optional[int] = None,
        max_time: Optional[int] = None,
        max_cpu_usage: Optional[int] = None
    ):
        """
        Initializes the ResourceLimits object.

        Parameters:
            max_memory (Optional[int]): 
                Maximum memory (in MB) to use.
            max_time (Optional[int]): 
                Maximum time (in seconds) allowed for extraction.
            max_cpu_usage (Optional[int]): 
                Maximum CPU percentage to use.
        """
        self.max_memory = max_memory
        self.max_time = max_time
        self.max_cpu_usage = max_cpu_usage

    def validate(self):
        """
        Validates the resource limits to ensure they are correctly specified.

        Raises:
            InvalidParameterError:
                If any of the resource limits are invalid.
        """
        if self.max_memory is not None:
            if not isinstance(self.max_memory, int) or self.max_memory <= 0:
                raise InvalidParameterError("max_memory must be a positive integer representing MB.")

        if self.max_time is not None:
            if not isinstance(self.max_time, int) or self.max_time <= 0:
                raise InvalidParameterError("max_time must be a positive integer representing seconds.")

        if self.max_cpu_usage is not None:
            if not isinstance(self.max_cpu_usage, int) or not (0 < self.max_cpu_usage <= 100):
                raise InvalidParameterError("max_cpu_usage must be an integer between 1 and 100.")


# Additional utility functions or classes can be added here as needed