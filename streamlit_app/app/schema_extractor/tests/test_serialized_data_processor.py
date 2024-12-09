# test_serialized_data_processor.py

import unittest
from schema_extractor import serialized_data_processor
from schema_extractor import ui_components
import json
import yaml
import xml.etree.ElementTree as ET

class TestSerializedDataProcessor(unittest.TestCase):
    def setUp(self):
        # Example sanitized data
        self.json_data = '{"name": "John Doe", "age": 30}'
        self.yaml_data = "name: Jane Doe\nage: 25"
        self.xml_data = "<root><person><name>John Smith</name><age>40</age></person></root>"
        self.sanitized_data = {
            'data.json': self.json_data,
            'data.yaml': self.yaml_data,
            'data.xml': self.xml_data
        }

    def test_parse_serialized_data(self):
        parsed_data = serialized_data_processor.parse_serialized_data(self.sanitized_data)
        self.assertIn('data.json', parsed_data)
        self.assertIn('data.yaml', parsed_data)
        self.assertIn('data.xml', parsed_data)

        # Test JSON parsing
        json_data = parsed_data['data.json']
        self.assertEqual(json_data['type'], 'json')
        self.assertEqual(json_data['data']['name'], 'John Doe')

        # Test YAML parsing
        yaml_data = parsed_data['data.yaml']
        self.assertEqual(yaml_data['type'], 'yaml')
        self.assertEqual(yaml_data['data']['name'], 'Jane Doe')

        # Test XML parsing
        xml_data = parsed_data['data.xml']
        self.assertEqual(xml_data['type'], 'xml')
        self.assertIsInstance(xml_data['data'], ET.Element)

    def test_extract_schema(self):
        parsed_data = serialized_data_processor.parse_serialized_data({'data.json': self.json_data})
        extracted_schemas = serialized_data_processor.extract_schema(parsed_data)
        self.assertIn('data.json', extracted_schemas)
        schema_info = extracted_schemas['data.json']
        self.assertEqual(schema_info['type'], 'json')
        self.assertIn('properties', schema_info['schema'])
        self.assertIn('name', schema_info['schema']['properties'])

    def test_validate_schema(self):
        parsed_data = serialized_data_processor.parse_serialized_data({'data.json': self.json_data})
        extracted_schemas = serialized_data_processor.extract_schema(parsed_data)
        # Simulate user customization (e.g., setting 'name' as required)
        schema = extracted_schemas['data.json']['schema']
        schema['required'] = ['name']
        extracted_schemas['data.json']['schema'] = schema
        try:
            serialized_data_processor.validate_schema(parsed_data, extracted_schemas)
        except Exception as e:
            self.fail(f"validate_schema raised an exception: {e}")

    def test_xml_to_dataframe(self):
        # Parse XML and convert to DataFrame
        parsed_data = serialized_data_processor.parse_serialized_data({'data.xml': self.xml_data})
        xml_data = parsed_data['data.xml']['data']
        df = serialized_data_processor.xml_to_dataframe(xml_data)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('name', df.columns)
        self.assertIn('age', df.columns)

if __name__ == '__main__':
    unittest.main()