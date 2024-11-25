# streamlit_app/app/entity_bridge/tests/test_ui_helper.py

import unittest
import pandas as pd
from unittest.mock import patch, MagicMock

# Adjust the import path if necessary
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui_helper import (
    display_file_upload,
    display_missing_data_options,
    display_enriched_data,
    download_enriched_data,
    display_similarity_threshold_setting,
    display_confirmation_dialog,
    display_field_selection,
    display_progress
)

class TestUIHelper(unittest.TestCase):

    @patch('ui_helper.st')
    def test_display_file_upload(self, mock_st):
        """
        Test the display_file_upload function.
        """
        # Mock the necessary Streamlit functions
        mock_st.header = MagicMock()
        mock_st.write = MagicMock()
        mock_st.file_uploader = MagicMock(return_value=[])
        mock_st.warning = MagicMock()

        uploaded_files = display_file_upload()
        # Check that the file_uploader was called
        mock_st.file_uploader.assert_called_once()
        # Check that warning is shown when no files are uploaded
        mock_st.warning.assert_called_once()

        # Test when files are uploaded
        mock_uploaded_file = MagicMock()
        mock_uploaded_file.name = 'test.csv'
        mock_st.file_uploader = MagicMock(return_value=[mock_uploaded_file])
        uploaded_files = display_file_upload()
        self.assertEqual(uploaded_files, [mock_uploaded_file])

    @patch('ui_helper.st')
    def test_display_missing_data_options(self, mock_st):
        """
        Test the display_missing_data_options function.
        """
        # Mock the necessary Streamlit functions
        mock_st.subheader = MagicMock()
        mock_st.selectbox = MagicMock(return_value='Fill missing values with defaults')
        mock_st.text_input = MagicMock(return_value='N/A')
        mock_st.slider = MagicMock(return_value=0.5)

        strategy, default_value, missing_threshold = display_missing_data_options(0, 'test.csv')
        self.assertEqual(strategy, 'fill')
        self.assertEqual(default_value, 'N/A')
        self.assertIsNone(missing_threshold)

        # Test 'remove' strategy
        mock_st.selectbox = MagicMock(return_value='Remove rows with missing values')
        strategy, default_value, missing_threshold = display_missing_data_options(0, 'test.csv')
        self.assertEqual(strategy, 'remove')
        self.assertIsNone(default_value)
        self.assertIsNone(missing_threshold)

        # Test 'skip' strategy
        mock_st.selectbox = MagicMock(return_value='Skip processing fields with excessive missing data')
        strategy, default_value, missing_threshold = display_missing_data_options(0, 'test.csv')
        self.assertEqual(strategy, 'skip')
        self.assertIsNone(default_value)
        self.assertEqual(missing_threshold, 0.5)

    @patch('ui_helper.st')
    def test_display_enriched_data(self, mock_st):
        """
        Test the display_enriched_data function.
        """
        # Mock the necessary Streamlit functions
        mock_st.header = MagicMock()
        mock_st.subheader = MagicMock()
        mock_st.dataframe = MagicMock()

        df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        enriched_data_frames = [df]
        display_enriched_data(enriched_data_frames)
        # Check that dataframe was displayed
        mock_st.dataframe.assert_called_once_with(df.head(20))

    @patch('ui_helper.st')
    def test_download_enriched_data(self, mock_st):
        """
        Test the download_enriched_data function.
        """
        # Mock the necessary Streamlit functions
        mock_st.header = MagicMock()
        mock_st.subheader = MagicMock()
        mock_st.selectbox = MagicMock(return_value='CSV')
        mock_st.download_button = MagicMock()

        df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        enriched_data_frames = [df]
        download_enriched_data(enriched_data_frames)
        # Check that download button was called
        self.assertTrue(mock_st.download_button.called)

    @patch('ui_helper.st')
    def test_display_similarity_threshold_setting(self, mock_st):
        """
        Test the display_similarity_threshold_setting function.
        """
        # Mock the necessary Streamlit functions
        mock_st.subheader = MagicMock()
        mock_st.slider = MagicMock(return_value=0.85)

        threshold = display_similarity_threshold_setting(entity_type='parent', default_threshold=0.9)
        self.assertEqual(threshold, 0.85)

    @patch('ui_helper.st')
    def test_display_confirmation_dialog(self, mock_st):
        """
        Test the display_confirmation_dialog function.
        """
        # Mock the necessary Streamlit functions
        mock_st.write = MagicMock()
        mock_st.radio = MagicMock(return_value='Yes')

        confirmation = display_confirmation_dialog("Do you confirm?", "confirm_key")
        self.assertTrue(confirmation)

        mock_st.radio = MagicMock(return_value='No')
        confirmation = display_confirmation_dialog("Do you confirm?", "confirm_key")
        self.assertFalse(confirmation)

    @patch('ui_helper.st')
    def test_display_field_selection(self, mock_st):
        """
        Test the display_field_selection function.
        """
        # Mock the necessary Streamlit functions
        mock_st.subheader = MagicMock()
        mock_st.selectbox = MagicMock(side_effect=[
            'ParentID',      # Parent ID Field
            'ParentName',    # Parent Name Field
            'None',          # Child ID Field
            'ChildName'      # Child Name Field
        ])
        mock_st.error = MagicMock()
        mock_st.stop = MagicMock()

        df = pd.DataFrame(columns=['ParentID', 'ParentName', 'ChildID', 'ChildName'])
        selected_fields = display_field_selection(df, 'test.csv', 0)
        expected_selected_fields = {
            'parent_id': 'ParentID',
            'parent_name': 'ParentName',
            'child_id': None,
            'child_name': 'ChildName'
        }
        self.assertEqual(selected_fields, expected_selected_fields)

        # Test when Parent ID and Parent Name are the same
        mock_st.selectbox = MagicMock(side_effect=[
            'ParentID',      # Parent ID Field
            'ParentID',      # Parent Name Field (same as Parent ID)
        ])
        # Since st.stop() halts execution, we need to check if st.error was called
        with self.assertRaises(SystemExit):
            selected_fields = display_field_selection(df, 'test.csv', 1)
        mock_st.error.assert_called_once_with("Parent ID Field and Parent Name Field cannot be the same.")

    @patch('ui_helper.st')
    def test_display_progress(self, mock_st):
        """
        Test the display_progress function.
        """
        # Mock the necessary Streamlit functions
        mock_st.write = MagicMock()
        mock_st.progress = MagicMock()

        display_progress("Processing...", 0.5)
        mock_st.write.assert_called_once_with("Processing...")
        mock_st.progress.assert_called_once_with(0.5)

if __name__ == '__main__':
    unittest.main()