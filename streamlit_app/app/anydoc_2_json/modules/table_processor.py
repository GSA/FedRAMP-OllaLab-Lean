# app/anydoc_2_json/modules/table_processor.py

import os
import json
import re
import copy
from .logger_manager import LoggerManager

class TableProcessor:
    """
    TableProcessor class for processing and enriching table data from JSON representation
    of Markdown files.

    This class processes the tables found in the JSON data, resolves spanning cell issues,
    merges multi-page tables, identifies key-value pairs based on table structure, and
    updates the JSON data accordingly.

    Dependencies:
        - Built-in `os` module for file system interactions.
        - Built-in `json` module for JSON serialization.
        - Built-in `re` module for regular expressions processing.
        - `copy` module for deep copying data structures.
        - `LoggerManager` class for logging functionalities.

    Upstream functions:
        - The main program or modules that need to process table data in JSON files.

    Downstream functions:
        - `process_tables`
        - Other helper methods for processing tables.

    """

    def __init__(self, json_data: dict, output_folder: str, logger: LoggerManager):
        """
        Initialize the TableProcessor instance.

        Parameters:
            json_data (dict):
                The JSON data containing the parsed Markdown content including tables.
            output_folder (str):
                The path to the output folder where the updated JSON file will be saved.
            logger (LoggerManager):
                An instance of LoggerManager for logging.

        Returns:
            None

        Raises:
            FileNotFoundError:
                If the output folder does not exist and cannot be created.
            PermissionError:
                If the program lacks permissions to create the output folder or write to it.

        Dependencies:
            - `os.makedirs` to create directories if they do not exist.
            - `logger` to log messages.

        Upstream functions:
            - Called by the main program or module that needs to process table data.

        Downstream functions:
            - None

        """
        self.json_data = json_data
        self.output_folder = output_folder
        self.logger = logger.get_logger()
        self.logger_manager = logger  # Keep a reference to log exceptions

        # Ensure the output directory exists
        if not os.path.exists(self.output_folder):
            try:
                os.makedirs(self.output_folder)
            except Exception as e:
                self.logger_manager.log_exception(e, context_message="Failed to create the output folder.",
                                                  file_name=self.output_folder)
                raise FileNotFoundError(f"Cannot create output directory '{self.output_folder}': {e}")

    def process_tables(self):
        """
        Processes the tables in the JSON data by resolving spanning cells, merging multi-page
        tables, identifying key-value pairs based on table structure, and updating the JSON data.

        This method modifies the `json_data` in-place, and prepares it for saving.

        Parameters:
            None

        Returns:
            None

        Raises:
            Exception:
                If an error occurs during processing, it is logged and re-raised.

        Dependencies:
            - `resolve_spanning_cells` to fix cell spanning issues.
            - `merge_multipage_tables` to merge tables with identical headers.
            - `identify_key_value_pairs` to convert tables into key-value pairs.
            - `update_json_data` to replace tables in `json_data` with processed data.

        Upstream functions:
            - Called by the main program or module to process tables.

        Downstream functions:
            - `resolve_spanning_cells`
            - `merge_multipage_tables`
            - `identify_key_value_pairs`
            - `update_json_data`

        """
        try:
            # Extract all tables from json_data
            table_paths = [
                ('document', 'content', 'content_text1', 'table'),
                ('document', 'content', 'content_text2', 'table')
            ]
            # Collect table paths for sections and subsections
            if 'section' in self.json_data['document']['content']:
                for i, section in enumerate(self.json_data['document']['content']['section']):
                    table_paths.append(('document', 'content', 'section', i, 'section_content', 'section_table'))
                    if 'sub_section' in section['section_content']:
                        for j, sub_section in enumerate(section['section_content']['sub_section']):
                            table_paths.append(('document', 'content', 'section', i, 'section_content', 'sub_section', j, 'sub_section_content', 'sub_section_table'))
                            if 'sub_sub_section' in sub_section['sub_section_content']:
                                for k, sub_sub_section in enumerate(sub_section['sub_section_content']['sub_sub_section']):
                                    table_paths.append(('document', 'content', 'section', i, 'section_content', 'sub_section', j, 'sub_section_content', 'sub_sub_section', k, 'sub_sub_section_table'))

            # Collect all tables
            all_tables = []
            for path in table_paths:
                tables = self._get_tables_at_path(self.json_data, path)
                if tables:
                    all_tables.extend(tables)

            # Process tables
            processed_tables = []
            for table_str in all_tables:
                # Convert table string to list of rows (list of lists)
                table = self._parse_table_string(table_str)
                
                # Remove empty rows and columns
                table = self.remove_empty_rows_and_columns(table)

                # Resolve spanning cells
                table = self.resolve_spanning_cells(table)

                # Append to processed_tables
                processed_tables.append(table)

            # Merge multi-page tables
            merged_tables = self.merge_multipage_tables(processed_tables)

            # Identify key-value pairs and update tables
            enriched_tables = []
            for table in merged_tables:
                key_value_table = self.identify_key_value_pairs(table)
                enriched_tables.append(key_value_table)

            # Update JSON data with enriched tables
            self.update_json_data(enriched_tables)

        except Exception as e:
            self.logger_manager.log_exception(e, context_message="Error processing tables.")
            raise

    def remove_empty_rows_and_columns(self, table: list) -> list:
        """
        Removes empty rows and columns from the table.

        Empty rows are defined as rows where all cells are empty strings (after stripping whitespace).

        Empty columns are defined as columns with more than 2 rows (number of rows > 2),
        where the first cell may or may not be empty, and the rest of the cells are empty
        (after stripping whitespace).

        Parameters:
            table (list of list of str):
                The table represented as a list of rows, where each row is a list of cell strings.

        Returns:
            list of list of str:
                The table after removing empty rows and columns.

        Raises:
            None

        Upstream functions:
            - `process_tables`: Calls this function to clean the table before further processing.

        Downstream functions:
            - `remove_empty_rows`: Removes empty rows from the table.
            - `remove_empty_columns`: Removes empty columns from the table.

        Dependencies:
            - `remove_empty_rows` method must correctly remove empty rows.
            - `remove_empty_columns` method must correctly remove empty columns.
        """
        # Remove empty rows
        table = self.remove_empty_rows(table)
        # Remove empty columns
        table = self.remove_empty_columns(table)
        return table

    def remove_empty_rows(self, table: list) -> list:
        """
        Removes empty rows from the table.

        A row is considered empty if all its cells are empty strings (after stripping whitespace).

        Parameters:
            table (list of list of str):
                The table represented as a list of rows, where each row is a list of cell strings.

        Returns:
            list of list of str:
                The table after removing empty rows.

        Raises:
            None

        Upstream functions:
            - `remove_empty_rows_and_columns`: Calls this function to remove empty rows.

        Downstream functions:
            None

        Dependencies:
            - None
        """
        return [row for row in table if not all(cell.strip() == '' for cell in row)]

    def remove_empty_columns(self, table: list) -> list:
        """
        Removes empty columns from the table.

        An empty column is defined as a column with more than 2 rows (number of rows > 2),
        where the first cell may or may not be empty, and the rest of the cells are empty
        (after stripping whitespace).

        Parameters:
            table (list of list of str):
                The table represented as a list of rows, where each row is a list of cell strings.

        Returns:
            list of list of str:
                The table after removing empty columns.

        Raises:
            None

        Upstream functions:
            - `remove_empty_rows_and_columns`: Calls this function to remove empty columns.

        Downstream functions:
            None

        Dependencies:
            - The table should be a list of lists, where each sub-list represents a row with cell strings.
        """
        num_rows = len(table)
        if num_rows == 0:
            return table  # Empty table

        # Determine the maximum number of columns
        max_cols = max(len(row) for row in table)

        # Pad rows with empty strings to have equal length
        padded_table = [row + [''] * (max_cols - len(row)) for row in table]

        # Transpose the table to get columns
        columns = list(map(list, zip(*padded_table)))

        # Indices of columns to keep
        columns_to_keep = []
        for idx, col in enumerate(columns):
            num_rows_in_col = len(col)
            if num_rows_in_col <= 2:
                # Keep columns with 2 or fewer rows regardless of content
                columns_to_keep.append(idx)
                continue
            remaining_cells = col[1:]
            # Check if all remaining cells are empty (after stripping whitespace)
            if all(cell.strip() == '' for cell in remaining_cells):
                # Empty column, do not keep
                continue
            else:
                columns_to_keep.append(idx)

        # Reconstruct columns by keeping only columns_to_keep
        columns_filtered = [columns[idx] for idx in columns_to_keep]

        if not columns_filtered:
            # All columns were removed
            return []

        # Transpose back to get rows
        cleaned_table = list(map(list, zip(*columns_filtered)))
        return cleaned_table

    def resolve_spanning_cells(self, table: list) -> list:
        """
        Resolves issues with cell spanning in a table.

        When tables are converted to Markdown, cell spanning is lost and content is duplicated
        across spanned cells. This method identifies such patterns and reconstructs the original
        table structure as per the program requirements.

        Parameters:
            table (list of list of str):
                The table represented as a list of rows, where each row is a list of cell strings.

        Returns:
            list of list of str:
                The table after resolving cell spanning issues.

        Raises:
            None

        Dependencies:
            - Uses pattern recognition to identify spanned cells.
            - Modifies the table in-place.

        Upstream functions:
            - Called by `process_tables` for each table.

        Downstream functions:
            - None

        """
        # Implement spanning cells resolution as per requirements
        # Note: Spanned cells result in identical content across cells.

        # Handle headers that span multiple rows
        if len(table) < 2:
            # Not enough rows to process spanning
            return table

        # Identify if the second row is part of the header
        second_row_part_of_header = self._is_second_row_part_of_header(table)

        # If second row is part of header, merge with first row
        if second_row_part_of_header:
            merged_header = []
            for cell1, cell2 in zip(table[0], table[1]):
                merged_cell = f"{cell1.strip()} - {cell2.strip()}".strip(' - ')
                merged_header.append(merged_cell)
            # Replace first row with merged header
            table[0] = merged_header
            # Remove second row from table
            table.pop(1)
        # Else, do nothing
        return table

    def merge_multipage_tables(self, tables: list) -> list:
        """
        Merges tables with identical headers, assuming they are parts of a multi-page table.

        Parameters:
            tables (list of list of list of str):
                A list of tables, where each table is a list of rows, and each row is a list of cell strings.

        Returns:
            list of list of list of str:
                A list of merged tables.

        Raises:
            None

        Dependencies:
            - Compares table headers for equality.
            - Merges table bodies if headers are identical.

        Upstream functions:
            - Called by `process_tables` after resolving spanning cells.

        Downstream functions:
            - None

        """
        merged_tables = []
        headers_map = {}  # Header tuple to table index mapping
        for table in tables:
            if not table:
                continue
            header = tuple(table[0])  # Use header row as key
            if header in headers_map:
                # Append the body of this table to existing table
                existing_table = merged_tables[headers_map[header]]
                existing_table.extend(table[1:])
            else:
                # Add new table
                merged_tables.append(table)
                headers_map[header] = len(merged_tables) -1
        return merged_tables

    def identify_key_value_pairs(self, table: list) -> dict:
        """
        Transforms the table into key-value pairs based on its structure.

        The method processes the table according to the specified rules depending on the table's
        structure (number of columns, header patterns, etc.)

        Parameters:
            table (list of list of str):
                The table represented as a list of rows, where each row is a list of cell strings.

        Returns:
            dict:
                A dictionary representing the key-value pairs extracted from the table.

        Raises:
            None

        Dependencies:
            - Implements logic per the program's table structure rules.

        Upstream functions:
            - Called by `process_tables` for each merged table.

        Downstream functions:
            - None

        """
        # Process the table according to the rules specified

        if not table or not table[0]:
            return {}

        num_columns = len(table[0])

        result = {}
        if num_columns ==1:  # Single column table
            key = table[0][0].strip()
            items = table[1:]  # Remaining rows
            sub_dict = {}
            for row in items:
                cell = row[0].strip()
                if ':' in cell:
                    sub_key, sub_value = cell.split(':', 1)
                    sub_key = sub_key.strip()
                    sub_value = sub_value.strip()
                    sub_dict[sub_key] = sub_value
                elif '\n' in cell:
                    lines = cell.split('\n')
                    sub_key = lines[0].strip()
                    sub_value = '\n'.join(lines[1:]).strip()
                    sub_dict[sub_key] = sub_value
                else:
                    sub_key = 'item'
                    sub_value = cell
                    # Ensure unique keys
                    if sub_key in sub_dict:
                        index = 1
                        while f"{sub_key}_{index}" in sub_dict:
                            index +=1
                        sub_key = f"{sub_key}_{index}"
                    sub_dict[sub_key] = sub_value
            result[key] = sub_dict
        else:
            # Multi-column table
            header = table[0]
            if all(cell.strip() == header[0].strip() for cell in header):
                # Header spans all columns (all cells in first row are identical)
                key = header[0].strip()
                sub_dict = {}
                for row in table[1:]:
                    if len(row)==2:
                        sub_key = row[0].strip()
                        value = row[1].strip()
                        sub_dict[sub_key] = value
                    elif len(row)>2:
                        sub_key = row[0].strip()
                        items = row[1:]
                        item_dict = {}
                        for idx, item in enumerate(items):
                            item_key = f"item_{idx+1}"
                            item_value = item.strip()
                            item_dict[item_key] = item_value
                        sub_dict[sub_key] = item_dict
                    else:
                        # row has less than 2 columns
                        continue
                result[key] = sub_dict
            elif len(set(header)) == len(header):
                # Header has multiple columns (row 1 has multiple cells with different values)
                # and table body is a single column (row 2 and below span all columns)
                if all(len(row)==1 for row in table[1:]):
                    merged_header = ' - '.join(cell.strip() for cell in header)
                    sub_dict = {}
                    for row in table[1:]:
                        cell = row[0].strip()
                        if ':' in cell:
                            sub_key, sub_value = cell.split(':',1)
                            sub_key = sub_key.strip()
                            sub_value = sub_value.strip()
                            sub_dict[sub_key] = sub_value
                        elif '\n' in cell:
                            lines = cell.split('\n')
                            sub_key = lines[0].strip()
                            sub_value = '\n'.join(lines[1:]).strip()
                            sub_dict[sub_key] = sub_value
                        else:
                            sub_key = 'item'
                            sub_value = cell
                            # Ensure unique keys
                            if sub_key in sub_dict:
                                index =1
                                while f"{sub_key}_{index}" in sub_dict:
                                    index +=1
                                sub_key = f"{sub_key}_{index}"
                            sub_dict[sub_key] = sub_value
                    result[merged_header] = sub_dict
                else:
                    # Table body has multiple columns
                    key = ' - '.join(cell.strip() for cell in header)
                    rows = table[1:]
                    data_list = []
                    for row in rows:
                        row_dict = {header[i].strip(): row[i].strip() if i<len(row) else '' for i in range(len(header))}
                        data_list.append(row_dict)
                    result[key] = data_list
            else:
                # Other cases, process as needed
                pass  # For this implementation, we can leave it empty or log that it's unhandled
        return result

    def update_json_data(self, enriched_tables: list):
        """
        Updates the JSON data by replacing original table entries with enriched table data.

        Parameters:
            enriched_tables (list of dict):
                A list of enriched table data as dictionaries.

        Returns:
            None

        Raises:
            None

        Dependencies:
            - Modifies `self.json_data` in-place.

        Upstream functions:
            - Called by `process_tables` after enriching tables.

        Downstream functions:
            - None

        """
        # Logic to replace tables in the json_data with enriched tables.
        # This requires keeping track of where the tables were in the original json_data.

        # For simplicity, we will assume that the order of enriched_tables matches the order
        # of tables in the json_data, and we can replace them accordingly.

        table_paths = []
        idx = 0  # Index to track position in enriched_tables

        # First, build list of table paths in the same order as when processing the tables
        table_paths = [
            ('document', 'content', 'content_text1', 'table'),
            ('document', 'content', 'content_text2', 'table')
        ]
        # Collect table paths for sections and subsections
        if 'section' in self.json_data['document']['content']:
            for i, section in enumerate(self.json_data['document']['content']['section']):
                table_paths.append(('document', 'content', 'section', i, 'section_content', 'section_table'))
                if 'sub_section' in section['section_content']:
                    for j, sub_section in enumerate(section['section_content']['sub_section']):
                        table_paths.append(('document', 'content', 'section', i, 'section_content', 'sub_section', j, 'sub_section_content', 'sub_section_table'))
                        if 'sub_sub_section' in sub_section['sub_section_content']:
                            for k, sub_sub_section in enumerate(sub_section['sub_section_content']['sub_sub_section']):
                                table_paths.append(('document', 'content', 'section', i, 'section_content', 'sub_section', j, 'sub_section_content', 'sub_sub_section', k, 'sub_sub_section_table'))
        # Now, replace the table entries with enriched data
        for path in table_paths:
            parent, key = self._get_parent_and_key(self.json_data, path)
            if key in parent:
                table_entries = parent[key]
                if isinstance(table_entries, list):
                    new_entries = []
                    for _ in table_entries:
                        if idx < len(enriched_tables):
                            new_entries.append(enriched_tables[idx])
                            idx += 1
                        else:
                            break
                    parent[key] = new_entries
        # If there are any enriched tables left unprocessed, we can log a warning
        if idx < len(enriched_tables):
            self.logger.warning("There are unprocessed enriched tables that could not be updated in json_data.")

    def save_updated_json(self, output_file_name: str):
        """
        Saves the updated JSON data to a file in the specified output folder.

        Parameters:
            output_file_name (str):
                The name of the output JSON file (without extension).

        Returns:
            None

        Raises:
            IOError:
                If there is an error writing the JSON file.

        Dependencies:
            - Uses `json.dump` for writing JSON.
            - Uses `os.path.join` to form the full output path.

        Upstream functions:
            - Called after processing to save the updated JSON data.

        Downstream functions:
            - None

        """
        try:
            output_path = os.path.join(self.output_folder, f"{output_file_name}_enriched.json")
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json.dump(self.json_data, json_file, indent=2)
            self.logger.info(f"Updated JSON data successfully saved to '{output_path}'")
        except Exception as e:
            self.logger_manager.log_exception(e,
                context_message="Error saving updated JSON file.",
                file_name=output_path)
            raise

    # Helper methods
    def _get_tables_at_path(self, data, path):
        """
        Retrieves table entries at a given path in the JSON data.

        Parameters:
            data (dict):
                The JSON data.
            path (tuple):
                A tuple representing the keys to traverse to reach the tables.

        Returns:
            list:
                A list of table strings found at the specified path.

        Raises:
            None

        Dependencies:
            - Recursive dictionary traversal.

        """
        current = data
        try:
            for key in path:
                current = current[key]
            if isinstance(current, list):
                return current
            else:
                return []
        except (KeyError, IndexError, TypeError):
            return []

    def _parse_table_string(self, table_str):
        """
        Parses a markdown table string into a list of rows.

        Parameters:
            table_str (str):
                The markdown table as a string.

        Returns:
            list of list of str:
                The table represented as a list of rows, each row is a list of cell strings.

        Raises:
            None

        Dependencies:
            - Uses regular expressions and string methods.

        """
        # Split table into lines
        lines = table_str.strip().split('\n')
        # Remove separator line (e.g., | --- | --- |)
        separator_pattern = re.compile(r'^\s*\|?\s*:?-+:?\s*\|')
        cleaned_lines = []
        for line in lines:
            if separator_pattern.match(line.strip()):
                continue
            else:
                cleaned_lines.append(line)
        # Parse lines into cells
        table = []
        for line in cleaned_lines:
            cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
            table.append(cells)
        return table

    def _is_second_row_part_of_header(self, table):
        """
        Determines if the second row is part of the table header.

        Parameters:
            table (list of list of str):
                The table represented as a list of rows.

        Returns:
            bool:
                True if the second row is part of the header; False otherwise.

        Raises:
            None

        Dependencies:
            - Compares cell content across rows.

        """
        if len(table) < 4:
            return False  # Not enough rows to decide

        second_row = table[1]
        third_row = table[2]
        fourth_row = table[3]
        # Check if the pattern of the second row matches third and fourth
        same_pattern = self._row_pattern(second_row) == self._row_pattern(third_row) == self._row_pattern(fourth_row)
        return not same_pattern

    def _row_pattern(self, row):
        """
        Creates a pattern representation of a row based on cell contents.

        Parameters:
            row (list of str):
                A row from the table.

        Returns:
            tuple:
                A tuple representing the pattern.

        Raises:
            None

        Dependencies:
            - None

        """
        return tuple(row)

    def _get_parent_and_key(self, data, path):
        """
        Retrieves the parent dictionary and key at the end of a path.

        Parameters:
            data (dict):
                The JSON data.
            path (tuple):
                A tuple representing the keys to traverse.

        Returns:
            tuple (dict, str):
                The parent dictionary and the final key.

        Raises:
            None

        Dependencies:
            - Recursive traversal.

        """
        current = data
        for key in path[:-1]:
            current = current[key]
        return current, path[-1]