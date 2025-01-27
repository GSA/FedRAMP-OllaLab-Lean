# structure_interpretation.py

from typing import List, Dict, Any, Optional
from copy import deepcopy

# Importing custom classes and exceptions
from .data_processing import Table, Cell
from .exceptions import StructureInterpretationError, MergedCellError, NestedTableParsingError

# Logging
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# You can configure logging handlers here (e.g., StreamHandler, FileHandler)

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
        logger.debug("Handling merged cells in table")
        data = table.data
        max_rows = len(data)
        max_cols = max(len(row) for row in data)

        grid = [[None for _ in range(max_cols)] for _ in range(max_rows)]

        for i, row in enumerate(data):
            col_index = 0
            for cell in row:
                while col_index < max_cols and grid[i][col_index] is not None:
                    col_index += 1
                if col_index >= max_cols:
                    logger.error("Column index exceeds max columns")
                    raise MergedCellError("Column index exceeds max columns")

                rowspan = getattr(cell, 'rowspan', 1)
                colspan = getattr(cell, 'colspan', 1)

                for rowspan_index in range(rowspan):
                    for colspan_index in range(colspan):
                        r = i + rowspan_index
                        c = col_index + colspan_index
                        if r >= max_rows or c >= max_cols:
                            logger.error("Cell span exceeds table dimensions")
                            raise MergedCellError("Cell span exceeds table dimensions")
                        if grid[r][c] is None:
                            # Clone the cell for each spanned position if needed
                            spanned_cell = deepcopy(cell)
                            grid[r][c] = spanned_cell
                        else:
                            logger.error("Overlapping cells detected")
                            raise MergedCellError("Overlapping cells detected")

                col_index += colspan

        # Remove any fully empty rows
        grid = [row for row in grid if any(cell is not None for cell in row)]

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
        logger.debug("Handling nested tables in table")
        for row in table.data:
            for cell in row:
                if getattr(cell, 'nested_table', None):
                    # Recursively process nested tables
                    nested_tables = []
                    for nested_table in cell.nested_table:
                        interpreted_nested_table = interpret_table_structure(nested_table, parameters)
                        nested_tables.append(interpreted_nested_table)
                    cell.nested_table = nested_tables
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
            The Table object normalized.

    Raises:
        StructureInterpretationError:
            If an error occurs during irregular table handling.
    """
    try:
        logger.debug("Handling irregular tables")
        # Find the maximum number of columns
        max_cols = max(len(row) for row in table.data)

        # Normalize each row to have the same number of columns
        for row in table.data:
            current_cols = len(row)
            if current_cols < max_cols:
                # Append empty Cells to match max_cols
                missing_cols = max_cols - current_cols
                row.extend([Cell(content='')] * missing_cols)

        return table
    except Exception as e:
        logger.exception("Error handling irregular tables")
        raise StructureInterpretationError(f"Error handling irregular tables: {str(e)}")