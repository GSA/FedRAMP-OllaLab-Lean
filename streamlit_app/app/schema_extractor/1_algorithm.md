# Problem Statement

Data schemas are essential for downstream data tasks but they can be hard to come by. The reasons include:

- Manual design of schemas can be expensive
- Publishers usually do not publish data schemas along with their datasets
- Publishers are not allowed to share full data schemas

Data Schema Extractor aims to:

- Provide a friendly Python/Streamlit graphical user interface for users to extract data schemas from user-provided data.
- Perform automatic data schema extraction and validation
- Provide meaningful interactions for users to audit and approve results
- Provide additional useful features such as extracting structured data from unstructured texts

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
- For JSON, use tools like jsonschema, pydantic, or cerberus to validate JSON data against the schema
- For XSD or DTD validation, use tools like lxml or xmllint
- User proper tools to validate other schema types
- If a tool can't be run in this Python/Streamlit application, inform the user of how to user the tool to validate the schemas


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
- Load the data
- Ask the user for a list of stopwords
- Remove unusual/harmful characters
- Normalize text, trim excessive white spaces, remove stopwords
- Tokenize texts and report the number of tokens
- Identify and report the most common words
- Perform n-gram analysis
- Identify and report the values and related statistics of bigrams and trigrams
- Identify and report the values and related statistics numeric values
- Calculate and report statistics on sentence lengths
- Display wordcloud
- Display bar charts for word frequencies
- Automatically discover topics and sub-topics within the texts
### Data Schema Design
#### Grouping similar values
Allow the user to create groups of trigrams and bigrams or groups of numeric values. The process is:
- Create a group name
- Choose the group type of "String" or "Numeric". The group cannot contain both n-grams (strings) and numeric values.
- Input group description
- Add identified trigrams and bigrams or identified numeric values.
#### Schema Design
Provide user with a schema builder with the following abilities:
1. Input schema title
2. Input schema description
3. Inform user that the schema type is "object" 
4. Add parent object properties:
  - As simple Key-Value pair by one of the following:
    - Select an identified group name as the key with data type inferred from the group values, the description from the group description.
    - Input the key name, select the data type from a list of string, number, integer, or boolean.
    - Example: "setup": { "type": "string", "description": "The setup of the joke",}
  - As Key with array/collection value:
    - Input the key name
    - Select the data type of "array"
    - Input the description
    - Select the data type of the items from a list of string, number, integer, or boolean
    - Example: "hobbies": { "type": "array", "description": "A list of hobbies", "items": { "type": "string" }
  - As a child object:
    - Input the object name
    - Select the type "object"
    - Add the object properties using steps similar to those of "Add parent object properties".
### Data Schema Validation
The schema is valid when it can be used to successfully extract structured data from unstructured data files.

## 5\. User Interface and Experience Improvements
To enhance usability:
- Organize UI elements logically, using tabs, accordions, or multi-step forms to manage complexity.
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
  - Provide robust undo and revert options can be challenging to implement effectively.
- Support Resources:
  - Offer support channels such as email, chat, or forums.
  - Regularly update documentation with FAQs and troubleshooting tips.

## 7\. Other Considerations
### Performance Considerations
Processing large datasets, especially in a web-based application like Streamlit, can lead to performance bottlenecks.

Recommendations:
    Data Chunking: Process data in chunks to manage memory usage efficiently.
    Asynchronous Processing: Use asynchronous programming to prevent the UI from freezing during long operations.
    Resource Limits: Set limits on the size of files that can be uploaded or provide warnings for large files.

### Security Concerns
Handling user-uploaded files introduces security risks such as malicious files, code injections, and exposure of sensitive data.

Recommendations:
    File Validation: Implement strict validation to ensure files are of the expected format and reject suspicious files.
    Sandboxed Execution: Process files in a secure, isolated environment to prevent malicious code execution.
    Data Encryption: Encrypt sensitive data during processing and storage.
    Compliance with Regulations: Ensure that the application complies with data protection laws like GDPR or HIPAA if handling personal or sensitive data.

### User Experience Considerations
The extensive features might overwhelm users, leading to a steep learning curve.

Recommendations:
    Simplify Interface: Design a clean, intuitive UI that presents options contextually rather than all at once.
    Guided Workflows: Implement wizards or step-by-step guides for complex tasks.
    Default Settings: Provide sensible default options to streamline common use cases.
    Feedback Mechanisms: Include tooltips, help sections, and the ability for users to provide feedback or request support.
