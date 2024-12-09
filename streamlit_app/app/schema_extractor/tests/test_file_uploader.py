# schema_extractor/tests/test_file_uploader.py

import unittest
from unittest.mock import patch, MagicMock
from schema_extractor.file_uploader import upload_files

class TestFileUploader(unittest.TestCase):
    """
    Test cases for the file_uploader module.
    """

    @patch('schema_extractor.file_uploader.st')
    @patch('schema_extractor.utils.detect_file_type')
    def test_no_files_uploaded(self, mock_detect_file_type, mock_st):
        """
        Test the behavior when no files are uploaded.
        """
        # Mock the file_uploader to return None
        mock_st.file_uploader.return_value = None

        uploaded_files, file_type_category = upload_files()

        self.assertIsNone(uploaded_files)
        self.assertIsNone(file_type_category)
        mock_st.info.assert_called_with("Please upload one or more files to proceed.")

    @patch('schema_extractor.file_uploader.st')
    @patch('schema_extractor.utils.detect_file_type')
    def test_single_valid_file(self, mock_detect_file_type, mock_st):
        """
        Test uploading a single valid file.
        """
        # Mock the uploaded file and detect_file_type function
        mock_file = MagicMock()
        mock_file.name = 'test.csv'
        mock_st.file_uploader.return_value = [mock_file]
        mock_detect_file_type.return_value = 'tabular'

        uploaded_files, file_type_category = upload_files()

        self.assertEqual(uploaded_files, [mock_file])
        self.assertEqual(file_type_category, 'tabular')
        mock_st.success.assert_called_once()
        mock_st.write.assert_called_with("Detected file type category: **tabular**")

    @patch('schema_extractor.file_uploader.st')
    @patch('schema_extractor.utils.detect_file_type')
    def test_multiple_files_same_type(self, mock_detect_file_type, mock_st):
        """
        Test uploading multiple files of the same type category.
        """
        # Mock the uploaded files and detect_file_type function
        mock_file1 = MagicMock()
        mock_file1.name = 'test1.csv'
        mock_file2 = MagicMock()
        mock_file2.name = 'test2.csv'
        mock_st.file_uploader.return_value = [mock_file1, mock_file2]
        mock_detect_file_type.return_value = 'tabular'

        uploaded_files, file_type_category = upload_files()

        self.assertEqual(uploaded_files, [mock_file1, mock_file2])
        self.assertEqual(file_type_category, 'tabular')
        mock_st.success.assert_called_once()
        mock_st.write.assert_called_with("Detected file type category: **tabular**")

    @patch('schema_extractor.file_uploader.st')
    @patch('schema_extractor.utils.detect_file_type')
    def test_files_different_types(self, mock_detect_file_type, mock_st):
        """
        Test uploading files of different type categories.
        """
        # Mock the uploaded files and their detected types
        mock_file1 = MagicMock()
        mock_file1.name = 'test.csv'
        mock_file2 = MagicMock()
        mock_file2.name = 'test.json'
        mock_st.file_uploader.return_value = [mock_file1, mock_file2]
        mock_detect_file_type.side_effect = ['tabular', 'serialized']

        uploaded_files, file_type_category = upload_files()

        self.assertIsNone(uploaded_files)
        self.assertIsNone(file_type_category)
        mock_st.warning.assert_called_with(
            "All uploaded files must be of the same type category (e.g., all tabular files, or all serialized data files)."
        )

    @patch('schema_extractor.file_uploader.st')
    @patch('schema_extractor.utils.detect_file_type')
    def test_unsupported_file_type(self, mock_detect_file_type, mock_st):
        """
        Test uploading a file with an unsupported type.
        """
        # Mock the uploaded file and detect_file_type function
        mock_file = MagicMock()
        mock_file.name = 'test.exe'
        mock_st.file_uploader.return_value = [mock_file]
        mock_detect_file_type.return_value = 'unknown'

        uploaded_files, file_type_category = upload_files()

        self.assertIsNone(uploaded_files)
        self.assertIsNone(file_type_category)
        mock_st.warning.assert_called_with(
            f"File '{mock_file.name}' has an unsupported file type or cannot be processed."
        )

if __name__ == '__main__':
    unittest.main()