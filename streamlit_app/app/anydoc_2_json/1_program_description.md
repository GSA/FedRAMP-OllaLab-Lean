# FedRAMP OllaLab - AnyDoc to JSON
## Problem Statement
Organizations frequently rely on structured data embedded within unstructured data files such as Microsoft Word and PDF documents for decision-making, reporting, and compliance. However, the process of manually extracting this data is often time-consuming, error-prone, and inefficient. Existing solutions may lack scalability, compatibility with various file formats, or the ability to handle complex table structures. This creates a bottleneck in workflows where rapid access to accurate, structured data is critical.

We aim to develop a solution to extract data from unstructured data files such as docx, pdf and save the results in structured JSON files. By addressing challenges like table complexity, format variability, and data integrity, this solution will enhance data accessibility, streamline decision-making, and support compliance efforts in dynamic organizational environments.

## Main Requirements
The following sub-sections describe the main program requirements. The operational requirements will be implicitly or explicitly described in the "Program Steps" section.
### **1. System Architecture and Design**
- **Modular Architecture**: The system must be designed using a modular architecture to facilitate the addition of new modules and features without impacting existing functionality.
- **Scalable Infrastructure**: Design the system to scale horizontally and vertically to handle increasing workloads and data volumes.
- **Separation of Concerns**: Ensure clear separation between data processing, business logic, and presentation layers to enhance maintainability.
- **Loose Coupling**: Use asynchronous communication and message queues to decouple system components, enhancing resilience and scalability.
- **Event-Driven Design**: Adopt an event-driven architecture to support real-time processing and responsiveness.
### **2. Accessibility and Interfaces**
- **Python backend**: core functionalities are implemented in Python and categorized into modules as needed.
- **Web Interface**: All modules must be accessible through an intuitive and user-friendly Streamlit web interface that supports all major browsers and devices. 
- **Command Line Interface**: All modules must be accessible through a python file that takes proper parameters and can be executed in command line interfaces of different operating systems.
### **3. Data Processing and Management**
- **Data Parsing**: Reliably parse and ingest any amount of text-based data, including MS Word files, PDFs, and web content, using both automatic and user-guided mechanisms.
- **Structured Data Extraction**: Accurately extract structured data (e.g., data tables, JSON) from unstructured sources.
### **4. User Interaction and Experience**
- **Intuitive UI/UX**: Provide an intuitive user interface that simplifies complex tasks, reduces the learning curve, and enhances productivity.
- **Documentation and Help**: Offer comprehensive documentation, tutorials, and tooltips within the user interface.
### **5. Logging, Monitoring, and Alerting**
- **Comprehensive Logging**: Implement detailed logging for all system components, capturing system events, errors, and user activities.
- **Alerting Mechanisms**: Set up automated alerts for critical events, failures, and security incidents.
- The system shall implement robust try/catch mechanisms at all major steps (file upload, parameter reading, file conversion, content extraction, table processing, and JSON enrichment).  
- In the event of a corrupted file or partial conversion:
  - Log detailed error messages (including error type, file name, timestamp, and stack trace) to the logs/ folder.  
  - Display clear user-facing error messages with suggested recovery actions (e.g., “The file appears to be corrupted. Please upload another copy or try again later.”) via both the Streamlit interface and CLI console output.  
  - For table or text extraction failures, the system should attempt a limited number of retry attempts (configurable in the parameter file) before resorting to saving any partially extracted data along with error annotations.  
### **6. Development and Deployment Practices**
- **Automated Testing**: Include unit tests, integration tests, and end-to-end tests to ensure system reliability and prevent regressions.
- **Version Control**: Use a robust version control system (e.g., Git) for all code, configurations, and scripts.
- **Large File Processing**:
  - Simulate large file uploads (both docx and pdf) to benchmark the time required for conversion, extraction, and JSON enrichment.
  - Define threshold limits to flag files that take longer than a set duration, logging performance metrics for review.
