# schema_extractor/tests/test_unstructured_data_processor.py

import unittest
from schema_extractor import unstructured_data_processor

class TestUnstructuredDataProcessor(unittest.TestCase):
    """
    Test cases for the unstructured_data_processor module.
    """

    def setUp(self):
        # Sample sanitized data for testing
        self.sanitized_data = {
            'sample.txt': "This is a test text with numbers 123 and 456.78. It includes bigrams and trigrams."
        }
        self.text_data = unstructured_data_processor.load_unstructured_data(self.sanitized_data)

    def test_load_unstructured_data(self):
        """
        Tests loading of unstructured data.
        """
        data = unstructured_data_processor.load_unstructured_data(self.sanitized_data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_extract_numeric_values(self):
        """
        Tests extraction of numeric values from text.
        """
        text = "The values are 10, 20.5, and 30."
        numeric_values = unstructured_data_processor.extract_numeric_values(text)
        expected_values = [10.0, 20.5, 30.0]
        self.assertEqual(numeric_values, expected_values)

    def test_get_ngrams(self):
        """
        Tests generation of n-grams.
        """
        tokens = ['this', 'is', 'a', 'test']
        ngrams = unstructured_data_processor.get_ngrams(tokens)
        self.assertIn(2, ngrams)
        self.assertIn(3, ngrams)
        self.assertIsInstance(ngrams[2], Counter)
        self.assertIsInstance(ngrams[3], Counter)

    def test_generate_wordcloud(self):
        """
        Tests wordcloud generation.
        """
        tokens = ['test', 'wordcloud', 'generation']
        fig = unstructured_data_processor.generate_wordcloud(tokens)
        self.assertIsNotNone(fig)

    def test_perform_topic_modeling(self):
        """
        Tests topic modeling functionality.
        """
        tokens = ['topic', 'modeling', 'test', 'data', 'analysis']
        topics = unstructured_data_processor.perform_topic_modeling(tokens)
        self.assertIsInstance(topics, list)
        self.assertTrue(len(topics) > 0)

    def test_extract_data_using_schema(self):
        """
        Tests data extraction using a schema.
        """
        text = "The price is 100 dollars."
        schema = {
            "properties": {
                "price": {"type": "number"}
            }
        }
        extracted_data = unstructured_data_processor.extract_data_using_schema(text, schema)
        self.assertIsInstance(extracted_data, dict)
        # Since the function is a placeholder, we expect an empty dict
        self.assertEqual(extracted_data, {})

if __name__ == '__main__':
    unittest.main()