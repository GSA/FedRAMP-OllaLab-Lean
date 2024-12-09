import unittest
import tempfile
import os
from io import BytesIO
import pandas as pd
from schema_extractor import utils

class UploadedFileMock:
    """
    Mock class for Streamlit's UploadedFile object.
    """
    def __init__(self, name, content):
        self.name = name
        self.content = content

    def getbuffer(self):
        return self.content

class TestUtils(unittest.TestCase):
    def test_detect_file_type(self):
        # Test with tabular file
        file_csv = UploadedFileMock('data.csv', b'col1,col2\n1,2')
        self.assertEqual(utils.detect_file_type(file_csv), 'tabular')

        # Test with serialized file
        file_json = UploadedFileMock('data.json', b'{"key": "value"}')
        self.assertEqual(utils.detect_file_type(file_json), 'serialized')

        # Test with unstructured file
        file_txt = UploadedFileMock('data.txt', b'This is some text.')
        self.assertEqual(utils.detect_file_type(file_txt), 'unstructured')

        # Test with unknown file extension
        file_unknown = UploadedFileMock('data.unknown', b'')
        self.assertEqual(utils.detect_file_type(file_unknown), 'unknown')

    def test_backup_file(self):
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdirname:
            file = UploadedFileMock('test.txt', b'Some content')
            backup_path = utils.backup_file(file, backup_dir=tmpdirname)
            # Check if file exists
            self.assertTrue(os.path.exists(backup_path))
            # Check file content
            with open(backup_path, 'rb') as f:
                content = f.read()
            self.assertEqual(content, b'Some content')

            # Test backup of file with existing name
            backup_path2 = utils.backup_file(file, backup_dir=tmpdirname)
            # Should have a different filename
            self.assertNotEqual(backup_path, backup_path2)
            self.assertTrue(os.path.exists(backup_path2))

    def test_handle_duplicates_dataframe(self):
        df = pd.DataFrame({
            'A': [1, 2, 2, 3],
            'B': ['x', 'y', 'y', 'z']
        })
        # Remove duplicates
        df_no_dups = utils.handle_duplicates(df, user_choice='remove')
        self.assertEqual(len(df_no_dups), 3)
        # Keep duplicates
        df_keep_dups = utils.handle_duplicates(df, user_choice='keep')
        self.assertEqual(len(df_keep_dups), 4)
        # Invalid choice
        with self.assertRaises(ValueError):
            utils.handle_duplicates(df, user_choice='invalid')

    def test_handle_duplicates_list(self):
        data = [1, 2, 2, 3]
        # Remove duplicates
        data_no_dups = utils.handle_duplicates(data, user_choice='remove')
        self.assertEqual(data_no_dups, [1, 2, 3])
        # Keep duplicates
        data_keep_dups = utils.handle_duplicates(data, user_choice='keep')
        self.assertEqual(data_keep_dups, [1, 2, 2, 3])
        # Invalid choice
        with self.assertRaises(ValueError):
            utils.handle_duplicates(data, user_choice='invalid')

    def test_handle_duplicates_invalid_type(self):
        data = 'not a list or dataframe'
        with self.assertRaises(TypeError):
            utils.handle_duplicates(data, user_choice='remove')

    def test_detect_sensitive_data_dataframe(self):
        df = pd.DataFrame({
            'Emails': ['test@example.com', 'not an email', 'hello@world.com'],
            'SSNs': ['123-45-6789', 'no ssn', '987-65-4321'],
            'Numbers': [1234567890123456, '4111 1111 1111 1111', 'not a cc number']
        })
        sensitive_data = utils.detect_sensitive_data(df)
        self.assertIn('Emails', sensitive_data)
        self.assertEqual(len(sensitive_data['Emails']), 2)
        self.assertIn('SSNs', sensitive_data)
        self.assertEqual(len(sensitive_data['SSNs']), 2)
        self.assertIn('Numbers', sensitive_data)
        self.assertEqual(len(sensitive_data['Numbers']), 2)

    def test_detect_sensitive_data_list(self):
        data = ['test@example.com', '123-45-6789', '4111 1111 1111 1111', 'nothing here']
        sensitive_data = utils.detect_sensitive_data(data)
        self.assertIn('List', sensitive_data)
        self.assertEqual(len(sensitive_data['List']), 3)

    def test_detect_sensitive_data_string(self):
        data = 'Contact me at test@example.com or 123-45-6789'
        sensitive_data = utils.detect_sensitive_data(data)
        self.assertIn('String', sensitive_data)
        self.assertEqual(len(sensitive_data['String']), 2)

    def test_detect_sensitive_data_invalid_type(self):
        data = 12345  # Not a str, list, or DataFrame
        with self.assertRaises(TypeError):
            utils.detect_sensitive_data(data)

if __name__ == '__main__':
    unittest.main()