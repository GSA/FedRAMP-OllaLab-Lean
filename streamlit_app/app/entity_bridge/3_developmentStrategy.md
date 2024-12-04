## **Development Strategy**

This initial development strategy does not reflect minor updates made after 12/03/2024

### **1. Set Up the Project Structure**

- **Initialize the Project Directory**:
  - Create the directory structure as outlined in your proposed files.
  - Ensure that you have a virtual environment set up to manage dependencies.

- **Version Control**:
  - Initialize Git in your project directory.
  - Create a `.gitignore` file to exclude unnecessary files (e.g., virtual environment folders, `.DS_Store`, etc.).

- **Install Required Packages**:
  - Install essential packages such as `streamlit`, `pandas`, `numpy`, etc.
  - Record all dependencies in a `requirements.txt` file for reproducibility.

```bash
pip install streamlit pandas numpy
pip freeze > requirements.txt
```

---

### **2. Develop Core Utility Functions**

#### **File: `utils.py`**

#### **Purpose**
Provides foundational functions used throughout the application.

#### **Functions to Implement**

1. **`generate_unique_identifier()`**
   - **Purpose**: Generates a unique identifier using the UUID4 standard.
   - **Usage**: Useful for creating unique IDs for entities when they are missing or need to be standardized across datasets.

2. **`calculate_similarity(s1, s2)`**
   - **Purpose**: Calculates the similarity score between two strings using sequence matching algorithms.
   - **Usage**: Helps in determining how closely two entity names match, aiding in the merging process.

3. **`normalize_text(text, custom_stopwords=None)`**
   - **Purpose**: Normalizes text by converting it to uppercase, removing punctuation, and eliminating stopwords.
   - **Usage**: Ensures consistency in entity names across different datasets by standardizing their format.

4. **`log_normalization_actions(actions_log, action_description)`**
   - **Purpose**: Logs actions performed during the normalization process.
   - **Usage**: Maintains a record of all normalization steps for transparency and debugging purposes.

---

### **3. Implement Data Loading and Handling**

#### **File: `data_loader.py`**
#### **Purpose**
Handles file uploads and initial data processing.
#### **Functions to Implement**

1. **`load_data(file)`**

    **Purpose**: This function handles the loading of data from an uploaded file into a pandas DataFrame.

    **File Format Support**: Supports CSV, TSV, and Excel files (`.csv`, `.tsv`, `.xls`, `.xlsx`).

    **Error Handling**: Raises a `ValueError` if the file format is unsupported or if an error occurs during loading.

    **Usage**: Used within the application to read user-uploaded files for further processing.

2. **`handle_missing_data(df, strategy, default_value=None, missing_threshold=0.5)`**

    **Purpose**: This function processes missing data in the DataFrame based on the user's selected strategy.

    **Strategies**:
      - `'remove'`: Removes rows with any missing values.
      - `'fill'`: Fills missing values with a user-specified default value.
      - `'skip'`: Removes columns where the percentage of missing data exceeds a user-defined threshold.
    **Parameters**:
      - `default_value`: Used when the strategy is `'fill'`.
      - `missing_threshold`: Used when the strategy is `'skip'`.

3. **`select_fields(df, file_name, idx)`**

    **Purpose**: This function allows the user to select the necessary fields from the DataFrame for processing.

    **Mandatory Fields**:
      - **Parent ID Field**: Must be selected and cannot be the same as the Parent Name Field.
      - **Parent Name Field**: Must be selected.
    **Optional Fields**:
      - **Child ID Field**: Can be selected or left as `None`.
      - **Child Name Field**: Can be selected or left as `None`.
    **Validation**: Ensures that the Parent ID and Parent Name Fields are not the same.

4. **`load_and_preprocess_files(uploaded_files)`**

    **Purpose**: This function orchestrates the loading and preprocessing of multiple uploaded files.

    **Process Flow**:
      1. **Load Data**: Calls `load_data` for each file.
      2. **Handle Missing Data**: Invokes `handle_missing_data` based on user selection.
      3. **Select Fields**: Uses `select_fields` to determine which columns to process.
      4. **Collect Results**: Stores the processed DataFrames and selected fields in a list.
    **Side Effects**: Interacts with the Streamlit UI to present options and display messages.
---

### **4. Build Data Normalization Module**

#### **File: `data_normalizer.py`**

#### **Purpose**: Normalizes IDs and entity names to ensure consistency.

