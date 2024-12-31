# Problem Statement

In interacting with LLMs, the quality of questions directly impacts the quality of answers. Prompt Engineering is all about crafting the best possible questions (prompts). Robust Prompt Engineering will help FedRAMP, GSA members, and all internal/external Stakeholders engage more effectively with LLMs.

Mainstream chat interfaces such as those provided by OpenAI and Anthropic have all or some of the following limitations:
- Lack of selective inclusion of chat results for more precise context
- Lack of abstraction interface for better content navigation and awareness
- Lack of back-up mechanisms for both prompts and results
- Lack of flexibility in sharing different abstractions of chat results
- Lack of supports for teamwork and convenient reusability

OllaLab - SimpleChat aims to solve the above limitations by providing key features of:
- Selectively save LLM responses to prompt variables
- Save prompts to prompt variables
- Automatically extract user-specified local folders and files to prompt variables
- Embed prompt variables in future prompts
- Chain prompt variables to form new variables
- Allow convenient share and reuse prompt variables
- Provide other automation/integration features


# Input Description

User inputs can be provided via:

1. simplechat.yaml file
2. Files copied to a local folder to be loaded by the application
3. Texts typed into the application
4. Texts typed into the prompt variable creation box

# Program Description
The following sections describes the components of the Simple Chat program.

## 1\. Program requirements
Program requirements are saved in the requirements.txt file

## 2\. Program variables
Program variables are saved in the simplechat.yaml file
**Local User Values**:
- Local user name (local_user_name): A string specified by the user to represent the user in certain activities and logs. The default value is "anonymous".
- Salt (salt): A random string specified by the user to append to data before it is hashed, making the hash more robust to attacks. The default value is "empty".

**LLM values**:
- Maximum context window (context_window): The maximum number of tokens that can be used as input for LLMs. The default value is 128000.
- Supported LLM platforms (llm_platform): A comma-separated list of supported LLM platforms. The default value is "Ollama, OpenAI, Google Vertex AI, Amazon Bedrock, Anthropic".
- Guard server (guard_server): The url of the LLM guard server. The default value is "empty".
- Monitoring server (monitoring_server): The url of the LLM monitoring server. The default value is "empty".
- Selected LLM platform (selected_provider): The LLM platform that the application will leverage. The default value is "Ollama".
- Selected LLM endpoint (selected_endpoint): The LLM endpoint that the application will leverage. The default value is "http://127.0.0.1:11434".

**Prompt Variable Values**:
- promptvariable_filepath: the path to the folder hosting all prompt variable files. The default value is /app/simple_chat/prompt_variables
- data_filepath: the path to the folder hosting all data folders and files. The default value is /app/simple_chat/data_files
- default_filename: the default name for a json prompt variable file when there is no existing prompt variable file. The default value is "default__promptvariables.json"
- postfix_filename: the text to append to the end of a user-declared file name for a prompt variable file. The default value is "_promptvariables"

## 3\. LLM endpoint selection and configuration
**User interface**
- Display the user interface for LLM endpoint selection and configuration on the side bar
- Get the list of supported LLM platforms from llm_platform
- Follow the default values for LLM endpoint and check if a connection with the default endpoint can be made.
- If there is an issue with the default endpoint, ask user to select a platform from the list
- For a selected platform, present the user with options to properly configure the platform API
- Once connection is successfully established with the selected LLM endpoint, fetch a list of LLMs supported by the platform, allow the user to select which supported LLM model to use.
- At anytime, user can use the interface to change the LLM platform and/or LLMs
- Use proper mechanisms to sustain/persist user-selected values until user decide to change them.
**Configuring Ollama**
- tba
**Configuring OpenAI**
- tba - make sure to use encryption to encrypt the keys
**Configuring Anthropic**
- tba - make sure to use encryption to encrypt the keys
**Configuring Google Vertex AI**
- tba
**Configuring Amazon Bedrock**
- tba

## 4\. The main application interface
The Simple Chat application interface contains the side bar and the main application interfaces. The main application interface can be described as follows:
- tba

## 5\. Promp Variable Management
**Components of a prompt variable**
- Variable name: the name of the variable, must be all lower case with no space, must have no special character.
- Variable type: the variable's type
- Variable value: the value to of the variable with one or more of the following sub values
  - Texts: the textual content assigned to the variable.
  - Source: the source of the Texts. For the "Question" type, this value is the local_user_name. For the "Answer" type, this value is the user selected LLM model within the user selected LLM platform. For the "File" type, this value is the path to a folder or a file. For the "Web" type, this value is a url. For the "API" type, this value is the API endpoint.
- Creation time: The time when the prompt variable was first created.
- Latest time: The time when the prompt variable was last updated.
- Hash: The hash of the content of Variavle value - Texts and Salt.
- Update logs: A comma-separated list of time values. The default value is the Creation time. 
**Prompt variable types**
- Question: the variable of this type was created from user's question. It should contain an inquiry.
- Answer: the variable of this type was created from an LLM's answer. It should not contain an inquiry.
- File: variables of this type was automatically created by crawlwing a user-specified local directory.
- Web: the variable of this type was created from extracting content from a user-specified website. 
- API: the variable of this type was created from extracting content from a user-specified API request.
**Prompt variable creation interface**
>>>>>>>>>>>> tba
**Create prompt variables of "File" type**
- Read and traverse all folders and files including shortcuts or symbolic links within data_filepath.
- Create a prompt variable for each folder follwing the format of \<folder level\>_\<folder name\>. The folder level number starts with 1 (top level) and reflects the folder level in the overall folder hierarchy within data_filepath.
- Create a prompt variable for each file follwing the format of \<folder level\>_\<file name\>. The folder level value is the same folder level value of the folder hosting the files.
- Supported file types are txt, rtf, wps, pdf, doc, docx, xls, tiff, xml, htm, html, .msg, .wpd.
- Save the variable with the following additional values
  - Variable value:
    - Texts: 
      - If it is a folder, the texts include the variables representing the folders and/or files within the folder.
      - If it is a file, the texts include the textual content of the file following this template:
        "My current \<file name\> is:
        \<extracted textual content of the file\>
        "
      - If it is a file, the textual content is extracted only when the variable was referenced by a user prompt or by another variable at run time. Before that, the default value is "pending extraction"
    - Source: The path to the folder or the file
  - Creation time: The time right before the variable was first saved to a variable file.
  - Latest time: The time right after the Texts were successfuly extracted and the variable is successfully updated.
  - Hash: The hash of the content of Variavle value - Texts and Salt.
  - Update logs: when there is a new "Latest time" value, append the value to this updated logs comma-separated list.
