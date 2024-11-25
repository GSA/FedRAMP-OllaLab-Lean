# tests/test_data_loader.py

import unittest
import pandas as pd
import sys
import os
import io

# Adjust the import path if necessary
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'entity_bridge')))

from data_loader import load_data, handle_missing_data

class TestDataLoader(unittest.TestCase):
    def test_load_data_csv(self):
        """
        Test loading a CSV file.
        """
        csv_content = "col1,col2,col3\n1,2,3\n4,5,6\n"
        csv_file = io.StringIO(csv_content)
        csv_file.name = 'test.csv'
        df = load_data(csv_file)
        self.assertEqual(len(df), 2)
        self.assertListEqual(df.columns.tolist(), ['col1', 'col2', 'col3'])

    def test_load_data_tsv(self):
        """
        Test loading a TSV file.
        """
        tsv_content = "col1\tcol2\tcol3\n1\t2\t3\n4\t5\t6\n"
        tsv_file = io.StringIO(tsv_content)
        tsv_file.name = 'test.tsv'
        df = load_data(tsv_file)
        self.assertEqual(len(df), 2)
        self.assertListEqual(df.columns.tolist(), ['col1', 'col2', 'col3'])

    def test_load_data_xlsx(self):
        """
        Test loading an XLSX file.
        """
        # Create a sample DataFrame
        df_original = pd.DataFrame({'col1': [1,4], 'col2': [2,5], 'col3': [3,6]})
        xlsx_file = io.BytesIO()
        df_original.to_excel(xlsx_file, index=False)
        xlsx_file.seek(0)
        xlsx_file.name = 'test.xlsx'
        df = load_data(xlsx_file)
        self.assertEqual(len(df), 2)
        self.assertListEqual(df.columns.tolist(), ['col1', 'col2', 'col3'])

    def test_load_data_unsupported_format(self):
        """
        Test that loading an unsupported file format raises ValueError.
        """
        content = "some content"
        txt_file = io.StringIO(content)
        txt_file.name = 'test.txt'
        with self.assertRaises(ValueError):
            load_data(txt_file)

    def test_handle_missing_data_remove(self):
        """
        Test handling missing data with the 'remove' strategy.
        """
        df = pd.DataFrame({
            'A': [1, 2, None],
            'B': [4, None, 6],
            'C': [7, 8, 9]
        })
        df_handled = handle_missing_data(df, 'remove')
        self.assertEqual(len(df_handled), 1)
        self.assertEqual(df_handled.isnull().sum().sum(), 0)

    def test_handle_missing_data_fill(self):
        """
        Test handling missing data with the 'fill' strategy.
        """
        df = pd.DataFrame({
            'A': [1, 2, None],
            'B': [4, None, 6],
            'C': [7, 8, 9]
        })
        df_handled = handle_missing_data(df, 'fill', default_value=0)
        self.assertEqual(df_handled.isnull().sum().sum(), 0)
        self.assertEqual(df_handled.loc[2,'A'], 0)
        self.assertEqual(df_handled.loc[1,'B'], 0)

    def test_handle_missing_data_skip(self):
        """
        Test handling missing data with the 'skip' strategy.
        """
        df = pd.DataFrame({
            'A': [1, None, None],
            'B': [4, None, 6],
            'C': [None, None, None],
            'D': [7, 8, 9]
        })
        df_handled = handle_missing_data(df, 'skip', missing_threshold=0.5)
        self.assertListEqual(df_handled.columns.tolist(), ['B', 'D'])

    def test_handle_missing_data_invalid_strategy(self):
        """
        Test that an invalid strategy raises ValueError.
        """
        df = pd.DataFrame({'A': [1, 2, 3]})
        with self.assertRaises(ValueError):
            handle_missing_data(df, 'unknown_strategy')

if __name__ == '__main__':
    unittest.main()