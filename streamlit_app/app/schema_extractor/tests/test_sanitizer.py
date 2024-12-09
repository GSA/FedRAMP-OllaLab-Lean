# schema_extractor/tests/test_sanitizer.py

import unittest
import pandas as pd
from schema_extractor import sanitizer
from unittest.mock import patch, MagicMock

class TestSanitizer(unittest.TestCase):
    """
    Test cases for the sanitizer module.
    """

    def setUp(self):
        # Setup code executed before each test
        pass

    def test_remove_harmful_characters(self):
        """
        Tests the remove_harmful_characters function.
        """
        data = {'text': ['Hello<>:', 'World/\\|?*']}
        df = pd.DataFrame(data)
        clean_df = sanitizer.remove_harmful_characters(df)
        expected_data = {'text': ['Hello', 'World']}
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(clean_df, expected_df)

    @patch('schema_extractor.sanitizer.st')
    def test_detect_and_redact_sensitive_data(self, mock_st):
        """
        Tests the detect_and_redact_sensitive_data function.
        """
        data = {'email': ['user@example.com', 'no_email'], 
                'text': ['SSN: 123-45-6789', 'No sensitive info']}
        df = pd.DataFrame(data)
        redacted_df = sanitizer.detect_and_redact_sensitive_data(df)
        expected_data = {'email': ['[REDACTED]', 'no_email'], 
                         'text': ['SSN: [REDACTED]', 'No sensitive info']}
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(redacted_df, expected_df)

    @patch('schema_extractor.sanitizer.st')
    def test_detect_and_handle_duplicates(self, mock_st):
        """
        Tests the detect_and_handle_duplicates function with mock user input.
        """
        data = {'col1': [1, 2, 2], 'col2': ['a', 'b', 'b']}
        df = pd.DataFrame(data)
        # Mock user selection
        mock_st.selectbox.return_value = "Remove duplicates"
        clean_df = sanitizer.detect_and_handle_duplicates(df)
        expected_df = df.drop_duplicates()
        pd.testing.assert_frame_equal(clean_df.reset_index(drop=True), expected_df.reset_index(drop=True))

    @patch('schema_extractor.sanitizer.st')
    def test_remove_stopwords_from_dataframe(self, mock_st):
        """
        Tests the remove_stopwords_from_dataframe function with mock user input.
        """
        data = {'text': ['This is a test', 'Another test']}
        df = pd.DataFrame(data)
        mock_st.text_input.return_value = 'is,a'
        clean_df = sanitizer.remove_stopwords_from_dataframe(df)
        expected_data = {'text': ['This test', 'Another test']}
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(clean_df, expected_df)

    @patch('schema_extractor.sanitizer.st')
    def test_detect_and_handle_unwanted_content(self, mock_st):
        """
        Tests the detect_and_handle_unwanted_content function with mock user input.
        """
        data = {'text': ['This is a badword1', 'Clean text']}
        df = pd.DataFrame(data)
        mock_st.selectbox.return_value = "Remove rows containing unwanted content"
        clean_df = sanitizer.detect_and_handle_unwanted_content(df)
        expected_df = pd.DataFrame({'text': ['Clean text']})
        pd.testing.assert_frame_equal(clean_df.reset_index(drop=True), expected_df.reset_index(drop=True))

    def test_remove_harmful_characters_text(self):
        """
        Tests the remove_harmful_characters_text function.
        """
        text = 'Hello<>:"/\\|?*\x01\x02 World'
        clean_text = sanitizer.remove_harmful_characters_text(text)
        expected_text = 'Hello World'
        self.assertEqual(clean_text, expected_text)

    @patch('schema_extractor.sanitizer.st')
    def test_detect_and_redact_sensitive_data_text(self, mock_st):
        """
        Tests the detect_and_redact_sensitive_data_text function.
        """
        text = 'Contact me at user@example.com. My SSN is 123-45-6789.'
        redacted_text = sanitizer.detect_and_redact_sensitive_data_text(text)
        expected_text = 'Contact me at [REDACTED]. My SSN is [REDACTED].'
        self.assertEqual(redacted_text, expected_text)

    @patch('schema_extractor.sanitizer.st')
    def test_remove_stopwords_from_text(self, mock_st):
        """
        Tests the remove_stopwords_from_text function with mock user input.
        """
        text = 'This is a test of the stopwords function.'
        mock_st.text_input.return_value = 'is,a,the'
        clean_text = sanitizer.remove_stopwords_from_text(text)
        expected_text = 'This test of stopwords function.'
        self.assertEqual(clean_text, expected_text)

    @patch('schema_extractor.sanitizer.st')
    def test_detect_and_handle_unwanted_content_text(self, mock_st):
        """
        Tests the detect_and_handle_unwanted_content_text function with mock user input.
        """
        text = 'This text contains badword1 and badword2.'
        mock_st.selectbox.return_value = "Remove unwanted content"
        clean_text = sanitizer.detect_and_handle_unwanted_content_text(text)
        expected_text = 'This text contains  and .'
        self.assertEqual(clean_text, expected_text)

if __name__ == '__main__':
    unittest.main()