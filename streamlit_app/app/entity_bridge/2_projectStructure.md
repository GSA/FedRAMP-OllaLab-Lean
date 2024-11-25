# Entity Bridge - Structure

## **Folder Structure and Files**

```
streamlit_app/
├── app/
│   ├── main.py                     # Main entry point of the Streamlit application
│   ├── pages/
│   │   └── Entity_Bridge.py        # Streamlit page for the Entity Bridge component
│   ├── entity_bridge/              # Package containing modules for Entity Bridge
│   │   ├── __init__.py             # Initialization file for the entity_bridge package
│   │   ├── data_loader.py          # Module for loading and handling data files
│   │   ├── data_normalizer.py      # Module for normalizing IDs and entity names
│   │   ├── duplicate_remover.py    # Module for identifying and removing duplicate rows
│   │   ├── entity_matcher.py       # Module for matching entities across datasets
│   │   ├── ui_helper.py            # Module containing UI helper functions
│   │   ├── llm_integration.py      # Module for integrating with various LLM APIs
│   │   ├── utils.py                # Module containing utility functions
```

---

### **Brief Descriptions**

- **streamlit_app/app/main.py**: Main entry point of the Streamlit application that initializes the app and provides navigation.
  
- **streamlit_app/app/pages/Entity_Bridge.py**: Streamlit page that implements the Entity Bridge component, handling user interactions and displaying results.