- **Concurrent Uploads and Horizontal Scaling**:
  - Develop tests that simulate multiple simultaneous users (both CLI and Streamlit interface) to evaluate concurrency limits.
  - Consider using message queues and asynchronous processes to ensure high availability. Benchmark scaling behavior when scaling horizontally (multiple instances) or vertically (more powerful resources).
- **Automated Stress Testing**:
  - Use automated testing tools (e.g., Locust, JMeter) to implement load testing scripts that mimic high-volume usage.
  - Record results and update system configuration or resource allocation as needed.
- **Reporting and Alerts**:
  - Track performance metrics and, when thresholds are exceeded (e.g., processing delays or high CPU/memory usage), alert system administrators.
  - Provide comprehensive reports that address system responsiveness under different load conditions.
### **7. Maintainability and Support**
- **Code Quality Standards**: Adhere to coding standards and best practices to enhance readability and maintainability.
- **Documentation**: Produce extensive documentation for system architecture, APIs, modules, and operational procedures.
- **Automated Maintenance Tasks**: Schedule and automate routine maintenance tasks like database indexing, log rotation, and system updates.
### **8. Data Quality and Validation**
- **Data Validation**: Implement validation rules to ensure data integrity and correctness at all stages of processing.
- **Error Correction**: Provide mechanisms to detect and correct errors or inconsistencies in data.
- **Quality Metrics**: Monitor and report on data quality metrics, such as completeness, accuracy, and consistency.

## Main folder structure

```
app/
│
├── main.py                       # The index of all FedRAMP OllaLab Streamlit apps
├── app_data/
│   │
│   ├── anydoc_2_json/            # AnyDoc to JSON folder to store result data
│   └── ...
├── pages/
│   │
│   ├── Anydoc_2_Json.py          # AnyDoc to JSON app main page
│   └── ...
└── anydoc_2_json/
    │
    ├── parameters/                 # The folder to store the parameter (.yaml) files
    ├── requirements.txt            # Required packages
    ├── README.md                   # Documentation
    ├── logs/                       # Logs directory for error, event logs, and audit trails
    ├── tests/                      # Unit and integration tests
    ├── modules/                    # Core logic for each step of the pipeline
    └── ...
```
## Document components
The common components of a general document are:
- Cover page
- Table of content
- Header, footer
- Sections: Headings, sub-headings, groups
- Paragraphs with unstructured texts
- Tables: rows, columns, cells, merged cells
- Lists: ordered and unordered lists with nesting
- Media: references or embedded data (ie pictures)
- Metadata: author, creation date, etc.

## Program steps
### 1. Initialization
#### Set target file
- With Streamlit GUI, user will upload the file.
- With CLI, user will use the paramer --target or -t to be followed by the path to the target file. This parameter is mandatory.
- The file must be either docx or pdf. Doc files will be converted to docx files.
- A folder with the same name as the uploaded/target file with appended current date/hour is created in app_data/anydoc_2_json/.  In subsequent write attempts to the folder, overwrite files with same names. We call this folder the "result folder".
- The uploaded/targeted file is copied to the result folder.
#### Set parameter file
- With Streamlit GUI, the program will look up for saved parameter files (.yaml) in the "parameters" folder. If there is more than one parameter file, the application will give the user an option to select which parameter file to be used. The application also allows the user to set the name of a new parameter file. Only displays the next steps once the parameter file was selected or a new name declared.
- With CLI, the user will use the parameter --param or -p to be followed by the path to the parameter file. The file must already exist.
- At program startup, mandatory parameters (e.g., –target / -t for file path) are validated immediately. If missing, the system will prompt the user (GUI) or exit with an intelligible error message (CLI).  
- For optional parameters:
  - For “replaceFormControls”: If not provided, default to “yes”.  
  - For “removeTexts”, “replaceText”, “anonymization”, and “adjustDates”: If rules are missing, the corresponding processing step is skipped.  
  - In CLI mode, in the absence of a specified parameter file (--param / -p), the system should either use a default template (provided in the parameters folder) or gracefully exit with a message instructing the user to supply one.  
