# FedRAMP OllaLab - Table to Json Extractor
## Problem Statement
Organizations frequently rely on tabular data embedded within unstructured data files such as Microsoft Word and PDF documents for decision-making, reporting, and compliance. However, the process of manually extracting this data is often time-consuming, error-prone, and inefficient. Existing solutions may lack scalability, compatibility with various file formats, or the ability to handle complex table structures. This creates a bottleneck in workflows where rapid access to accurate, structured data is critical.

To improve efficiency and accuracy in workflows reliant on tabular data, we aim to develop an automated solution that extracts tables from Microsoft Word and PDF documents, outputs them in structured JSON format, and integrates seamlessly with existing systems. By addressing challenges like table complexity, format variability, and data integrity, this solution will enhance data accessibility, streamline decision-making, and support compliance efforts in dynamic organizational environments.

## Requirements
### **1. System Architecture and Design**
- **Modular Architecture**: The system must be designed using a modular architecture to facilitate the addition of new modules and features without impacting existing functionality.
- **Microservices Approach**: Implement a microservices architecture where each module (PEM, PAM, DEM) operates as an independent service with well-defined APIs.
- **Scalable Infrastructure**: Design the system to scale horizontally and vertically to handle increasing workloads and data volumes.
- **Separation of Concerns**: Ensure clear separation between data processing, business logic, and presentation layers to enhance maintainability.
- **Loose Coupling**: Use asynchronous communication and message queues to decouple system components, enhancing resilience and scalability.
- **Event-Driven Design**: Adopt an event-driven architecture to support real-time processing and responsiveness.

### **2. Accessibility and Interfaces**
- **Web Interface**: All modules must be accessible through an intuitive and user-friendly web interface that supports all major browsers and devices.
- **Command Line Interface**: All functionalities can be executed in the command line interface.

### **3. Data Processing and Management**
- **Data Parsing**: Reliably parse and ingest any amount of text-based data, including MS Word files, PDFs, and web content, using both automatic and user-guided mechanisms.
- **Structured Data Extraction**: Accurately extract structured data (e.g., data tables, JSON) from unstructured sources.

### **4. User Interaction and Experience**
- **Intuitive UI/UX**: Provide an intuitive user interface that simplifies complex tasks, reduces the learning curve, and enhances productivity.
- **Documentation and Help**: Offer comprehensive documentation, tutorials, and tooltips within the user interface.

### **5. Logging, Monitoring, and Alerting**
- **Comprehensive Logging**: Implement detailed logging for all system components, capturing system events, errors, and user activities.
- **Alerting Mechanisms**: Set up automated alerts for critical events, failures, and security incidents.

### **6. Development and Deployment Practices**
- **Continuous Integration/Continuous Deployment (CI/CD)**: Implement CI/CD pipelines for automated testing, building, and deployment of code changes.
- **Automated Testing**: Include unit tests, integration tests, and end-to-end tests to ensure system reliability and prevent regressions.
- **Containerization**: Use container technologies (e.g., Docker) to package applications for consistent deployment across environments.
- **Infrastructure as Code (IaC)**: Manage infrastructure configurations using IaC tools (e.g., Terraform, Ansible) for reproducibility and scalability.
- **Version Control**: Use a robust version control system (e.g., Git) for all code, configurations, and scripts.

### **7. Maintainability and Support**
- **Code Quality Standards**: Adhere to coding standards and best practices to enhance readability and maintainability.
- **Documentation**: Produce extensive documentation for system architecture, APIs, modules, and operational procedures.
- **Automated Maintenance Tasks**: Schedule and automate routine maintenance tasks like database indexing, log rotation, and system updates.
- **Support Infrastructure**: Set up support channels (e.g., ticketing systems, knowledge bases) to assist users and administrators.

### **8. Usability and Accessibility**
- **User-Centered Design**: Employ user research and feedback to design interfaces that meet user needs and preferences.
- **Accessibility Compliance**: Ensure the system complies with accessibility standards (e.g., WCAG 2.1) to support users with disabilities.
- **Responsive Design**: Design the web interface to be responsive across different devices and screen sizes.
- **Internationalization (i18n)**: Support multiple languages and regional settings to accommodate a global user base.

### **9. Data Quality and Validation**
- **Data Validation**: Implement validation rules to ensure data integrity and correctness at all stages of processing.
- **Error Correction**: Provide mechanisms to detect and correct errors or inconsistencies in data.
- **Quality Metrics**: Monitor and report on data quality metrics, such as completeness, accuracy, and consistency.

