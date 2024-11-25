# Entity Bridge

Entity Bridge is a powerful tool that leverages Large Language Models (LLM) to merge multiple datasets based on Entity Names. 

## Features

- Integration with various Large Language Models (LLMs) for advanced entity matching.
- Automated matching using similarity scores.
- User confirmation for ambiguous matches.
- Streamlit UI for ease of use.
- Rich test suite for verification and validation.
- Modularized design for extensibility.

## Requirements

- Python 3.8 or later
- Libraries: Streamlit, pandas, numpy, Levenshtein, <others>

## Installation

To set up the project follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/Entity_Bridge.git
    ```
2. Navigate into the project directory:
    ```bash
    cd Entity_Bridge
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run the Streamlit app:
    ```bash
    streamlit run app/main.py
    ```

## Usage

To use Entity Bridge:
1. Navigate to the URL of the Streamlit app in a web browser.
2. Upload the datasets you wish to merge on the home page.
3. Specify how missing data should be handled and the columns to use for matching entities.
4. Adjust the similarity threshold for automated entity matching, or manually confirm ambiguous matches.
5. The enriched data will be displayed on-screen. You can also download it for further analysis.

## Project Structure

The project has the following structure:
- **streamlit_app/app/main.py**: Main entry point of the Streamlit application.
- **streamlit_app/app/pages/Entity_Bridge.py**: Streamlit page for the Entity Bridge component.
- **streamlit_app/app/entity_bridge/**: Package containing modules for the Entity Bridge functionality.

## Components

Entity Bridge comprises several modules, each responsible for a specific piece of functionality:

- **data_loader**: Module responsible for loading and preprocessing data files.
- **data_normalizer**: Module that normalizes IDs and entity names to ensure consistency.
- **duplicate_remover**: Module that identifies and removes duplicate rows from datasets.
- **entity_matcher**: Module to match entities across datasets using similarity metrics.
- **llm_integration**: Module to integrate with various LLMs for advanced entity matching.
- **ui_helper**: Module containing helper functions for building Streamlit UI components.
- **utils**: Utility module containing shared functions used across the application.

## Contribution

Contributions are welcome! Please read the contribution guidelines before starting.

## Support and Documentation

Comprehensive user and technical documentation are provided. For support, please reach us via email at support@email.com.

## License

Entity Bridge is licensed under the Apache License 2.0. See LICENSE for more details.