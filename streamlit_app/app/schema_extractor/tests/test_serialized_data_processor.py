# test_serialized_data_processor.py

import unittest
from schema_extractor.serialized_data_processor import (
    parse_serialized_data,
    perform_eda,
    extract_schema,
    validate_schema
)
from unittest.mock import patch
import json
import yaml
import xml.etree.ElementTree as ET

class TestSerializedDataProcessor(unittest.TestCase):
    """
    Test cases for the serialized_data_processor module.
    """

    def test_parse_serialized_data_json(self):
        """
        Test parsing of JSON serialized data.
        """
        sample_data = {
            'test.json': {
                'content': '{"name": "John", "age": 30}',
                'file_type': 'json'
            }
        }
        parsed_data = parse_serialized_data(sample_data)
        self.assertIsInstance(parsed_data, dict)
        self.assertIn('test.json', parsed_data)
        self.assertEqual(parsed_data['test.json']['name'], 'John')
        self.assertEqual(parsed_data['test.json']['age'], 30)

    def test_parse_serialized_data_yaml(self):
        """
        Test parsing of YAML serialized data.
        """
        sample_data = {
            'test.yaml': {
                'content': 'name: John\nage: 30',
                'file_type': 'yaml'
            }
        }
        parsed_data = parse_serialized_data(sample_data)
        self.assertIsInstance(parsed_data, dict)
        self.assertIn('test.yaml', parsed_data)
        self.assertEqual(parsed_data['test.yaml']['name'], 'John')
        self.assertEqual(parsed_data['test.yaml']['age'], 30)

    def test_parse_serialized_data_xml(self):
        """
        Test parsing of XML serialized data.
        """
        sample_data = {
            'test.xml': {
                'content': '<root><name>John</name><age>30</age></root>',
                'file_type': 'xml'
            }
        }
        parsed_data = parse_serialized_data(sample_data)
        self.assertIsInstance(parsed_data, dict)
        self.assertIn('test.xml', parsed_data)
        self.assertIsInstance(parsed_data['test.xml'], ET.ElementTree)

    def test_extract_schema_json(self):
        """
        Test schema extraction from JSON data.
        """
        parsed_data = {
            'test.json': {
                'name': 'John',
                'age': 30
            }
        }
        with patch('streamlit.write'), patch('streamlit.json'):
            schemas = extract_schema(parsed_data)
        self.assertIsInstance(schemas, dict)
        self.assertIn('test.json', schemas)
        self.assertIn('properties', schemas['test.json'])
        self.assertIn('name', schemas['test.json']['properties'])
        self.assertIn('age', schemas['test.json']['properties'])

    def test_validate_schema_json(self):
        """
        Test validation of JSON data against schema.
        """
        parsed_data = {
            'test.json': {
                'name': 'John',
                'age': 30
            }
        }
        schemas = {
            'test.json': {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                },
                "required": ["name", "age"]
            }
        }
        with patch('streamlit.write'), patch('streamlit.success'), patch('streamlit.error'), patch('streamlit.warning'):
            validate_schema(parsed_data, schemas)

    # Additional tests can be added as needed

if __name__ == '__main__':
    unittest.main()