# Input Description
## Required Inputs
### Source Documents
- **MS Word Files**: The `.doc` or `.docx` files containing the tables you wish to extract.
- **PDF Files**: The `.pdf` files that include the tables to be processed.
### User Guidance and Specifications
The user will need to specify the following guidance and specifications.
#### **1. Extraction Parameters**
Extraction parameters are settings and guidelines that dictate how the data extraction process should be conducted. They can include instructions on aspects such as formatting, data types, and other characteristics that need attention during extraction. Key categories of extraction parameters can include:
- **Column Headers**: Specify if the first row or a designated row of the table should be treated as headers to identify data categories.
- **Data Types**: Define expected data types (e.g., string, integer, date) for each column to enforce validation during extraction.
- **Formatting Rules**: Include rules for recognizing and preserving formatting, such as boldface or italicized text, which can indicate significance or categorization in the data.
- **Data Length Constraints**: Set limits on the character length for certain fields to manage how data is treated (e.g., ensuring no overly long entries are captured).
- **Cell Merging and Nesting Handling**: Instruction on how to handle merged cells (where a single cell spans multiple columns or rows) and nested tables (tables within tables) is vital. For example, specifying how to represent merged cells in JSON format or whether nested tables should be flattened or retained.
- **Omission Rules**: Parameters to specify conditions under which certain rows or columns may be excluded from extraction (e.g., skipping empty rows or columns).
- **Data Formatting**: Indications on how to format the extracted data for output (e.g., date formats, numerical formats).
- **Error Handling Instructions**: Guidelines for how the system should behave when it encounters unexpected data formats or extraction errors, such as what fallback mechanisms to engage or how to log such occurrences.

#### **2. Table Selection**
Table selection allows users to specify which tables to extract from a document, particularly important when multiple tables are present or when only certain data is relevant. Consider the following aspects of table selection:
- **Table Indexing**: Users can refer to tables by their index (e.g., Table 1, Table 2) based on their order in the document. This requires a preview functionality so users can see a summary or a thumbnail of the tables available for extraction.
- **Selective Extraction by Criteria**: Users may define specific criteria for the tables they need. This could include:
  - **Keyword Matching**: Use keywords or phrases that must appear in the table content or header for it to be selected for extraction. For example, selecting only tables that have the word "Summary" in the header.
  - **Row or Column Criteria**: Users can specify conditions based on the data within rows or columns. For instance, extract only tables with a specified number of rows or where a particular column contains values above a certain threshold.
- **Structured Preview**: Incorporate a structured preview feature where users can visualize the tables extracted temporarily without fully committing to the extraction. This functionality allows users to confirm selections before proceeding to structured extraction.
- **Multiple Table Selection**: Provide the ability for users to select multiple tables simultaneously by checking boxes or using a multi-select dropdown list, enhancing the efficiency of the extraction process.
- **Saved Queries/Profiles**: Allow users to save predefined extraction profiles based on their often-used parameters, including selection criteria, formatting expectations, and data handling rules. This feature supports repeatability for users who extract similar data frequently.
- **Regular Expression Matching**: Use regular expressions to identify tables or specific data patterns across the document, facilitating more complex and flexible selection rules.

#### **3. Structure Interpretation**
Effective structure interpretation is crucial for accurately extracting and representing complex tables from files like Microsoft Word and PDF documents. Complex tables often include features such as merged cells, nested tables, irregular structures, and hierarchical data. Properly interpreting these structures ensures that the extracted data maintains its intended meaning and usability. User will need to clarify the guidelines and strategies for interpreting various complex table structures during the extraction process:
- **1. Handling Merged Cells**
  - **a. Identification of Merged Cells:**
    - **Detection:** Utilize the document's underlying markup (e.g., XML in Word documents) or layout analysis in PDFs to identify cells that span multiple rows or columns.
    - **Attributes:** Extract attributes such as `rowspan` and `colspan` that indicate the extent of the merge.
  - **b. Data Placement Strategy:**
    - **Single Representation:** Decide whether to represent merged cells in the JSON output as a single key-value pair or distribute the data across the affected cells.
    - **Placeholder Cells:** For JSON and Markdown representations, insert `null` or empty placeholders in the positions occupied by the merged cells to maintain the table's structural integrity.
  - **c. Maintaining Data Integrity:**
    - **Consolidation:** Consolidate data from merged cells to avoid duplication and ensure that the information is represented accurately.
    - **Contextual Information:** Include metadata indicating the original merged structure to preserve context, which can be useful for downstream processing or display.
  - **d. Markdown Representation:**
    - **Row and Column Spanning:** Since Markdown has limited support for spanning, consider alternative representations:
    - **Nested Tables:** Embed smaller tables within a single cell to represent complex spanning.
    - **Visual Indicators:** Use annotations or comments to indicate merged areas, though this may require custom rendering solutions.
