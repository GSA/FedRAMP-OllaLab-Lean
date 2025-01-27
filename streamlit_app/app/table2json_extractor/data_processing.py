import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# For Word document parsing
import docx
from docx import Document as DocxDocument
from docx.table import _Cell, Table as DocxTable
from docx.text.paragraph import Paragraph
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
from .exceptions import (
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
        nested_table (Optional[List['Table']]):
            A nested Table object if the cell contains a nested table.
    """

    def __init__(
        self,
        content: Any,
        rowspan: int = 1,
        colspan: int = 1,
        styles: Optional[Dict[str, Any]] = None,
        nested_table: Optional[List['Table']] = None,
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

class ParsedDocument:
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

def parse_documents(file_paths: List[str]) -> Tuple[List[ParsedDocument], List[str]]:
    """
    Parses multiple documents and extracts raw table data.

    Parameters:
        file_paths (List[str]): 
            A list of file paths to the documents (MS Word or PDF) to be parsed.

    Returns:
        Tuple[List[ParsedDocument], List[str]]:
            A tuple containing:
            - A list of ParsedDocument objects containing extracted table data and metadata.
            - A list of error messages for files that failed to parse.

    Dependencies:
        - Requires access to file system to read the specified documents.
        - Depends on libraries for reading Word and PDF documents (e.g., python-docx, pdfplumber).
    """
    documents = []
    errors = []
    for file_path in file_paths:
        logger.debug(f"Parsing document: {file_path}")
        if not os.path.exists(file_path):
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            errors.append(error_msg)
            continue  # Skip to the next file
        file_extension = Path(file_path).suffix.lower()
        try:
            if file_extension == '.docx':
                document = read_word_document(file_path)
            elif file_extension == '.pdf':
                document = read_pdf_document(file_path)
            else:
                error_msg = f"Unsupported file type: {file_extension}. Please upload .docx or .pdf files."
                logger.error(error_msg)
                errors.append(f"{os.path.basename(file_path)}: {error_msg}")
                continue  # Skip unsupported file types
            logger.debug(f"Extracting tables from document: {file_path}")
            document.tables = extract_raw_tables(document)
            documents.append(document)
        except Exception as e:
            error_msg = f"An error occurred while parsing {os.path.basename(file_path)}: {str(e)}"
            logger.exception(error_msg)
            errors.append(error_msg)
            continue  # Continue processing other files
    return (documents, errors)

def read_word_document(file_path: str) -> ParsedDocument:
    """
    Reads a Microsoft Word document and prepares it for table extraction.

    Parameters:
        file_path (str): 
            The file path to the Word document.

    Returns:
        ParsedDocument:
            A ParsedDocument object containing the content of the Word file.

    Raises:
        DocxFileError:
            If an error occurs while reading the Word document.
    """
    try:
        logger.debug(f"Reading Word document: {file_path}")
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        if file_extension == '.doc':
            logger.error("DOC files are not supported. Please convert to DOCX.")
            raise DocxFileError("DOC files are not supported. Please convert to DOCX.")
        doc = DocxDocument(file_path)
        parsed_document = ParsedDocument(file_path=file_path, content=doc)
        return parsed_document
    except Exception as e:
        logger.exception(f"Error reading Word document: {file_path}")
        raise DocxFileError(f"Error reading Word document {file_path}: {str(e)}")

def read_pdf_document(file_path: str) -> ParsedDocument:
    """
    Reads a PDF document and prepares it for table extraction.

    Parameters:
        file_path (str): 
            The file path to the PDF document.

    Returns:
        ParsedDocument:
            A ParsedDocument object containing the content of the PDF file.

    Raises:
        PDFFileError:
            If an error occurs while reading the PDF document.
    """
    try:
        logger.debug(f"Reading PDF document: {file_path}")
        pdf = pdfplumber.open(file_path)
        parsed_document = ParsedDocument(file_path=file_path, content=pdf)
        return parsed_document
    except Exception as e:
        logger.exception(f"Error reading PDF document: {file_path}")
        raise PDFFileError(f"Error reading PDF document {file_path}: {str(e)}")

def extract_raw_tables(document: ParsedDocument) -> List[Table]:
    """
    Extracts raw tables from a single document object.

    Parameters:
        document (ParsedDocument): 
            A ParsedDocument object representing the parsed document content.

    Returns:
        List[Table]:
            A list of Table objects extracted from the document.

    Raises:
        TableExtractionError:
            If an error occurs during table extraction.
    """
    tables = []
    try:
        if isinstance(document.content, DocxDocument):
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

def extract_tables_from_word(doc: DocxDocument) -> List[Table]:
    logger.debug("Extracting tables from Word document")
    tables = []
    try:
        all_tables = []
        for block in iter_block_items(doc):
            if isinstance(block, DocxTable):
                all_tables.append(block)

        for idx, word_table in enumerate(all_tables):
            logger.debug(f"Processing table {idx} in Word document")
            table_obj = process_docx_table(word_table, idx)
            tables.append(table_obj)
        return tables
    except Exception as e:
        logger.exception("Error extracting tables from Word document")
        raise TableExtractionError(f"Error extracting tables from Word document: {str(e)}")

def iter_block_items(parent):
    if isinstance(parent, DocxDocument):
        parent_elm = parent.element.body
    else:
        parent_elm = parent._element

    for child in parent_elm.iterchildren():
        if child.tag.endswith('}p'):
            yield Paragraph(child, parent)
        elif child.tag.endswith('}tbl'):
            yield DocxTable(child, parent)
        else:
            pass  # Handle other elements if necessary

def process_docx_table(word_table: docx.table.Table, position: int) -> Table:
    try:
        table_data = []
        grid, max_row, max_col = build_table_grid(word_table)
        for r in range(max_row):
            row_data = []
            for c in range(max_col):
                cell = grid[r][c]
                if cell:
                    row_data.append(cell)
                else:
                    empty_cell = Cell(content='')
                    row_data.append(empty_cell)
            table_data.append(row_data)
        table_obj = Table(data=table_data, position=position)
        return table_obj
    except Exception as e:
        logger.exception(f"Error processing table at position {position}")
        raise TableExtractionError(f"Error processing table at position {position}: {str(e)}")

def build_table_grid(word_table: DocxTable) -> Tuple[List[List[Optional[Cell]]], int, int]:
    """
    Builds a grid representing the table, correctly accounting for merged cells.

    Parameters:
        word_table (docx.table.Table): 
            The Word table object.

    Returns:
        Tuple[List[List[Optional[Cell]]], int, int]:
            - The grid as a list of lists containing Cell objects or None.
            - The maximum number of rows.
            - The maximum number of columns.
    """
    grid = {}
    max_row = 0
    max_col = 0

    for row_idx, row in enumerate(word_table.rows):
        col_idx = 0
        for cell in row.cells:
            while (row_idx, col_idx) in grid:
                col_idx += 1

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

            # Mark the grid positions occupied by this cell
            for i in range(rowspan):
                for j in range(colspan):
                    r = row_idx + i
                    c = col_idx + j
                    grid[(r, c)] = cell_obj
                    if r + 1 > max_row:
                        max_row = r + 1
                    if c + 1 > max_col:
                        max_col = c + 1
            col_idx += colspan

    # Build the grid
    grid_list = [[None for _ in range(max_col)] for _ in range(max_row)]
    for (r, c), cell_obj in grid.items():
        grid_list[r][c] = cell_obj

    return grid_list, max_row, max_col

def get_cell_span(cell: _Cell) -> Tuple[int, int]:
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
    rowspan = 1
    if v_merge:
        v_merge_val = v_merge[0].get(qn('w:val'))
        if v_merge_val == 'restart' or v_merge_val is None:
            rowspan = count_row_span(cell)
        else:
            rowspan = 0  # This cell is a continuation of a vertically merged cell
    else:
        rowspan = 1

    return rowspan, colspan

def count_row_span(cell: _Cell) -> int:
    """
    Counts how many rows a cell spans in a vertical merge.

    Parameters:
        cell (docx.table._Cell):
            The starting cell of the vertical merge.

    Returns:
        int:
            The number of rows the cell spans.
    """
    rowspan = 1
    current_tc = cell._tc
    current_row = current_tc.getparent().getparent()
    table = current_row.getparent()
    rows = list(table.iterchildren())

    current_row_idx = rows.index(current_row)
    total_rows = len(rows)

    for row_idx in range(current_row_idx + 1, total_rows):
        next_row = rows[row_idx]
        tc_list = next_row.findall('.//w:tc', cell._element.nsmap)
        for next_tc in tc_list:
            next_v_merge = next_tc.xpath("./w:tcPr/w:vMerge")
            if not next_v_merge:
                continue
            next_v_merge_val = next_v_merge[0].get(qn('w:val'))
            if next_v_merge_val == 'continue' or next_v_merge_val is None:
                rowspan += 1
                break  # Found the vertically merged cell in this row
        else:
            break  # No vertically merged cell found in this row

    return rowspan

def extract_cell_styles(cell: _Cell) -> Dict[str, Any]:
    """
    Extracts styles from a Word cell.

    Parameters:
        cell (docx.table._Cell): 
            The cell object from which to extract styles.

    Returns:
        Dict[str, Any]:
            A dictionary of styles applied to the cell.
    """
    styles = {
        'bold': False,
        'italic': False,
        'underline': False,
        'font_size': None,
        'font_name': None,
        'color': None
    }
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            if run.bold:
                styles['bold'] = True
            if run.italic:
                styles['italic'] = True
            if run.underline:
                styles['underline'] = True
            if run.font.size and (styles['font_size'] is None or run.font.size.pt > styles['font_size']):
                styles['font_size'] = run.font.size.pt
            if run.font.name and styles['font_name'] is None:
                styles['font_name'] = run.font.name
            if run.font.color and run.font.color.rgb and styles['color'] is None:
                styles['color'] = str(run.font.color.rgb)
    return styles

def extract_word_nested_tables(cell: _Cell) -> Optional[List['Table']]:
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
            grid, max_row, max_col = build_table_grid(nested_table)
            table_data = []
            for r in range(max_row):
                row_data = []
                for c in range(max_col):
                    cell_obj = grid[r][c]
                    if cell_obj:
                        row_data.append(cell_obj)
                    else:
                        empty_cell = Cell(content='')
                        row_data.append(empty_cell)
                table_data.append(row_data)
            nested_table_obj = Table(data=table_data, position=0)
            nested_tables.append(nested_table_obj)
        return nested_tables if nested_tables else None
    except Exception as e:
        logger.exception("Error extracting nested tables from cell")
        raise NestedTableParsingError(f"Error extracting nested tables: {str(e)}")

def extract_tables_from_pdf(pdf: pdfplumber.PDF) -> List[Table]:
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