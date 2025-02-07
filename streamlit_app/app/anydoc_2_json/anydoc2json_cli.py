import os
import sys
import argparse
from pathlib import Path
import datetime
import shutil
import json

# Import modules
from anydoc_2_json.modules.param_manager import ParamManager
from anydoc_2_json.modules.logger_manager import LoggerManager
from anydoc_2_json.modules.doc_preprocessor import DocPreprocessor
from anydoc_2_json.modules.doc_converter import DocConverter
from anydoc_2_json.modules.md_parser import MdParser
from anydoc_2_json.modules.table_processor import TableProcessor

def parse_arguments():
    """
    Parses command-line arguments for the AnyDoc to JSON CLI application.

    Parameters:
        None

    Returns:
        argparse.Namespace:
            A namespace containing the parsed command-line arguments.

    Raises:
        None

    Upstream functions:
        - Called by the main() function.

    Downstream functions:
        - Uses argparse.ArgumentParser() to parse command-line arguments.

    Dependencies:
        - argparse module.

    Command-line Arguments:
        --target, -t:
            Type: str
            Description: Path to the target file (mandatory). This should be a DOCX or PDF file.
        --param, -p:
            Type: str
            Description: Path to the parameter file (mandatory). This parameter file must already exist.
    """
    parser = argparse.ArgumentParser(description='AnyDoc to JSON CLI Application.')
    parser.add_argument('--target', '-t', required=True, help='Path to the target DOCX or PDF file.')
    parser.add_argument('--param', '-p', required=True, help='Path to the parameter YAML file.')
    args = parser.parse_args()
    return args

def validate_files(target_file_path: str, param_file_path: str):
    """
    Validates the target file and the parameter file.

    Parameters:
        target_file_path (str):
            The path to the target DOCX or PDF file. This file must exist and have a .docx or .pdf extension.
        param_file_path (str):
            The path to the parameter YAML file. This file must exist.

    Returns:
        None

    Raises:
        SystemExit:
            If the target file or the parameter file does not exist or is not valid.

    Upstream functions:
        - Called by main() to validate input files.

    Downstream functions:
        - None

    Dependencies:
        - os.path.exists() to check if files exist.
        - os.path.splitext() to get file extensions.
    """
    if not os.path.exists(target_file_path):
        print(f"Error: Target file '{target_file_path}' does not exist.")
        sys.exit(1)
    if not os.path.exists(param_file_path):
        print(f"Error: Parameter file '{param_file_path}' does not exist.")
        sys.exit(1)
    _, file_extension = os.path.splitext(target_file_path)
    if file_extension.lower() not in ['.docx', '.pdf', '.doc']:
        print(f"Error: Target file '{target_file_path}' must be a DOCX or PDF file.")
        sys.exit(1)

def perform_pre_processing(input_file_path: str, output_folder: str, param_manager: ParamManager, logger_manager: LoggerManager):
    """
    Performs pre-conversion processing steps on the input document, as specified in the parameter file.

    Parameters:
        input_file_path (str):
            The path to the input DOCX or PDF file to be processed.
        output_folder (str):
            The directory where the processed document will be saved.
        param_manager (ParamManager):
            An instance of ParamManager containing processing parameters.
        logger_manager (LoggerManager):
            An instance of LoggerManager for logging events and errors.

    Returns:
        None

    Raises:
        Exception:
            If any error occurs during pre-processing, it is logged and re-raised.

    Upstream functions:
        - Called by main() to perform pre-conversion processing steps.

    Downstream functions:
        - doc_preprocessor.DocPreprocessor()
        - doc_preprocessor.DocPreprocessor.process_document()

    Dependencies:
        - Requires the 'doc_preprocessor' module.
        - Depends on the parameters specified in 'param_manager'.

    Notes:
        - The processed file is saved to the 'output_folder' with the same name as the input file.
    """
    try:
        doc_preprocessor = DocPreprocessor(input_file=input_file_path,
                                           output_folder=output_folder,
                                           param_manager=param_manager,
                                           logger_manager=logger_manager)
        doc_preprocessor.process_document()
        logger = logger_manager.get_logger()
        logger.info("Pre-processing completed successfully.")
    except Exception as e:
        logger_manager.log_exception(e, "Error during pre-processing", input_file_path)
        raise e