- **2. Managing Nested Tables**
  - **a. Detection of Nested Structures:**
    - **Parsing Hierarchy:** Analyze the document's structure to detect when a table exists within a cell of another table.
    - **Depth Tracking:** Maintain a hierarchy level to understand the nesting depth, which aids in proper JSON structuring.
  - **b. Recursive Extraction:**
    - **Modular Approach:** Implement recursive logic to extract nested tables as separate JSON objects or arrays within the parent table's structure.
    - **Referencing Parent Context:** Ensure that nested tables maintain a reference to their parent table to preserve relational context.
  - **c. JSON Representation:**
    - **Embedded Objects:** Represent nested tables as nested JSON objects or arrays within the relevant cell of the parent table.
    ```json
    {
        "table": [
        {
            "column1": "Data",
            "column2": {
            "nestedTable": [
                {
                "nestedColumn1": "Nested Data 1",
                "nestedColumn2": "Nested Data 2"
                }
            ]
            }
        }
        ]
    }
    ```
  - **d. Markdown Representation:**
    - **Inline Tables:** Embed Markdown tables within a cell using code blocks or indentation.
    - Example:
        ```
        | Column 1     | Column 2                  |
        |--------------|---------------------------|
        | Data         | 
        |              | Nested Table:
        |              | 
        |              | | Nested Column 1 | Nested Column 2 |
        |              | |-----------------|-----------------|
        |              | | Nested Data 1   | Nested Data 2   |
        ```
  - **e. Rendering Considerations:**
    - **Custom Extensions:** Since standard Markdown may not support complex nesting elegantly, consider using or developing Markdown extensions that can handle nested tables more gracefully.
- **3. Managing Irregular Table Structures**
  - **a. Detection of Irregularities:**
    - **Structural Analysis:** Identify inconsistencies such as varying numbers of columns across rows, non-uniform cell sizes, or unconventional layouts.
    - **Error Handling:** Implement robust error detection to handle unexpected structures without causing extraction failures.
  - **b. Standardization:**
    - **Normalization:** Transform irregular tables into a normalized form with consistent row and column counts, possibly by inserting empty cells where data is missing.
    - **Alignment Correction:** Adjust misaligned data to fit into the appropriate rows and columns based on contextual clues or defined rules.
  - **c. JSON Representation:**
    - **Flexible JSON Schemas:** Design JSON schemas that can accommodate variability, such as using arrays of objects with optional fields.
    ```json
    {
        "table": [
        {
            "column1": "Data",
            "column2": "Data"
        },
        {
            "column1": "Data",
            // column2 is missing
        }
        ]
    }
    ```
  - **d. Markdown Representation:**
    - **Consistent Column Counts:** Ensure all rows have the same number of columns by inserting placeholders where necessary.
    - Example:
        ```
        | Column 1 | Column 2 |
        |----------|----------|
        | Data     | Data     |
        | Data     |          |
        ```
  - **e. Documentation of Irregularities:**
    - **Metadata Inclusion:** Include metadata in the JSON output that captures information about any irregularities, aiding in transparency and further processing.
    ```json
    {
        "table": [
        {
            "column1": "Data",
            "column2": "Data"
        }
        ],
        "metadata": {
        "irregularRows": 1,
        "notes": "Row 2 is missing data in column 2."
        }
    }
    ```
