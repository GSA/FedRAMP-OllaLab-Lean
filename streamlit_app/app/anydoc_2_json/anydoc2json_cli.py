# anydoc2json_cli.py

import os
import sys
import argparse
import datetime
import shutil
import json
from pathlib import Path

# Import modules
from modules.param_manager import ParamManager
from modules.logger_manager import LoggerManager
from modules.doc_preprocessor import DocPreprocessor
from modules.doc_converter import DocConverter
from modules.md_parser import MdParser
from modules.table_processor import TableProcessor
from modules.markdown_preprocessor import MarkdownPreprocessor

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
            Description: Path to the target file (mandatory). This should be a DOCX, DOC, or PDF file.
        --param, -p:
            Type: str
            Description: Path to the parameter file (mandatory). This parameter file must already exist.
    """
    parser = argparse.ArgumentParser(description='AnyDoc to JSON CLI Application.')
    parser.add_argument('--target', '-t', required=True, help='Path to the target DOCX, DOC, or PDF file.')
    parser.add_argument('--param', '-p', required=True, help='Path to the parameter YAML file.')
    parser.add_argument('--output', '-o', required=False, default='app_data/anydoc_2_json/', help='Path to the folder where output folders will be stored.')
    args = parser.parse_args()
    return args

def validate_target(target_path: str) -> list:
    """
    Validates the target path, which can be a file or a directory, and collects applicable files.

    Parameters:
        target_path (str):
            The path to the target DOCX, DOC, or PDF file, or directory containing them.

    Returns:
        List[str]:
            A list of valid file paths to process.

    Raises:
        SystemExit:
            If the target path does not exist or contains no valid files.
            - If the target path does not exist.
            - If the target is a directory but contains no valid files with supported extensions.

    Upstream functions:
        - Called by main() to validate and collect target files.

    Downstream functions:
        - None

    Dependencies:
        - os.path.exists() to check if the path exists.
        - os.path.isfile() and os.path.isdir() to check the type of the path.
        - os.walk() to traverse directories.
        - os.path.splitext() to get file extensions.

    Notes:
        - Supported file extensions are '.docx', '.doc', and '.pdf'.
        - If the target is a file, it must have a supported extension.
        - If the target is a directory, all files with supported extensions within it (and subdirectories) are collected.
    """
    import os
    import sys
    if not os.path.exists(target_path):
        print(f"Error: Target path '{target_path}' does not exist.")
        sys.exit(1)
    files_to_process = []
    if os.path.isfile(target_path):
        _, file_extension = os.path.splitext(target_path)
        if file_extension.lower() in ['.docx', '.pdf', '.doc']:
            files_to_process.append(target_path)
        else:
            print(f"Error: Target file '{target_path}' must be a DOCX, DOC, or PDF file.")
            sys.exit(1)
    elif os.path.isdir(target_path):
        # List all files in the directory
        for root, dirs, files in os.walk(target_path):
            for file in files:
                _, file_extension = os.path.splitext(file)
                if file_extension.lower() in ['.docx', '.pdf', '.doc']:
                    files_to_process.append(os.path.join(root, file))
        if not files_to_process:
            print(f"Error: No DOCX, DOC, or PDF files found in directory '{target_path}'.")
            sys.exit(1)
    else:
        print(f"Error: Target path '{target_path}' is neither a file nor a directory.")
        sys.exit(1)
    return files_to_process

def validate_files(target_file_path: str, param_file_path: str):
    """
    Validates the target file and the parameter file.

    Parameters:
        target_file_path (str):
            The path to the target DOCX, DOC, or PDF file. This file must exist.
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
        print(f"Error: Target file '{target_file_path}' must be a DOCX, DOC, or PDF file.")
        sys.exit(1)

