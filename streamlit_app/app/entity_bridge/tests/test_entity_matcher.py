# streamlit_app/app/entity_bridge/tests/test_entity_matcher.py

import unittest
import pandas as pd
from collections import defaultdict

# Adjust the import path if necessary
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from entity_matcher import (
    compute_similarity_scores,
    automated_entity_matching,
    construct_unique_entity_list,
    enrich_data_frames_with_unique_ids
)

# Mock streamlit functions for testing purposes
import streamlit as st
from unittest.mock import MagicMock
st.write = MagicMock()
st.slider = MagicMock(return_value=0.9)
st.progress = MagicMock(return_value=MagicMock())
st.radio = MagicMock(return_value='Yes, same entity')

# Import utilities
from utils import calculate_similarity, generate_unique_identifier

class TestEntityMatcher(unittest.TestCase):

    def setUp(self):
        # Prepare sample DataFrames
        self.df1 = pd.DataFrame({
            'ParentName': ['Apple Inc', 'Google LLC', 'Amazon.com'],
            'ChildName': ['iPhone', 'Search', 'Online Shopping']
        })
        self.selected_fields1 = {'parent_name': 'ParentName', 'child_name': 'ChildName'}

        self.df2 = pd.DataFrame({
            'ParentName': ['Apple Incorporated', 'Google', 'Amazon'],
            'ChildName': ['iPad', 'Maps', 'Prime Video']
        })
        self.selected_fields2 = {'parent_name': 'ParentName', 'child_name': 'ChildName'}

        self.data_frames = [(self.df1, self.selected_fields1), (self.df2, self.selected_fields2)]

    def test_compute_similarity_scores(self):
        similarity_df = compute_similarity_scores(self.data_frames, 'parent_name')
        # Check that the similarity_df has the expected columns
        self.assertListEqual(sorted(similarity_df.columns.tolist()), ['EntityA', 'EntityB', 'SimilarityScore'])
        # Check that the DataFrame is not empty
        self.assertTrue(not similarity_df.empty)

    def test_automated_entity_matching(self):
        # Prepare a small similarity_df for testing
        similarity_df = pd.DataFrame({
            'EntityA': ['Apple Inc', 'Apple Inc'],
            'EntityB': ['Apple Incorporated', 'Google LLC'],
            'SimilarityScore': [0.95, 0.2]
        })
        threshold = 0.9
        entity_groups = automated_entity_matching(similarity_df, threshold)
        self.assertEqual(entity_groups['Apple Inc'], entity_groups['Apple Incorporated'])
        self.assertNotEqual(entity_groups['Apple Inc'], entity_groups['Google LLC'])

    def test_construct_unique_entity_list(self):
        unique_parents_df = construct_unique_entity_list(self.data_frames, 'parent')
        # Check that the DataFrame has the expected columns
        self.assertListEqual(sorted(unique_parents_df.columns.tolist()), ['ParentName', 'UniqueParentID'])
        # Check that unique identifiers are assigned
        self.assertEqual(len(unique_parents_df), len(unique_parents_df['UniqueParentID'].unique()))

    def test_enrich_data_frames_with_unique_ids(self):
        # Construct unique parent list
        unique_parents_df = pd.DataFrame({
            'ParentName': ['Apple Inc', 'Apple Incorporated', 'Google LLC', 'Google', 'Amazon.com', 'Amazon'],
            'UniqueParentID': ['UID1', 'UID1', 'UID2', 'UID2', 'UID3', 'UID3']
        })
        enriched_data_frames = enrich_data_frames_with_unique_ids(self.data_frames, unique_parents_df, entity_type='parent')

        # Check that the enriched data frames have the UniqueParentID column
        for df in enriched_data_frames:
            self.assertIn('UniqueParentID', df.columns)
            self.assertTrue(df['UniqueParentID'].notnull().all())

        # Verify that 'Apple Inc' and 'Apple Incorporated' have the same UniqueParentID
        uid_df1 = enriched_data_frames[0][enriched_data_frames[0]['ParentName'] == 'Apple Inc']['UniqueParentID'].iloc[0]
        uid_df2 = enriched_data_frames[1][enriched_data_frames[1]['ParentName'] == 'Apple Incorporated']['UniqueParentID'].iloc[0]
        self.assertEqual(uid_df1, uid_df2)

    def test_construct_unique_parent_list(self):
        unique_parents_df = construct_unique_entity_list(self.data_frames, 'parent')
        # Mocking calculate_similarity to ensure deterministic behavior
        with unittest.mock.patch('entity_matcher.calculate_similarity', return_value=0.95):
            entity_groups = automated_entity_matching(unique_parents_df, 0.9)
            # Check that similar entities are grouped together

    def test_construct_unique_child_list(self):
        unique_children_df = construct_unique_entity_list(self.data_frames, 'child')
        # Check that the DataFrame has the expected columns
        self.assertListEqual(sorted(unique_children_df.columns.tolist()), ['ChildName', 'UniqueChildID'])
        # Check that unique identifiers are assigned
        self.assertEqual(len(unique_children_df), len(unique_children_df['UniqueChildID'].unique()))

    def test_enrich_data_frames_with_unique_parent_and_child_ids(self):
        # Construct unique parent list
        unique_parents_df = pd.DataFrame({
            'ParentName': ['Apple Inc', 'Apple Incorporated', 'Google LLC', 'Google', 'Amazon.com', 'Amazon'],
            'UniqueParentID': ['UID1', 'UID1', 'UID2', 'UID2', 'UID3', 'UID3']
        })
        # Construct unique child list
        unique_children_df = pd.DataFrame({
            'ChildName': ['iPhone', 'iPad', 'Search', 'Maps', 'Online Shopping', 'Prime Video'],
            'UniqueChildID': ['CID1', 'CID1', 'CID2', 'CID2', 'CID3', 'CID3']
        })
        enriched_data_frames = enrich_data_frames_with_unique_ids(
            self.data_frames, unique_parents_df, unique_children_df)

        # Check that the enriched data frames have both UniqueParentID and UniqueChildID columns
        for df in enriched_data_frames:
            self.assertIn('UniqueParentID', df.columns)
            self.assertIn('UniqueChildID', df.columns)
            self.assertTrue(df['UniqueParentID'].notnull().all())
            self.assertTrue(df['UniqueChildID'].notnull().all())

        # Verify that entities are correctly enriched
        uid_df1 = enriched_data_frames[0][enriched_data_frames[0]['ParentName'] == 'Apple Inc']['UniqueParentID'].iloc[0]
        cid_df1 = enriched_data_frames[0][enriched_data_frames[0]['ChildName'] == 'iPhone']['UniqueChildID'].iloc[0]
        self.assertEqual(uid_df1, 'UID1')
        self.assertEqual(cid_df1, 'CID1')

if __name__ == '__main__':
    unittest.main()