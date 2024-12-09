# schema_extractor/tests/test_unstructured_data_processor.py

import unittest
from unittest.mock import patch, MagicMock
from schema_extractor import unstructured_data_processor as udp

class TestUnstructuredDataProcessor(unittest.TestCase):
    """
    Test cases for the unstructured_data_processor module.
    """

    def setUp(self):
        """
        Set up test data for the tests.
        """
        self.sample_data = {
            'sample1.txt': 'This is a sample text. It contains numbers like 123 and 456.',
            'sample2.txt': 'Another sample text! Testing, one, two, three.',
            'sample3.txt': 'More data with numbers 789 and words.'
        }

    def test_load_unstructured_data(self):
        """
        Tests the load_unstructured_data function.
        """
        with patch('schema_extractor.unstructured_data_processor.logger') as mock_logger:
            text_data = udp.load_unstructured_data(self.sample_data)
            self.assertEqual(len(text_data), 3)
            self.assertIn('This is a sample text. It contains numbers like 123 and 456.', text_data)
            self.assertIn('Another sample text! Testing, one, two, three.', text_data)
            self.assertIn('More data with numbers 789 and words.', text_data)

    def test_clean_text(self):
        """
        Tests the clean_text function.
        """
        raw_text = "Hello, World! This is a test.\nNew line and 123 numbers."
        cleaned = udp.clean_text(raw_text)
        expected = "Hello World This is a test New line and 123 numbers"
        self.assertEqual(cleaned, expected)

    def test_extract_numeric_stats(self):
        """
        Tests the extract_numeric_stats function.
        """
        numeric_stats = udp.extract_numeric_stats(self.sample_data.values())
        expected = {
            'count': 5,
            'mean': 123.0,
            'median': 123,
            'max': 789,
            'min': 123
        }
        self.assertEqual(numeric_stats['count'], 5)
        self.assertEqual(numeric_stats['max'], 789)
        self.assertEqual(numeric_stats['min'], 123)
        # Mean and median can be computed based on the sample data

    def test_generate_wordcloud(self):
        """
        Tests the generate_wordcloud function.
        """
        words = ['test', 'data', 'sample', 'test', 'word']
        wordcloud = udp.generate_wordcloud(words)
        self.assertIsInstance(wordcloud, udp.WordCloud)

    def test_perform_topic_modeling(self):
        """
        Tests the perform_topic_modeling function.
        """
        cleaned_data = [
            'this is a sample text about data science',
            'another text concerning machine learning',
            'more data related to artificial intelligence'
        ]
        topics = udp.perform_topic_modeling(cleaned_data, num_topics=2)
        self.assertEqual(len(topics), 2)
        for topic in topics:
            self.assertIn('topic_id', topic)
            self.assertIn('top_words', topic)
            self.assertEqual(len(topic['top_words']), 10)

    def test_group_similar_values(self):
        """
        Tests the group_similar_values function.
        """
        common_ngrams = {
            'bigram_freq': [(('sample', 'text'), 2)],
            'trigram_freq': [(('more', 'data', 'related'), 1)]
        }
        numeric_stats = {
            'count': 3,
            'mean': 456.0,
            'median': 456,
            'max': 789,
            'min': 123
        }
        groups = udp.group_similar_values(list(self.sample_data.values()), common_ngrams, numeric_stats)
        self.assertIn('Common Trigrams', groups)
        self.assertIn('Common Bigrams', groups)
        self.assertIn('Numeric Values', groups)
        self.assertEqual(groups['Common Bigrams']['values'], ['sample text'])
        self.assertEqual(groups['Common Trigrams']['values'], ['more data related'])
        self.assertEqual(groups['Numeric Values']['values'], numeric_stats)

    def test_design_schema(self):
        """
        Tests the design_schema function.
        """
        groups = {
            'Common Trigrams': {
                'type': 'String',
                'description': 'Frequently occurring three-word sequences.',
                'values': ['more data related']
            },
            'Common Bigrams': {
                'type': 'String',
                'description': 'Frequently occurring two-word sequences.',
                'values': ['sample text']
            },
            'Numeric Values': {
                'type': 'Numeric',
                'description': 'Extracted numeric values from the text.',
                'values': {
                    'count': 3,
                    'mean': 456.0,
                    'median': 456,
                    'max': 789,
                    'min': 123
                }
            }
        }
        schema = udp.design_schema(groups)
        self.assertIn('properties', schema)
        self.assertIn('common_trigrams', schema['properties'])
        self.assertIn('common_bigrams', schema['properties'])
        self.assertIn('numeric_values', schema['properties'])
        self.assertEqual(schema['properties']['common_trigrams']['type'], 'string')
        self.assertEqual(schema['properties']['numeric_values']['type'], 'object')
        self.assertIn('mean', schema['properties']['numeric_values']['properties'])

    def test_validate_schema(self):
        """
        Tests the validate_schema function.
        """
        cleaned_data = ['Sample text with numbers 123 and 456.']
        schema = {
            "title": "Test Schema",
            "description": "A test schema.",
            "type": "object",
            "properties": {
                "common_trigrams": {
                    "type": "string",
                    "description": "Test description."
                }
            }
        }
        is_valid = udp.validate_schema(cleaned_data, schema)
        self.assertTrue(is_valid)

    def test_process_unstructured_data(self):
        """
        Tests the entire process_unstructured_data function.
        """
        with patch('schema_extractor.unstructured_data_processor.load_unstructured_data') as mock_load, \
             patch('schema_extractor.unstructured_data_processor.perform_eda') as mock_eda, \
             patch('schema_extractor.unstructured_data_processor.group_similar_values') as mock_group, \
             patch('schema_extractor.unstructured_data_processor.design_schema') as mock_design, \
             patch('schema_extractor.unstructured_data_processor.validate_schema') as mock_validate:

            mock_load.return_value = ['Sample text for processing.']
            mock_eda.return_value = {'common_ngrams': {'bigram_freq': [], 'trigram_freq': []}, 'numeric_stats': {}}
            mock_group.return_value = {}
            mock_design.return_value = {}
            mock_validate.return_value = True

            result = udp.process_unstructured_data(self.sample_data)
            self.assertIn('eda_results', result)
            self.assertIn('schema', result)
            self.assertIn('is_valid', result)
            self.assertTrue(result['is_valid'])

if __name__ == '__main__':
    unittest.main()