- **streamlit_app/app/entity_bridge/**: Package containing all modules related to the Entity Bridge functionality.

  - **__init__.py**: Initialization file for the entity_bridge package.

  - **data_loader.py**: Module responsible for loading data files and handling missing data.

  - **data_normalizer.py**: Module that normalizes IDs and entity names to ensure consistency.

  - **duplicate_remover.py**: Module that identifies and removes duplicate rows from datasets.

  - **entity_matcher.py**: Module that matches entities across datasets using similarity metrics.

  - **ui_helper.py**: Module containing helper functions for building Streamlit UI components.

  - **llm_integration.py**: Module that integrates with various Large Language Models (LLMs) for advanced entity matching.

  - **utils.py**: Utility module containing shared functions used across the application.

---

## **Content of Each Proposed File**

Below are the contents of each file, excluding specific function or method implementation details but including detailed docstrings for classes and functions.

---

### **streamlit_app/app/main.py**

```python
"""
Main Entry Point of the Streamlit Application

This module initializes the Streamlit app and provides navigation between different pages.
"""

import streamlit as st

def main():
    """
    Main function to run the Streamlit application.
    """
    st.set_page_config(page_title="Entity Bridge", layout="wide")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Entity Bridge", "Other Page"])

    if page == "Entity Bridge":
        from pages import Entity_Bridge
        Entity_Bridge.app()
    else:
        st.write("Welcome to the Other Page.")

if __name__ == "__main__":
    main()
```

---

### **streamlit_app/app/pages/Entity_Bridge.py**

```python
"""
Entity Bridge - Streamlit Page

This module defines the Entity Bridge component page for the Streamlit application.
"""

import streamlit as st
from entity_bridge import data_loader
from entity_bridge import data_normalizer
from entity_bridge import duplicate_remover
from entity_bridge import entity_matcher
from entity_bridge import ui_helper
from entity_bridge import llm_integration

def app():
    """
    Main function to run the Entity Bridge page.

    This function sets up the UI for the Entity Bridge, handles user inputs,
    and displays the results after processing.
    """
    st.title("Entity Bridge")
    st.write("Merge multiple datasets containing entity information with overlapping entities.")

    # File upload section
    uploaded_files = ui_helper.display_file_upload()

    if uploaded_files:
        # Load and preprocess the data files
        data_frames = data_loader.load_and_preprocess_files(uploaded_files)

        # Normalize IDs and Names
        normalized_data_frames = data_normalizer.normalize_data_frames(data_frames)

        # Remove duplicate rows
        deduplicated_data_frames = duplicate_remover.remove_duplicates(normalized_data_frames)

        # Construct unique parent and child name lists
        unique_parents = entity_matcher.construct_unique_parent_list(deduplicated_data_frames)
        unique_children = entity_matcher.construct_unique_child_list(deduplicated_data_frames)

        # Enrich original data frames with unique IDs
        enriched_data_frames = entity_matcher.enrich_data_frames_with_unique_ids(
            deduplicated_data_frames, unique_parents, unique_children
        )

        # Display or allow download of the enriched data
        ui_helper.display_enriched_data(enriched_data_frames)

        # Save the resulting datasets if needed
        ui_helper.download_enriched_data(enriched_data_frames)
```

---

### **streamlit_app/app/entity_bridge/__init__.py**

```python
"""
Entity Bridge Package Initialization

This package contains modules for the Entity Bridge application,
which facilitates the merging of datasets based on entity names.
"""

# You can import commonly used functions or classes here
```

---

### **streamlit_app/app/entity_bridge/data_loader.py**

```python
"""
Data Loader Module

This module provides functions to load and handle data files, including
file I/O operations and initial preprocessing steps.
"""

import pandas as pd
import streamlit as st

def load_data(file):
    """
    Load data from an uploaded file into a pandas DataFrame.

    Args:
        file (UploadedFile): The file uploaded by the user.

    Returns:
        DataFrame: A pandas DataFrame containing the data from the file.

    Raises:
        ValueError: If the file format is unsupported or an error occurs during loading.
    """
    pass  # Implementation goes here

def handle_missing_data(df, strategy):
    """
    Handle missing data in the DataFrame based on the specified strategy.

    Args:
        df (DataFrame): The DataFrame to process.
        strategy (str): The strategy to handle missing data ('remove', 'fill', 'skip').

    Returns:
        DataFrame: The DataFrame after handling missing data.

    Raises:
        ValueError: If the strategy is unsupported.
    """
    pass  # Implementation goes here

def load_and_preprocess_files(uploaded_files):
    """
    Load and preprocess multiple uploaded files.

    Args:
        uploaded_files (list): List of files uploaded by the user.

    Returns:
        list: List of preprocessed pandas DataFrames.

    Side Effects:
        Displays options and messages in the Streamlit UI.
    """
    pass  # Implementation goes here
```

---

### **streamlit_app/app/entity_bridge/data_normalizer.py**

```python
"""
Data Normalizer Module

This module includes functions to normalize IDs and entity names to ensure
consistent formatting across datasets.
"""

import pandas as pd

def normalize_ids(df, id_columns, name_columns):
    """
    Normalize IDs in the DataFrame, generating new IDs if they are missing.

    Args:
        df (DataFrame): The DataFrame to process.
        id_columns (list): List of ID column names to normalize.
        name_columns (list): List of name column names related to the IDs.

    Returns:
        DataFrame: The DataFrame with normalized IDs.
    """
    pass  # Implementation goes here

def normalize_entity_names(df, name_columns, custom_stopwords=None):
    """
    Normalize entity names in the DataFrame by applying various text preprocessing steps.

    Args:
        df (DataFrame): The DataFrame to process.
        name_columns (list): List of name column names to normalize.
        custom_stopwords (list, optional): List of custom stopwords to remove from names.

    Returns:
        DataFrame: The DataFrame with normalized names.
    """
    pass  # Implementation goes here

def normalize_data_frames(data_frames):
    """
    Apply normalization to a list of DataFrames.

    Args:
        data_frames (list): List of DataFrames to normalize.

    Returns:
        list: List of normalized DataFrames.
    """
    pass  # Implementation goes here
```

---

### **streamlit_app/app/entity_bridge/duplicate_remover.py**

```python
"""
Duplicate Remover Module

This module provides functions to identify and remove duplicate rows from DataFrames.
"""

import pandas as pd

def identify_duplicates(df, subset_columns):
    """
    Identify duplicate rows in the DataFrame based on subset columns.

    Args:
        df (DataFrame): The DataFrame to check for duplicates.
        subset_columns (list): List of column names to consider when identifying duplicates.

    Returns:
        DataFrame: A DataFrame containing only duplicate rows.
    """
    pass  # Implementation goes here

def remove_duplicates(df, subset_columns):
    """
    Remove duplicate rows from the DataFrame based on subset columns.

    Args:
        df (DataFrame): The DataFrame to process.
        subset_columns (list): List of column names to consider when removing duplicates.

    Returns:
        DataFrame: The DataFrame after removing duplicates.
    """
    pass  # Implementation goes here

def remove_duplicates_from_data_frames(data_frames):
    """
    Remove duplicates from a list of DataFrames.

    Args:
        data_frames (list): List of DataFrames to process.

    Returns:
        list: List of DataFrames with duplicates removed.
    """
    pass  # Implementation goes here
```

---

### **streamlit_app/app/entity_bridge/entity_matcher.py**

```python
"""
Entity Matcher Module

This module provides functions to match entities across datasets using
similarity metrics and user input for ambiguous cases.
"""

import pandas as pd

def compute_similarity_scores(df_list, column_name):
    """
    Compute similarity scores between entities across multiple DataFrames.

    Args:
        df_list (list): List of DataFrames to compare.
        column_name (str): The name of the column containing the entities.

    Returns:
        DataFrame: A DataFrame containing pairs of entities and their similarity scores.
    """
    pass  # Implementation goes here

def automated_entity_matching(similarity_df, threshold):
    """
    Automatically match entities based on a similarity threshold.

    Args:
        similarity_df (DataFrame): DataFrame containing similarity scores.
        threshold (float): Similarity threshold for automatic matching.

    Returns:
        DataFrame: DataFrame containing matched entities.
    """
    pass  # Implementation goes here

def user_confirm_ambiguous_matches(ambiguous_matches):
    """
    Present ambiguous matches to the user for confirmation.

    Args:
        ambiguous_matches (DataFrame): DataFrame containing ambiguous entity matches.

    Returns:
        DataFrame: DataFrame with user-confirmed matches.
    """
    pass  # Implementation goes here

def construct_unique_parent_list(data_frames):
    """
    Construct a unique parent entity list from the data frames.

    Args:
        data_frames (list): List of DataFrames containing parent entities.

    Returns:
        DataFrame: DataFrame containing unique parent entities with unique identifiers.
    """
    pass  # Implementation goes here

def construct_unique_child_list(data_frames):
    """
    Construct a unique child entity list from the data frames.

    Args:
        data_frames (list): List of DataFrames containing child entities.

    Returns:
        DataFrame: DataFrame containing unique child entities with unique identifiers.
    """
    pass  # Implementation goes here

def enrich_data_frames_with_unique_ids(data_frames, unique_parents, unique_children):
    """
    Enrich the original data frames with unique parent and child IDs.

    Args:
        data_frames (list): List of original DataFrames to enrich.
        unique_parents (DataFrame): DataFrame containing unique parent entities.
        unique_children (DataFrame): DataFrame containing unique child entities.

    Returns:
        list: List of enriched DataFrames.
    """
    pass  # Implementation goes here
```

---

### **streamlit_app/app/entity_bridge/ui_helper.py**

```python
"""
UI Helper Module

This module contains helper functions to build and manage the Streamlit UI components.
"""

import streamlit as st

def display_file_upload():
    """
    Display file upload widgets and return the uploaded files.

    Returns:
        list: List of UploadedFile objects.

    Side Effects:
        Renders file upload widgets in the Streamlit UI.
    """
    uploaded_files = st.file_uploader("Upload one or more data files", type=['csv', 'tsv', 'xlsx'], accept_multiple_files=True)
    return uploaded_files

def display_missing_data_options():
    """
    Display options for handling missing data and return the user's choice.

    Returns:
        str: The selected strategy for handling missing data ('remove', 'fill', 'skip').

    Side Effects:
        Renders radio buttons in the Streamlit UI.
    """
    options = ['Remove rows with missing values', 'Fill missing values with defaults', 'Skip processing fields with excessive missing data']
    choice = st.radio("Select how to handle missing data:", options)
    strategy_mapping = {
        'Remove rows with missing values': 'remove',
        'Fill missing values with defaults': 'fill',
        'Skip processing fields with excessive missing data': 'skip'
    }
    return strategy_mapping.get(choice, 'remove')

def display_enriched_data(enriched_data_frames):
    """
    Display the enriched data frames in the Streamlit UI.

    Args:
        enriched_data_frames (list): List of enriched DataFrames to display.

    Side Effects:
        Renders data frames and relevant information in the Streamlit UI.
    """
    pass  # Implementation goes here

def download_enriched_data(enriched_data_frames):
    """
    Provide options to download the enriched data frames.

    Args:
        enriched_data_frames (list): List of enriched DataFrames to download.

    Side Effects:
        Adds download buttons to the Streamlit UI.
    """
    pass  # Implementation goes here

def display_similarity_threshold_setting(default_threshold=0.9):
    """
    Display a slider to adjust the similarity threshold.

    Args:
        default_threshold (float): Default value for the similarity threshold.

    Returns:
        float: The user-selected similarity threshold.

    Side Effects:
        Renders a slider in the Streamlit UI.
    """
    threshold = st.slider("Set similarity threshold for matching:", min_value=0.0, max_value=1.0, value=default_threshold, step=0.01)
    return threshold
```

---

### **streamlit_app/app/entity_bridge/llm_integration.py**

```python
"""
LLM Integration Module

This module provides functions to integrate with various Large Language Models (LLMs)
such as OpenAI, Ollama, Anthropic, Google Vertex AI, and AWS Bedrock.
"""

def setup_llm_client(provider, **credentials):
    """
    Set up the LLM client based on the selected provider and credentials.

    Args:
        provider (str): The name of the LLM provider ('ollama', 'openai', 'anthropic', 'vertexai', 'bedrock').
        **credentials: Keyword arguments containing necessary credentials.

    Returns:
        object: An instance of the LLM client.

    Raises:
        ValueError: If the provider is unsupported or credentials are missing.
    """
    pass  # Implementation goes here

def generate_entity_mappings_with_llm(prompt, client, model_name):
    """
    Generate entity mappings using the provided LLM client.

    Args:
        prompt (str): The prompt to send to the LLM.
        client (object): The LLM client instance.
        model_name (str): The name of the LLM model to use.

    Returns:
        dict: A dictionary containing the entity mappings generated by the LLM.

    Raises:
        Exception: If the LLM generation fails.
    """
    pass  # Implementation goes here

def integrate_llm_in_entity_matching(similarity_df, client, model_name):
    """
    Use LLM to enhance entity matching, especially for ambiguous cases.

    Args:
        similarity_df (DataFrame): DataFrame containing entities and similarity scores.
        client (object): The LLM client instance.
        model_name (str): The LLM model to use.

    Returns:
        DataFrame: An updated DataFrame with improved entity matching.

    Side Effects:
        May involve additional API calls to the LLM provider.
    """
    pass  # Implementation goes here
```

---

### **streamlit_app/app/entity_bridge/utils.py**

```python
"""
Utilities Module

This module contains utility functions used throughout the Entity Bridge application.
"""

import uuid
import re
from difflib import SequenceMatcher

def generate_unique_identifier():
    """
    Generate a unique identifier string.

    Returns:
        str: A unique identifier generated using UUID4.
    """
    return str(uuid.uuid4())

def calculate_similarity(s1, s2):
    """
    Calculate the similarity between two strings using sequence matching.

    Args:
        s1 (str): The first string.
        s2 (str): The second string.

    Returns:
        float: The similarity score between 0.0 and 1.0.
    """
    return SequenceMatcher(None, s1, s2).ratio()

def normalize_text(text, custom_stopwords=None):
    """
    Normalize text by uppercase conversion, punctuation removal, and stopwords removal.

    Args:
        text (str): The text to normalize.
        custom_stopwords (list, optional): List of custom stopwords to remove.

    Returns:
        str: The normalized text.
    """
    pass  # Implementation goes here

def log_normalization_actions(actions_log, action_description):
    """
    Record a normalization action to the actions log.

    Args:
        actions_log (list): List maintaining logs of normalization actions.
        action_description (str): Description of the normalization action performed.

    Side Effects:
        Updates the actions_log list.
    """
    actions_log.append(action_description)
```

---

## **Notes**

- **LLM Integration Details**: The `llm_integration.py` module is designed to support multiple LLM providers. The `setup_llm_client` function handles the instantiation of clients for different providers based on provided credentials. This approach ensures that support for providers like OpenAI, Ollama, Anthropic, Google Vertex AI, and AWS Bedrock is modular and maintainable.

- **Error Handling and Logging**: Throughout the modules, appropriate error handling should be implemented. For example, when loading files or making API calls, exceptions should be caught and informative messages displayed to the user. Logging should be implemented to keep track of actions and facilitate debugging.

- **Modularity and Extensibility**: The code structure is modular, allowing for easy extension. For example, new normalization rules or matching algorithms can be added without significant changes to the existing codebase.

- **User Interface Considerations**: The `ui_helper.py` module abstracts UI components, making it easier to manage and update the UI elements separately from the business logic.

- **Data Security and Privacy**: Since user data and credentials are involved, ensure that sensitive information is handled securely. Avoid logging sensitive data and consider implementing secure methods for credential storage and usage.

- **Comments and Documentation**: All modules and functions include detailed docstrings, following best practices for documentation, which aids in maintenance and collaborative development.