#### **Functions to Implement**:
1. **`normalize_ids(df, selected_fields)`**

    **Purpose**: This function ensures that every entity has a unique identifier:

    **Parent IDs**:
      - If the `parent_id` field is present and contains missing values, it fills them using forward fill (`ffill`) method.
      - If the `parent_id` field is not provided, it generates unique IDs using the `Parent Name` and updates the `selected_fields` accordingly.

    **Child IDs**:
      - If the `child_name` field is present:
        - If the `child_id` field exists and has missing values, it fills them with forward fill.
        - If the `child_id` field is not provided, it generates unique IDs based on `Child Name` and updates the `selected_fields`.

    **Logging**:
      - All actions taken are logged using the `log_normalization_actions` function and displayed to the user.

2. **`normalize_entity_names(df, selected_fields, custom_stopwords=None)`**

    **Purpose**: This function normalizes entity names:

    - Creates a copy of the original entity name columns, appending `_original` to the column name.
    - Applies text normalization to `Parent Name` and `Child Name` columns using the `normalize_text` function, which involves:
        - Converting text to uppercase.
        - Removing punctuation.
        - Removing stopwords (with the option to include `custom_stopwords`).

    **Logging**:
    - Logs the actions taken and displays them to the user.

3. **`normalize_data_frames(data_frames, custom_stopwords=None)`**

    **Purpose**: This function iterates over each DataFrame and applies the normalization processes:

    - Calls `normalize_ids` and `normalize_entity_names` for each DataFrame.
    - Collects the normalized DataFrames along with updated `selected_fields`.

---

### **5. Create Duplicate Remover Module**

#### **File: `duplicate_remover.py`**

#### **Purpose**: Identifies and removes duplicate rows based on normalized data.

#### **Functions to Implement**:
1. **`identify_duplicates(df, selected_fields)`**

    **Purpose**: This function identifies duplicate rows within a DataFrame based on a combination of normalized fields.

    **Process**:
    - Prepares a list of columns to consider based on provided `selected_fields`.
    - Uses pandas' `duplicated` method to find duplicates across the specified subset of columns.
    - Logs and displays the number of duplicate rows found using Streamlit.

    **Parameters**:
    - `df`: The DataFrame to check for duplicates.
    - `selected_fields`: A dictionary containing field names to use for duplication checks.

    **Returns**:
    - A DataFrame containing the duplicate rows.

2. **`remove_duplicates(df, selected_fields)`**

    **Purpose**:This function removes duplicate rows from a DataFrame based on the specified normalized fields.

    **Process**:
    - Identifies duplicates using the same method as `identify_duplicates`.
    - Removes duplicates using pandas' `drop_duplicates` method, keeping the first occurrence.
    - Logs the number of duplicates removed and displays the information using Streamlit.

    **Parameters**:
    - `df`: The DataFrame from which to remove duplicates.
    - `selected_fields`: A dictionary containing field names to use for duplication checks.

    **Returns**:
    - The DataFrame after duplicates have been removed.

3. **`remove_duplicates_from_data_frames(data_frames)`**

    **Purpose**:This function applies the duplicate removal process to a list of DataFrames.

    **Process**:
    - Iterates over each DataFrame and its corresponding `selected_fields`.
    - Calls `identify_duplicates` and `remove_duplicates` for each DataFrame.
    - Collects the deduplicated DataFrames and returns them.

    **Parameters**:
    - `data_frames`: A list of tuples, each containing a DataFrame and its `selected_fields`.

    **Returns**:
    - A list of deduplicated DataFrames with their associated `selected_fields`.

---

### **6. Develop Entity Matching Logic**

#### **File: `entity_matcher.py`**

#### **Purpose**
Matches entities across datasets using similarity metrics.

#### **Functions to Implement**:

1. **`compute_similarity_scores(df_list, column_name)`**
    **Purpose**: Computes similarity scores between all pairs of entities across multiple DataFrames based on the specified column (either 'parent_name' or 'child_name').

    **Parameters**:
    - `df_list`: List of tuples `(DataFrame, selected_fields)` to extract entities from.
    - `column_name`: The key in `selected_fields` specifying which column to use ('parent_name' or 'child_name').

    **Returns**: A DataFrame containing entity pairs and their similarity scores.

    **Implementation Details**:
    - Collects all unique entities from the DataFrames.
    - Uses `calculate_similarity` from `utils.py` to compute similarity between entity pairs.
    - Displays progress using Streamlit's `progress` bar.

