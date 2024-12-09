# Schema Extractor - Dev Strategy

To ensure efficient development and seamless integration of components in Schema Extractor application, it's important to follow a strategy that respects the dependencies among the project files. Below is a proposed development approach that outlines the order in which to develop the modules, based on their interdependencies:

---

### **1. Foundational Modules**

These modules have minimal or no dependencies and will be used by multiple other modules. Developing them first provides a strong base for the rest of the application.

#### **a. `utils.py`**

- **Purpose**: Provides utility functions (e.g., normalization of column names, sensitive data detection).
- **Dependencies**: None.
- **Action**: 
  - **Develop `utils.py` first** to establish the utility functions needed across the application.
  - **Include utility functions** identified in our solution, such as `normalize_column_names`, `detect_sensitive_data`, and `remove_stopwords`.

#### **b. `logger.py`**

- **Purpose**: Handles logging and auditing of user actions and system processes.
- **Dependencies**: None.
- **Action**: 
  - **Set up `logger.py`** early to enable consistent logging throughout the application.
  - **Define the logging configuration** and create utility functions like `setup_logger` and `log_action`.

---

### **2. Data Loading Module**

#### **`file_loader.py`**

- **Purpose**: Handles file uploads and detects file types.
- **Dependencies**:
  - Depends on `utils.py` for any utility functions.
  - Uses `logger.py` for logging actions.
- **Action**:
  - **Implement `file_loader.py`** to handle file uploads.
  - **Develop functions** `load_files`, `detect_file_type`, and `detect_file_types`.
  - **Ensure it integrates** with the Streamlit file uploader component.

---

### **3. Data Sanitization Module**

#### **`sanitizer.py`**

- **Purpose**: Sanitizes the content of the loaded files.
- **Dependencies**:
  - Requires data loaded by `file_loader.py`.
  - Uses `utils.py` for operations like removing stopwords.
  - Uses `logger.py` for logging actions.
- **Action**:
  - **Develop `sanitizer.py`** to clean and preprocess data.
  - **Implement functions** like `sanitize_data`, `backup_data`, and `detect_and_handle_malformed_data`.
  - **Address security concerns** by implementing data validation and harmful content detection.

---

### **4. Exploratory Data Analysis Module**

#### **`eda.py`**

- **Purpose**: Performs automated Exploratory Data Analysis on sanitized data.
- **Dependencies**:
  - Requires sanitized data from `sanitizer.py`.
  - Uses `utils.py` and `logger.py`.
- **Action**:
  - **Implement `eda.py`** to generate insights from data.
  - **Use libraries** (e.g., Pandas Profiling, Ydata Profiling) to automate EDA.
  - **Develop functions** like `perform_eda` and `generate_eda_report`.

---

### **5. Schema Extraction Module**

#### **`schema_extraction.py`**

- **Purpose**: Automatically extracts data schemas from sanitized data.
- **Dependencies**:
  - Uses outputs from `sanitizer.py` and `eda.py`.
  - Uses `utils.py` and `logger.py`.
- **Action**:
  - **Develop `schema_extraction.py`** to extract schemas.
  - **Implement functions** like `extract_schema`, `extract_json_schema`, and `extract_tabular_schema`.
  - **Integrate tools** like `genson` for JSON, `xmllint` for XML.

---

### **6. Schema Validation Module**

#### **`schema_validator.py`**

- **Purpose**: Validates data against extracted schemas.
- **Dependencies**:
  - Requires data and schemas from `sanitizer.py` and `schema_extraction.py`.
  - Uses `utils.py` and `logger.py`.
- **Action**:
  - **Implement `schema_validator.py`**.
  - **Develop functions** like `validate_schema` and `validate_data_against_schema`.
  - **Use validation tools** such as `jsonschema` for JSON data.

---

### **7. UI Components Module**

#### **`ui_components.py`**

- **Purpose**: Provides reusable UI components for the Streamlit app.
- **Dependencies**:
  - Uses Streamlit.
  - May use `utils.py` and `logger.py`.
- **Action**:
  - **Develop `ui_components.py`** to create UI elements.
  - **Implement functions** like `file_uploader`, `display_eda`, `display_schema`, and `progress_indicator`.
  - **This module can be developed in parallel** with modules that need UI components.

---

### **8. Schema Builder Module**

#### **`schema_builder.py`**

