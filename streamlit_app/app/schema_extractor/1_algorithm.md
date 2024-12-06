# Problem Statement

Data schemas are essential for downstream data tasks but they can be hard to come by. The reasons include:

- Manual design of schemas can be expensive
- Publishers usually do not publish data schemas along with their datasets
- Publishers are not allowed to share full data schemas

Data Schema Extractor aims to:

- Provide a friendly Python/Streamlit graphical user interface for users to extract data schemas from user-provided data.
- Perform automatic data schema extraction and validation
- Provide meaningful interactions for users to audit and approve results

# Input Description

User upload files of the following types:

1. Tabular files: csv, tsv, xlsx, parquet, feather, HDF5
2. Serialized data files: json, xml, yaml, pickle, msgpack, bson, proto, arvro
3. Unstructured text files: doc, docx, pdf, txt, md, log, rtf,

# Solution

## 1\. Load files and detect file types
**File Upload**: The user uploads one or more files of the same type
**Detect File Type**: Detect file format and structure
**Sanitize File Content**:
- Back up the data
- Detect malformed data, ask user to discard or fix corrupted records
- Remove harmful characters
- Detect and redact sensitive data, inform the user
- Normalize formats and unify encodings
- Detect duplicated records, ask the user to remove or leave the records as they are
- Ask user to input a list of stopwords and remove stopwords from the data
- Detect harmful or unwanted content and report to the user for removal
- Save sanitized data for downstream processing

## 2\. Process Serialized Data Files
### Exploratory Data Analysis (EDA)
- Parse the serialized data
- Iterate through the data, identify key-value pairs, nested objects, arrays, and attributes
- Note each unique field or element name
- Determine data types
- Flatten the serialized data to data frames
- Produce EDA reports using automatic EDA tool like Ydata Profiling
### Data Schema Extraction
Use tools for automated schema extraction.
- Tools like genson or jsonschema for JSON schema extraction
- Toos like xmllint for XML schema extraction
- Avro libraries for Avro schema extraction
- Use LLM and engineered prompts for schema extraction
- Ask the user to set and/or confirm constraints such as:
  - Required fields
  - Field length limits
  - Unique constraints
  - Enumerated values for categorical fields
### Data Schema Validation
- For JSON, use tools like jsonschema, pydantic, or cerberus to validate JSON data against the schema.
- For XSD or DTD validation, use tools like lxml or xmllint

## 3\. Process Tabular Data Files
### Exploratory Data Analysis
- Perform automated Exploratory Data Analysis
### Data Schema Extraction
- Analyze column headers, extract column names
- Normalize column names
- Infer data types of each column
- Use tools like Pandera, Great Expectations, or Dataprep to infer schema.
- Provide user with a schema builder with the following abilities:
  - Add simple Key-Value pair with the column name as the key. User can optionally select another column of which values will be used as metadata.
  - Add nested Key-Value pair. User inputs the key and select the column names for nested keys. User can optionally select another column of which values will be used as metadata.
  - Add Key with array/collection value. User select the column name of which values are deliminated lists. User declares the deliminator. User can optionally select another column of which values will be used as metadata.
  - Add Key that maps to array of objects. User inputs the key and then add array elements which is any combination of the above Key-Value types.
### Data Schema Validation
The schema is valid when it can be used to successfully transform the tabular data to a serialized data file.

## 4\. Process Unstructured Data Files
### Exploratory Data Analysis
tba
### Data Schema Extraction
tba
### Data Schema Validation
tba

## 5\. User Interface and Experience Improvements
To enhance usability:
- Progress Indicators:
  - Display progress bars or status updates during lengthy operations.
- Undo and Revert Options:
  - Allow users to undo recent actions or revert to previous steps without restarting.
- Help and Guidance:
  - Provide tooltips, FAQs, and a help section within the interface.
  - Offer examples and suggestions during field selection and parameter settings.
- Error Handling:
  - Present clear, actionable error messages.
  - Guide users on how to resolve issues when they occur.

## 6\. Testing, Validation, Documentation, and Extensibility

To ensure reliability and future-proofing:

- Unit Testing:
  - Develop unit tests for each function and component.
  - Use test-driven development practices where feasible.
- Performance Testing:
  - Evaluate performance with datasets of varying sizes and complexities.
  - Optimize algorithms based on profiling results.
- Extensibility:
  - Design the system to handle multiple datasets beyond just two.
  - Support additional data formats (e.g., JSON, XML) and database connections.
  - Modularize components to allow for easy updates and feature additions.

To aid users and developers:

- Comprehensive Documentation:
  - Provide a detailed user manual with step-by-step instructions.
  - Include technical documentation for developers, outlining system architecture and codebase.
- Logging and Auditability:
  - Implement detailed logging of user actions and system processes.
  - Store logs securely and provide access for audit purposes if needed.
- Support Resources:
  - Offer support channels such as email, chat, or forums.
  - Regularly update documentation with FAQs and troubleshooting tips.