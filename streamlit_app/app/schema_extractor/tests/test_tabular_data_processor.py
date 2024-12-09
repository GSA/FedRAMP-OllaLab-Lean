# schema_extractor/tests/test_tabular_data_processor.py

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from schema_extractor import tabular_data_processor

class TestTabularDataProcessor(unittest.TestCase):
    """
    Test cases for the tabular_data_processor module.
    """

    def setUp(self):
        """
        Setup sample data for testing.
        """
        self.sample_csv = pd.DataFrame({
            'id': [1, 2, 3, 4],
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'age': [25, 30, 35, 40],
            'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'david@example.com']
        })
        self.sample_json = pd.DataFrame({
            'product_id': [101, 102, 103],
            'product_name': ['Widget', 'Gadget', 'Thingamajig'],
            'price': [19.99, 29.99, 39.99],
            'in_stock': [True, False, True]
        })
        self.sanitized_data = {
            'sample.csv': self.sample_csv,
            'products.json': self.sample_json
        }

    @patch('schema_extractor.tabular_data_processor.load_tabular_data')
    @patch('schema_extractor.tabular_data_processor.perform_eda')
    @patch('schema_extractor.tabular_data_processor.extract_schema')
    @patch('schema_extractor.tabular_data_processor.schema_builder_interface')
    @patch('schema_extractor.tabular_data_processor.validate_data_against_schema')
    def test_process_tabular_data(self, mock_validate, mock_schema_builder, mock_extract_schema, mock_eda, mock_load):
        """
        Tests the process_tabular_data function.
        """
        mock_load.return_value = self.sanitized_data
        mock_eda.return_value = {'sample.csv': 'EDA Report'}
        mock_extract_schema.return_value = 'Inferred Schema'
        mock_schema_builder.return_value = 'User Defined Schema'
        mock_validate.return_value = True

        with patch('streamlit.write') as mock_write, \
             patch('streamlit.header') as mock_header, \
             patch('streamlit.subheader') as mock_subheader, \
             patch('streamlit.json') as mock_json, \
             patch('streamlit.success') as mock_success, \
             patch('streamlit.error') as mock_error, \
             patch('streamlit.warning') as mock_warning, \
             patch('streamlit.selectbox') as mock_selectbox:

            # Mock Streamlit widgets
            mock_selectbox.return_value = "Remove Duplicates"

            # Call the function
            tabular_data_processor.process_tabular_data(self.sanitized_data)

            # Assertions to ensure all steps are called
            mock_header.assert_any_call("Process Tabular Data")
            mock_load.assert_called_once_with(self.sanitized_data)
            mock_eda.assert_called_once_with(self.sanitized_data)
            mock_extract_schema.assert_called_once_with(self.sanitized_data)
            mock_schema_builder.assert_called_once_with('Inferred Schema')
            mock_validate.assert_called_once_with(self.sanitized_data, 'User Defined Schema')
            mock_json.assert_called_with('Inferred Schema')

    def test_infer_schema_with_pandera(self):
        """
        Tests the infer_schema_with_pandera function.
        """
        df = self.sample_csv
        schema = tabular_data_processor.infer_schema_with_pandera(df)
        self.assertIsNotNone(schema)
        self.assertIn('id', schema.columns)
        self.assertIn('name', schema.columns)
        self.assertIn('age', schema.columns)
        self.assertIn('email', schema.columns)

    def test_validate_schema(self):
        """
        Tests the validate_schema function.
        """
        df = self.sample_csv
        schema = tabular_data_processor.infer_schema_with_pandera(df)
        # Assuming the schema matches the data
        is_valid = tabular_data_processor.validate_schema({'sample.csv': df}, schema)
        self.assertTrue(is_valid)

        # Modify the DataFrame to violate the schema
        df_invalid = df.copy()
        df_invalid.loc[0, 'age'] = 'twenty-five'  # Invalid integer
        is_valid = tabular_data_processor.validate_schema({'sample.csv': df_invalid}, schema)
        self.assertFalse(is_valid)

if __name__ == '__main__':
    unittest.main()