- In the Streamlit GUI, whenever an optional parameter is not set, display clear tooltips or placeholders indicating the default behavior and what input is expected.  
- Include parameter validation testing as part of automated tests to ensure that missing or partial parameters are handled gracefully.
### 2. Pre-conversion processing
Users have the option to perform the following actions, to be executed in the following order:
- **Replacing interactive form controls**: the program will skip or replace the interactive form controls with text strings. This decision is recorded as parameter "replaceFormControls" with values of "yes" (default) or "no". 
  - "Form controls" means both the dynamic fillable form controls and their ASCII character representation. For example, clickable check boxes, the checked-box character, and the unchecked-box character.
  - The current supported controls are check boxes and radio buttons.
  - With Streamlit GUI, this function is executed if "replaceFormControls" is "yes". The user will be informed of sucessful execution or errors. Once succesfully executed, the state and results will persist through subsequent page refreshes.
  - With CLI, the rules are in the parameter file. The program will parse the rule and execute accordingly.
  - Once replacement is authorized, the program will do the following:
      - {{checked box}} is the default value for checked checkbox replacement.
      - {{unchecked box}} is the default value for unchecked checkbox replacement.
      - {{selected radio button}} is the default value for selected radio button replacement.
      - {{unselected radio button}} is the default value for unselected radio button replacement.
- **Remove texts within two markers**: This option allows the user to specify the start marker and end marker. The "end of line" is supported as a marker. All text between these markers will be removed. The user may have more than one instance of this rule.
  - The parameters for this feature is recorded as follows:
    - The main parameter name is "removeTexts". This parameter is optional.
    - Each removal rule is a dictionary with two keys: "start" specifies the start marker string and "end" specifies the end marker string
  - With Streamlit GUI, the user can click the button "Skip this step" to skip this step or click the button "Add text removal rule" to start adding the first text removal rule. If the button "Add text removal rule" is clicked:
    - The program displays two input boxes of "Start marker" and "End marker"
    - There are notes displayed regarding accepted special characters for the markers such as the "end of line". These special characters can be used in both Streamlit GUI and the CLI.
    - The user input the marker strings to finish a removal rule
    - The user can click the button "Add text removal rule" again to create another removal rule
    - Once done, the user can click the "Remove Texts" button to save the parameter values to the parameter file and run the rule(s).
    - Only display the next steps when either "Skip this step" or "Remove Texts" is clicked.
    - Once succesfully executed, the state and results will persist through subsequent page refreshes.
  - With CLI, the rules are in the parameter file. The program will parse the rule(s) and execute accordingly.
  - When running, each rule will do the following:
    - Find the first instance of "Start marker" and "End marker"
    - Remove the text between the the first instances of "Start marker" and "End marker" by a space character " "
    - Repeat the process by looking for the next instances of "Start marker" and "End marker"
    - Do nothing if either "Start marker" or "End marker" is not found
- **Find and replace texts**: This option allows the user to replace a string with another string. The user may have more than one instance of this rule.
  - The parameters for this feature is recorded as follows:
    - The main parameter name is "replaceText". This parameter is optional.
    - Each replacement is a dictionary with two keys: "from" specifies the string to be replaced and "to" specifies the replacement string
  - With Streamlit GUI, the user can click the button "Skip this step" to skip this step or click the button "Add text replacement rule" to start adding the first text replacement rule. If the button "Add text replacement rule" is clicked:
    - The program displays two input boxes of "Find" and "Replace"
    - There are notes displayed regarding accepted special characters for the markers such as the "end of line". These special characters can be used in both Streamlit GUI and the CLI.
    - The user input the marker strings to finish a replacement rule
    - The user can click the button "Add text replacement rule" again to create another removal rule
    - Once done, the user can click the "Replace Texts" button to save the parameter values to the parameter file and to run the rule(s)
    - Only display the next steps when either "Skip this step" or "Replace Texts" is clicked
    - Once succesfully executed, the state and results will persist through subsequent page refreshes
  - With CLI, the rules are in the parameter file. The program will parse the rule(s) and execute accordingly
  - When running, each rule will do the following:
    - If the value of "Find" is "" or None, the rule is ignored
    - Find all occurrences of "Find" value text string
    - Replace the "Find" value text string with the "Find" value text string which can be empty
