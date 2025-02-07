# app/anydoc_2_json/modules/md_parser.py

import os
import json
import re
import traceback
from .logger_manager import LoggerManager
from .param_manager import ParamManager

class MdParser:
    """
    MdParser class for parsing Markdown files into structured JSON data according to a specified schema.

    The class reads a Markdown file, parses its content according to the provided JSON schema instructions,
    and generates a structured JSON object.

    Dependencies:
        - Built-in `os` module for file system interactions.
        - Built-in `json` module for JSON serialization.
        - Built-in `re` module for regular expressions processing.
        - Built-in `traceback` module for exception traceback extraction.
        - `LoggerManager` class for logging functionalities.
        - `ParamManager` class for accessing parameters if needed.

    Upstream functions:
        - The main program or modules that need to parse a Markdown file into JSON.

    Downstream functions:
        - `parse_markdown`
        - `save_json`
        - Helper methods for parsing different parts of the Markdown content.

    """

    def __init__(self, md_file_path: str, output_folder: str, logger: LoggerManager):
        """
        Initialize the MdParser instance.

        Parameters:
            md_file_path (str):
                The full path to the Markdown (.md) file to be parsed.
            output_folder (str):
                The path to the output folder where the JSON file will be saved.
            logger (LoggerManager):
                An instance of LoggerManager for logging.

        Returns:
            None

        Raises:
            FileNotFoundError:
                If the Markdown file does not exist at the specified path.
            PermissionError:
                If the program lacks permissions to read the Markdown file.

        Dependencies:
            - `os.path.exists` to check if the file exists.
            - `logger` to log messages.

        Upstream functions:
            - Called by the main program or module that needs to parse a Markdown file.

        Downstream functions:
            - None

        """
        self.md_file_path = md_file_path
        self.output_folder = output_folder
        self.logger = logger.get_logger()
        self.logger_manager = logger  # Keep a reference to log exceptions

        if not os.path.exists(self.md_file_path):
            self.logger.error(f"Markdown file not found: '{self.md_file_path}'")
            raise FileNotFoundError(f"Markdown file not found: '{self.md_file_path}'")

        # Read the Markdown file into a list of lines
        try:
            with open(self.md_file_path, 'r', encoding='utf-8') as file:
                self.lines = file.readlines()
        except Exception as e:
            self.logger_manager.log_exception(e, 
                context_message="Failed to read the Markdown file.",
                file_name=self.md_file_path)
            raise

    def parse_markdown(self) -> dict:
        """
        Parses the Markdown content into a JSON structure according to the specified schema.

        Follows the refined instructions to parse the Markdown file and populate the JSON fields.

        Parameters:
            None

        Returns:
            dict:
                The JSON data structure representing the parsed Markdown content.

        Raises:
            Exception:
                Any exception during parsing is logged and re-raised.

        Dependencies:
            - Uses `self.lines` read during initialization.
            - Calls helper methods to parse different content types.
            - Uses `self.position_counter` to keep track of element positions.
            - Uses regular expressions for parsing.

        Upstream functions:
            - Called by the main program or module to get the JSON data.

        Downstream functions:
            - `_parse_title`
            - `_parse_content`
            - Logging methods from `LoggerManager`.

        """
        try:
            json_data = {
                "document": {
                    "title": "",
                    "content": []
                }
            }

            index = 0  # Line index
            total_lines = len(self.lines)

            # Initialize position counter
            self.position_counter = 1

            # Extract document title
            title, index = self._parse_title(index)
            json_data["document"]["title"] = title

            # Set initial parent and level
            parent = "document"
            current_level = 1

            # Parse the rest of the content
            content, index = self._parse_content(index, parent, current_level)

            json_data["document"]["content"].extend(content)

            return json_data

        except Exception as e:
            self.logger_manager.log_exception(e, context_message="Error parsing Markdown file.",
                                            file_name=self.md_file_path)
            raise

    def _parse_content(self, index: int, parent: str, current_level: int) -> (list, int):
        """
        Parses the Markdown content into a list of content items according to the specified schema.

        Parameters:
            index (int):
                The current line index in the Markdown file.
            parent (str):
                The parent container type or heading text. Indicates where the current content belongs.
            current_level (int):
                The current heading level (e.g., 1 for H1, 2 for H2).

        Returns:
            tuple (list, int):
                - A list of content items (dict) parsed from the Markdown file.
                - The updated line index after parsing.

        Raises:
            None

        Dependencies:
            - Calls helper methods to parse paragraphs, lists, tables, and headings.
            - Uses regular expressions to identify different Markdown elements.
            - Uses `self.position_counter` to assign sequential positions to elements.

        Upstream functions:
            - Called by `parse_markdown`.
            - Recursively called within itself when parsing sub-headings.

        Downstream functions:
            - `_is_heading_line`
            - `_get_heading_level`
            - `_collect_list_items`
            - `_collect_table_lines`
            - Other helper methods for parsing lists, tables, paragraphs.

        """
        content = []
        total_lines = len(self.lines)
        buffer_paragraph = []
        while index < total_lines:
            line = self.lines[index]
            stripped_line = line.strip()
            if self._is_heading_line(stripped_line):
                heading_level = self._get_heading_level(stripped_line)
                if heading_level <= current_level:
                    # End of current section; higher or same level heading
                    break
                else:
                    # New sub-heading
                    heading_text = stripped_line[heading_level+1:].strip()
                    # Create content item for heading
                    content_item = {
                        "type": "heading",
                        "content": heading_text,
                        "position": self.position_counter,
                        "parent": parent,
                        "level": heading_level
                    }
                    content.append(content_item)
                    self.position_counter += 1
                    # Update parent to this heading
                    new_parent = heading_text
                    # Recursively parse the content under this heading
                    index += 1
                    sub_content, index = self._parse_content(index, new_parent, heading_level)
                    content.extend(sub_content)
                    # Continue parsing
                    continue
            elif self._is_list_item(stripped_line):
                # Parse list
                list_items, index = self._collect_list_items(index)
                content_item = {
                    "type": "list",
                    "list_items": list_items,
                    "position": self.position_counter,
                    "parent": parent
                }
                content.append(content_item)
                self.position_counter += 1
            elif self._is_table_line(stripped_line):
                # Parse table
                table_lines, index = self._collect_table_lines(index)
                content_item = {
                    "type": "table",
                    "table": table_lines,
                    "position": self.position_counter,
                    "parent": parent
                }
                content.append(content_item)
                self.position_counter += 1
            elif stripped_line == '':
                # Empty line, possible paragraph separator
                if buffer_paragraph:
                    paragraph_text = ' '.join(buffer_paragraph).strip()
                    content_item = {
                        "type": "paragraph",
                        "content": paragraph_text,
                        "position": self.position_counter,
                        "parent": parent
                    }
                    content.append(content_item)
                    self.position_counter += 1
                    buffer_paragraph = []
                index += 1
            else:
                # Collect paragraph lines
                buffer_paragraph.append(stripped_line)
                index += 1

        # Add any remaining buffered paragraph
        if buffer_paragraph:
            paragraph_text = ' '.join(buffer_paragraph).strip()
            content_item = {
                "type": "paragraph",
                "content": paragraph_text,
                "position": self.position_counter,
                "parent": parent
            }
            content.append(content_item)
            self.position_counter += 1
            buffer_paragraph = []

        return content, index
    
    def _collect_list_items(self, index: int) -> (list, int):
        """
        Collects consecutive list items starting from the given index.

        Parameters:
            index (int):
                The current line index in the Markdown file.

        Returns:
            tuple (list, int):
                - A list of list item strings.
                - The updated line index after parsing the list.

        Raises:
            None

        Dependencies:
            - Uses `_is_list_item` method to identify list items.

        Upstream functions:
            - Called by `_parse_content` when a list is detected.

        Downstream functions:
            - None

        """
        list_items = []
        total_lines = len(self.lines)
        while index < total_lines:
            line = self.lines[index]
            stripped_line = line.strip()
            if self._is_list_item(stripped_line):
                # Remove list marker
                item_text = re.sub(r'^(\*|\-|\+|\d+\.)\s', '', stripped_line).strip()
                list_items.append(item_text)
                index += 1
            else:
                break
        return list_items, index

    def _collect_table_lines(self, index: int) -> (list, int):
        """
        Collects consecutive table lines starting from the given index.

        Parameters:
            index (int):
                The current line index in the Markdown file.

        Returns:
            tuple (list, int):
                - A list of table line strings.
                - The updated line index after parsing the table.

        Raises:
            None

        Dependencies:
            - Uses `_is_table_line` method to identify table lines.
            - Uses regular expressions to detect table separator lines.

        Upstream functions:
            - Called by `_parse_content` when a table is detected.

        Downstream functions:
            - None

        """
        table_lines = []
        total_lines = len(self.lines)
        while index < total_lines:
            line = self.lines[index]
            stripped_line = line.strip()
            if self._is_table_line(stripped_line) or re.match(r'^\s*\|?(---|\:?\-+\:)\|', stripped_line):
                table_lines.append(stripped_line)
                index += 1
            else:
                break
        return table_lines, index    
    def save_json(self, json_data: dict, output_file_name: str):
        """
        Saves the JSON data to a file in the specified output folder.

        Parameters:
            json_data (dict):
                The JSON data to be saved.
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
            - Called after parsing to save the generated JSON data.

        Downstream functions:
            - None

        """
        try:
            output_path = os.path.join(self.output_folder, f"{output_file_name}.json")
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, indent=2)
            self.logger.info(f"JSON data successfully saved to '{output_path}'")
        except Exception as e:
            self.logger_manager.log_exception(e, 
                context_message="Error saving JSON file.",
                file_name=output_path)
            raise

    def _parse_title(self, index: int) -> (str, int):
        """
        Parses the document title from the Markdown content.

        Parameters:
            index (int):
                The current line index in the Markdown file.

        Returns:
            tuple (str, int):
                - The document title as a string.
                - The updated line index after parsing the title.

        Raises:
            None

        Dependencies:
            - Uses regular expressions to identify the '# ' heading.
            - Uses `self.logger` to log information.

        Upstream functions:
            - Called by `parse_markdown`.

        Downstream functions:
            - None

        """
        title = ""
        total_lines = len(self.lines)
        while index < total_lines:
            line = self.lines[index].strip()
            if line.startswith('# '):  # Level 1 heading
                title = line[2:].strip()
                index += 1
                break
            elif line == '':
                index += 1
                continue
            else:
                # No title found, use first non-empty line or file name
                if title == '':
                    title = os.path.splitext(os.path.basename(self.md_file_path))[0]
                break
        if title == '':
            title = os.path.splitext(os.path.basename(self.md_file_path))[0]
        self.logger.info(f"Document title parsed: '{title}'")
        return title, index

    def _parse_content_text1(self, index: int) -> (dict, int):
        """
        Parses the content before the first '##' heading.

        Parameters:
            index (int):
                The current line index in the Markdown file.

        Returns:
            tuple (dict, int):
                - A dictionary containing paragraphs, lists, and tables before the first '##'.
                - The updated line index after parsing.

        Raises:
            None

        Dependencies:
            - Calls helper methods to parse paragraphs, lists, and tables.

        Upstream functions:
            - Called by `parse_markdown`.

        Downstream functions:
            - `_parse_paragraphs`
            - `_parse_lists`
            - `_parse_tables`

        """
        content_text1 = {
            "paragraph": [],
            "list": [],
            "table": []
        }
        buffer = []
        total_lines = len(self.lines)
        while index < total_lines:
            line = self.lines[index]
            stripped_line = line.strip()
            if stripped_line.startswith('## '):
                break  # Reached first section
            elif stripped_line.startswith('# '):
                # Already parsed title, skip
                index += 1
                continue
            elif self._is_list_item(stripped_line):
                # Parse list
                list_items, index = self._parse_list(index)
                content_text1["list"].append({"list_item": list_items})
            elif self._is_table_line(stripped_line):
                # Parse table
                table_str, index = self._parse_table(index)
                content_text1["table"].append(table_str)
            elif stripped_line == '':
                # Empty line, possible paragraph separator
                if buffer:
                    paragraph = ' '.join(buffer).strip()
                    if paragraph:
                        content_text1["paragraph"].append(paragraph)
                    buffer = []
                index += 1
            else:
                buffer.append(stripped_line)
                index += 1

        # Add any remaining buffered paragraph
        if buffer:
            paragraph = ' '.join(buffer).strip()
            if paragraph:
                content_text1["paragraph"].append(paragraph)
            buffer = []

        return content_text1, index

    def _parse_sections(self, index: int) -> (list, int):
        """
        Parses the sections starting with '##' headings.

        Parameters:
            index (int):
                The current line index in the Markdown file.

        Returns:
            tuple (list, int):
                - A list of sections parsed.
                - The updated line index after parsing.

        Raises:
            None

        Dependencies:
            - Calls methods to parse section content and subsections.

        Upstream functions:
            - Called by `parse_markdown`.

        Downstream functions:
            - `_parse_section`

        """
        sections = []
        total_lines = len(self.lines)
        while index < total_lines:
            line = self.lines[index]
            stripped_line = line.strip()
            if stripped_line.startswith('## '):
                # Start a new section
                section_header = stripped_line[3:].strip()
                index += 1
                section_content, index = self._parse_section_content(index, section_level=2)
                section = {
                    "section_header": section_header,
                    "section_content": section_content
                }
                sections.append(section)
            else:
                # Not a section heading, possibly end of sections
                break

        return sections, index

    def _parse_content_text2(self, index: int) -> (dict, int):
        """
        Parses the content after the last '##' heading.

        Parameters:
            index (int):
                The current line index in the Markdown file.

        Returns:
            tuple (dict, int):
                - A dictionary containing paragraphs, lists, and tables after the last '##'.
                - The updated line index after parsing.

        Raises:
            None

        Dependencies:
            - Similar to `_parse_content_text1`.

        Upstream functions:
            - Called by `parse_markdown`.

        Downstream functions:
            - Same helper methods as `_parse_content_text1`.

        """
        content_text2 = {
            "paragraph": [],
            "list": [],
            "table": []
        }
        buffer = []
        total_lines = len(self.lines)
        while index < total_lines:
            line = self.lines[index]
            stripped_line = line.strip()
            if self._is_heading_line(stripped_line):
                # We should not encounter headings here, but skip if we do
                index += 1
                continue
            elif self._is_list_item(stripped_line):
                # Parse list
                list_items, index = self._parse_list(index)
                content_text2["list"].append({"list_item": list_items})
            elif self._is_table_line(stripped_line):
                # Parse table
                table_str, index = self._parse_table(index)
                content_text2["table"].append(table_str)
            elif stripped_line == '':
                # Empty line, possible paragraph separator
                if buffer:
                    paragraph = ' '.join(buffer).strip()
                    if paragraph:
                        content_text2["paragraph"].append(paragraph)
                    buffer = []
                index += 1
            else:
                buffer.append(stripped_line)
                index += 1

        # Add any remaining buffered paragraph
        if buffer:
            paragraph = ' '.join(buffer).strip()
            if paragraph:
                content_text2["paragraph"].append(paragraph)
            buffer = []

        return content_text2, index

    def _parse_section_content(self, index: int, section_level: int) -> (dict, int):
        """
        Parses the content within a section, handling subsections.

        Parameters:
            index (int):
                The current line index in the Markdown file.
            section_level (int):
                The current section level (e.g., 2 for '##', 3 for '###').

        Returns:
            tuple (dict, int):
                - A dictionary containing section content (paragraphs, lists, tables, subsections).
                - The updated line index after parsing.

        Raises:
            None

        Dependencies:
            - Calls helper methods to parse paragraphs, lists, tables, subsections.

        Upstream functions:
            - Called by `_parse_sections` and recursively by itself for subsections.

        Downstream functions:
            - `_parse_subsection_content`
            - `_is_heading_line`
            - `_is_list_item`
            - `_parse_list`
            - `_is_table_line`
            - `_parse_table`

        """
        content = {
            f"section_paragraph" if section_level == 2 else f"sub_section_paragraph" if section_level == 3 else f"sub_sub_section_paragraph": [],
            f"section_list" if section_level == 2 else f"sub_section_list" if section_level == 3 else f"sub_sub_section_list": [],
            f"section_table" if section_level == 2 else f"sub_section_table" if section_level == 3 else f"sub_sub_section_table": [],
        }

        subsection_key = None
        if section_level == 2:
            subsection_key = "sub_section"
        elif section_level == 3:
            subsection_key = "sub_sub_section"

        if subsection_key:
            content[subsection_key] = []

        buffer = []
        total_lines = len(self.lines)
        while index < total_lines:
            line = self.lines[index]
            stripped_line = line.strip()
            if self._is_heading_line(stripped_line):
                heading_level = self._get_heading_level(stripped_line)
                if heading_level == section_level:
                    # Next section at the same level; end parsing this section
                    break
                elif heading_level == section_level + 1:
                    # Subsection
                    sub_header = stripped_line[heading_level+1:].strip()
                    index += 1
                    sub_content, index = self._parse_section_content(index, section_level + 1)
                    if section_level == 2:
                        sub_section = {
                            "sub_section_header": sub_header,
                            "sub_section_content": sub_content
                        }
                    elif section_level == 3:
                        sub_section = {
                            "sub_sub_section_header": sub_header,
                            "sub_sub_section_paragraph": sub_content.get("sub_sub_section_paragraph", []),
                            "sub_sub_section_list": sub_content.get("sub_sub_section_list", []),
                            "sub_sub_section_table": sub_content.get("sub_sub_section_table", [])
                        }
                    # Remove any keys with empty or None values
                    sub_section = {k: v for k, v in sub_section.items() if v}
                    content[subsection_key].append(sub_section)
                    # Remove None values
                    sub_section = {k: v for k, v in sub_section.items() if v is not None}
                    content[subsection_key].append(sub_section)
                else:
                    # Heading level deeper than expected, skip or handle as needed
                    index += 1
            elif self._is_list_item(stripped_line):
                # Parse list
                list_items, index = self._parse_list(index)
                list_key = f"section_list" if section_level ==2 else f"sub_section_list" if section_level ==3 else f"sub_sub_section_list"
                content[list_key].append({"list_item": list_items})
            elif self._is_table_line(stripped_line):
                # Parse table
                table_str, index = self._parse_table(index)
                table_key = f"section_table" if section_level ==2 else f"sub_section_table" if section_level ==3 else f"sub_sub_section_table"
                content[table_key].append(table_str)
            elif stripped_line == '':
                # Empty line, possible paragraph separator
                if buffer:
                    paragraph = ' '.join(buffer).strip()
                    if paragraph:
                        paragraph_key = f"section_paragraph" if section_level ==2 else f"sub_section_paragraph" if section_level ==3 else f"sub_sub_section_paragraph"
                        content[paragraph_key].append(paragraph)
                    buffer = []
                index += 1
            else:
                buffer.append(stripped_line)
                index += 1

        # Add any remaining buffered paragraph
        if buffer:
            paragraph = ' '.join(buffer).strip()
            if paragraph:
                paragraph_key = f"section_paragraph" if section_level ==2 else f"sub_section_paragraph" if section_level ==3 else f"sub_sub_section_paragraph"
                content[paragraph_key].append(paragraph)
            buffer = []

        return content, index

    def _is_heading_line(self, line: str) -> bool:
        """
        Checks if a line is a Markdown heading.

        Parameters:
            line (str):
                The line to check.

        Returns:
            bool:
                True if the line is a heading (starts with '#'); False otherwise.

        Raises:
            None

        Dependencies:
            - Uses string methods.

        Upstream functions:
            - Called by parsing methods to detect headings.

        Downstream functions:
            - None

        """
        return line.startswith('#')

    def _get_heading_level(self, line: str) -> int:
        """
        Determines the heading level of a Markdown heading.

        Parameters:
            line (str):
                The heading line.

        Returns:
            int:
                The heading level (number of '#' characters).

        Raises:
            None

        Dependencies:
            - Uses string methods.

        Upstream functions:
            - Used to determine heading levels during parsing.

        Downstream functions:
            - None

        """
        return len(line) - len(line.lstrip('#'))

    def _is_list_item(self, line: str) -> bool:
        """
        Checks if a line is a list item.

        Parameters:
            line (str):
                The line to check.

        Returns:
            bool:
                True if the line is a list item; False otherwise.

        Raises:
            None

        Dependencies:
            - Uses regular expressions.

        Upstream functions:
            - Called by parsing methods to detect lists.

        Downstream functions:
            - None

        """
        return re.match(r'^(\*|\-|\+|\d+\.)\s', line) is not None

    def _parse_list(self, index: int) -> (list, int):
        """
        Parses a list from the Markdown content.

        Parameters:
            index (int):
                The current line index in the Markdown file.

        Returns:
            tuple (list, int):
                - A list of list items.
                - The updated line index after parsing the list.

        Raises:
            None

        Dependencies:
            - Uses regular expressions to identify list items.

        Upstream functions:
            - Called when a list is detected during parsing.

        Downstream functions:
            - None

        """
        list_items = []
        total_lines = len(self.lines)
        while index < total_lines:
            line = self.lines[index]
            stripped_line = line.strip()
            if self._is_list_item(stripped_line):
                item = re.sub(r'^(\*|\-|\+|\d+\.)\s', '', stripped_line).strip()
                list_items.append(item)
                index +=1
            else:
                break
        return list_items, index

    def _is_table_line(self, line: str) -> bool:
        """
        Checks if a line is part of a Markdown table.

        Parameters:
            line (str):
                The line to check.

        Returns:
            bool:
                True if the line is part of a table; False otherwise.

        Raises:
            None

        Dependencies:
            - Uses string methods.

        Upstream functions:
            - Called during parsing to detect tables.

        Downstream functions:
            - None

        """
        return '|' in line and line.strip().startswith('|')

    def _parse_table(self, index: int) -> (str, int):
        """
        Parses a Markdown table from the content.

        Parameters:
            index (int):
                The current line index in the Markdown file.

        Returns:
            tuple (str, int):
                - The full table as a string.
                - The updated line index after parsing the table.

        Raises:
            None

        Dependencies:
            - Collects lines containing table content.

        Upstream functions:
            - Called when a table is detected during parsing.

        Downstream functions:
            - None

        """
        table_lines = []
        total_lines = len(self.lines)
        while index < total_lines:
            line = self.lines[index]
            if self._is_table_line(line) or re.match(r'^\s*\|?(---|\:?\-+\:)\|', line.strip()):
                table_lines.append(line.rstrip())
                index +=1
            else:
                break
        table_str = '\n'.join(table_lines)
        return table_str, index