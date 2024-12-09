import unittest
from unittest.mock import patch, MagicMock
import streamlit as st
from schema_extractor import ui_components

class TestUIComponents(unittest.TestCase):
    """
    Test cases for the ui_components module.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        # Clear session state before each test
        st.session_state.clear()

    @patch('streamlit.radio')
    def test_select_processing_option(self, mock_radio):
        """
        Test the select_processing_option function.
        """
        mock_radio.return_value = "Process Tabular data"
        choice = ui_components.select_processing_option()
        self.assertEqual(choice, "Process Tabular data")
        mock_radio.assert_called_once_with(
            "Choose a processing path:",
            ["Process Serialized data", "Process Tabular data", "Process Unstructured data"]
        )

    def test_display_validation_results_valid(self):
        """
        Test the display_validation_results function when validation is successful.
        """
        with patch('streamlit.success') as mock_success:
            ui_components.display_validation_results(True)
            mock_success.assert_called_once_with("Data is valid against the schema.")

    def test_display_validation_results_invalid(self):
        """
        Test the display_validation_results function when validation fails.
        """
        with patch('streamlit.error') as mock_error, \
             patch('streamlit.write') as mock_write:
            errors = ["Error 1", "Error 2"]
            ui_components.display_validation_results(False, errors)
            mock_error.assert_called_once_with("Data is not valid against the schema.")
            mock_write.assert_called()

    def test_display_schema_structure(self):
        """
        Test the display_schema_structure function.
        """
        schema = {
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'integer'},
                'address': {
                    'type': 'object',
                    'properties': {
                        'street': {'type': 'string'},
                        'city': {'type': 'string'}
                    }
                }
            }
        }
        with patch('streamlit.markdown') as mock_markdown:
            ui_components.display_schema_structure(schema)
            self.assertTrue(mock_markdown.called)

    def test_schema_builder_interface_initialization(self):
        """
        Test the initialization part of the schema_builder_interface function.
        """
        with patch('streamlit.text_input', return_value='Test Schema') as mock_text_input, \
             patch('streamlit.text_area', return_value='Schema Description') as mock_text_area, \
             patch('streamlit.write'), \
             patch('streamlit.form_submit_button', return_value=False):
            schema = ui_components.schema_builder_interface()
            self.assertIsNone(schema)
            self.assertEqual(st.session_state['schema']['title'], 'Test Schema')
            self.assertEqual(st.session_state['schema']['description'], 'Schema Description')
            mock_text_input.assert_called_with("Schema Title", value='')
            mock_text_area.assert_called_with("Schema Description", value='')

if __name__ == '__main__':
    unittest.main()