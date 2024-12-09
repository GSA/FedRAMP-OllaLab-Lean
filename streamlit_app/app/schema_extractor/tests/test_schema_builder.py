# schema_extractor/tests/test_schema_builder.py

import unittest
import pandas as pd
from schema_extractor import schema_builder
from pandera import Column, Check, DataFrameSchema
import pandera as pa

class TestSchemaBuilder(unittest.TestCase):
    """
    Test cases for the schema_builder module.
    """

    def test_build_schema_from_serialized_data(self):
        """
        Tests building schema from serialized data (JSON).
        """
        # Sample JSON data
        data = {
            "name": "Alice",
            "age": 30,
            "gender": "Female"
        }
        user_inputs = {
            'required_fields': ['name', 'age'],
            'field_constraints': {
                'name': {'maxLength': 50},
                'age': {'minimum': 0, 'maximum': 100},
                'gender': {'enum': ['Male', 'Female', 'Other']}
            }
        }

        schema = schema_builder.build_schema(data, 'serialized', user_inputs)
        self.assertIsInstance(schema, dict)
        self.assertIn('required', schema)
        self.assertEqual(schema['required'], ['name', 'age'])
        self.assertIn('properties', schema)
        self.assertIn('gender', schema['properties'])
        self.assertIn('enum', schema['properties']['gender'])

    def test_validate_serialized_data_against_schema(self):
        """
        Tests validating serialized data against schema.
        """
        data = {
            "name": "Bob",
            "age": 25,
            "gender": "Male"
        }
        schema = {
            "type": "object",
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string", "maxLength": 50},
                "age": {"type": "number", "minimum": 0, "maximum": 100},
                "gender": {"type": "string", "enum": ["Male", "Female", "Other"]}
            }
        }
        is_valid = schema_builder.validate_data_against_schema(data, schema, 'serialized')
        self.assertTrue(is_valid)

    def test_build_schema_from_tabular_data(self):
        """
        Tests building schema from tabular data (DataFrame).
        """
        data = {
            'name': ['Alice', 'Bob'],
            'age': [30, 25],
            'gender': ['Female', 'Male']
        }
        df = pd.DataFrame(data)
        user_inputs = {
            'columns': {
                'age': {
                    'dtype': 'int',
                    'nullable': False,
                    'checks': {
                        'greater_than_or_equal_to': 0,
                        'less_than_or_equal_to': 100
                    }
                },
                'name': {
                    'dtype': 'string',
                    'nullable': False,
                    'checks': {
                        'str_length': {'min_value': 1, 'max_value': 50}
                    }
                }
            }
        }

        schema = schema_builder.build_schema(df, 'tabular', user_inputs)
        self.assertIsInstance(schema, pa.DataFrameSchema)
        self.assertIn('age', schema.columns)
        age_column = schema.columns['age']
        self.assertEqual(age_column.dtype, 'int')
        self.assertFalse(age_column.nullable)

    def test_validate_tabular_data_against_schema(self):
        """
        Tests validating tabular data against schema.
        """
        data = {
            'name': ['Alice', 'Bob'],
            'age': [30, 25],
            'gender': ['Female', 'Male']
        }
        df = pd.DataFrame(data)
        schema = DataFrameSchema({
            'name': Column(pa.String, nullable=False),
            'age': Column(pa.Int, [
                Check.ge(0),
                Check.le(100)
            ]),
            'gender': Column(pa.String, Check.isin(['Male', 'Female', 'Other']))
        })
        is_valid = schema_builder.validate_data_against_schema(df, schema, 'tabular')
        self.assertTrue(is_valid)

    def test_build_schema_from_unstructured_data(self):
        """
        Tests building schema from unstructured data.
        """
        # User inputs defining the schema
        user_inputs = {
            'title': 'Simple Text Schema',
            'description': 'Extracts dates from text',
            'type': 'object',
            'properties': {
                'date': {
                    'type': 'string',
                    'pattern': r'\b\d{4}-\d{2}-\d{2}\b',
                    'description': 'Extracted date in YYYY-MM-DD format'
                }
            },
            'required': ['date']
        }

        schema = schema_builder.build_schema(None, 'unstructured', user_inputs)
        self.assertIsInstance(schema, dict)
        self.assertIn('title', schema)
        self.assertEqual(schema['title'], 'Simple Text Schema')

    def test_validate_unstructured_data_against_schema(self):
        """
        Tests validating unstructured data against schema.
        """
        text_data = "The event will be held on 2023-09-21."
        schema = {
            'title': 'Date Extractor',
            'type': 'object',
            'properties': {
                'date': {
                    'type': 'string',
                    'pattern': r'\b\d{4}-\d{2}-\d{2}\b',
                    'description': 'Date in YYYY-MM-DD format'
                }
            },
            'required': ['date']
        }
        is_valid = schema_builder.validate_data_against_schema(text_data, schema, 'unstructured')
        self.assertTrue(is_valid)

        # Test with invalid text data
        invalid_text_data = "No date here."
        is_valid = schema_builder.validate_data_against_schema(invalid_text_data, schema, 'unstructured')
        self.assertFalse(is_valid)

if __name__ == '__main__':
    unittest.main()