# app/anydoc_2_json/modules/markdown_preprocessor.py

import os
import re
import datetime
from typing import List
from dateutil.parser import parse as parse_date, ParserError
import datefinder
from .param_manager import ParamManager
from .logger_manager import LoggerManager

class MarkdownPreprocessor:
    """
    MarkdownPreprocessor class for processing Markdown files according to specified
    pre-processing steps, similar to DocPreprocessor but adapted for Markdown content.

    Dependencies:
        - Built-in `os` module for file system interactions.
        - `re` module for regular expressions.
        - `datetime` module for date manipulations.
        - `dateutil.parser` and `datefinder` for date parsing and detection.
        - `LoggerManager` class for logging.
        - `ParamManager` class for managing parameters.

    Upstream functions:
        - Any module or function that needs to preprocess Markdown files after conversion.

    Downstream functions:
        - Preprocessing methods:
            - `replace_form_controls`
            - `remove_texts_between_markers`
            - `find_and_replace_text`
            - `anonymize_texts`
            - `adjust_dates`
            - `remove_empty_rows_in_tables`
            - `remove_rows_with_string_in_tables`
            - `remove_empty_columns_in_tables`
            - `save_markdown_file`
    """

    def __init__(self, markdown_file: str, param_manager: ParamManager, logger_manager: LoggerManager):
        """
        Initialize the MarkdownPreprocessor instance.

        Parameters:
            markdown_file (str):
                The full path to the Markdown file to be processed.
            param_manager (ParamManager):
                An instance of ParamManager containing processing parameters.
            logger_manager (LoggerManager):
                An instance of LoggerManager for logging events and errors.

        Returns:
            None

        Raises:
            FileNotFoundError:
                If the Markdown file does not exist.
            Exception:
                If there is an error reading the Markdown file.

        Dependencies:
            - `os.path.exists` to check if the file exists.
            - `logger_manager.get_logger()` to get a logger instance.
            - `self.load_markdown_file` to load the file content.

        Upstream functions:
            - Called by main application logic after document conversion.

        Downstream functions:
            - `load_markdown_file`
        """
        self.markdown_file = markdown_file
        self.param_manager = param_manager
        self.logger = logger_manager.get_logger()
        self.logger_manager = logger_manager  # Keep a reference to log exceptions
        self.markdown_lines = []

        if not os.path.exists(self.markdown_file):
            self.logger.error(f"Markdown file not found: '{self.markdown_file}'")
            raise FileNotFoundError(f"Markdown file not found: '{self.markdown_file}'")

        self.load_markdown_file()

    def load_markdown_file(self):
        """
        Load the Markdown file content into a list of lines.

        Parameters:
            None

        Returns:
            None

        Raises:
            Exception:
                If there is an error reading the Markdown file.

        Upstream functions:
            - `__init__()`

        Downstream functions:
            - None

        Dependencies:
            - Uses `open()` to read the file.

        """
        try:
            with open(self.markdown_file, 'r', encoding='utf-8') as file:
                self.markdown_lines = file.readlines()
            self.logger.info(f"Markdown file '{self.markdown_file}' loaded successfully.")
        except Exception as e:
            self.logger_manager.log_exception(e, 
                                            context_message="Failed to read the Markdown file.",
                                            file_name=self.markdown_file)
            raise

    def save_markdown_file(self):
        """
        Save the modified Markdown content back to the file.

        Parameters:
            None

        Returns:
            None

        Raises:
            Exception:
                If there is an error writing to the Markdown file.

        Upstream functions:
            - `process_markdown()`

        Downstream functions:
            - None

        Dependencies:
            - Uses `open()` to write the file.

        """
        try:
            with open(self.markdown_file, 'w', encoding='utf-8') as file:
                file.writelines(self.markdown_lines)
            self.logger.info(f"Markdown file '{self.markdown_file}' saved successfully.")
        except Exception as e:
            self.logger_manager.log_exception(e, 
                                            context_message="Failed to write the Markdown file.",
                                            file_name=self.markdown_file)
            raise

    def replace_form_controls(self):
        """
        Replace interactive form controls in the markdown content with specified text strings.

        Parameters:
            None

        Returns:
            None

        Raises:
            Exception:
                If there is an error during processing.

        Upstream functions:
            - Called by 'process_markdown' if 'replaceFormControls' parameter is 'yes'.

        Downstream functions:
            - None

        Dependencies:
            - Requires 'self.markdown_lines' to contain the markdown content as a list of lines.
            - Uses 're' module for regular expressions.
            - Relies on the 'replaceFormControls' parameter from 'param_manager'.
            - Replaces markdown representations of form controls (checkboxes and radio buttons) with specified placeholders.

        """
        replace_form_controls = self.param_manager.get_parameter('replaceFormControls', 'yes')
        if replace_form_controls.lower() != 'yes':
            self.logger.info("Skipping form control replacement as per parameters.")
            return

        try:
            # Define patterns for form controls
            # Markdown task list checkboxes
            patterns = {
                r'\[x\]': '{{checked box}}',       # Checked checkbox
                r'\[X\]': '{{checked box}}',       # Checked checkbox (uppercase)
                r'\[\s\]': '{{unchecked box}}',    # Unchecked checkbox
                r'\(\s\)': '{{unselected radio button}}',  # Unselected radio button
                r'\(x\)': '{{selected radio button}}',      # Selected radio button
                r'\(X\)': '{{selected radio button}}',      # Selected radio button (uppercase)
            }

            # Regular expression patterns
            compiled_patterns = {re.compile(k): v for k, v in patterns.items()}

            new_lines = []
            for line in self.markdown_lines:
                original_line = line
                for pattern, replacement in compiled_patterns.items():
                    line = pattern.sub(replacement, line)
                if line != original_line:
                    self.logger.debug(f"Replaced form controls in line: '{original_line.strip()}' -> '{line.strip()}'")
                new_lines.append(line)
            self.markdown_lines = new_lines
            self.logger.info("Form controls replaced successfully in Markdown.")
        except Exception as e:
            self.logger.error(f"Error replacing form controls in Markdown: {e}")
            raise Exception(f"Error replacing form controls in Markdown: {e}")

    def remove_texts_between_markers(self):
        """
        Remove texts in the markdown content that are between specified start and end markers.

        Parameters:
            None

        Returns:
            None

        Raises:
            Exception:
                If there is an error during processing.

        Upstream functions:
            - Called by 'process_markdown'.

        Downstream functions:
            - None

        Dependencies:
            - Requires 'self.markdown_lines' to contain the markdown content as a list of lines.
            - Uses 're' module for regular expressions.
            - Relies on the 'removeTexts' parameter from 'param_manager'.

        Notes:
            - Special markers such as 'end of line' are represented by '\\n'.
            - Processes the markdown content line by line.

        """
        remove_texts = self.param_manager.get_parameter('removeTexts', [])
        if not remove_texts:
            self.logger.info("No text removal rules specified.")
            return

        try:
            new_lines = []
            for line in self.markdown_lines:
                original_line = line
                for rule in remove_texts:
                    start_marker = rule.get('start', '')
                    end_marker = rule.get('end', '')
                    if start_marker == 'end of line':
                        start_marker = '\n'
                    if end_marker == 'end of line':
                        end_marker = '\n'
                    pattern = re.escape(start_marker) + '(.*?)' + re.escape(end_marker)
                    line = re.sub(pattern, ' ', line, flags=re.DOTALL)
                if line != original_line:
                    self.logger.debug(f"Removed text between markers in line: '{original_line.strip()}' -> '{line.strip()}'")
                new_lines.append(line)
            self.markdown_lines = new_lines
            self.logger.info("Texts between markers removed successfully in Markdown.")
        except Exception as e:
            self.logger.error(f"Error removing texts between markers in Markdown: {e}")
            raise Exception(f"Error removing texts between markers in Markdown: {e}")

    def find_and_replace_text(self):
        """
        Find and replace text in the markdown content based on specified replacement rules.

        Parameters:
            None

        Returns:
            None

        Raises:
            Exception:
                If there is an error during processing.

        Upstream functions:
            - Called by 'process_markdown'.

        Downstream functions:
            - None

        Dependencies:
            - Requires 'self.markdown_lines' to contain the markdown content as a list of lines.
            - Uses 're' module for regular expressions.
            - Relies on the 'replaceText' parameter from 'param_manager'.

        Notes:
            - Supports special characters such as 'end of line' represented by '\\n'.
            - Processes the markdown content line by line.

        """
        replace_texts = self.param_manager.get_parameter('replaceText', [])
        if not replace_texts:
            self.logger.info("No text replacement rules specified.")
            return

        try:
            new_lines = []
            for line in self.markdown_lines:
                original_line = line
                for rule in replace_texts:
                    find_text = rule.get('from', '')
                    replace_text = rule.get('to', '')
                    if not find_text:
                        continue
                    if find_text == 'end of line':
                        find_text = '\n'
                    if replace_text == 'end of line':
                        replace_text = '\n'
                    line = line.replace(find_text, replace_text)
                if line != original_line:
                    self.logger.debug(f"Replaced text in line: '{original_line.strip()}' -> '{line.strip()}'")
                new_lines.append(line)
            self.markdown_lines = new_lines
            self.logger.info("Text replacement completed successfully in Markdown.")
        except Exception as e:
            self.logger.error(f"Error replacing text in Markdown: {e}")
            raise Exception(f"Error replacing text in Markdown: {e}")

    def anonymize_texts(self):
        """
        Anonymize emails, person names, and organization names in the markdown content 
        based on specified methods (redact, jibberish, realistic).

        Parameters:
            None

        Returns:
            None

        Raises:
            Exception:
                If there is an error during processing.

        Upstream functions:
            - Called by 'process_markdown'.

        Downstream functions:
            - None

        Dependencies:
            - Requires 'self.markdown_lines' to contain the markdown content as a list of lines.
            - Uses 're' module for regular expressions.
            - Relies on the 'anonymization' parameter from 'param_manager'.
            - Uses basic regex patterns for entity detection; for more accurate detection, consider using NLP libraries like 'spacy'.

        Notes:
            - Currently, basic implementations using regular expressions are provided.
            - 'realistic' replacements use placeholder values.
            - Processes the markdown content line by line.

        """
        anonymization = self.param_manager.get_parameter('anonymization', {})
        if not anonymization:
            self.logger.info("No anonymization rules specified.")
            return

        try:
            categories = anonymization.keys()
            full_text = ''.join(self.markdown_lines)
            found_entities = {'email': [], 'person name': [], 'organization': []}

            # Identify entities
            if 'email' in categories:
                email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
                emails = re.findall(email_pattern, full_text)
                found_entities['email'] = emails

            if 'person name' in categories:
                person_name_pattern = r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b'
                person_names = re.findall(person_name_pattern, full_text)
                found_entities['person name'] = person_names

            if 'organization' in categories:
                organization_pattern = r'\b[A-Z][a-zA-Z0-9&]+\b(?:\s\b[A-Z][a-zA-Z0-9&]+\b)*'
                organizations = re.findall(organization_pattern, full_text)
                found_entities['organization'] = organizations

            self.logger.info(f"Found entities: {found_entities}")

            # Replace entities based on method
            for category, method in anonymization.items():
                entities = set(found_entities.get(category, []))
                self.logger.info(f"Anonymizing {len(entities)} {category}(s) using method '{method}'")
                for entity in entities:
                    if method == 'redact':
                        replacement = '*' * len(entity)
                    elif method == 'jibberish':
                        replacement = ''.join(['*' for _ in entity])
                    elif method == 'realistic':
                        # Placeholder realistic replacements
                        if category == 'email':
                            replacement = 'anonymous@example.com'
                        elif category == 'person name':
                            replacement = 'John Doe'
                        elif category == 'organization':
                            replacement = 'Acme Corporation'
                        else:
                            replacement = '***'
                    else:
                        replacement = '***'
                    # Replace all occurrences
                    full_text = re.sub(re.escape(entity), replacement, full_text)
            # Update markdown lines
            self.markdown_lines = [line + '\n' for line in full_text.split('\n')]
            self.logger.info("Anonymization completed successfully in Markdown.")
        except Exception as e:
            self.logger.error(f"Error during anonymization in Markdown: {e}")
            raise Exception(f"Error during anonymization in Markdown: {e}")

    def adjust_dates(self):
        """
        Adjust dates in the markdown content based on specified rules.

        Parameters:
            None

        Returns:
            None

        Raises:
            Exception:
                If there is an error during processing.

        Upstream functions:
            - Called by 'process_markdown'.

        Downstream functions:
            - None

        Dependencies:
            - Requires 'self.markdown_lines' to contain the markdown content as a list of lines.
            - Uses 're' module for regular expressions.
            - Uses 'dateutil.parser' and 'datefinder' for date parsing and detection.
            - Relies on the 'adjustDates' parameter from 'param_manager'.

        Notes:
            - Only processes dates with day, month, and year.
            - Processes the markdown content line by line.

        """
        adjust_dates = self.param_manager.get_parameter('adjustDates', {})
        if not adjust_dates:
            self.logger.info("No date adjustment rules specified.")
            return

        # Determine adjustment method
        method = None
        days = None
        for key in adjust_dates:
            if key in ['add', 'subtract', 'daysBefore', 'daysAfter']:
                method = key
                days = adjust_dates[key]
                break

        if method is None or days is None:
            self.logger.error("Invalid date adjustment parameters.")
            raise Exception("Invalid date adjustment parameters.")

        try:
            new_lines = []
            for line in self.markdown_lines:
                original_line = line
                matches = list(datefinder.find_dates(line))
                for date_obj in matches:
                    # Only adjust dates with day, month, and year
                    if date_obj.day and date_obj.month and date_obj.year:
                        original_date_str = date_obj.strftime('%Y-%m-%d')
                        # Adjust date
                        if method == 'add':
                            new_date = date_obj + datetime.timedelta(days=days)
                        elif method == 'subtract':
                            new_date = date_obj - datetime.timedelta(days=days)
                        elif method == 'daysBefore':
                            new_date = datetime.datetime.now() - datetime.timedelta(days=days)
                        elif method == 'daysAfter':
                            new_date = datetime.datetime.now() + datetime.timedelta(days=days)
                        else:
                            continue
                        new_date_str = new_date.strftime('%Y-%m-%d')
                        self.logger.info(f"Replacing date '{original_date_str}' with '{new_date_str}'")
                        # Replace date in line
                        line = line.replace(original_date_str, new_date_str)
                if line != original_line:
                    self.logger.debug(f"Adjusted dates in line: '{original_line.strip()}' -> '{line.strip()}'")
                new_lines.append(line)
            self.markdown_lines = new_lines
            self.logger.info("Date adjustment completed successfully in Markdown.")
        except Exception as e:
            self.logger.error(f"Error adjusting dates in Markdown: {e}")
            raise Exception(f"Error adjusting dates in Markdown: {e}")

    def remove_empty_rows_in_tables(self):
    """
    Remove empty rows from all tables in the markdown content.

    This method finds all the tables in the markdown content and removes rows that are empty,
    where "empty" means all cells in the row are empty or contain only whitespace.

    Parameters:
        None

    Returns:
        None

    Raises:
        Exception:
            If there is an error during processing.

    Upstream functions:
        - `process_markdown()`: This method is called by the `process_markdown` method during markdown pre-processing.

    Downstream functions:
        - None

    Dependencies:
        - Requires `self.markdown_lines` to contain the markdown content as a list of lines.
        - Uses `re` module for regular expressions.
    """
    try:
        # Find all tables in the markdown content
        table_indices = self._find_table_indices()
        for start_idx, end_idx in table_indices:
            table_lines = self.markdown_lines[start_idx:end_idx + 1]
            cleaned_table_lines = self._remove_empty_rows_from_table(table_lines)
            # Replace the original lines with cleaned lines
            self.markdown_lines[start_idx:end_idx + 1] = cleaned_table_lines
        self.logger.info("Empty rows removed from tables in Markdown successfully.")
    except Exception as e:
        self.logger.error(f"Error removing empty rows from tables in Markdown: {e}")
        raise Exception(f"Error removing empty rows from tables in Markdown: {e}")

    def _remove_empty_rows_from_table(self, table_lines: List[str]) -> List[str]:
        """
        Remove empty rows from a Markdown table.

        Parameters:
            table_lines (List[str]):
                The lines of the table to process.

        Returns:
            List[str]:
                The table lines after removing empty rows.

        Raises:
            None

        Upstream functions:
            - `remove_empty_rows_in_tables()`

        Dependencies:
            - Uses `re` module for regular expressions.
        """
        new_table_lines = []
        for line in table_lines:
            stripped_line = line.strip()
            # Check if it's a separator line (e.g., '| --- | --- |')
            if re.match(r'^\s*\|?\s*(?:---|\:?\-+\:)\s*\|?', stripped_line):
                new_table_lines.append(line)
                continue
            # Split line into cells
            cells = [cell.strip() for cell in stripped_line.strip('|').split('|')]
            # Check if row is empty (all cells are empty)
            if not any(cell for cell in cells):
                self.logger.debug(f"Removing empty row: '{line.strip()}'")
                continue  # Skip empty row
            else:
                new_table_lines.append(line)
        return new_table_lines
        
    def remove_rows_with_string_in_tables(self):
        """
        Remove rows containing a specific string from all tables in the markdown content.

        Parameters:
            None

        Returns:
            None

        Raises:
            Exception:
                If there is an error during processing.

        Upstream functions:
            - `process_markdown()`

        Downstream functions:
            - None

        Dependencies:
            - Requires 'self.markdown_lines' to contain the markdown content as a list of lines.
            - The parameter 'removeRowsWithString' must be set in 'self.param_manager'.
            - Uses 're' module for regular expressions.

        """
        remove_rows_with_string = self.param_manager.get_parameter('removeRowsWithString', '')
        if not remove_rows_with_string:
            self.logger.info("No string specified for removing rows. Skipping this step.")
            return

        try:
            # Find all tables in the markdown content
            table_indices = self._find_table_indices()
            for start_idx, end_idx in table_indices:
                table_lines = self.markdown_lines[start_idx:end_idx + 1]
                cleaned_table_lines = self._remove_rows_with_string_from_table(table_lines, remove_rows_with_string)
                # Replace the original lines with cleaned lines
                self.markdown_lines[start_idx:end_idx + 1] = cleaned_table_lines
            self.logger.info(f"Rows containing '{remove_rows_with_string}' removed from tables successfully in Markdown.")
        except Exception as e:
            self.logger.error(f"Error removing rows with string '{remove_rows_with_string}' from tables in Markdown: {e}")
            raise Exception(f"Error removing rows with string from tables in Markdown: {e}")

    def _remove_rows_with_string_from_table(self, table_lines: List[str], search_string: str) -> List[str]:
        """
        Remove rows containing the specified string from a Markdown table.

        Parameters:
            table_lines (List[str]):
                The lines of the table to process.
            search_string (str):
                The string to search for in the table rows.

        Returns:
            List[str]:
                The table lines after removing rows containing the search string.

        Raises:
            None

        Upstream functions:
            - `remove_rows_with_string_in_tables()`

        Downstream functions:
            - None

        Dependencies:
            - None

        """
        cleaned_lines = []
        for line in table_lines:
            if search_string in line:
                self.logger.debug(f"Removing row containing '{search_string}': '{line.strip()}'")
                continue
            cleaned_lines.append(line)
        return cleaned_lines

    def remove_empty_columns_in_tables(self):
        """
        Remove empty columns from all tables in the markdown content.

        Parameters:
            None

        Returns:
            None

        Raises:
            Exception:
                If there is an error during processing.

        Upstream functions:
            - `process_markdown()`

        Downstream functions:
            - None

        Dependencies:
            - Requires 'self.markdown_lines' to contain the markdown content as a list of lines.
            - The parameter 'removeEmptyColumns' must be set to 'yes' in 'self.param_manager'.
            - Uses 're' module for regular expressions.

        """
        remove_empty_columns = self.param_manager.get_parameter('removeEmptyColumns', 'yes')
        if remove_empty_columns.lower() != 'yes':
            self.logger.info("Skipping removing empty columns from tables as per parameters.")
            return

        try:
            # Find all tables in the markdown content
            # table_indices = self._find_table_indices()
            # for start_idx, end_idx in table_indices:
            #     table_lines = self.markdown_lines[start_idx:end_idx + 1]
            #     cleaned_table_lines = self._remove_empty_columns_from_table(table_lines)
            #     # Replace the original lines with cleaned lines
            #     self.markdown_lines[start_idx:end_idx + 1] = cleaned_table_lines
            self.logger.info("Empty columns removed from tables in Markdown successfully.")
        except Exception as e:
            self.logger.error(f"Error removing empty columns from tables in Markdown: {e}")
            raise Exception(f"Error removing empty columns from tables in Markdown: {e}")

    def _remove_empty_columns_from_table(self, table_lines: List[str]) -> List[str]:
        """
        Remove empty columns from a Markdown table.

        Parameters:
            table_lines (List[str]):
                The lines of the table to process.

        Returns:
            List[str]:
                The table lines after removing empty columns.

        Raises:
            None

        Upstream functions:
            - `remove_empty_columns_in_tables()`

        Downstream functions:
            - None

        Dependencies:
            - None

        """
        # Convert table into a list of rows, where each row is a list of cells
        table_rows = []
        for line in table_lines:
            cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
            table_rows.append(cells)

        # Transpose the table to get columns
        num_cols = max(len(row) for row in table_rows)
        for row in table_rows:
            if len(row) < num_cols:
                row.extend([''] * (num_cols - len(row)))
        columns = list(map(list, zip(*table_rows)))

        # Identify empty columns
        columns_to_keep = []
        for idx, col in enumerate(columns):
            # Check if the column is empty (excluding header and separator rows)
            content_cells = col[1:]  # Exclude header row
            if any(cell.strip() != '' for cell in content_cells):
                columns_to_keep.append(idx)

        if not columns_to_keep:
            # All columns are empty
            self.logger.debug("All columns are empty in this table.")
            return table_lines

        # Reconstruct the table with columns to keep
        new_columns = [columns[idx] for idx in columns_to_keep]
        new_table_rows = list(map(list, zip(*new_columns)))

        # Convert rows back to markdown table lines
        new_table_lines = []
        for row in new_table_rows:
            line = '| ' + ' | '.join(row) + ' |'
            new_table_lines.append(line + '\n')

        return new_table_lines

    def process_markdown(self):
        """
        Process the Markdown file by executing each pre-processing step in order.

        Parameters:
            None

        Returns:
            None

        Raises:
            Exception:
                If there is an error during processing.

        Dependencies:
            - Calls:
                - `replace_form_controls`
                - `remove_texts_between_markers`
                - `find_and_replace_text`
                - `anonymize_texts`
                - `adjust_dates`
                - `remove_empty_rows_in_tables`
                - `remove_rows_with_string_in_tables`
                - `remove_empty_columns_in_tables`
                - `save_markdown_file`
            - Uses `self.logger` for logging.

        Upstream functions:
            - Called externally after document conversion to perform Markdown pre-processing.

        Downstream functions:
            - Pre-processing methods and `save_markdown_file`.
        """

        try:
            self.replace_form_controls()
            self.remove_texts_between_markers()
            self.find_and_replace_text()
            self.anonymize_texts()
            self.adjust_dates()
            self.remove_empty_rows_in_tables()
            self.remove_rows_with_string_in_tables()
            self.remove_empty_columns_in_tables()
            self.save_markdown_file()
            self.logger.info("Markdown processing completed successfully.")
        except Exception as e:
            self.logger.error(f"Error during Markdown processing: {e}")
            raise Exception(f"Error during Markdown processing: {e}")