2. **`automated_entity_matching(similarity_df, threshold)`**

    **Purpose**: Automatically groups entities into clusters if their similarity score exceeds the given threshold.

    **Parameters**:
    - `similarity_df`: DataFrame containing pairs of entities and their similarity scores.
    - `threshold`: Similarity score threshold for considering entities as the same.

    **Returns**: A dictionary mapping each entity to a group identifier.

    **Implementation Details**:
    - Sorts the similarity DataFrame in descending order of similarity scores.
    - Iterates over sorted pairs and groups entities using union-find logic.
    - Entities below the threshold are not grouped together.

3. **`user_confirm_ambiguous_matches(ambiguous_matches)`**

    **Purpose**: Presents ambiguous entity matches (those not automatically matched due to low similarity scores) to the user for manual confirmation.

    **Parameters**:
    - `ambiguous_matches`: DataFrame containing ambiguous entity pairs and their similarity scores.

    **Returns**: A dictionary of user-confirmed entity groupings.

    **Implementation Details**:
    - Uses Streamlit to display entities to the user and collect their input.
    - Assigns the same or different group IDs based on user input.

4. **`construct_unique_entity_list(data_frames, entity_type='parent')`**

    **Purpose**: Builds a DataFrame of unique entities (either parents or children) from the data frames, assigning a unique identifier to each.

    **Parameters**:
    - `data_frames`: List of tuples `(DataFrame, selected_fields)`.
    - `entity_type`: 'parent' or 'child' indicating which entity type to process.

    **Returns**: A DataFrame containing unique entities and their assigned unique IDs.

    **Implementation Details**:
    - Extracts all unique entity names.
    - Generates unique IDs using `generate_unique_identifier` from `utils.py`.

5. **`enrich_data_frames_with_unique_ids(data_frames, unique_entities_df, entity_type='parent')`**

    **Purpose**: Adds the unique entity IDs to the original DataFrames by merging on the entity names.

    **Parameters**:
    - `data_frames`: List of tuples `(DataFrame, selected_fields)`.
    - `unique_entities_df`: DataFrame containing unique entities and unique IDs.
    - `entity_type`: 'parent' or 'child' indicating which entity type to process.

    **Returns**: List of enriched DataFrames.

    **Implementation Details**:
    - Merges each DataFrame with the unique entities DataFrame on the relevant entity name.
    - Drops redundant columns after the merge to clean up the DataFrame.

6. **`construct_unique_parent_list(data_frames)`**

    **Purpose**: Specifically constructs the unique parent entities list by utilizing the functions above.

    **Parameters**:
    - `data_frames`: List of tuples `(DataFrame, selected_fields)`.

    **Returns**: DataFrame containing unique parent entities and their unique IDs.

    **Implementation Details**:
    - Calls `compute_similarity_scores` and `automated_entity_matching` for parent entities.
    - Allows the user to set the similarity threshold via a Streamlit slider.
    - Constructs the unique parents DataFrame based on the grouping.

7. **`construct_unique_child_list(data_frames)`**

    **Purpose**: Specifically constructs the unique child entities list, if child names are provided.

    **Parameters**:
    - `data_frames`: List of tuples `(DataFrame, selected_fields)`.

    **Returns**: DataFrame containing unique child entities and their unique IDs.

    **Implementation Details**:
    - Similar to `construct_unique_parent_list`, but for child entities.
    - Checks if child names are provided in any of the datasets before proceeding.

8. **`enrich_data_frames_with_unique_ids(data_frames, unique_parents_df, unique_children_df)`**

    **Purpose**: Enriches the original data frames with both unique parent and child IDs.

    **Parameters**:
    - `data_frames`: List of tuples `(DataFrame, selected_fields)`.
    - `unique_parents_df`: DataFrame containing unique parent entities.
    - `unique_children_df`: DataFrame containing unique child entities.

    **Returns**: List of enriched DataFrames.
---

### **7. Incorporate LLM Integration**

#### **File: `llm_integration.py`**

