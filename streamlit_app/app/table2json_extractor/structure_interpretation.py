# structure_interpretation.py

"""
structure_interpretation.py

Module responsible for interpreting the structure of extracted tables,
particularly handling complexities such as merged cells, nested tables, and
irregular table structures.

Functions:
- interpret_table_structure: Main function that applies interpretation rules.
- handle_merged_cells: Processes merged cells in tables.
- handle_nested_tables: Processes nested tables within cells.
- handle_irregular_tables: Normalizes irregular tables to consistent structures.

Dependencies:
- data_processing: For Table and Cell classes.
- exceptions: For custom exception classes.
"""

from typing import List, Dict, Any, Optional
from copy import deepcopy

# Importing custom classes and exceptions
from .data_processing import Table, Cell
from .exceptions import (
    StructureInterpretationError,
    MergedCellError,
    NestedTableParsingError,
)

# Logging
import logging

# Initialize logger
logger = logging.getLogger(__name__)
# Configure logger if not already configured
if not logger.hasHandlers():
    logger.setLevel(logging.DEBUG)
    # Configure logging handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    ch.setFormatter(formatter)
    # Add the handler to the logger
    logger.addHandler(ch)


def interpret_table_structure(table: Table, parameters) -> Table:
    """
    Interprets the structure of a table according to the specified parameters.

    Parameters:
        table (Table):
            The Table object to be interpreted.
        parameters (ExtractionParameters):
            Parameters guiding the interpretation.

    Returns:
        Table:
            The Table object with structure interpreted as per the parameters.

    Raises:
        StructureInterpretationError:
            If an error occurs during structure interpretation.
    """
    try:
        logger.debug(f"Interpreting structure for table at position {table.position}")
        # Deep copy the table to avoid modifying the original
        interpreted_table = deepcopy(table)

        # Handle merged cells if specified
        if parameters.structure_interpretation.handle_merged_cells:
            interpreted_table = handle_merged_cells(interpreted_table)

        # Handle nested tables if specified
        if parameters.structure_interpretation.handle_nested_tables:
            interpreted_table = handle_nested_tables(interpreted_table, parameters)

        # Handle irregular tables if parameters specify
        if parameters.structure_interpretation.handle_irregular_structures:
            interpreted_table = handle_irregular_tables(interpreted_table)

        return interpreted_table
    except Exception as e:
        logger.exception("Error interpreting table structure")
        raise StructureInterpretationError(f"Error interpreting table structure: {str(e)}")


def handle_merged_cells(table: Table) -> Table:
    """
    Processes merged cells in a table and adjusts the data structure accordingly.

    Parameters:
        table (Table):
            The Table object containing raw data with merged cells.

    Returns:
        Table:
            A new Table object with merged cells properly expanded.

    Raises:
        MergedCellError:
            If an error occurs during merged cell handling.
    """
    try:
        logger.debug(f"Handling merged cells in table at position {table.position}")
        data = table.data
        max_rows = len(data)
        max_cols = max(len(row) for row in data)

        # Initialize grid with None
        grid = [[None for _ in range(max_cols)] for _ in range(max_rows)]

        for row_idx, row in enumerate(data):
            col_idx = 0
            for cell in row:
                # Find the next available position in grid
                while col_idx < max_cols and grid[row_idx][col_idx] is not None:
                    col_idx += 1
                if col_idx >= max_cols:
                    logger.error("Column index exceeds max columns in merged cell handling")
                    raise MergedCellError("Column index exceeds max columns")

                rowspan = cell.rowspan
                colspan = cell.colspan

                for r in range(rowspan):
                    for c in range(colspan):
                        current_row = row_idx + r
                        current_col = col_idx + c
                        if current_row >= max_rows or current_col >= max_cols:
                            logger.error("Cell span exceeds table dimensions during merged cell handling")
                            raise MergedCellError("Cell span exceeds table dimensions")
                        if grid[current_row][current_col] is None:
                            # Assign the cell to the spanned positions
                            if r == 0 and c == 0:
                                # Use the original cell for the first position
                                grid[current_row][current_col] = cell
                            else:
                                # Use a placeholder or clone for spanned positions
                                spanned_cell = Cell(
                                    content='',
                                    rowspan=1,
                                    colspan=1,
                                    styles=cell.styles.copy(),
                                    nested_table=deepcopy(cell.nested_table) if cell.nested_table else None
                                )
                                grid[current_row][current_col] = spanned_cell
                        else:
                            logger.error("Overlapping cells detected during merged cell handling")
                            raise MergedCellError("Overlapping cells detected")

                col_idx += colspan

        # Update table data
        table.data = grid
        return table
    except Exception as e:
        logger.exception("Error handling merged cells")
        raise MergedCellError(f"Error handling merged cells: {str(e)}")


def handle_nested_tables(table: Table, parameters) -> Table:
    """
    Processes nested tables within a table and represents them appropriately.

    Parameters:
        table (Table):
            The Table object that may contain nested tables.
        parameters (ExtractionParameters):
            Extraction parameters guiding interpretation.

    Returns:
        Table:
            The Table object with nested tables processed and represented.

    Raises:
        NestedTableParsingError:
            If an error occurs during nested table handling.
    """
    try:
        logger.debug(f"Handling nested tables in table at position {table.position}")
        for row in table.data:
            for cell in row:
                if cell.nested_table:
                    # Process each nested table
                    processed_nested_tables = []
                    for nested_table in cell.nested_table:
                        logger.debug("Processing nested table within cell")
                        interpreted_nested_table = interpret_table_structure(nested_table, parameters)
                        processed_nested_tables.append(interpreted_nested_table)
                    cell.nested_table = processed_nested_tables
        return table
    except Exception as e:
        logger.exception("Error handling nested tables")
        raise NestedTableParsingError(f"Error handling nested tables: {str(e)}")


def handle_irregular_tables(table: Table) -> Table:
    """
    Handles irregular table structures by normalizing them.

    Parameters:
        table (Table):
            The Table object that may have irregular structures.

    Returns:
        Table:
            The Table object normalized, with all rows having the same number of columns.

    Raises:
        StructureInterpretationError:
            If an error occurs during irregular table handling.
    """
    try:
        logger.debug(f"Handling irregular tables at position {table.position}")
        # Find the maximum number of columns
        max_cols = max(len(row) for row in table.data)
        logger.debug(f"Maximum columns in table: {max_cols}")

        # Normalize each row to have the same number of columns
        for row_idx, row in enumerate(table.data):
            current_cols = len(row)
            if current_cols < max_cols:
                # Append empty Cells to match max_cols
                missing_cols = max_cols - current_cols
                logger.debug(f"Row {row_idx} has {current_cols} columns; adding {missing_cols} empty cells to match max columns.")
                row.extend([Cell(content='') for _ in range(missing_cols)])
        return table
    except Exception as e:
        logger.exception("Error handling irregular tables")
        raise StructureInterpretationError(f"Error handling irregular tables: {str(e)}")