def convert_document(input_file_path: str, output_folder: str, param_manager: ParamManager, logger_manager: LoggerManager):
    """
    Converts the input document to Markdown using Docling and handles heading adjustments.

    Parameters:
        input_file_path (str):
            The path to the input DOCX or PDF file (after pre-processing).
        output_folder (str):
            The directory where the converted Markdown file will be saved.
        param_manager (ParamManager):
            An instance of ParamManager containing processing parameters.
        logger_manager (LoggerManager):
            An instance of LoggerManager for logging events and errors.

    Returns:
        str:
            The path to the converted Markdown file.

    Raises:
        Exception:
            If any error occurs during document conversion, it is logged and re-raised.

    Upstream functions:
        - Called by main() to convert the document to Markdown.

    Downstream functions:
        - doc_converter.DocConverter()
        - doc_converter.DocConverter.convert_document()

    Dependencies:
        - Requires the 'doc_converter' module.

    Notes:
        - The converted Markdown file is saved to the 'output_folder' with the same base name as the input file.
    """
    try:
        logger = logger_manager.get_logger()
        # Set document_title
        file_name_without_extension = os.path.splitext(os.path.basename(input_file_path))[0]
        param_manager.set_parameter('document_title', file_name_without_extension)

        doc_converter = DocConverter(logger_manager=logger_manager, param_manager=param_manager)
        markdown_file_path = doc_converter.convert_document(input_file=input_file_path,
                                                            output_folder=output_folder)
        logger.info(f"Document converted to Markdown: {markdown_file_path}")
        return markdown_file_path
    except Exception as e:
        logger_manager.log_exception(e, "Error during document conversion", input_file_path)
        raise e

def extract_structured_data(markdown_file_path: str, output_folder: str, logger_manager: LoggerManager, base_file_name: str):
    """
    Extracts structured data from the Markdown file using MdParser and saves the raw JSON data.

    Parameters:
        markdown_file_path (str):
            The path to the Markdown (.md) file to be parsed.
        output_folder (str):
            The directory where the raw JSON data will be saved.
        logger_manager (LoggerManager):
            An instance of LoggerManager for logging events and errors.
        base_file_name (str):
            The base file name to use for saving the raw JSON data.

    Returns:
        dict:
            The JSON data parsed from the Markdown file.

    Raises:
        Exception:
            If any error occurs during structured data extraction, it is logged and re-raised.

    Upstream functions:
        - Called by main() to extract structured data from Markdown.

    Downstream functions:
        - md_parser.MdParser()
        - md_parser.MdParser.parse_markdown()
        - Saves the raw JSON data to a file.

    Dependencies:
        - Requires the 'md_parser' module.
        - Uses 'json' module to save the JSON data.

    Notes:
        - The raw JSON data is saved to the 'output_folder' with '_raw.json' suffix.
    """
    try:
        logger = logger_manager.get_logger()
        md_parser = MdParser(md_file_path=markdown_file_path,
                             output_folder=output_folder,
                             logger=logger_manager)
        json_data = md_parser.parse_markdown()
        # Save raw JSON data
        json_output_file = os.path.join(output_folder, f"{base_file_name}_raw.json")
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        logger.info(f"Raw JSON data saved to '{json_output_file}'")
        return json_data
    except Exception as e:
        logger_manager.log_exception(e, "Error during structured data extraction", markdown_file_path)
        raise e

def process_tables(json_data: dict, output_folder: str, logger_manager: LoggerManager, base_file_name: str):
    """
    Processes tables in the JSON data, enriches them, and saves the enriched JSON data.

    Parameters:
        json_data (dict):
            The JSON data obtained from parsing the Markdown file.
        output_folder (str):
            The directory where the enriched JSON data will be saved.
        logger_manager (LoggerManager):
            An instance of LoggerManager for logging events and errors.
        base_file_name (str):
            The base file name to use for saving the enriched JSON data.

    Returns:
        None

    Raises:
        Exception:
            If any error occurs during table processing, it is logged and re-raised.

    Upstream functions:
        - Called by main() to process tables in the JSON data.

    Downstream functions:
        - table_processor.TableProcessor()
        - table_processor.TableProcessor.process_tables()
        - table_processor.TableProcessor.save_updated_json()

    Dependencies:
        - Requires the 'table_processor' module.

    Notes:
        - The enriched JSON data is saved to the 'output_folder' with '_enriched.json' suffix.
    """
    try:
        logger = logger_manager.get_logger()
        table_processor = TableProcessor(json_data=json_data,
                                         output_folder=output_folder,
                                         logger=logger_manager)
        table_processor.process_tables()
        # Save enriched JSON data
        table_processor.save_updated_json(base_file_name)
        logger.info(f"Enriched JSON data saved.")
    except Exception as e:
        logger_manager.log_exception(e, "Error during table processing")
        raise e