**Create prompt variables of "Web" type**
- Crawl and extract a website content using user-provided url and optional div tag. Once a div tag is provided, only extract html content within the div tag. Clean up extracted texts.
- Create a prompt variable of type "Web" with the user-provided variable name.
- Save the variable with the following additional values
  - Variable value:
    - Texts: the cleaned up extracted texts
    - Source: the user-provided url
  - Creation time: The time right before the variable was first saved to a variable file.
  - Latest time: The time when the url was last visited, its content was successfully extracted, and the variable is successfully updated.
  - Hash: The hash of the content of Variavle value - Texts and Salt.
  - Update logs: when there is a new "Latest time" value, append the value to this updated logs comma-separated list.
**Create prompt variables of "API" type**
- Save the variable with the following additional values
  - Variable value:
    - Texts: the cleaned up extracted texts
    - Source: the user 
  - Creation time:
  - Latest time:
  - Hash: The hash of the content of Variavle value - Texts and Salt.
  - Update logs: when there is a new "Latest time" value, append the value to this updated logs comma-separated list.
**Create prompt variables of other types**
- Save the variable with the following additional values
  - Variable value:
    - Texts: the cleaned up extracted texts
    - Source: the user 
  - Creation time:
  - Latest time:
  - Hash
  - Update logs:
**Load and display prompt variable content and statistics**
- Display a user-clicked prompt variable content and statistics in a st.dialog
- Integrity check
- Dependency check (both parent and child)
- Tokens
**Context window awareness**
- Display total tokens for input, for reasoning and output. Make sure user is aware.
- >>>>>>>>> tba
**Modify/update prompt variable interface**
- 
**Update prompt variables of "File" type**
- Variable value:
  - Texts:
  - Source:
- Creation time:
- Latest time:
- Hash
- Update logs:
**Update prompt variables of "Web" type**
- Variable value:
  - Texts:
  - Source:
- Creation time:
- Latest time:
- Hash
- Update logs:
**Create prompt variables of "API" type**
- Variable value:
  - Texts:
  - Source:
- Creation time:
- Latest time:
- Hash
- Update logs:
**Create prompt variables of other types**
- Variable value:
  - Texts:
  - Source:
- Creation time:
- Latest time:
- Hash
- Update logs:

## 6\. Promp Variable File Management
**Prompt variable file user interface**:
- Prompt variable files are ordered alphabetically and displayed within a drop down box in the application side bar. User selects one prompt variable file to use.
- When a new prompt variable file was successfully created and saved, update the drop down box.
- User can click the "Create new prompt variable file" button to create new prompt variable file. Once clicked, a streamlit dialog box appears with options for user to create a new file.
**Create new prompt variable file**:
- Ask user to put in the file name
- If the file already exists, ask the user for another name
- User will then be able to choose whether to create a new blank file or from an existing prompt variable file.
- If user chose to create a new file from an existing prompt variable file, allow the user to chose which file.
- Save the file to the prompt variable folder (promptvariable_filepath)
**Load and save prompt variable files**:
- User selects a prompt variable file name (json file)
- Load the file from the prompt variable folder (promptvariable_filepath)
- When saveing a prompt varible file, saves the file as a json with indent=4 to the prompt variable folder (promptvariable_filepath)

## 7\. Supports for Apache AirFlow
- >>>>>>>tba

## 8\. User Interface and Experience Improvements
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

## 9\. Testing, Validation, Documentation, and Extensibility

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

## 10\. Other Considerations
### Performance Considerations
Processing large datasets, especially in a web-based application like Streamlit, can lead to performance bottlenecks.

Recommendations:
- Data Chunking: Process data in chunks to manage memory usage efficiently.
- Asynchronous Processing: Use asynchronous programming to prevent the UI from freezing during long operations.
- Resource Limits: Set limits on the size of files that can be uploaded or provide warnings for large files.

### Streamlit Execution Flow Optimization
Reruns are a central part of every Streamlit app. When users interact with widgets, our script reruns from top to bottom, and our app's frontend is updated. Streamlit provides several features to help us develop our app within this execution model. Streamlit version 1.37.0 introduced fragments to allow rerunning a portion of our code instead of our full script. As our app grows larger and more complex, these fragment reruns help our app be efficient and performant. Fragments give us finer, easy-to-understand control over our app's execution flow.

Streamlit provides a decorator (st.fragment) to turn any function into a fragment function. When we call a fragment function that contains a widget function, a user triggers a fragment rerun instead of a full rerun when they interact with that fragment's widget. During a fragment rerun, only our fragment function is re-executed. Anything within the main body of our fragment is updated on the frontend, while the rest of our app remains the same. 

Please use the decorator "@st.fragment", st.session_state variables, "Refresh" and "Reset" buttons properly on and within UI component functions to optimize the application's execution flow.