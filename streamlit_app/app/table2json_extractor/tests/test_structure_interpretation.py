# tests/test_structure_interpretation.py

"""
test_structure_interpretation.py

Unit tests for the structure_interpretation module.
"""

import unittest
from data_processing import Cell, Table
from structure_interpretation import interpret_table_structure, handle_merged_cells, handle_nested_tables
from exceptions import StructureInterpretationError

class TestStructureInterpretation(unittest.TestCase):
    def test_handle_merged_cells_no_merges(self):
        """
        Test handling of a table without any merged cells.
        """
        # Create a simple 2x2 table
        cell1 = Cell(content='A1')
        cell2 = Cell(content='A2')
        cell3 = Cell(content='B1')
        cell4 = Cell(content='B2')

        table = Table(data=[[cell1, cell2], [cell3, cell4]])

        # Process the table
        processed_table = handle_merged_cells(table)

        # Verify the table structure remains the same
        self.assertEqual(len(processed_table.data), 2)
        self.assertEqual(len(processed_table.data[0]), 2)
        self.assertEqual(processed_table.data[0][0].content, 'A1')
        self.assertEqual(processed_table.data[0][1].content, 'A2')
        self.assertEqual(processed_table.data[1][0].content, 'B1')
        self.assertEqual(processed_table.data[1][1].content, 'B2')

    def test_handle_merged_cells_with_merges(self):
        """
        Test handling of a table with merged cells.
        """
        # Create cells with colspan and rowspan
        cell1 = Cell(content='A1', colspan=2)
        cell2 = Cell(content='B1')
        cell3 = Cell(content='B2')

        table = Table(data=[[cell1], [cell2, cell3]])

        # Process the table
        processed_table = handle_merged_cells(table)

        # Expected grid after handling merges:
        # [cell1, placeholder]
        # [cell2, cell3]

        self.assertEqual(len(processed_table.data), 2)
        self.assertEqual(len(processed_table.data[0]), 2)
        self.assertEqual(processed_table.data[1][0].content, 'B1')
        self.assertEqual(processed_table.data[1][1].content, 'B2')
        self.assertIsNone(processed_table.data[0][1].content)

    def test_handle_nested_tables(self):
        """
        Test handling of a table with a nested table.
        """
        # Nested table inside a cell
        nested_cell1 = Cell(content='Nested A1')
        nested_cell2 = Cell(content='Nested A2')
        nested_table = Table(data=[[nested_cell1, nested_cell2]])

        cell1 = Cell(content='A1', nested_table=nested_table)
        cell2 = Cell(content='A2')

        table = Table(data=[[cell1, cell2]])

        # Process the table
        processed_table = handle_nested_tables(table)

        # Verify that the nested table has been processed (in this case, unchanged)
        self.assertIsNotNone(processed_table.data[0][0].nested_table)
        nested_table_processed = processed_table.data[0][0].nested_table
        self.assertEqual(nested_table_processed.data[0][0].content, 'Nested A1')
        self.assertEqual(nested_table_processed.data[0][1].content, 'Nested A2')

    def test_interpret_table_structure(self):
        """
        Test full interpretation of a table with merged cells and nested tables.
        """
        # Create a complex table
        nested_cell = Cell(content='Nested', colspan=2)
        nested_table = Table(data=[[nested_cell]])

        cell1 = Cell(content='A1', colspan=2)
        cell2 = Cell(content='A2', nested_table=nested_table)
        cell3 = Cell(content='A3')
        cell4 = Cell(content='A4')

        table = Table(data=[[cell1], [cell2, cell3, cell4]])

        # Process the table
        processed_table = interpret_table_structure(table)

        # Verify the structure after processing
        self.assertEqual(len(processed_table.data), 2)
        self.assertEqual(len(processed_table.data[0]), 2)
        self.assertEqual(processed_table.data[0][0].content, 'A1')
        self.assertIsNone(processed_table.data[0][1].content)  # Placeholder due to colspan

        self.assertIsNotNone(processed_table.data[1][0].nested_table)
        self.assertEqual(processed_table.data[1][1].content, 'A3')

    def test_handle_merged_cells_error(self):
        """
        Test handling of errors when merged cells exceed table bounds.
        """
        # Create a cell that exceeds table bounds
        cell1 = Cell(content='A1', rowspan=3)  # Only 2 rows in the table
        cell2 = Cell(content='A2')

        table = Table(data=[[cell1, cell2], [cell2, cell2]])

        with self.assertRaises(StructureInterpretationError):
            handle_merged_cells(table)

    def test_handle_nested_tables_error(self):
        """
        Test handling of errors when nested table processing fails.
        """
        # Create a cell with an invalid nested table
        cell1 = Cell(content='A1', nested_table='NotATableObject')
        cell2 = Cell(content='A2')

        table = Table(data=[[cell1, cell2]])

        with self.assertRaises(StructureInterpretationError):
            handle_nested_tables(table)

if __name__ == '__main__':
    unittest.main()