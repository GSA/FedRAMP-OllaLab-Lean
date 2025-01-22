# data_processing.py

import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# For Word document parsing
import docx
from docx.table import _Cell as DocxCell
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# For PDF parsing
import pdfplumber

# For OCR
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Logging
import logging

# Import custom exceptions
from exceptions import (
    UnsupportedFileTypeError,
    ParsingError,
    TableExtractionError,
    DocxFileError,
    PDFFileError,
    StructureInterpretationError,
    NestedTableParsingError,
    MergedCellError,
)

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# You can configure logging handlers here (e.g., StreamHandler, FileHandler)

class Cell:
    """
    Represents an individual cell within a table.

    Attributes:
        content (Any):
            The text or data within the cell.
        rowspan (int):
            Number of rows this cell spans.
        colspan (int):
            Number of columns this cell spans.
        styles (Dict[str, Any]):
            Styling information (bold, italic, font size, etc.).
        nested_table (Optional[Table]):
            A nested Table object if the cell contains a nested table.
    """

    def __init__(
        self,
        content: Any,
        rowspan: int = 1,
        colspan: int = 1,
        styles: Optional[Dict[str, Any]] = None,
        nested_table: Optional['Table'] = None,
    ):
        self.content = content
        self.rowspan = rowspan
        self.colspan = colspan
        self.styles = styles if styles is not None else {}
        self.nested_table = nested_table

