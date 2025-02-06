# app/anydoc_2_json/modules/data_enricher.py

import os
import argparse
import json
import traceback

from .logger_manager import LoggerManager
from .param_manager import ParamManager
from .md_parser import MdParser
from .table_processor import TableProcessor

def parse_arguments():
    """
    Parses command-line arguments for the data_enricher script.

    Parameters:
        None

    Returns:
        argparse.Namespace:
            A namespace containing the parsed command-line arguments with attributes:
                - md_file (str): The path to the input Markdown (.md) file.
                - output_folder (str): The path to the output folder. If not provided, uses current directory.
                - log_file (str): The path to the log file. If not provided, uses default 'data_enricher.log'.

    Raises:
        None

    Dependencies:
        - argparse module

    Upstream functions:
        - Called by main()

    Downstream functions:
        - Uses argparse.ArgumentParser()

    """
    parser = argparse.ArgumentParser(description='Data Enricher Script for AnyDoc to JSON conversion.')
    parser.add_argument('--md_file', '-m', required=True, help='Path to the input Markdown (.md) file.')
    parser.add_argument('--output_folder', '-o', required=False, default='.', help='Path to the output folder.')
    parser.add_argument('--log_file', '-l', required=False, default='data_enricher.log', help='Path to the log file.')
    args = parser.parse_args()
    return args

def initialize_logger(log_file_path):
    """
    Initializes the LoggerManager instance for logging.

    Parameters:
        log_file_path (str):
            The path to the log file where logs will be saved.

    Returns:
        LoggerManager:
            An instance of LoggerManager configured with the given log file path.

    Raises:
        Exception:
            If an error occurs during logger initialization.

    Dependencies:
        - LoggerManager class

    Upstream functions:
        - Called by main()

    Downstream functions:
        - LoggerManager.__init__()

    """
    try:
        logger_manager = LoggerManager(log_file_path=log_file_path)
        return logger_manager
    except Exception as e:
        print(f"Failed to initialize logger: {e}")
        raise

def main():
    """
    Main function for the data_enricher script.

    The function orchestrates the process of parsing a Markdown file into JSON,
    processing tables within the JSON data, enriching the JSON data, and saving
    the enriched JSON data to a file.

    Parameters:
        None

    Returns:
        None

    Raises:
        None

    Dependencies:
        - os module
        - logger_manager module
        - md_parser module
        - table_processor module

    Upstream functions:
        - Executed when the script is run directly.

    Downstream functions:
        - parse_arguments()
        - initialize_logger()
        - MdParser()
        - MdParser.parse_markdown()
        - TableProcessor()
        - TableProcessor.process_tables()
        - TableProcessor.save_updated_json()

    """
    args = parse_arguments()
    logger_manager = initialize_logger(args.log_file)
    logger = logger_manager.get_logger()

    try:
        # Paths
        md_file_path = args.md_file
        output_folder = args.output_folder

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Initialize MdParser
        md_parser = MdParser(md_file_path=md_file_path, output_folder=output_folder, logger=logger_manager)
        json_data = md_parser.parse_markdown()

        # Save the initial JSON data (raw)
        base_file_name = os.path.splitext(os.path.basename(md_file_path))[0]
        json_output_file = os.path.join(output_folder, f"{base_file_name}_raw.json")
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        logger.info(f"Raw JSON data saved to '{json_output_file}'")

        # Initialize TableProcessor
        table_processor = TableProcessor(json_data=json_data, output_folder=output_folder, logger=logger_manager)
        table_processor.process_tables()
        # Save the enriched JSON data
        table_processor.save_updated_json(base_file_name)

    except Exception as e:
        logger_manager.log_exception(e, context_message="An error occurred during data enrichment.")
        print(f"An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()