# streamlit_app/app/entity_bridge/tests/test_data_normalizer.py

import unittest
import pandas as pd

# Adjust the import path if necessary
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_normalizer import (
    normalize_ids,
    normalize_entity_names,
    normalize_data_frames
)

from utils import generate_unique_identifier

class TestDataNormalizer(unittest.TestCase):
    def test_normalize_ids_with_missing_parent_id(self):
        """
        Test that missing Parent IDs are generated when not provided.
        """
        df = pd.DataFrame({
            'ParentName': ['Entity A', 'Entity B', 'Entity C']
        })
        selected_fields = {'parent_id': None, 'parent_name': 'ParentName'}
        df_normalized, updated_fields = normalize_ids(df, selected_fields)

        self.assertIn('generated_parent_id', df_normalized.columns)
        self.assertEqual(len(df_normalized['generated_parent_id'].unique()), 3)
        self.assertEqual(updated_fields['parent_id'], 'generated_parent_id')

    def test_normalize_ids_with_existing_parent_id_and_missing_values(self):
        """
        Test that missing Parent IDs are filled using forward fill.
        """
        df = pd.DataFrame({
            'ParentID': ['P1', None, 'P3'],
            'ParentName': ['Entity A', 'Entity B', 'Entity C']
        })
        selected_fields = {'parent_id': 'ParentID', 'parent_name': 'ParentName'}
        df_normalized, updated_fields = normalize_ids(df, selected_fields)

        self.assertFalse(df_normalized['ParentID'].isnull().any())
        self.assertEqual(df_normalized.loc[1, 'ParentID'], 'P1')

    def test_normalize_ids_generate_child_id(self):
        """
        Test that Child IDs are generated when not provided.
        """
        df = pd.DataFrame({
            'ParentID': ['P1', 'P2', 'P3'],
            'ParentName': ['Entity A', 'Entity B', 'Entity C'],
            'ChildName': ['Child A', 'Child B', 'Child C']
        })
        selected_fields = {
            'parent_id': 'ParentID',
            'parent_name': 'ParentName',
            'child_id': None,
            'child_name': 'ChildName'
        }
        df_normalized, updated_fields = normalize_ids(df, selected_fields)

        self.assertIn('generated_child_id', df_normalized.columns)
        self.assertEqual(len(df_normalized['generated_child_id'].unique()), 3)
        self.assertEqual(updated_fields['child_id'], 'generated_child_id')

    def test_normalize_entity_names_basic(self):
        """
        Test normalization of entity names without custom stopwords.
        """
        df = pd.DataFrame({
            'ParentName': ['Entity Inc.', 'Company LLC', 'Corporation Corp.']
        })
        selected_fields = {'parent_name': 'ParentName'}
        df_normalized = normalize_entity_names(df, selected_fields)

        self.assertIn('ParentName_original', df_normalized.columns)
        expected = ['ENTITY', 'COMPANY', 'CORPORATION']
        self.assertListEqual(df_normalized['ParentName'].tolist(), expected)

    def test_normalize_entity_names_with_custom_stopwords(self):
        """
        Test normalization of entity names with custom stopwords.
        """
        df = pd.DataFrame({
            'ParentName': ['The Best Entity', 'A Great Company', 'An Awesome Organization']
        })
        selected_fields = {'parent_name': 'ParentName'}
        custom_stopwords = ['THE', 'A', 'AN']
        df_normalized = normalize_entity_names(df, selected_fields, custom_stopwords)

        expected = ['BEST ENTITY', 'GREAT COMPANY', 'AWESOME ORGANIZATION']
        self.assertListEqual(df_normalized['ParentName'].tolist(), expected)

    def test_normalize_entity_names_preserve_original(self):
        """
        Test that original names are preserved with '_original' suffix.
        """
        df = pd.DataFrame({
            'ParentName': ['Entity One', 'Entity Two', 'Entity Three']
        })
        selected_fields = {'parent_name': 'ParentName'}
        df_normalized = normalize_entity_names(df, selected_fields)

        self.assertIn('ParentName_original', df_normalized.columns)
        self.assertListEqual(df_normalized['ParentName_original'].tolist(), ['Entity One', 'Entity Two', 'Entity Three'])
        self.assertListEqual(df_normalized['ParentName'].tolist(), ['ENTITY ONE', 'ENTITY TWO', 'ENTITY THREE'])

    def test_normalize_data_frames(self):
        """
        Test normalization of multiple data frames.
        """
        df1 = pd.DataFrame({
            'ParentID': ['P1', None],
            'ParentName': ['Entity A Inc.', 'Entity B LLC']
        })
        selected_fields1 = {'parent_id': 'ParentID', 'parent_name': 'ParentName'}

        df2 = pd.DataFrame({
            'ParentName': ['Entity C Corp.', 'Entity D']
        })
        selected_fields2 = {'parent_id': None, 'parent_name': 'ParentName'}

        data_frames = [(df1, selected_fields1), (df2, selected_fields2)]
        normalized_data_frames = normalize_data_frames(data_frames)

        df1_normalized, selected_fields1_updated = normalized_data_frames[0]
        df2_normalized, selected_fields2_updated = normalized_data_frames[1]

        # Test df1 normalization
        self.assertFalse(df1_normalized['ParentID'].isnull().any())
        self.assertIn('ParentName_original', df1_normalized.columns)
        expected_names_df1 = ['ENTITY A', 'ENTITY B']
        self.assertListEqual(df1_normalized['ParentName'].tolist(), expected_names_df1)

        # Test df2 normalization
        self.assertIn('generated_parent_id', df2_normalized.columns)
        self.assertIn('ParentName_original', df2_normalized.columns)
        expected_names_df2 = ['ENTITY C', 'ENTITY D']
        self.assertListEqual(df2_normalized['ParentName'].tolist(), expected_names_df2)

        # Test updated selected_fields
        self.assertEqual(selected_fields1_updated['parent_id'], 'ParentID')
        self.assertEqual(selected_fields2_updated['parent_id'], 'generated_parent_id')

if __name__ == '__main__':
    unittest.main()