- **Anonymize texts**: This option allows the user to replace emails, names, organization names. 
  - The program will detect if there are emails, names, or organization names within the file content and report the number of found occurances per category to the user.
  - The parameters for this feature is recorded as follows:
    - The main parameter name is "anonymization" which is a dictionary. This parameter is optional.
    - The keys for the dictionary must be unique and can be any of the following: email, person name, and organization
    - The value of the key can be any of the following: redact, jibberish, realistic
  - With Streamlit GUI, the user can either click "Skip this step" to skip this step or click the button "Add anonymization rule" to start adding the first text anonymization rule. If the button "Add anonymization rule" is clicked:
    - The programs displays two drop down lists of "Category" and "Methods" together in one row
    - The values of "Category" are: email, person name, and organization
    - The values of "Methods" are: redact, jibberish, realistic
    - The user can click the button "Add anonymization rule" again to create another removal rule for the remaining categories.
    - Once done, the user can click the "Anonymize Texts" button to save the parameter values to the parameter file and to run the rule(s)
    - Only display the next steps when either "Skip this step" or "Anonymize Texts" is clicked
    - Once succesfully executed, the state and results will persist through subsequent page refreshes
  - With CLI, the rules are in the parameter file. The program will parse the rule(s) and execute accordingly.
  - When running, each rule will do the following:
    - For each found entry within a category, replace all occurences of that entry following the selected method for that category.
    - The redact method replaces a found string of x characters by a string of x stars
    - The jibberish method replaces a found string of x characters by a string of x stars. Email structure (the "." and "@") remains unchanged
    - The realistic method replaces a found email, person name, or organization name with another fake email, person name, or organization name
- **Adjust dates**: This option allows the user to adjust the values of found dates which must have the values for day, month, and year.
  - The program will detect if there are dates within the file content and report the number of found occurances to the user.
   - The parameters for this feature is recorded as follows:
    - The main parameter name is "adjustDates" which is a dictionary. This parameter is optional.
    - The keys for the dictionary must be only one of the following: add, subtract, daysBefore, daysAfter
    - The value of the key must be an integer greater than 0.
  - With Streamlit GUI, the user can either click "Skip this step" to skip this step or click the button "Add date adjustment rule" to start adding the date adjustment rule. If the button "Add date adjustment rule" is clicked:
    - The programs displays a drop down list of "Adjustment methods" and an input box of "Number of days" together in one row
    - The values of "Adjustment methods" are: add days, subtract days, days before now, and days after now
    - The value of "Number of days" is any integer greater than 0
    - Once done, the user can click the "Adjust dates" button to save the parameter values to the parameter file and to run the rule
    - Only display the next steps when either "Skip this step" or "Adjust dates" is clicked
    - Once succesfully executed, the state and results will persist through subsequent page refreshes
  - With CLI, the rules are in the parameter file. The program will parse the rule(s) and execute accordingly.
  - When running, the rule will do the following for each found date:
    - The "add days" option adds the "number of days" value to the date to form a new date.
    - The "subtract days" option subtracts the "number of days" value from the date to form a new date.
    - The "days before now" option changes the date to a date that is "number of days" value before the current system date.
    - The "days after now" option changes the date to a date that is "number of days" value after the current system date.
- **Find and Remove Rows**
  - Remove empty rows
    - In GUI, it's a check-box of "Remove empty rows". It is saved as pararameter "removeEmptyRows" with default value of "yes"
    - The program will find and remove all empty rows.
  - Remove rows with certain string
    - In GUI, it's an input box of "Remove rows with the following string". It is saved as parameter "removeRowsWithString".
    - The program with find and remove rows that has the user input string
- **Find and Remove Columns**
  - Remove empty columns
    - In GUI, it's a check-box of "Remove empty columns". It is saved as pararameter "removeEmptyColumns" with default value of "yes"
    - The program will find and remove all empty columns.