#### **Purpose**: Enhances entity matching using LLMs for ambiguous cases.
#### **Functions to Implement**:
1. **`setup_llm_client(provider: str, **credentials)`**

    **Purpose**: Sets up the client for the specified LLM provider using the provided credentials.
    
    **Supported Providers**:
    - **OpenAI**: Requires the `openai` library and an API key.
    - **Anthropic**: Requires the `anthropic` library and an API key.
    - **Google Vertex AI**: Requires the `google-cloud-aiplatform` library. Authentication is handled via environment variables or service accounts.
    - **AWS Bedrock**: Requires the `boto3` library. Authentication is handled via AWS credentials.
    - **Ollama**: Assumes a custom client (placeholder implementation provided). Requires a base URL.

    **Error Handling**:
    - Checks if the necessary libraries are installed.
    - Validates the presence of required credentials.
    - Raises `ImportError` or `ValueError` as appropriate.

2. **`generate_entity_mappings_with_llm(prompt: str, client: Any, provider: str, model_name: str)`**

    **Purpose**: Sends a prompt to the LLM and parses the response to obtain entity mappings.
    
    **Implementation Details**:
    - For each provider, uses the appropriate method to generate a response from the LLM.
    - Parses the LLM output using the `parse_llm_output` function.
    - Supports specific parameters like `max_tokens`, `temperature`, etc.

    **Error Handling**:
    - Catches exceptions during the LLM call.
    - Logs errors and re-raises exceptions with informative messages.

3. **`integrate_llm_in_entity_matching(similarity_df, client, provider: str, model_name: str)`**

    **Purpose**: Enhances entity matching by using the LLM to resolve ambiguous cases.

    **Implementation Details**:
    - Filters ambiguous cases based on similarity scores.
    - Iterates over these cases and uses the LLM to determine if entities match.
    - Updates the `similarity_df` DataFrame with LLM results.

    **Side Effects**:
    - Displays progress and messages in the Streamlit UI.

4. **`parse_llm_output(output_text: str)`**

    **Purpose**: Parses the raw text output from the LLM into a structured dictionary.

    **Implementation Details**:
    - Attempts to parse the output as JSON.
    - If JSON parsing fails, uses simple text parsing to extract decisions.

---

### **8. Develop UI Components**

#### **File: `ui_helper.py`**

#### **Purpose**: Manages Streamlit UI components for user interaction.
#### **Functions to Implement**:
1. **`display_file_upload()`**

    **Purpose**: This function renders the file upload widget in the Streamlit UI, allowing users to upload multiple files for processing.

    **Implementation Details**:
    - Uses `st.file_uploader` with `accept_multiple_files=True`.
    - Filters file types to CSV, TSV, and Excel formats.
    - Displays a warning if no files are uploaded.

    **Side Effects**: Displays the file upload area and warning messages in the UI.

2. **`display_missing_data_options(idx, file_name)`**

    **Purpose**: Presents options to the user for handling missing data in a specific file.

    **Implementation Details**:
    - Uses `st.selectbox` to offer strategies: 'remove', 'fill', 'skip'.
    - Depending on the chosen strategy, additional inputs are displayed:
        - For 'fill': Prompts for a default value.
        - For 'skip': Displays a slider to select a missing data threshold.
    - Unique keys are used for Streamlit widgets to maintain state.

    **Side Effects**: Renders select boxes, text inputs, and sliders in the UI.

3. **`display_enriched_data(enriched_data_frames)`**

    **Purpose**: Displays a preview of the enriched data frames after processing.

    **Implementation Details**:
    - Iterates over each DataFrame and displays the first 20 rows using `st.dataframe`.

    **Side Effects**: Renders dataframes in the UI for user inspection.

4. **`download_enriched_data(enriched_data_frames)`**

    **Purpose**: Provides the functionality for users to download the enriched data frames in their preferred format.

    **Implementation Details**:
    - For each DataFrame, offers a select box to choose between 'CSV' and 'Excel'.
    - Uses `st.download_button` to allow users to download the data.
    **Handling File Formats**:
    - **CSV**: Converts the DataFrame to CSV format and encodes it.
    **Excel**: Writes the DataFrame to an Excel buffer and reads the data for download.

5. **`display_similarity_threshold_setting(entity_type='parent', default_threshold=0.9)`**

    **Purpose**: Allows users to adjust the similarity threshold for entity matching.

    **Implementation Details**:
    - Uses `st.slider` to present a range from 0.0 to 1.0.
    - The `entity_type` parameter customizes the label for 'parent' or 'child' entities.

    **Returns**: The user-selected similarity threshold value.

6. **`display_confirmation_dialog(message, key)`**

    **Purpose**: Displays a simple confirmation dialog with 'Yes' and 'No' options.

    **Implementation Details**:
    - Uses `st.radio` to present options.
    - The `key` parameter ensures widget states are maintained correctly.

    **Returns**: A boolean value indicating the user's choice.

