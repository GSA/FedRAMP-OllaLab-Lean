# Problem Statement

We face the challenge of merging multiple datasets containing pairs of {Unique IDs, Entity Names}, where entities overlap but have different Unique IDs across datasets due to independent publishing sources. Our objective is to accurately merge these datasets based on Entity Names by leveraging Large Language Model (LLM) knowledge of real-world entities. The entities must represent actual entities, and the LLM's embedded knowledge should facilitate the merging process.

# Input Description

We have at least two data files of type csv, tsv, or xlsx. Each file has at least one pair of {Unique IDs, Entity Names}. A file may have up to two pairs of {Unique IDs, Entity Names} where one pair represent the parent and the other pair represents the child. A child has no child of its own. A parent pair has at least one child. Data in pairs for child cannot appear in the parent columns meaning the Parent-Child relationship only goes 1 level (there is no grand parent).

# Solution

## 1\. Load files and normalize data

### File Loading

1. **File Upload**: The user uploads two or more files (e.g. F1, F2, F3)
2. **Data Frame Creation**: Files are loaded into data frames (F1, F2, F3).
3. **Handling Missing Data**:
- The program checks for empty cells and allows the user to choose how to handle them:
  - Remove rows with missing values.
  - Fill missing values with defaults or placeholders.
  - Skip processing fields with excessive missing data.  
4. **Field Selection with Validation:**
- For each file, the user must select the following fields from a list of columns:
  - Parent ID Field (optional).
  - Parent Name Field (mandatory).
  - Child ID Field (optional).
  - Child Name Field (optional).
- The program validates selected fields for correct data types and formats.
- Provides immediate feedback if invalid fields are selected.
5. **Reset Option**: A "Reset" button is always available to restart the process.
6. **Saving Initial Data Frames**: Selected columns are saved to initial data frames (e.g., F1_initial, F2_initial).

### Normalize IDs

For each initial data frame:

1. **Parent IDs**:
- If the table has no Parent Name, the program will halt and issue an error message. The program will not move forward in this case.
- If the table lacks a Parent ID but has Parent Names, generate a unique Parent ID for each unique Parent Name.
2. **Child IDs**:
- If the table lacks Child IDs but has Child Names, generate unique Child IDs for each unique Child Name.
3. **Handling Missing Child Names**:
- If Child Names are missing but Child IDs are present:
  - Prompt the user to provide a naming convention.
  - Use a placeholder or combine Parent Name with Child ID to create a meaningful Child Name.
4. **Ensuring Data Integrity**:
- Verify that after processing, each record has a Parent ID and Parent Name.
- Implement error handling for records that still lack mandatory fields.

### Normalize Entity Names

To prevent over-normalization and preserve essential parts of entity names:

1. **Duplicate Original Names**:
- Create copies of Parent Name and Child Name columns with a _original suffix.

2. **Normalization Steps**:
- Case Normalization: Convert all letters to uppercase.
- Punctuation Removal: Remove dots (.), hyphens (-), underscores (_), commas (,), and other non-essential punctuation while maintaining readability.
- Controlled Prefix/Suffix Removal:
  - Use a predefined list of non-essential terms (e.g., "INC", "LLC", "CORP") to remove from Parent Names.
  - Avoid removing words that are integral to the entity's identity.
  - Allow users to customize the list of terms if necessary.
- Logging Changes:
  - Record all normalization actions in a log for transparency and debugging.

3. **Retain Mappings**:
- Maintain a mapping of original to normalized names to prevent confusion during later stages.

### Remove duplicated rows

To ensure data remains manageable and analyzable:

1. **Identify Duplicates Using Normalized Fields**:
- Use combinations of normalized Parent IDs, Parent Names, Child IDs, and Child Names.

2. **Handle Duplicates**:
- Instead of merging data into lists within a cell, create a separate mapping table that relates duplicate IDs to a unique entity ID.
- Preserve the tabular structure for compatibility with data analysis tools.

## 2\. Construct Unique Parent Name List

a. **Automated Matching Using Similarity Metrics**:
- Apply string similarity algorithms (e.g., Levenshtein distance, Jaro-Winkler) to compute similarity scores between normalized Parent Names across all data frames.
- Set a similarity threshold (e.g., 90%) to automatically group names above this threshold.
- Implement efficient data structures (e.g., inverted indices, clustering) to reduce computational complexity.
- Use blocking techniques to group entities and limit comparisons.

b. **User Input for Ambiguous Cases**:
- Present ambiguous matches (below the threshold) to the user for confirmation.

c. **Create Unique Parent Names Data Frame**:
- Assign a unique identifier (UniqueParentID) to each grouped entity.
- Maintain mappings to original Parent IDs and names from each dataset.

d. **User Interface Enhancements**:
- Provide bulk actions to approve or reject suggested matches.
- Allow adjustment of similarity thresholds and reprocess matches accordingly.
- Allow saving UniqueParentID, normalized Parent Names, and mmapping of original Parent Names to normalized Parent Names to a unique parent name output file.

## 3\. Construct Unique Children Name List

Similar to constructing the unique parent name list:

a. **Automated Matching Using Similarity Metrics**: Compute similarity scores between normalized Child Names across all data frames.

b. **User Input for Ambiguous Cases**: Present ambiguous matches (below the threshold) to the user for confirmation.
   
c. **Efficient Comparison Process**: Use optimized algorithms suitable for larger datasets.

d. **Create Unique Child Names Data Frame**:
- Assign unique identifiers (UniqueChildID) to each group of similar child entities.
- Maintain mappings to original Child IDs and names.
- Allow saving UniqueChildID, normalized Child Names, and mmapping of original Child Names to normalized Child Names to a unique parent name output file.

## 4\. Enrich Original Data Frames with UniqueParentID and UniqueChildID
a. **Prepare for Enrichment**:
- Duplicate original data frames (e.g. F1) to create enriched versions (e.g., F1_enriched).

b. **Matching Using Normalized Names and IDs**:
- Use Parent Name field or Child Name field to search for matching UniqueParentID or UniqueChildID leveraging the information in the Unique Parent Name List or the Unique Child Name List.
- If a match is found, add to the column UniqueParentID or UniqueChildID

c. **Save to file**:
- Allow the user to save/download the enriched data frame.

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

## 6\. Testing, Validation, and Extensibility

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

11. Documentation and Support

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