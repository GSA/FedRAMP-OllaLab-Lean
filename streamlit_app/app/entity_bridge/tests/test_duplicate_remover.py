# streamlit_app/app/entity_bridge/tests/test_duplicate_remover.py

import unittest
import pandas as pd

# Adjust the import path if necessary
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from duplicate_remover import identify_duplicates, remove_duplicates, remove_duplicates_from_data_frames

# Mock streamlit functions for testing purposes
import streamlit as st
from unittest.mock import MagicMock
st.write = MagicMock()
st.header = MagicMock()

class TestDuplicateRemover(unittest.TestCase):
    def test_identify_duplicates_no_duplicates(self):
        """
        Test identifying duplicates when there are none.
        """
        df = pd.DataFrame({
            'ParentID': ['P1', 'P2', 'P3'],
            'ParentName': ['Entity A', 'Entity B', 'Entity C'],
            'ChildID': ['C1', 'C2', 'C3'],
            'ChildName': ['Child A', 'Child B', 'Child C']
        })
        selected_fields = {
            'parent_id': 'ParentID',
            'parent_name': 'ParentName',
            'child_id': 'ChildID',
            'child_name': 'ChildName'
        }
        duplicates = identify_duplicates(df, selected_fields)
        self.assertTrue(duplicates.empty)

    def test_identify_duplicates_with_duplicates(self):
        """
        Test identifying duplicates when duplicates are present.
        """
        df = pd.DataFrame({
            'ParentID': ['P1', 'P1', 'P3'],
            'ParentName': ['Entity A', 'Entity A', 'Entity C'],
            'ChildID': ['C1', 'C1', 'C3'],
            'ChildName': ['Child A', 'Child A', 'Child C']
        })
        selected_fields = {
            'parent_id': 'ParentID',
            'parent_name': 'ParentName',
            'child_id': 'ChildID',
            'child_name': 'ChildName'
        }
        duplicates = identify_duplicates(df, selected_fields)
        self.assertEqual(len(duplicates), 2)

    def test_remove_duplicates_no_duplicates(self):
        """
        Test removing duplicates when there are none.
        """
        df = pd.DataFrame({
            'ParentID': ['P1', 'P2', 'P3'],
            'ParentName': ['Entity A', 'Entity B', 'Entity C'],
            'ChildID': ['C1', 'C2', 'C3'],
            'ChildName': ['Child A', 'Child B', 'Child C']
        })
        selected_fields = {
            'parent_id': 'ParentID',
            'parent_name': 'ParentName',
            'child_id': 'ChildID',
            'child_name': 'ChildName'
        }
        df_no_duplicates = remove_duplicates(df, selected_fields)
        self.assertEqual(len(df_no_duplicates), len(df))

    def test_remove_duplicates_with_duplicates(self):
        """
        Test removing duplicates when duplicates are present.
        """
        df = pd.DataFrame({
            'ParentID': ['P1', 'P1', 'P3', 'P3'],
            'ParentName': ['Entity A', 'Entity A', 'Entity C', 'Entity C'],
            'ChildID': ['C1', 'C1', 'C3', 'C3'],
            'ChildName': ['Child A', 'Child A', 'Child C', 'Child C']
        })
        selected_fields = {
            'parent_id': 'ParentID',
            'parent_name': 'ParentName',
            'child_id': 'ChildID',
            'child_name': 'ChildName'
        }
        df_no_duplicates = remove_duplicates(df, selected_fields)
        self.assertEqual(len(df_no_duplicates), 2)
        # Check that duplicates have been removed
        expected_df = df_no_duplicates.reset_index(drop=True)
        expected_data = {
            'ParentID': ['P1', 'P3'],
            'ParentName': ['Entity A', 'Entity C'],
            'ChildID': ['C1', 'C3'],
            'ChildName': ['Child A', 'Child C']
        }
        expected_df_expected = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(expected_df, expected_df_expected)

    def test_remove_duplicates_from_data_frames(self):
        """
        Test removing duplicates from multiple DataFrames.
        """
        df1 = pd.DataFrame({
            'ParentID': ['P1', 'P1', 'P2'],
            'ParentName': ['Entity A', 'Entity A', 'Entity B'],
        })
        selected_fields1 = {
            'parent_id': 'ParentID',
            'parent_name': 'ParentName',
        }
        df2 = pd.DataFrame({
            'ParentID': ['P3', 'P3', 'P4'],
            'ParentName': ['Entity C', 'Entity C', 'Entity D'],
        })
        selected_fields2 = {
            'parent_id': 'ParentID',
            'parent_name': 'ParentName',
        }
        data_frames = [(df1, selected_fields1), (df2, selected_fields2)]
        deduplicated_data_frames = remove_duplicates_from_data_frames(data_frames)
        df1_deduped, _ = deduplicated_data_frames[0]
        df2_deduped, _ = deduplicated_data_frames[1]
        self.assertEqual(len(df1_deduped), 2)
        self.assertEqual(len(df2_deduped), 2)

if __name__ == '__main__':
    unittest.main()