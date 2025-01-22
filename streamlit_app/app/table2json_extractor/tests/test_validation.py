# test_validation.py

"""
Unit tests for the validation.py module.
"""

import unittest
from validation import validate_user_inputs, validate_extracted_data
from exceptions import ValidationError, DataValidationError
from extraction_parameters import (
    ExtractionParameters,
    TableSelectionCriteria,
    FormattingRules,
    ErrorHandlingStrategy,
    ParserConfiguration,
)
from typing import Dict, Any, List, Type

class TestValidation(unittest.TestCase):

    def test_validate_user_inputs_success(self):
        user_inputs = {
            'source_documents': ['doc1.docx', 'doc2.pdf'],
            'table_selection': {
                'method': 'indexing',
                'indices': [0, 1]
            },
            'extraction_parameters': {
                'formatting_rules': {
                    'date_format': '%Y-%m-%d',
                    'number_format': '.2f',
                    'encoding': 'utf-8'
                },
                'data_types': {
                    'Column1': 'int',
                    'Column2': 'float',
                    'DateColumn': 'date'
                }
            }
        }
        try:
            validate_user_inputs(user_inputs)
        except ValidationError:
            self.fail("validate_user_inputs raised ValidationError unexpectedly!")

    def test_validate_user_inputs_missing_required_field(self):
        user_inputs = {
            'source_documents': ['doc1.docx', 'doc2.pdf'],
            # 'table_selection' is missing
            'extraction_parameters': {}
        }
        with self.assertRaises(ValidationError) as context:
            validate_user_inputs(user_inputs)
        self.assertIn("Missing required input: table_selection", str(context.exception))

    def test_validate_user_inputs_invalid_method(self):
        user_inputs = {
            'source_documents': ['doc1.docx'],
            'table_selection': {
                'method': 'invalid_method'
            },
            'extraction_parameters': {}
        }
        with self.assertRaises(ValidationError) as context:
            validate_user_inputs(user_inputs)
        self.assertIn("Invalid table selection method 'invalid_method'", str(context.exception))

    def test_validate_user_inputs_invalid_data_type(self):
        user_inputs = {
            'source_documents': ['doc1.docx'],
            'table_selection': {
                'method': 'indexing',
                'indices': [0]
            },
            'extraction_parameters': {
                'data_types': {
                    'Column1': 'integer'  # invalid data type
                }
            }
        }
        with self.assertRaises(ValidationError) as context:
            validate_user_inputs(user_inputs)
        self.assertIn("Invalid data type 'integer' for column 'Column1'", str(context.exception))

    def test_validate_extracted_data_success(self):
        data = [
            {'Column1': 1, 'Column2': 2.5, 'DateColumn': datetime.date.today()},
            {'Column1': 2, 'Column2': 3.5, 'DateColumn': datetime.date.today()}
        ]
        data_types = {'Column1': int, 'Column2': float, 'DateColumn': 'date'}
        parameters = ExtractionParameters(
            table_selection=None,
            formatting_rules=None,
            data_types=data_types,
            error_handling=None,
            parser_config=None
        )
        try:
            validate_extracted_data(data, parameters)
        except DataValidationError:
            self.fail("validate_extracted_data raised DataValidationError unexpectedly!")

    def test_validate_extracted_data_type_mismatch(self):
        data = [
            {'Column1': 1, 'Column2': 'not a float', 'DateColumn': datetime.date.today()}
        ]
        data_types = {'Column1': int, 'Column2': float, 'DateColumn': 'date'}
        parameters = ExtractionParameters(
            table_selection=None,
            formatting_rules=None,
            data_types=data_types,
            error_handling=None,
            parser_config=None
        )
        with self.assertRaises(DataValidationError) as context:
            validate_extracted_data(data, parameters)
        self.assertIn("Invalid data type for column 'Column2'", str(context.exception))

    def test_validate_extracted_data_missing_column(self):
        data = [
            {'Column1': 1, 'DateColumn': datetime.date.today()}  # Missing 'Column2'
        ]
        data_types = {'Column1': int, 'Column2': float, 'DateColumn': 'date'}
        parameters = ExtractionParameters(
            table_selection=None,
            formatting_rules=None,
            data_types=data_types,
            error_handling=None,
            parser_config=None
        )
        # Assuming that missing values are acceptable
        try:
            validate_extracted_data(data, parameters)
        except DataValidationError:
            self.fail("validate_extracted_data raised DataValidationError unexpectedly!")

if __name__ == '__main__':
    unittest.main()