- **4. Representing Hierarchical Data in Markdown**
  - **a. Hierarchical Structures:**
    - **Multi-Level Data:** Tables may contain hierarchical relationships, such as parent-child data or grouped categories.
  - **b. Markdown Techniques:**
    - **Indented Lists:** Use indented lists within table cells to represent hierarchical relationships.
    - Example:
        ```
        | Category      | Details                |
        |---------------|------------------------|
        | Electronics   | - Phones               |
        |               |   - Smartphones        |
        |               |   - Feature Phones     |
        |               | - Computers            |
        | Furniture     | - Chairs               |
        |               | - Tables               |
        ```
    - **Bullet Points:** Incorporate bullet points or numbering within cells to indicate levels of hierarchy.
    - Example:
        ```
        | Department | Teams                           |
        |------------|---------------------------------|
        | Sales      | 1. Domestic Sales               |
        |            | 2. International Sales          |
        | HR         | 1. Recruitment                   |
        |            | 2. Employee Relations           |
        ```
  - **c. Nested Tables for Complex Hierarchies:**
    - **Sub-Tables:** Embed smaller tables within a cell to represent deeper hierarchical levels.
    - Example:
        ```
        | Project       | Milestones                   |
        |---------------|------------------------------|
        | Project Alpha | | Phase | Tasks            |
        |               | |-------|-------------------|
        |               | | Start | Initial Setup     |
        |               | | Mid   | Development        |
        |               | | End   | Deployment         |
        ```
  - **d. Leveraging Markdown Extensions:**
    - **Enhanced Syntax:** Use Markdown extensions or flavors (e.g., GitHub Flavored Markdown) that support more advanced table features to better represent hierarchical data.
    - **Custom Rendering Tools:** Develop or utilize rendering tools that can interpret and display hierarchical Markdown tables more effectively.
  - **e. JSON Representation for Hierarchical Data:**
    - **Nested JSON Objects:** Represent hierarchical relationships using nested JSON structures, which can then be transformed into hierarchical Markdown as needed.
    ```json
    {
        "table": [
        {
            "Category": "Electronics",
            "Details": {
            "Phones": ["Smartphones", "Feature Phones"],
            "Computers": []
            }
        },
        {
            "Category": "Furniture",
            "Details": {
            "Chairs": [],
            "Tables": []
            }
        }
        ]
    }
    ```
  - **f. Ensuring Readability and Accessibility:**
    - **Clarity:** Maintain clarity in hierarchical representations to ensure that the Markdown remains readable and accessible.
    - **Consistent Formatting:** Apply consistent formatting rules across all hierarchical elements to enhance user comprehension.
- **5. General Best Practices for Structure Interpretation**
  - **a. Comprehensive Parsing Logic:**
    - Develop robust parsing algorithms capable of detecting and interpreting a wide range of table structures, minimizing the risk of data loss or misinterpretation.
  - **b. Flexibility and Configurability:**
    - Allow users to define or adjust interpretation rules based on the specific characteristics of their documents, enhancing the system's adaptability to diverse table formats.
  - **c. Error Handling and Recovery:**
    - Implement mechanisms to gracefully handle unanticipated structures, providing informative error messages or fallback strategies to maintain workflow continuity.
  - **d. Metadata Preservation:**
    - Retain essential metadata related to table structures (e.g., original formatting details, positional information) to support advanced use cases or future reprocessing needs.
  - **e. Validation and Testing:**
    - Regularly validate the structure interpretation logic against a diverse set of table samples to ensure accuracy and reliability.
    - Utilize automated testing frameworks to detect regressions or issues arising from updates to the interpretation algorithms.
  - **f. User Feedback and Iterative Improvement:**
    - Incorporate user feedback mechanisms to identify and address challenges in structure interpretation, fostering continuous improvement of the extraction process.
### Configuration Settings
- **Formatting Preferences**:
    - **Markdown Styles**: Preferences for how the tables should be formatted in Markdown (e.g., GitHub Flavored Markdown, MultiMarkdown).
    - **Data Formatting**: Specifications for data formatting within the tables, such as numerical precision, date formats, or text encoding.
- **Parser Configuration**: Settings that control how the parsing engine processes the document.
    - **OCR Options** (for PDFs): If the PDF is a scanned document, Optical Character Recognition (OCR) settings might be necessary.
    - **Language Settings**: Specify the language of the document to assist with accurate text extraction.
    - **Error Handling**: Instructions on how to handle parsing errors, such as skipping problematic tables or stopping the process to alert the user.
- **Resource Limits**:
    - **Memory and Time Constraints**: Limits on system resources to allocate for the extraction process, important for handling large or numerous documents.

## Optional Inputs
### Access Credentials (if applicable)
   - **Protected Documents**: If the Word or PDF files are password-protected or encrypted, you need to provide the necessary passwords or decryption keys.
   - **Network Access**: If the documents are stored in a remote location (e.g., cloud storage, web URLs), you'll need to provide access credentials or API keys to retrieve them.
### Supplementary Files (if necessary)
   - **Stylesheets or Templates**: Custom stylesheets or templates that dictate how the Markdown output should be formatted.
   - **Lookup Tables or Reference Data**: Additional data required to interpret the table contents accurately, such as mappings for abbreviations or codes used within the tables.
### Environmental Specifications
   - **System Locale Settings**: Ensure that the system's locale settings match the formatting of the documents, especially for dates, numbers, and currency.
   - **Software Dependencies**: Any specific software versions or dependencies required by the extraction tools (e.g., specific versions of Python libraries).
### User Permissions and Compliance Requirements
   - **Data Privacy Consents**: If the tables contain sensitive information, ensure that you have the necessary permissions and consents to process the data.
   - **Compliance Specifications**: Any regulatory requirements that dictate how data should be handled during extraction and conversion.

# Solution