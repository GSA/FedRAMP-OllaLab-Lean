# app/anydoc_2_json/modules/doc_converter.py

import os
from pathlib import Path
from typing import Union

from docling.document_converter import DocumentConverter, InputFormat, ConversionResult, ConversionStatus
from .logger_manager import LoggerManager
from .param_manager import ParamManager

class DocConverter:
    """
    DocConverter class for converting documents to Markdown using Docling,
    handling heading adjustments, and saving the resulting markdown file.

    Dependencies:
        - `os` and `pathlib.Path` modules for file system interactions.
        - `docling.document_converter` for document conversion functionalities.
        - `LoggerManager` for logging management.
        - `ParamManager` for accessing parameters.

    Upstream functions:
        - Initialized and called by main application scripts or modules that require document conversion.

    Downstream functions:
        - `convert_document`
        - `adjust_headings`
        - `save_markdown`
        - `get_markdown_headings`
        - `add_document_title`
        - `increment_headings_level`

    """

    def __init__(self, logger_manager: LoggerManager, param_manager: ParamManager):
        """
        Initialize the DocConverter instance.

        Parameters:
            logger_manager (LoggerManager):
                The LoggerManager instance for logging.
            param_manager (ParamManager):
                The ParamManager instance for accessing parameters.

        Returns:
            None

        Raises:
            None

        Dependencies:
            - Assigns `self.logger` from `logger_manager`.
            - Accesses parameters from `param_manager`.

        Upstream functions:
            - Constructor called by modules requiring document conversion.

        Downstream functions:
            - None

        """
        self.logger = logger_manager.get_logger()
        self.param_manager = param_manager

    def convert_document(self, input_file: Union[str, Path], output_folder: Union[str, Path]) -> Path:
        """
        Convert the input document to Markdown using Docling and save it to the output folder.

        Parameters:
            input_file (str or Path):
                The path to the input document (.docx or .pdf).
            output_folder (str or Path):
                The path to the output folder where the markdown file will be saved.

        Returns:
            Path:
                The path to the saved markdown file.

        Raises:
            ValueError:
                If the input file format is not supported.
            Exception:
                If any error occurs during conversion.

        Dependencies:
            - `os` and `pathlib.Path` for file operations.
            - `docling.document_converter.DocumentConverter` for conversion.
            - `self.adjust_headings` to adjust headings in the markdown content.
            - `self.save_markdown` to save the markdown file.
            - Logging via `self.logger`.

        Upstream functions:
            - Called by modules or scripts that need to convert documents.

        Downstream functions:
            - `self.adjust_headings`
            - `self.save_markdown`

        """
        try:
            input_path = Path(input_file)
            output_folder = Path(output_folder)
            file_extension = input_path.suffix.lower()
            supported_formats = ['.docx', '.pdf']

            if file_extension not in supported_formats:
                self.logger.error(f"Unsupported file format: {file_extension}")
                raise ValueError(f"Unsupported file format: {file_extension}")

            # Initialize DocumentConverter
            doc_converter = DocumentConverter()

            # Determine input format
            if file_extension == '.docx':
                input_format = InputFormat.DOCX
            elif file_extension == '.pdf':
                input_format = InputFormat.PDF
            else:
                self.logger.error(f"Unsupported file format: {file_extension}")
                raise ValueError(f"Unsupported file format: {file_extension}")

            # Convert document
            conversion_result = doc_converter.convert(str(input_path))
            if conversion_result.status != ConversionStatus.SUCCESS:
                self.logger.error(f"Conversion failed with status: {conversion_result.status}")
                if conversion_result.errors:
                    for error in conversion_result.errors:
                        self.logger.error(f"Error: {error}")
                raise Exception("Document conversion failed")

            # Extract markdown content
            markdown_content = conversion_result.document.export_to_markdown()

            # Adjust headings
            adjusted_markdown = self.adjust_headings(markdown_content, input_path.stem)

            # Save markdown file
            markdown_file_path = self.save_markdown(adjusted_markdown, input_path, output_folder)

            self.logger.info(f"Markdown file saved to {markdown_file_path}")

            return markdown_file_path

        except Exception as e:
            self.logger.exception(e)
            self.logger.error(f"An error occurred during document conversion: {input_file}")
            raise

    def adjust_headings(self, markdown_content: str, default_title: str) -> str:
        """
        Adjust headings in the markdown content by adding a document title and
        incrementing existing headings' levels if necessary.

        Parameters:
            markdown_content (str):
                The original markdown content.
            default_title (str):
                The default title to use if no title is provided.

        Returns:
            str:
                The adjusted markdown content.

        Raises:
            None

        Dependencies:
            - `self.get_markdown_headings` to analyze headings.
            - Uses `self.param_manager` to get the document title if provided.
            - `self.add_document_title` to add the title.
            - `self.increment_headings_level` to adjust headings.

        Upstream functions:
            - Called by `convert_document`.

        Downstream functions:
            - `self.get_markdown_headings`
            - `self.add_document_title`
            - `self.increment_headings_level`

        """
        try:
            # Analyze headings
            headings = self.get_markdown_headings(markdown_content)
            num_level1_headings = sum(1 for h in headings if h.startswith('# '))

            # Determine document title
            # In Streamlit, the user may provide a 'document_title' parameter
            # For CLI, we use the default_title (file name without extension)
            document_title = self.param_manager.get_parameter('document_title', default_title)

            if num_level1_headings != 1:
                # Adjust headings level
                markdown_content = self.increment_headings_level(markdown_content)

                # Add document title
                markdown_content = self.add_document_title(markdown_content, document_title)

            elif num_level1_headings == 0:
                # Add document title
                markdown_content = self.add_document_title(markdown_content, document_title)

            return markdown_content

        except Exception as e:
            self.logger.exception(e)
            self.logger.error("An error occurred during heading adjustment")
            raise

    def get_markdown_headings(self, markdown_content: str) -> list:
        """
        Extract headings from markdown content.

        Parameters:
            markdown_content (str):
                The markdown content to analyze.

        Returns:
            list:
                A list of headings found in the markdown content.

        Raises:
            None

        Dependencies:
            - `str.splitlines` to split content into lines.

        Upstream functions:
            - Called by `adjust_headings`.

        Downstream functions:
            - None

        """
        lines = markdown_content.splitlines()
        headings = [line for line in lines if line.strip().startswith('#')]
        return headings

    def add_document_title(self, markdown_content: str, document_title: str) -> str:
        """
        Add a level 1 heading with the document title at the beginning of the markdown content.

        Parameters:
            markdown_content (str):
                The markdown content.
            document_title (str):
                The document title to add.

        Returns:
            str:
                The markdown content with the document title added.

        Raises:
            None

        Dependencies:
            - None

        Upstream functions:
            - Called by `adjust_headings`.

        Downstream functions:
            - None

        """
        title_heading = f"# {document_title}\n\n"
        return title_heading + markdown_content

    def increment_headings_level(self, markdown_content: str) -> str:
        """
        Increment the level of all existing headings in the markdown content by one.

        Parameters:
            markdown_content (str):
                The markdown content.

        Returns:
            str:
                The markdown content with headings adjusted.

        Raises:
            None

        Dependencies:
            - `str.replace` and processing lines.

        Upstream functions:
            - Called by `adjust_headings`.

        Downstream functions:
            - None

        """
        lines = markdown_content.splitlines()
        adjusted_lines = []
        for line in lines:
            stripped_line = line.lstrip()
            if stripped_line.startswith('#'):
                num_hashes = len(stripped_line) - len(stripped_line.lstrip('#'))
                rest_of_line = stripped_line.lstrip('#')
                new_hashes = '#' * (num_hashes + 1)
                adjusted_line = f"{new_hashes}{rest_of_line}"
                adjusted_lines.append(adjusted_line)
            else:
                adjusted_lines.append(line)
        return '\n'.join(adjusted_lines)

    def save_markdown(self, markdown_content: str, input_path: Path, output_folder: Path) -> Path:
        """
        Save the markdown content to a file in the output folder.

        Parameters:
            markdown_content (str):
                The markdown content to save.
            input_path (Path):
                The path to the input file (used to derive the output file name).
            output_folder (Path):
                The path to the output folder.

        Returns:
            Path:
                The path to the saved markdown file.

        Raises:
            IOError:
                If the markdown file cannot be written.

        Dependencies:
            - `os` and `pathlib.Path` for file operations.

        Upstream functions:
            - Called by `convert_document`.

        Downstream functions:
            - None

        """
        try:
            output_folder.mkdir(parents=True, exist_ok=True)
            output_file_name = input_path.stem + '.md'
            output_file_path = output_folder / output_file_name

            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            self.logger.info(f"Markdown file saved at {output_file_path}")

            return output_file_path

        except Exception as e:
            self.logger.exception(e)
            self.logger.error(f"An error occurred while saving markdown file: {output_file_path}")
            raise IOError(f"Failed to save markdown file: {e}")