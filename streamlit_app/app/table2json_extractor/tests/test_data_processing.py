# test_data_processing.py

"""
test_data_processing.py

Unit tests for the data_processing module.
"""

import os
import pytest

from ..data_processing import (
    parse_documents,
    read_word_document,
    read_pdf_document,
    extract_raw_tables,
    Document,
    Table
)
from ..exceptions import (
    UnsupportedFileTypeError,
    ParsingError,
    DocxFileError,
    PDFFileError,
    TableExtractionError
)

# Test data directory (adjust the path as needed)
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')

def test_read_word_document_success():
    """
    Test reading a valid Word document.
    """
    test_file_path = os.path.join(TEST_DATA_DIR, 'test_document.docx')
    document = read_word_document(test_file_path)
    assert isinstance(document, Document)
    assert document.file_path == test_file_path
    assert document.content is not None
    assert hasattr(document.content, 'tables')

def test_read_word_document_file_not_found():
    """
    Test reading a non-existent Word document.
    """
    with pytest.raises(FileNotFoundError):
        read_word_document('nonexistent_file.docx')

def test_read_word_document_invalid_file():
    """
    Test reading an invalid Word document.
    """
    test_file_path = os.path.join(TEST_DATA_DIR, 'invalid_document.docx')
    with pytest.raises(DocxFileError):
        read_word_document(test_file_path)

def test_read_pdf_document_success():
    """
    Test reading a valid PDF document.
    """
    test_file_path = os.path.join(TEST_DATA_DIR, 'test_document.pdf')
    document = read_pdf_document(test_file_path)
    assert isinstance(document, Document)
    assert document.file_path == test_file_path
    assert document.content is not None
    assert hasattr(document.content, 'pages')

def test_read_pdf_document_file_not_found():
    """
    Test reading a non-existent PDF document.
    """
    with pytest.raises(FileNotFoundError):
        read_pdf_document('nonexistent_file.pdf')

def test_read_pdf_document_invalid_file():
    """
    Test reading an invalid PDF document.
    """
    test_file_path = os.path.join(TEST_DATA_DIR, 'invalid_document.pdf')
    with pytest.raises(PDFFileError):
        read_pdf_document(test_file_path)

def test_parse_documents_success():
    """
    Test parsing multiple valid documents.
    """
    test_file_paths = [
        os.path.join(TEST_DATA_DIR, 'test_document.docx'),
        os.path.join(TEST_DATA_DIR, 'test_document.pdf'),
    ]
    documents = parse_documents(test_file_paths)
    assert len(documents) == 2
    for doc in documents:
        assert isinstance(doc, Document)
        assert len(doc.tables) > 0

def test_parse_documents_unsupported_file_type():
    """
    Test parsing documents with unsupported file types.
    """
    test_file_paths = [
        os.path.join(TEST_DATA_DIR, 'unsupported_file.txt'),
    ]
    with pytest.raises(UnsupportedFileTypeError):
        parse_documents(test_file_paths)

def test_extract_raw_tables_docx():
    """
    Test extracting tables from a Word document.
    """
    test_file_path = os.path.join(TEST_DATA_DIR, 'test_document.docx')
    document = read_word_document(test_file_path)
    extract_raw_tables(document)
    assert len(document.tables) > 0
    for table in document.tables:
        assert isinstance(table, Table)
        assert len(table.data) > 0

def test_extract_raw_tables_pdf():
    """
    Test extracting tables from a PDF document.
    """
    test_file_path = os.path.join(TEST_DATA_DIR, 'test_document.pdf')
    document = read_pdf_document(test_file_path)
    extract_raw_tables(document)
    assert len(document.tables) > 0
    for table in document.tables:
        assert isinstance(table, Table)
        assert len(table.data) > 0

def test_extract_raw_tables_no_tables():
    """
    Test extracting tables from a document with no tables.
    """
    test_file_path = os.path.join(TEST_DATA_DIR, 'document_no_tables.docx')
    document = read_word_document(test_file_path)
    extract_raw_tables(document)
    assert len(document.tables) == 0

def test_extract_raw_tables_error():
    """
    Test handling errors during table extraction.
    """
    # Assuming 'corrupted_document.docx' causes an error during extraction
    test_file_path = os.path.join(TEST_DATA_DIR, 'corrupted_document.docx')
    document = read_word_document(test_file_path)
    with pytest.raises(TableExtractionError):
        extract_raw_tables(document)