class Table:
    """
    Represents a table extracted from a document.

    Attributes:
        data (List[List[Cell]]): 
            The data of the table as a list of rows, each row being a list of Cell objects.
        position (int): 
            The index position of the table in the document.
        metadata (Dict[str, Any]): 
            Metadata about the table, such as page number, titles, etc.
    """

    def __init__(
        self,
        data: List[List[Cell]],
        position: int,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.data = data
        self.position = position
        self.metadata = metadata if metadata is not None else {}

class Document:
    """
    Represents a parsed document and its content.

    Attributes:
        file_path (str): 
            The file path to the document.
        content (Any): 
            The raw content of the document.
        tables (List[Table]): 
            A list of tables extracted from the document.
        metadata (Dict[str, Any]): 
            Metadata associated with the document.
    """

    def __init__(
        self,
        file_path: str,
        content: Any,
        tables: Optional[List[Table]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.file_path = file_path
        self.content = content
        self.tables = tables if tables is not None else []
        self.metadata = metadata if metadata is not None else {}

def parse_documents(file_paths: List[str]) -> List[Document]:
    """
    Parses multiple documents and extracts raw table data.

    Parameters:
        file_paths (List[str]): 
            A list of file paths to the documents (MS Word or PDF) to be parsed.

    Returns:
        List[Document]:
            A list of Document objects containing extracted table data and metadata.

    Raises:
        FileNotFoundError:
            If any of the files in `file_paths` cannot be found.
        UnsupportedFileTypeError:
            If any of the files are not supported types (.doc, .docx, .pdf).
        ParsingError:
            If an error occurs during parsing of any document.

    Dependencies:
        - Requires access to file system to read the specified documents.
        - Depends on libraries for reading Word and PDF documents (e.g., python-docx, pdfplumber).
    """
    documents = []
    for file_path in file_paths:
        logger.debug(f"Parsing document: {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"The file {file_path} was not found.")
        file_extension = Path(file_path).suffix.lower()
        try:
            if file_extension in ['.doc', '.docx']:
                document = read_word_document(file_path)
            elif file_extension == '.pdf':
                document = read_pdf_document(file_path)
            else:
                logger.error(f"Unsupported file type: {file_extension}")
                raise UnsupportedFileTypeError(f"The file type {file_extension} is not supported.")
            logger.debug(f"Extracting tables from document: {file_path}")
            document.tables = extract_raw_tables(document)
            documents.append(document)
        except Exception as e:
            logger.exception(f"An error occurred while parsing {file_path}")
            raise ParsingError(f"An error occurred while parsing {file_path}: {str(e)}")
    return documents

def read_word_document(file_path: str) -> Document:
    """
    Reads a Microsoft Word document and prepares it for table extraction.

    Parameters:
        file_path (str): 
            The file path to the Word document.

    Returns:
        Document:
            A Document object containing the content of the Word file.

    Raises:
        FileNotFoundError:
            If the file at `file_path` does not exist.
        DocxFileError:
            If an error occurs while reading the Word document.
    """
    try:
        logger.debug(f"Reading Word document: {file_path}")
        doc = docx.Document(file_path)
        document = Document(file_path=file_path, content=doc)
        return document
    except Exception as e:
        logger.exception(f"Error reading Word document: {file_path}")
        raise DocxFileError(f"Error reading Word document {file_path}: {str(e)}")

def read_pdf_document(file_path: str) -> Document:
    """
    Reads a PDF document and prepares it for table extraction.

    Parameters:
        file_path (str): 
            The file path to the PDF document.

    Returns:
        Document:
            A Document object containing the content of the PDF file.

    Raises:
        FileNotFoundError:
            If the file at `file_path` does not exist.
        PDFFileError:
            If an error occurs while reading the PDF document.
    """
    try:
        logger.debug(f"Reading PDF document: {file_path}")
        pdf = pdfplumber.open(file_path)
        document = Document(file_path=file_path, content=pdf)
        return document
    except Exception as e:
        logger.exception(f"Error reading PDF document: {file_path}")
        raise PDFFileError(f"Error reading PDF document {file_path}: {str(e)}")

def extract_raw_tables(document: Document) -> List[Table]:
    """
    Extracts raw tables from a single document object.

    Parameters:
        document (Document): 
            A Document object representing the parsed document content.

    Returns:
        List[Table]:
            A list of Table objects extracted from the document.

    Raises:
        TableExtractionError:
            If an error occurs during table extraction.
    """
    tables = []
    try:
        if isinstance(document.content, docx.Document):
            tables = extract_tables_from_word(document.content)
        elif isinstance(document.content, pdfplumber.PDF):
            tables = extract_tables_from_pdf(document.content)
        else:
            logger.error("Unsupported document content type.")
            raise TableExtractionError("Unsupported document content type.")
        return tables
    except Exception as e:
        logger.exception(f"Error extracting tables from document {document.file_path}")
        raise TableExtractionError(f"Error extracting tables from document {document.file_path}: {str(e)}")

def extract_tables_from_word(doc) -> List[Table]:
    """
    Extracts tables from a Word document.

    Parameters:
        doc (docx.Document): 
            The Word document object.

    Returns:
        List[Table]:
            A list of Table objects extracted from the document.

    Raises:
        TableExtractionError:
            If an error occurs during table extraction.
    """
    logger.debug("Extracting tables from Word document")
    tables = []
    try:
        for idx, table in enumerate(doc.tables):
            logger.debug(f"Processing table {idx} in Word document")
            max_columns = get_max_columns_in_table(table)
            # Initialize grid to None
            grid = []
            row_spans = {}  # Key: (row_idx, col_idx), Value: remaining rowspan

            for row_idx, row in enumerate(table.rows):
                grid_row = [None] * max_columns
                col_idx = 0

                while col_idx < max_columns:
                    # Check for cells that are spanned from previous rows
                    if (row_idx, col_idx) in row_spans and row_spans[(row_idx, col_idx)] > 0:
                        # This position is occupied by a cell with rowspan > 1
                        row_spans[(row_idx, col_idx)] -= 1
                        col_idx += 1
                        continue

                    # Get the corresponding cell in the current row
                    cell = get_cell(table, row_idx, col_idx)
                    if cell is None:
                        col_idx += 1
                        continue

                    cell_text = cell.text.strip()
                    cell_styles = extract_cell_styles(cell)
                    rowspan, colspan = get_cell_span(cell)

                    nested_table = None
                    if cell.tables:
                        nested_table = extract_word_nested_tables(cell)

                    cell_obj = Cell(
                        content=cell_text,
                        rowspan=rowspan,
                        colspan=colspan,
                        styles=cell_styles,
                        nested_table=nested_table,
                    )

                    # Place cell_obj in grid positions considering rowspan and colspan
                    for i in range(rowspan):
                        for j in range(colspan):
                            r = row_idx + i
                            c = col_idx + j
                            if r >= len(grid):
                                # Extend grid to accommodate new rows
                                grid.append([None] * max_columns)
                            grid[r][c] = cell_obj
                            if i > 0:
                                row_spans[(r, c)] = rowspan - i - 1
                    col_idx += colspan
                # Increment row index

            # Remove any extra rows
            grid = grid[:len(grid)]
            table_obj = Table(data=grid, position=idx)
            tables.append(table_obj)
        return tables
    except Exception as e:
        logger.exception("Error extracting tables from Word document")
        raise TableExtractionError(f"Error extracting tables from Word document: {str(e)}")

def get_max_columns_in_table(table) -> int:
    """
    Determines the maximum number of columns in the table considering cells with colspan.

    Parameters:
        table (docx.table.Table): 
            The table object.

    Returns:
        int: The maximum number of columns in the table.
    """
    max_columns = 0
    for row in table.rows:
        col_count = 0
        for cell in row.cells:
            _, colspan = get_cell_span(cell)
            col_count += colspan
        if col_count > max_columns:
            max_columns = col_count
    return max_columns

def get_cell(table, row_idx, col_idx):
    """
    Retrieves a cell object from a table at the given row and column indices.

    Parameters:
        table (docx.table.Table): 
            The table object.
        row_idx (int):
            The row index.
        col_idx (int):
            The column index.

    Returns:
        docx.table._Cell or None:
            The cell object, or None if not found.
    """
    try:
        row = table.rows[row_idx]
        cells = row.cells
        if col_idx < len(cells):
            return cells[col_idx]
        else:
            return None
    except IndexError:
        # Cell may be spanned, return None
        return None

def extract_tables_from_pdf(pdf) -> List[Table]:
    """
    Extracts tables from a PDF document.

    Parameters:
        pdf (pdfplumber.PDF): 
            The PDF document object.

    Returns:
        List[Table]:
            A list of Table objects extracted from the document.

    Raises:
        TableExtractionError:
            If an error occurs during table extraction.
    """
    logger.debug("Extracting tables from PDF document")
    tables = []
    idx = 0
    try:
        for page_number, page in enumerate(pdf.pages, start=1):
            logger.debug(f"Processing page {page_number} in PDF document")
            extracted_tables = page.extract_tables()
            for table in extracted_tables:
                table_data = []
                for row in table:
                    row_data = []
                    for cell_content in row:
                        cell_text = cell_content.strip() if cell_content else ''
                        cell_obj = Cell(content=cell_text)
                        row_data.append(cell_obj)
                    table_data.append(row_data)
                table_obj = Table(
                    data=table_data,
                    position=idx,
                    metadata={'page_number': page_number}
                )
                tables.append(table_obj)
                idx += 1
        return tables
    except Exception as e:
        logger.exception("Error extracting tables from PDF document")
        raise TableExtractionError(f"Error extracting tables from PDF document: {str(e)}")

def extract_cell_styles(cell: DocxCell) -> Dict[str, Any]:
    """
    Extracts styles from a Word cell.

    Parameters:
        cell (docx.table._Cell): 
            The cell object from which to extract styles.

    Returns:
        Dict[str, Any]:
            A dictionary of styles applied to the cell.
    """
    styles = {}
    # Extract styles from the first run of the first paragraph
    if cell.paragraphs and cell.paragraphs[0].runs:
        run = cell.paragraphs[0].runs[0]
        styles['bold'] = run.bold
        styles['italic'] = run.italic
        styles['underline'] = run.underline
        styles['font_size'] = run.font.size.pt if run.font.size else None
        styles['font_name'] = run.font.name
        styles['color'] = run.font.color.rgb if run.font.color else None
    return styles

def get_cell_span(cell: DocxCell) -> Tuple[int, int]:
    """
    Determines the rowspan and colspan of a Word cell.

    Parameters:
        cell (docx.table._Cell): 
            The cell object from which to determine span.

    Returns:
        Tuple[int, int]:
            A tuple containing (rowspan, colspan)
    """
    # Access the underlying XML to find the gridSpan and vMerge attributes
    tc = cell._tc  # The XML element
    grid_span = tc.xpath("./w:tcPr/w:gridSpan")
    v_merge = tc.xpath("./w:tcPr/w:vMerge")

    # Colspan
    if grid_span:
        colspan = int(grid_span[0].get(qn('w:val')))
    else:
        colspan = 1

    # Rowspan
    if v_merge:
        v_merge_val = v_merge[0].get(qn('w:val'))
        if v_merge_val == 'restart' or v_merge_val is None:
            rowspan = 1
            # We need to check following rows to find how many rows are merged
            rowspan += count_row_span(cell)
        else:
            rowspan = 0  # Continuation of merge, will be handled in cell placement
    else:
        rowspan = 1

    return rowspan, colspan

def count_row_span(cell: DocxCell) -> int:
    """
    Counts how many rows a cell spans in a vertical merge.

    Parameters:
        cell (docx.table._Cell):
            The starting cell of the vertical merge.

    Returns:
        int:
            The number of rows the cell spans.
    """
    rowspan = 0
    cell_element = cell._tc
    grid_span = cell_element.xpath("./w:tcPr/w:gridSpan")
    if grid_span:
        colspan = int(grid_span[0].get(qn('w:val')))
    else:
        colspan = 1

    v_merge = cell_element.xpath("./w:tcPr/w:vMerge")
    if v_merge:
        v_merge_val = v_merge[0].get(qn('w:val'))
        if v_merge_val == 'restart' or v_merge_val is None:
            rowspan = 1
            current_row = cell._element.getparent()
            next_row = current_row.getnext()
            while next_row is not None:
                cells_in_row = next_row.findall('.//w:tc', cell._element.nsmap)
                if not cells_in_row:
                    break
                next_cell = cells_in_row[0]  # Assuming the cells are in order
                v_merge_next = next_cell.xpath("./w:tcPr/w:vMerge")
                if v_merge_next:
                    v_merge_val_next = v_merge_next[0].get(qn('w:val'))
                    if v_merge_val_next == 'continue':
                        rowspan += 1
                        next_row = next_row.getnext()
                        continue
                break  # End of merged cells
    return rowspan

def extract_word_nested_tables(cell: DocxCell) -> Optional[List['Table']]:
    """
    Extracts nested tables from a Word document cell.

    Parameters:
        cell (docx.table._Cell): 
            The cell object from which to extract nested tables.

    Returns:
        Optional[List[Table]]:
            A list of Table objects representing the nested tables, if any.
    """
    try:
        nested_tables = []
        for nested_table in cell.tables:
            logger.debug("Extracting nested table from cell")
            table_data = []
            for row in nested_table.rows:
                row_data = []
                for nested_cell in row.cells:
                    cell_text = nested_cell.text.strip()
                    nested_cell_tables = extract_word_nested_tables(nested_cell)
                    cell_obj = Cell(content=cell_text, nested_table=nested_cell_tables)
                    row_data.append(cell_obj)
                table_data.append(row_data)
            nested_table_obj = Table(data=table_data, position=0)
            nested_tables.append(nested_table_obj)
        return nested_tables if nested_tables else None
    except Exception as e:
        logger.exception("Error extracting nested tables from cell")
        raise NestedTableParsingError(f"Error extracting nested tables: {str(e)}")

# Additional code for OCR handling could be added here if needed