- **2pass Cleanup**: This option allows the above steps to be executed again at the end of step 3
  - Add a checked check-box of "Attempt these steps post-conversion". Once checked, the parameter "2pass_cleanup" is recorded to the parameter file with value "yes".
  - If the parameter "2pass_cleanup" is "yes", the same steps (step 3.1 to 3.7) in "Pre-conversion processing" with corresponding set parameters will be ran again at the end of "Convert document to MarkDown using Docling". Please note that the file format changed from docx or pdf to markdown so while the tasks (step 3.1 to 3.7) are the same, the code implementation can be different.
### 3. Convert document to MarkDown using Docling
- In this step, the program will convert the document to MarkDown, saved to disk a file with the same name but with a ".md" extension using Docling, and report the result status to the user. The procedure is as follows:
  - Convert the document to markdown using Docling
  - Remove empty markdown headings (for example, lines with just the "#" characters)
  - Find how many level 1 heading (a line started with "#") in the markdown document
  - If there are more than one level 1 heading, do the following:
    - In the Streamlit GUI: Displays a text box entitled "Document title" asking the user to put in the title of the file
    - With CLI, use the file name without extension as the document title
    - Add one more level to all existing heading. For example, "#" will become "##", "##" will become "###"
    - Add the "Document title" as the level 1 heading at the beginning of the file content
  - If there is no level 1 heading, do the following:
    - In the Streamlit GUI: Displays a text box entitled "Document title" asking the user to put in the title of the file
    - With CLI, use the file name without extension as the document title
    - Add the "Document title" as the level 1 heading at the beginning of the file content
  - Markdown heading normalization by recursive execution of the following:
    - Identify the current highest heading level exists in the document (for example, "#" is higher than "##")
    - Search for the next highest heading level in the document
    - If there is a gap in heading level value between the current highest heading level (for example, "#" - level 1) and the next highest heading level (for example, "###" - level 3), close the gap (for example, change "###" - level 3 to "##" - level 2)
    - Set the current highest heading level to the current next heading level (for example, "##" - level 2) and repeat the process until the next highest heading value is not found.
  - Save the document to the result folder
  - With Streamlit GUI, the markdown content will be displayed in a collapsible expander
  - With CLI, print the full path of the .md file to screen as a way to report successful conversion
- Once succesfully executed, the state and results will persist through subsequent page refreshes
### 4. Get structured data using default JSON schema designing per Docling supported document components
Below is a formal JSON Schema to use as the basis for converting Markdown content into a structured JSON document. Following the schema, there are refined instructions that clarify how to parse the Markdown file and populate the JSON fields.

#### THE MARKDOWN TO JSON SCHEMA (Draft-07 or later)
```
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "http://example.com/document-structure.json",
  "title": "MarkDown Document Structure Schema",
  "description": "A schema describing the structure of a MarkDown document, including relative positions of elements.",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "document": {
      "type": "object",
      "description": "Container for the entire document.",
      "additionalProperties": false,
      "properties": {
        "title": {
          "type": "string"
        },
        "content": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "properties": {
              "type": {
                "type": "string",
                "enum": ["paragraph", "list", "table", "heading"] // Add "heading" for headings
              },
              "content": {
                "type": "string" // For simple content like paragraphs
              },
              "list_items": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              },
              "table": {
                "type": "array",
                "description": "Array of MarkDown table text to be parsed later on",
                "items": {
                  "type": "string"
                }
              },
              "position": {
                "type": "integer",
                "description": "Sequential position of the element within its parent container"
              },
              "parent": {
                "type": "string",
                "description": "Type of the parent container (e.g., 'document', 'section')"
              },
              "level": {
                "type": "integer",
                "description": "Heading level (1 for H1, 2 for H2, etc.)"
              }
            }
          }
        }
      }
    }
  },
  "required": ["title", "content"]
}
```