def convert_doc_to_docx(doc_file_path: str, output_folder: str) -> str:
    """
    Converts a .doc file to a .docx file using LibreOffice command-line tool.

    Parameters:
        doc_file_path (str):
            The path to the .doc file to be converted.
        output_folder (str):
            The directory where the converted .docx file will be saved.

    Returns:
        str:
            The path to the converted .docx file.

    Raises:
        Exception:
            If conversion fails due to any reason (e.g., LibreOffice not installed, conversion error).

    Upstream functions:
        - Called by main() when the target file is a .doc file.

    Downstream functions:
        - Utilizes the system's LibreOffice 'soffice' command-line tool to perform the conversion.

    Dependencies:
        - Requires LibreOffice installed on the system and accessible via the command line.

    Notes:
        - The function uses 'subprocess' module to call 'soffice' command.
        - The converted .docx file is saved in the output_folder with the same base name.
    """
    import subprocess
    try:
        if not os.path.exists(doc_file_path):
            raise FileNotFoundError(f"Input file '{doc_file_path}' not found.")

        base_name = os.path.basename(doc_file_path)
        output_path = os.path.join(output_folder, os.path.splitext(base_name)[0] + '.docx')

        command = [
            'soffice',
            '--headless',
            '--convert-to',
            'docx',
            '--outdir',
            output_folder,
            doc_file_path
        ]
        subprocess.run(command, check=True)
        if not os.path.exists(output_path):
            raise Exception(f"Conversion failed, output file '{output_path}' not found.")
        return output_path
    except Exception as e:
        raise Exception(f"Error converting '{doc_file_path}' to DOCX: {e}")

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