- **Purpose**: Allows users to interactively build or modify the data schema.
- **Dependencies**:
  - Depends on schemas from `schema_extraction.py`.
  - Uses `ui_components.py` for UI elements.
  - Uses `utils.py` and `logger.py`.
- **Action**:
  - **Implement `schema_builder.py`** to provide an interactive schema design interface.
  - **Develop functions** like `build_schema`, `add_field_to_schema`, and `remove_field_from_schema`.
  - **Ensure seamless integration** with the existing schemas and user inputs.

---

### **9. Main Application Page**

#### **`app/pages/Schema_Extractor.py`**

- **Purpose**: Streamlit page that orchestrates the application workflow.
- **Dependencies**:
  - Integrates all previously developed modules.
  - Uses `ui_components.py` for the UI.
  - Uses `logger.py` for logging user actions.
- **Action**:
  - **Develop `Schema_Extractor.py`** to tie everything together.
  - **Implement the `app()` function** that manages the application's flow.
  - **Handle user interactions** and display results to the user.

---

### **10. Entry Point Script**

#### **`app/main.py`**

- **Purpose**: The main entry point of the Streamlit application.
- **Dependencies**:
  - Must integrate `Schema_Extractor.py` and other application pages.
- **Action**:
  - **Update `main.py`** to include navigation to the Schema Extractor page.
  - **Ensure overall application structure** supports the new module.

---

### **11. Testing Modules**

#### **Tests in `app/schema_extractor/tests/`**

- **Purpose**: Contains unit tests for each module.
- **Dependencies**:
  - Each test module depends on its corresponding module.
- **Action**:
  - **Develop tests alongside each module** to ensure correctness.
  - **Implement test cases** for functions in `file_loader.py`, `sanitizer.py`, `eda.py`, etc.
  - **Use a testing framework** such as `unittest` or `pytest`.

---

### **12. Refinement and Integration**

- **Action**:
  - **Integrate all modules** and perform end-to-end testing.
  - **Refine interfaces** between modules for consistency.
  - **Address any bugs or issues** discovered during integration.

---

### **13. Performance Optimization**

- **Purpose**: Ensure the application performs well with large datasets.
- **Dependencies**: Optimizations may affect multiple modules.
- **Action**:
  - **Profile the application** to identify bottlenecks.
  - **Implement optimizations** such as data chunking and asynchronous processing.
  - **Adjust resource limits** and provide user feedback for large files.

---

### **14. Security and Compliance**

- **Purpose**: Address security concerns related to file handling and data processing.
- **Dependencies**: Applies to modules like `file_loader.py` and `sanitizer.py`.
- **Action**:
  - **Implement security checks** in file handling modules.
  - **Ensure data encryption** and compliance with regulations.
  - **Review code** for vulnerabilities and implement sandboxing if necessary.

---

### **15. Documentation and User Guidance**

- **Purpose**: Provide guidance for users and developers.
- **Dependencies**: Documentation refers to all modules.
- **Action**:
  - **Write comprehensive documentation** including user manuals and API references.
  - **Include docstrings** in all modules and functions.
  - **Develop help sections** and tooltips within the application.

---

### **16. Deployment and Maintenance**

- **Action**:
  - **Prepare the application for deployment** by handling dependencies and environments.
  - **Set up continuous integration and deployment (CI/CD)** pipelines.
  - **Plan for maintenance** and future feature additions.

---

**Additional Considerations:**

- **Parallel Development**: Some modules can be developed concurrently by different team members, especially those that don't directly depend on each other (e.g., `schema_builder.py` and `eda.py` after shared dependencies are satisfied).

- **Iterative Development**: Adopt an iterative approach, revisiting and refining modules as new insights are gained and as integration proceeds.

- **Continuous Testing**: Continuously run tests to catch issues early. Incorporate automated testing into the development workflow.

- **User Feedback**: Once a working version is available, gather user feedback to improve usability and functionality.

- **Version Control**: Use a version control system like Git to manage changes and collaborate effectively.

**Summary:**

By following this strategy, We ensure that each module is developed when its dependencies are available, reducing errors and rework. Starting with foundational utilities and progressing through the data processing pipeline aligns development with the flow of data, making it logical and manageable. Testing and documentation are integral parts of the process, enhancing code quality and maintainability. This structured approach lays a solid foundation for a robust, efficient, and user-friendly application.