def main():
    """
    Main function for the AnyDoc to JSON CLI application.

    This function orchestrates the entire process of converting an unstructured document
    (DOCX or PDF) into a structured JSON file, following the specified steps:

    1. Parse command-line arguments.
    2. Validate provided parameters and files.
    3. Initialize logging and parameter management.
    4. Create result folder and copy the target file.
    5. Perform pre-conversion processing steps as per the parameter file.
    6. Convert the document to Markdown using Docling.
    7. Extract structured data from the Markdown file.
    8. Process tables and enrich the JSON data.
    9. Save the resulting JSON files to the result folder.

    Parameters:
        None

    Returns:
        None

    Raises:
        SystemExit:
            If any critical error occurs during execution, the program exits with a non-zero status.

    Upstream functions:
        - Entry point of the CLI application.

    Downstream functions:
        - parse_arguments()
        - validate_files()
        - perform_pre_processing()
        - convert_document()
        - extract_structured_data()
        - process_tables()

    Dependencies:
        - Requires the modules:
            - os
            - sys
            - argparse
            - datetime
            - pathlib.Path
            - shutil
            - json
            - AnyDoc to JSON modules:
                - param_manager
                - logger_manager
                - doc_preprocessor
                - doc_converter
                - md_parser
                - table_processor
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Validate files
    validate_files(args.target, args.param)

    # Initialize param_manager
    param_manager = ParamManager(param_file_path=args.param)

    # Initialize logger_manager with log file in result folder
    # Create result folder
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H")  # only use the hour
    target_file_name = os.path.splitext(os.path.basename(args.target))[0]
    result_folder_name = f"{target_file_name}_{timestamp}"
    result_folder = os.path.join('app_data', 'anydoc_2_json', result_folder_name)
    os.makedirs(result_folder, exist_ok=True)

    # Initialize logger_manager
    log_file_path = os.path.join(result_folder, 'processing.log')
    logger_manager = LoggerManager(log_file_path=log_file_path)
    logger = logger_manager.get_logger()

    try:
        # Copy target file to result folder
        target_file_in_result_folder = os.path.join(result_folder, os.path.basename(args.target))
        shutil.copy(args.target, target_file_in_result_folder)
        logger.info(f"Copied target file to {target_file_in_result_folder}")

        # Update 'target' parameter in param_manager
        param_manager.set_parameter('target', target_file_in_result_folder)

        # Perform pre-processing
        perform_pre_processing(input_file_path=target_file_in_result_folder,
                               output_folder=result_folder,
                               param_manager=param_manager,
                               logger_manager=logger_manager)

        # Convert document
        markdown_file_path = convert_document(input_file_path=target_file_in_result_folder,
                                              output_folder=result_folder,
                                              param_manager=param_manager,
                                              logger_manager=logger_manager)

        # Base file name
        base_file_name = os.path.splitext(os.path.basename(target_file_in_result_folder))[0]

        # Extract structured data
        json_data = extract_structured_data(markdown_file_path=markdown_file_path,
                                            output_folder=result_folder,
                                            logger_manager=logger_manager,
                                            base_file_name=base_file_name)

        # Process tables
        process_tables(json_data=json_data,
                       output_folder=result_folder,
                       logger_manager=logger_manager,
                       base_file_name=base_file_name)

        logger.info("Processing completed successfully.")
        print("Processing completed successfully.")
        print(f"Results are saved in {result_folder}")

    except Exception as e:
        logger_manager.log_exception(e, "An error occurred during processing.")
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()