def perform_markdown_preprocessing(markdown_file_path: str, param_manager: ParamManager, logger_manager: LoggerManager):
    """
    Performs post-conversion preprocessing steps on the Markdown file, as specified in the parameter file.

    If the '2pass_cleanup' parameter in the parameter file is 'yes', this function will apply the same preprocessing steps
    to the converted Markdown file. The implementation differs from the pre-conversion processing because it operates on Markdown content.

    Parameters:
        markdown_file_path (str):
            The path to the Markdown (.md) file to be processed.
        param_manager (ParamManager):
            An instance of ParamManager containing processing parameters.
        logger_manager (LoggerManager):
            An instance of LoggerManager for logging events and errors.

    Returns:
        None

    Raises:
        Exception:
            If any error occurs during markdown preprocessing, it is logged and re-raised.

    Upstream functions:
        - Called by main() if the '2pass_cleanup' parameter is 'yes'.

    Downstream functions:
        - markdown_preprocessor.MarkdownPreprocessor()
        - markdown_preprocessor.MarkdownPreprocessor.process_markdown()

    Dependencies:
        - Requires the 'markdown_preprocessor' module.
        - Depends on the parameters specified in 'param_manager'.
        - The '2pass_cleanup' parameter in 'param_manager' must be 'yes' to perform markdown preprocessing.

    Notes:
        - The processed Markdown file is saved in-place, overwriting the original Markdown file.
    """
    try:
        logger = logger_manager.get_logger()
        two_pass_cleanup = param_manager.get_parameter('2pass_cleanup', 'no')
        if two_pass_cleanup.lower() != 'yes':
            logger.info("Skipping Markdown post-processing as per parameters.")
            return

        md_preprocessor = MarkdownPreprocessor(markdown_file=markdown_file_path,
                                               param_manager=param_manager,
                                               logger_manager=logger_manager)
        md_preprocessor.process_markdown()
        logger.info("Markdown post-processing completed successfully.")
    except Exception as e:
        logger_manager.log_exception(e, "Error during Markdown post-processing", markdown_file_path)
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

    This function orchestrates the entire process of converting unstructured documents
    (DOCX or PDF) into structured JSON files, following the specified steps:

    1. Parse command-line arguments.
    2. Validate provided parameters and target path.
    3. For each file in target path:
        - Initialize parameter management.
        - Create result folder in the specified output directory.
        - Initialize logging for that file.
        - Copy the target file to the result folder.
        - Convert DOC files to DOCX if necessary.
        - Perform pre-conversion processing steps as per the parameter file.
        - Convert the document to Markdown using Docling.
        - Perform post-conversion processing (2-pass cleanup) if specified.
        - Extract structured data from the Markdown file.
        - Process tables and enrich the JSON data.
        - Save the resulting JSON files to the result folder.

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
        - validate_target()
        - ParamManager()
        - LoggerManager()
        - convert_doc_to_docx()
        - perform_pre_processing()
        - convert_document()
        - perform_markdown_preprocessing()
        - extract_structured_data()
        - process_tables()

    Dependencies:
        - os, sys, argparse, datetime, shutil, json modules.
        - modules.param_manager.ParamManager
        - modules.logger_manager.LoggerManager
        - Custom functions defined in the script.
    """
    import os
    import sys
    import datetime
    import shutil

    # Parse command-line arguments
    args = parse_arguments()

    # Validate target and get list of files to process
    files_to_process = validate_target(args.target)

    # For each file in files_to_process
    for file_path in files_to_process:
        try:
            # Initialize param_manager for this file
            param_manager = ParamManager(param_file_path=args.param)

            # Get base name of the file
            base_file_name = os.path.splitext(os.path.basename(file_path))[0]
            # Create result folder in the output directory
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # include seconds for uniqueness
            result_folder_name = f"{base_file_name}_{timestamp}"
            result_folder = os.path.join(args.output, result_folder_name)
            os.makedirs(result_folder, exist_ok=True)

            # Initialize logger_manager for this file
            log_file_path = os.path.join(result_folder, 'processing.log')
            logger_manager = LoggerManager(log_file_path=log_file_path)
            logger = logger_manager.get_logger()

            # Copy target file to result folder
            target_file_extension = os.path.splitext(file_path)[1].lower()
            target_file_in_result_folder = os.path.join(result_folder, os.path.basename(file_path))
            shutil.copy(file_path, target_file_in_result_folder)
            logger.info(f"Copied target file to {target_file_in_result_folder}")

            # If the target file is a .doc file, convert it to .docx
            if target_file_extension == '.doc':
                logger.info(f"Converting '{target_file_in_result_folder}' to DOCX format.")
                input_file_path = convert_doc_to_docx(target_file_in_result_folder, result_folder)
                logger.info(f"Conversion completed. New file: '{input_file_path}'")
                # Remove the original .doc file from the result folder
                os.remove(target_file_in_result_folder)
                logger.info(f"Removed original .doc file '{target_file_in_result_folder}'")
            else:
                input_file_path = target_file_in_result_folder

            # Update 'target' parameter in param_manager
            param_manager.set_parameter('target', input_file_path)

            # Perform pre-processing
            perform_pre_processing(input_file_path=input_file_path,
                                   output_folder=result_folder,
                                   param_manager=param_manager,
                                   logger_manager=logger_manager)

            # Convert document
            markdown_file_path = convert_document(input_file_path=input_file_path,
                                                  output_folder=result_folder,
                                                  param_manager=param_manager,
                                                  logger_manager=logger_manager)

            # Perform Markdown post-processing (2-pass cleanup) if specified
            perform_markdown_preprocessing(markdown_file_path=markdown_file_path,
                                           param_manager=param_manager,
                                           logger_manager=logger_manager)

            # Base file name for output files
            base_file_name = os.path.splitext(os.path.basename(input_file_path))[0]

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

            logger.info(f"Processing completed successfully for '{file_path}'.")
            print(f"Processing completed successfully for '{file_path}'. Results are saved in {result_folder}")

        except Exception as e:
            logger_manager.log_exception(e, f"An error occurred while processing '{file_path}'.")
            print(f"An error occurred while processing '{file_path}': {e}")
            continue  # Continue with the next file

if __name__ == "__main__":
    main()