#### REFINED INSTRUCTIONS FOR PARSING MARKDOWN INTO THIS SCHEMA
Below is a step-by-step guide for how a programmer could parse a Markdown file and then populate the JSON object according to the schema above. These instructions assume you have a way to read the raw Markdown lines and identify headings, lists, and tables.
##### High-Level Flow
1. Identify the top-level document title, which corresponds to the Markdown line starting with "# " (H1).  
2. Gather any text (paragraphs, lists, tables) that appear before the first "## " heading; store these under "content_text1".  
3. For each "## " heading encountered, start a new item in the "section" array. Extract the heading text as "section_header".  
4. Within each section, parse its content (paragraphs, lists, tables) until you reach either the next "## " heading or the end of the file.  
   - If you encounter a "### " heading, that content belongs to a new "sub_section" item inside the "section_content".  
   - For a "#### " heading, create a new item in "sub_sub_section" within the correct sub-section.  
5. After parsing all sections (i.e., after the last "## "), gather any remaining text (paragraphs, lists, tables) and store them in "content_text2".  
##### Detailed Steps
1. Extracting "document → title":
  - Scan the beginning of the Markdown file for a line starting with a single "#" (H1).  
  - The text following "# " is assigned to document.title.  
  - Do not include the leading "#" in the title.  
2. Handling Pre-Section Text ("content_text1"):
  - All content (paragraphs, lists, tables) before the first "## " is stored in "content_text1".  
  - Paragraphs: Consecutive lines of non-list and non-heading text can be grouped into entries of "paragraph".  
  - Lists: A block of text that starts with either "-", "*", or a numbered format ("1.", "2.", etc.) belongs to a single list. Accumulate each item under "list_item". If you encounter a second distinct list block, create a new object in the "list" array.  
  - Tables: If you detect a Markdown table (lines containing "|" separators in a table-like format), store the entire raw table syntax as a single string in the "table" array.  
3. Creating "section" Objects for "## " headings:
  - Each time you see "## " (H2 heading), start a new element in the "content.section" array.  
  - The text after "## " goes into "section_header".  
  - Everything following this section header (but before the next "## " or end of file) belongs to "section_content".  
4. Parsing Content Within a Section ("section_content"):
  - "section_paragraph": Group all standalone lines into array items, similarly to paragraphs in content_text1.  
  - "section_list": Group each distinct list block into an object that has a "list_item" array.  
  - "section_table": Each Markdown table is stored as a string inside this array.  
  - If a "### " (H3 heading) is encountered, it indicates a new "sub_section".  
5. Handling "sub_section" (for "### " headings):
  - For each "### " heading, create a new object in "sub_section".  
  - The text after "### " is "sub_section_header".  
  - All content (paragraphs/lists/tables) following that heading (until the next "### " or "## " or end of file) belongs to "sub_section_content".  
  - If a "#### " heading is found, that indicates a new "sub_sub_section" within the current sub_section_content.  
6. Handling "sub_sub_section" (for "#### " headings):
  - For each "#### " heading, create a new object in the "sub_sub_section" array.  
  - The text after "#### " is "sub_sub_section_header".  
  - Content (paragraphs/lists/tables) that follows, up to the next heading of equal or higher level, belongs to this sub-sub-section.  
7. Handling Post-Section Text ("content_text2"):
  - Any paragraphs, lists, or tables appearing after the last "## " heading in the document belongs to "content_text2".  
  - Parse these elements the same way you parsed "content_text1": paragraphs go into an array of strings, lists go into an array of objects each containing "list_item" array, and tables go into an array of strings.  
