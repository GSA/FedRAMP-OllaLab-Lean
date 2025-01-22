# streamlit_app/app/table2json_extractor/tests/test_user_interface.py

"""
test_user_interface.py

Unit tests for user_interface.py module.
"""

import unittest
from user_interface import process_user_input, process_documents, render_results
from exceptions import InvalidUserInputError, ProcessingError, RenderingError
from extraction_parameters import ExtractionParameters
import tempfile
import os

class TestUserInterface(unittest.TestCase):

    def test_process_user_input_valid(self):
        user_inputs = {
            'table_selection': {
                'method': 'indexing',
                'indices': [0]
            },
            'formatting_rules': {
                'preserve_styles': False,
                'date_format': "%Y-%m-%d",
                'number_format': None,
                'encoding': "utf-8",
                'placeholder_for_missing': None
            },
            'error_handling': {
                'on_parsing_error': 'log',
                'on_validation_error': 'omit',
                'fallback_mechanisms': []
            },
            'parser_config': {
                'ocr_enabled': False,
                'language': 'en',
                'resource_limits': {}
            },
            'data_types': {}
        }
        try:
            extraction_parameters = process_user_input(user_inputs)
            self.assertIsInstance(extraction_parameters, ExtractionParameters)
        except Exception as e:
            self.fail(f"process_user_input raised an exception {e}")

    def test_process_user_input_invalid(self):
        user_inputs = {}
        with self.assertRaises(InvalidUserInputError):
            process_user_input(user_inputs)

    def test_process_documents_empty_file_paths(self):
        extraction_parameters = ExtractionParameters(
            table_selection=None,
            formatting_rules=None,
            data_types=None,
            error_handling=None,
            parser_config=None
        )
        with self.assertRaises(ProcessingError):
            process_documents([], extraction_parameters)

    def test_render_results_invalid_format(self):
        data = [{'test': 'data'}]
        with self.assertRaises(RenderingError):
            render_results(data, 'xml')

    def test_render_results_json(self):
        data = [{'test': 'data'}]
        try:
            result = render_results(data, 'json')
            self.assertIsInstance(result, str)
        except Exception as e:
            self.fail(f"render_results raised an exception {e}")

if __name__ == '__main__':
    unittest.main()