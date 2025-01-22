# exceptions.py

"""
exceptions.py

Module containing custom exception classes for the Table to JSON Extractor.
"""

class UnsupportedFileTypeError(Exception):
    """Raised when an unsupported file type is encountered."""
    pass

class ParsingError(Exception):
    """Raised when an error occurs during document parsing."""
    pass

class DocxFileError(Exception):
    """Raised when an error occurs while reading a Word document."""
    pass

class PDFFileError(Exception):
    """Raised when an error occurs while reading a PDF document."""
    pass

class TableExtractionError(Exception):
    """Raised when an error occurs during table extraction."""
    pass

class InvalidParameterError(Exception):
    """Raised when an invalid parameter is provided."""
    pass

class StructureInterpretationError(Exception):
    """Raised when an error occurs during structure interpretation."""
    pass

class InvalidUserInputError(Exception):
    """Raised when user inputs fail validation checks."""
    pass

class DataValidationError(Exception):
    """Raised when extracted data fails validation checks."""
    def __init__(self, message):
        super().__init__(message)

class ProcessingError(Exception):
    """Raised when an error occurs during document processing."""
    pass

class RenderingError(Exception):
    """Raised when an error occurs during data rendering."""
    pass

class NestedTableParsingError(Exception):
    """Raised when an error occurs during nested table parsing."""
    pass

class ValidationError(Exception):
    """Raised when validation of user inputs fails."""
    def __init__(self, message):
        super().__init__(message)