##### Implementation Notes
- Pay attention to heading hierarchy: H2 (##) → Section, H3 (###) → Sub-section, H4 (####) → Sub-sub-section.  
- When you see a heading, you typically finish capturing content in the current block, then start a new block at the appropriate level.  
- Paragraph segmentation can be handled by looking for blank lines or heading/list boundaries.  
- Lists may be nested in raw Markdown, but for simplicity in this schema, collect each top-level list at the appropriate location. If you do need deeper nesting, you could adapt the schema to store sub-lists.  
- Markdown tables can be captured verbatim as raw strings or parsed into a more detailed structure. This schema simply stores them as strings for simplicity.  
- You may want to set default values for empty arrays if no paragraphs/lists/tables are found in a particular content block.  

### 5. Process MarkDown tables
This section describes how section_table, sub_section_table, and sub_sub_section_table can be further parsed into more detailed structure. The procedures to process the table raw strings are as follows:
#### Remove empty rows and columns
- Empty columns are columns with more than 2 rows. The first row may or may not be empty. The rest of the rows are empty.
- Empty rows are rows with empty cells.
- These empty rows and columns must be removed before processing further.
#### Resolve issues with spanning cells
When translating tables to markdown tables, Docling will remove the spanning of a cell resulting new empty cells and copy the original content of the spanned cell over to the newly created cells. Before we translate markdown tables to structured json, we need to clarify and solve the spanning problem especially spanning happens on the table header.
1. Spanning patterns after being converted to markdown tables
  - Span all columns in a row: all cells in the row have identical content
  - Span some columns in a row: some consecutive cells in the row have identical content
  - Span all rows in a column: all cells in the column have identical content
  - Span some rows in a column: some consecutive cells in the column have identical content
2. Spanning cells are in the first row or the second row or both
  a. Identify if the second row is part of the header
    - We assume the tables header reaches to a maximum of two rows.
    - Check and compare the spanning patterns among the second row and the third, forth rows.
    - If the spanning patterns are the same across the second, third, and forth rows, the second row is not a part of the header. Otherwise, the second row is part of the header.
  b. If the second row is part of the header, merge the second row with the first row on the per-column basis with " - " as the delimiter. For example, if the first cell of row 1 is "Value r1c1" and the first cell of row 2 is "Value r2c1", then the resulting new first cell of row 1 will be "Value r1c1 - Value r2c1".
  c. If the second row is not a part of the header, the program does nothing.
3. Spanning cells are in rows other than the first nor the second rows
  - The program does nothing.
#### Merge multi-page tables
After resolving spanning cell issues in all tables, we need to merge tables with identical first row. We assume that with multi-page tables, the producers include table header in the table sections that span to new pages.
#### Save the JSON data
- Save the JSON data to a json file in the result folder
- The json file has the same name as the uploaded file with appended "_raw".

### 6. Enrich the JSON data
#### Identify key-value pairs based on table structure
1. If table has only one colummn
  - Row 1 becomes the key. Within this key, each single-cell row is processed as follows: 
    - If cell has ":", the string preceeding the first ":" becomes the sub-key and the following string becomes the key's value.
    - If cell has multi lines, the first line becomes the sub-key and the rest becomes the key's value.
    - If none of the above applied, "item" becomes the sub-key and the cell value becomes the key's value.
2. If table header has multiple columns (row 1 has multiple cells with different values) and table body is a single column (row 2 and below span all columns)
  - Merge the content of the header (first row) cells into the first cell with " - " as the delimiter. For example, "cell 1 value", "cell 2 value" will become "cell 1 value - cell 2 value".
  - Keep the first column and remove other columns. The table will become a single column table.
  - Process the table as a single column table as shown in item 1 above.
3. If the header spans all columns (all cells in row 1 are identical) and table body has more than one column, the first cell in row 1 (the header) becomes the key. Within this key, each follwing row is processed as follows:
  - If row has two columns (two cells per row), the first cell becomes a sub-key and the second cell becomes the key's value.
  - If row has more than two columns:
    - The first cell becomes the sub-key.
    - Under this sub-key, one "item" key is created for each of the following cells with the cells' values as the "item" keys' values.
- First row cells are the key
#### Update the JSON data
- Translate the tables to JSON data based on the identified key-value pairs.
- Replace section_table, sub_section_table, and sub_sub_section_table with the corresponding JSON data
- Save the updated JSON data to a json file in the result folder
- The json file has the same name as the uploaded file with appended "_enriched".

### 7. Wrapping up
- Check and make sure parameters are properly saved to the specified parameter file.
- In the GUI, offer the user the option to reset everything and start a new session. In this case, make sure sure application session state variables are properly resetted.