7. **`display_field_selection(df, file_name, idx)`**

    **Purpose**: Enables users to select the appropriate fields (columns) from the DataFrame that correspond to required data elements.

    **Implementation Details**:
    - Uses `st.selectbox` to list available columns for selection.
    - Validates that the 'Parent ID' and 'Parent Name' fields are not the same.
    - Allows 'Child ID' and 'Child Name' to be optional.

    **Error Handling**:
    - If 'Parent ID' and 'Parent Name' are the same, an error is displayed using `st.error`, and `st.stop()` halts execution.

8. **`display_progress(message, progress_value)`**

    **Purpose**: Provides feedback to the user on the progress of long-running tasks.

    **Implementation Details**:
    - Displays a message using `st.write`.
    - Updates a progress bar using `st.progress` with the provided progress value.
---

### **9. Integrate Data Modules with the UI**

#### **File: `entity_bridge.py`**

#### **Purpose**: Serves as the main entry point, integrating backend modules with UI.
#### **Steps**:

- **Set Up Streamlit App Structure**:
  - Import necessary modules.
  - Create a function `main()` that orchestrates the flow.

- **Implement Data Loading Workflow**:
  - Use UI components to get user input.
  - Call `data_loader.load_and_preprocess_files(uploaded_files)`.

- **Test End-to-End Flow**:
  - Run the app and ensure data is loaded and displayed.

---

### **10. Add Error Handling and Logging**

- **Implement Error Handling**:
  - Use try-except blocks where necessary.
  - Provide meaningful error messages to the user using `st.error()`.

- **Implement Logging**:
  - Use Python’s `logging` module to record events.
  - Configure logging levels for development and production.

---

### **11. Perform Testing**

- **Unit Tests**:
  - Write tests for utility functions and modules.
  - Use frameworks like `unittest` or `pytest`.

- **Integration Tests**:
  - Test the entire workflow with different datasets.
  - Ensure that the application behaves as expected under various conditions.

---

### **12. Improve User Interface and Experience**

#### **Enhancements**:

- **Progress Indicators**:
  - Use `st.progress()` to show processing status during long operations.

- **User Feedback**:
  - Add `st.success()`, `st.warning()`, and `st.info()` messages where appropriate.

- **Help and Guidance**:
  - Include tooltips and explanations using `st.tooltip()` or help arguments.

- **Reset Options**:
  - Implement a reset button to clear the session state.

---

### **13. Documentation and Support**

- **Code Documentation**:
  - Ensure all modules and functions have comprehensive docstrings.

- **User Guide**:
  - Create a `README.md` with instructions on how to use the application.

- **Technical Documentation**:
  - Document the architecture and design decisions.

---

### **14. Deployment**

- **Prepare for Deployment**:
  - Ensure all dependencies are listed in `requirements.txt`.
  - Remove any hard-coded paths or debug code.

- **Deploy the Application**:
  - Consider using Streamlit Sharing, Heroku, or AWS for deployment.
  - Securely manage secrets and API keys.

---

### **15. Extensibility and Future Enhancements**

- **Add Support for More LLMs**:
  - Extend `llm_integration.py` to include other providers.

- **Optimize Performance**:
  - For large datasets, consider optimizing similarity calculations.

- **UI Improvements**:
  - Implement advanced features like undo actions or state management.

---

## **Suggested Order of File Development**

1. **`utils.py`**: Provides foundational functions needed elsewhere.

2. **`data_loader.py`**: Enables data to be loaded and is essential for testing subsequent modules.

3. **`data_normalizer.py`**: Depends on data from `data_loader.py` and utilities from `utils.py`.

4. **`duplicate_remover.py`**: Requires normalized data to function correctly.

5. **`ui_helper.py`**: Early development allows you to test the UI and get immediate feedback.

6. **`main.py` and `Entity_Bridge.py`**: Integrate the above modules to form the core application.

7. **`entity_matcher.py`**: Introduces core functionality after data can be loaded, normalized, and displayed.

8. **`llm_integration.py`**: Optional for initial versions but adds significant value when implemented.

9. **Testing and Documentation**: Should be done continuously but formalized once the core functionality is in place.

---

By following this structured approach, you develop the application incrementally, ensuring that each component works correctly before moving on to the next. This reduces complexity and helps in isolating and fixing issues early in the development process.

Remember to frequently run your application and test it with different datasets to ensure robustness and reliability.