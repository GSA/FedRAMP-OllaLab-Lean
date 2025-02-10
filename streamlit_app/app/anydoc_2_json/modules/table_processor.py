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
    merges multi-page tables (if applicable), identifies key-value pairs based on table structure, and
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
        - `collect_tables`
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
        tables (if applicable), identifying key-value pairs based on table structure, and updating the JSON data.

        This method modifies the `json_data` in-place, and prepares it for saving.

        Parameters:
            None

        Returns:
            None

        Raises:
            Exception:
                If an error occurs during processing, it is logged and re-raised.

        Dependencies:
            - `collect_tables` to find all tables in the json_data.
            - For each table:
                - `remove_empty_rows_and_columns` to clean the table.
                - `resolve_spanning_cells` to fix cell spanning issues.
                - `identify_key_value_pairs` to convert tables into key-value pairs.
            - Updates the table item in `json_data`.

        Upstream functions:
            - Called by the main program or module to process tables.

        Downstream functions:
            - `collect_tables`
            - `remove_empty_rows_and_columns`
            - `resolve_spanning_cells`
            - `identify_key_value_pairs`

        """
        try:
            # Collect all tables from json_data
            self.tables_info = []  # To store info about tables and their positions for updating
            self.collect_tables(self.json_data['document']['content'])

            # Process each table
            for table_info in self.tables_info:
                table_item = table_info['table_item']
                table_content = table_item.get('table', [])
                # table_content is a list of table lines (strings)

                # Convert table string to list of rows (list of lists)
                table = self._parse_table_lines(table_content)

                # Remove empty rows and columns
                table = self.remove_empty_rows_and_columns(table)

                # Resolve spanning cells
                table = self.resolve_spanning_cells(table)

                # Identify key-value pairs and update table
                enriched_table = self.identify_key_value_pairs(table)

                # Replace the 'table' key in table_item with enriched data
                table_item['table'] = enriched_table
                # Optionally, update the 'type' to indicate it's been enriched
                table_item['type'] = 'enriched_table'

        except Exception as e:
            self.logger_manager.log_exception(e, context_message="Error processing tables.")
            raise

    def collect_tables(self, content_list: list):
        """
        Recursively traverses the content list to collect all table content items.

        Parameters:
            content_list (list):
                A list of content items from the JSON data.

        Returns:
            None

        Raises:
            None

        Dependencies:
            - Uses recursion to traverse nested content items.
            - Collects tables and their positions for later updating.

        Upstream functions:
            - Called by process_tables.

        Downstream functions:
            - collect_tables (recursion)

        """
        for index, item in enumerate(content_list):
            if isinstance(item, dict):
                if item.get('type') == 'table':
                    table_info = {
                        'table_item': item,
                        'parent_list': content_list,
                        'index': index
                    }
                    self.tables_info.append(table_info)
                elif item.get('type') == 'heading':
                    # Heading may have nested content
                    # In this schema, we need to check if 'subcontent' exists
                    if 'subcontent' in item:
                        self.collect_tables(item['subcontent'])
                else:
                    # For other types, do nothing
                    pass
            else:
                continue  # Skip non-dict items

    def _parse_table_lines(self, table_lines: list) -> list:
        """
        Parses markdown table lines into a list of rows.

        Parameters:
            table_lines (list of str):
                The table represented as a list of markdown table lines.

        Returns:
            list of list of str:
                The table represented as a list of rows, where each row is a list of cell strings.

        Raises:
            None

        Dependencies:
            - Uses regular expressions and string methods.

        Upstream functions:
            - Called by process_tables.

        Downstream functions:
            - None

        """
        # Remove separator line (e.g., | --- | --- |)
        separator_pattern = re.compile(r'^\s*\|?\s*(:?-+:?\s*\|)+\s*(:?-+:?\s*)?$')
        cleaned_lines = []
        for line in table_lines:
            if separator_pattern.match(line.strip()):
                continue
            else:
                cleaned_lines.append(line)
        # Parse lines into cells
        table = []
        for line in cleaned_lines:
            # Remove leading and trailing '|'
            line = line.strip().strip('|')
            # Split by '|'
            cells = [cell.strip() for cell in line.split('|')]
            table.append(cells)
        return table

    def remove_empty_rows_and_columns(self, table: list) -> list:
        """
        Removes empty rows and columns from the table.

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
            - None

        Dependencies:
            - None
        """
        return [row for row in table if any(cell.strip() != '' for cell in row)]

    def remove_empty_columns(self, table: list) -> list:
        """
        Removes empty columns from the table.

        Note: As per additional requirements, the column removal functionality is disabled.
        This function does not alter the table and returns it unchanged.

        Parameters:
        table (list):
            Type: list of list of str
            Description: The table represented as a list of rows, where each row is a list of cell strings.

        Returns:
        list:
            Type: list of list of str
            Description: The original table is returned without any modifications.

        Raises:
        None

        Upstream functions:
        - Called by remove_empty_rows_and_columns() within this TableProcessor module.

        Downstream functions:
        - None

        Dependencies:
        - Requires that the table be provided as a list of rows.
        - Uses self.logger to log a debug message.
        """
        self.logger.info("Column removal is disabled per additional requirements. Returning original table.")
        # The original code below was commented out to disable empty column removal:
        # if not table:
        #    return table
        #
        # num_rows = len(table)
        # num_cols = max(len(row) for row in table)
        # padded_table = [row + [''] * (num_cols - len(row)) for row in table]
        # columns = list(zip(*padded_table))
        # columns_to_keep = []
        # for idx, col in enumerate(columns):
        #     if len(col) <= 2:
        #         columns_to_keep.append(idx)
        #     else:
        #         remaining_cells = col[1:]
        #         if all(cell.strip() == '' for cell in remaining_cells):
        #             continue  # Empty column
        #         else:
        #             columns_to_keep.append(idx)
        # new_columns = [columns[idx] for idx in columns_to_keep]
        # new_table = list(map(list, zip(*new_columns)))
        # return new_table
        return table

    def resolve_spanning_cells(self, table: list) -> list:
        """
        Resolves issues with cell spanning in a table.

        Parameters:
            table (list of list of str):
                The table represented as a list of rows, where each row is a list of cell strings.

        Returns:
            list of list of str:
                The table after resolving cell spanning issues.

        Raises:
            None

        Dependencies:
            - Modifies the table in-place.

        Upstream functions:
            - Called by `process_tables` for each table.

        Downstream functions:
            - None

        """
        # Implement spanning cells resolution as per requirements

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
                # Merge cells with ' - ' if both are not empty
                if cell1.strip() and cell2.strip():
                    merged_cell = f"{cell1.strip()} - {cell2.strip()}"
                elif cell1.strip():
                    merged_cell = cell1.strip()
                elif cell2.strip():
                    merged_cell = cell2.strip()
                else:
                    merged_cell = ''
                merged_header.append(merged_cell)
            # Replace first row with merged header
            table[0] = merged_header
            # Remove second row from table
            table.pop(1)
        # Else, do nothing
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
        pattern_second = self._row_pattern(second_row)
        pattern_third = self._row_pattern(third_row)
        pattern_fourth = self._row_pattern(fourth_row)

        return not (pattern_second == pattern_third == pattern_fourth)

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
        return tuple('CELL' if cell.strip() else 'EMPTY' for cell in row)

    def identify_key_value_pairs(self, table: list) -> dict:
        """
        Transforms the table into key-value pairs based on its structure.

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
            - Called by `process_tables` for each table.

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
            if len(set([cell.strip() for cell in header])) == 1:
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
            elif all(len(row)==1 for row in table[1:]):
                # Header has multiple columns, body has single column spanning all columns
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
                # Other cases, process as needed
                # For simplicity, we can convert the table into a list of dictionaries
                # where each dictionary represents a row with keys from the header
                data_list = []
                for row in table[1:]:
                    row_dict = {header[i].strip(): row[i].strip() if i<len(row) else '' for i in range(len(header))}
                    data_list.append(row_dict)
                result['table_data'] = data_list

        return result

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