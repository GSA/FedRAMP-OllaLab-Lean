# FedRAMP OllaLab - Simple Chat 
## Problem Statement

In interacting with LLMs, the quality of questions directly impacts the quality of answers. Prompt Engineering is all about crafting the best possible questions (prompts). Robust Prompt Engineering will help FedRAMP, GSA members, and all internal/external Stakeholders engage more effectively with LLMs in solving any kind of problems.

Mainstream chat application interfaces such as those provided by OpenAI and Anthropic have all or some of the following limitations:
- Lack of selective inclusion of chat results for more precise context
- Lack of abstraction interface for better content navigation and awareness
- Lack of back-up mechanisms for both prompts and results
- Lack of flexibility in sharing different abstractions of chat results
- Lack of supports for teamwork and convenient reusability

OllaLab - SimpleChat aims to:
1. Improve context building by allowing users to:
  - Selectively save LLM responses to prompt variables
  - Save prompts to prompt variables
  - Automatically extract user-specified local folders and files to prompt variables
  - Embed prompt variables in any fashion in prompts
2. Improve content abstraction with supports for:
  - Prompt variable chaining
  - Prompt variable files containing prompt chains
3. Improve prompt back-up mechanisms by allowing the users to:
  - Save modified prompt versions to prompt variables
  - Commit prompt variable files to versioning platforms like GitHub
4. Provide flexibility in sharing chat results and team collaboration by:
  - Allow convenient share and reuse prompt variables
  - Allow prompt variable file to be shared using existing systems' file sharing features
  - Provide other automation/integration features


## Input Description

User inputs can be provided via:

1. simplechat.yaml file
2. Files copied to a local folder to be loaded by the application
3. Texts typed into the application
4. Texts typed into the prompt variable creation box

## Program Description
The following sections describes the components of the Simple Chat program.

### 1\. Program requirements
- Software dependencies such as needed python packages are saved in the requirements.txt file.
- The program must support Streamlit graphical user interface.
- The program must have a Python API interface.
- Python functions and API interface must support Apache AirFlow.
- >>>>>> << other key requirements here >>

### 2\. Program variables
Program variables are saved in the simplechat.yaml file. The variable details are:
**Local User Values**:
- Local user name (local_user_name): A string specified by the user to represent the user in certain activities and logs. The default value is "anonymous". The recommended value is the user's unique organization email which will provide implicit supports for user name collision avoidance and collaboration.
- Salt (salt): A random string specified by the user to append to data before it is hashed, making the hash more robust to attacks. The default value is "empty".
**LLM values**:
- Maximum context window (context_window): The maximum number of tokens that can be used as input for LLMs. The default value is 128000.
- Prompt size over context window ratio (prompt_ratio): The maximum ratio of number of prompt tokens over context window token. The default value is 0.85.
- Supported LLM platforms (llm_platform): A comma-separated list of supported LLM platforms. The default value is "Ollama, OpenAI, Google Vertex AI, Amazon Bedrock, Anthropic".
- Guard server (guard_server): The url of the LLM guard server. The default value is "empty".
- Monitoring server (monitoring_server): The url of the LangFuse LLM monitoring server. The default value is "empty".
- Selected LLM platform (selected_provider): The LLM platform that the application will leverage. The default value is "Ollama".
- Selected LLM endpoint (selected_endpoint): The LLM endpoint that the application will leverage. The default value is "http://127.0.0.1:11434".
- Allowed OpenAI models (allowed_openai_models): A comma-separated list of allowed OpenAI models. The default value is 'gpt-4o', 'gpt-4o-mini', 'o1-mini', 'o1-preview', 'o1', 'o3'
- Allowed Google Vertex models (allowed_vertex_models): A comma-separated list of allowed Google Vertex models. The default value is "chat-bison@001"
- Allowed AWS Bedrock models (allowed_bedrock_models): A comma-separated list of allowed AWS Bedrock models. The default value is - - Allowed Anthropic models (allowed_anthropic_models): A comma-separated list of allowed Anthropic models. The default value is "anthropic.claude-v2", "ai21.j2-jumbo-instruct"
'claude-3-5-sonnet-latest', 'claude-3-5-haiku-latest', 'claude-3-opus-latest', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'
- LLM model feedback form (feedback_form): The Google form link to collect user feedback.
**Prompt Management Values**:
- promptvariable_filepath: the path to the folder hosting all prompt variable files. The default value is /app/simple_chat/prompt_variables
- promptvariable_autoinclusion: automatically append the newly created prompt variables of types other than "File" and "Question" into the current user's text area. The default value is "True".
- data_filepath: the path to the folder hosting all data folders and files. The default value is /app/simple_chat/data_files
- default_filename: the default name for a json prompt variable file when there is no existing prompt variable file. The default value is "default__promptvariables.json".
- postfix_filename: the text to append to the end of a user-declared file name for a prompt variable file. The default value is "_promptvariables".
- prompt_improvement_instruction: instruction template for getting LLM suggested improvements of any prompt. The default value is:
  ```
  Please check to see if:
  - The purpose and expected outcome can be better defined.
  - There are potential areas for ambiguity elimination by actions such as providing more precise details, examples, or instructions.
  - The focus needs to be narrowed to avoid overly broad or vague responses.
  - A format should be described if there is no format described. If a format is described, check to see if it is the best suitable format if it can be better described.
  - The context can be better defined.
  - There are potential areas for biases and eliminate those potential biases.
  - The prompt can be more concise.
  - Constraints, limitations, and boundaries need to be added to guide the responses more effectively.
  - The content is aligned with the intended topic or goal.
  ```
- prompt_improvement_questions_instructional: quality control questions for instructional prompts. The default value is:
  ```
  - Is the instruction clear and easy to follow?
  - Have I defined the expected format or structure?
  - Did I specify the desired level of detail?
  - Is the task broken into manageable steps?
  - Are there any ambiguities that could confuse the response?
  - Have I included relevant examples for clarity?
  - Did I explain the purpose or goal of the instruction?
  - Is the tone appropriate for the audience?
  - Are unnecessary details removed for simplicity?
  - Would this instruction make sense to someone unfamiliar with the topic?
  ```
- prompt_improvement_questions_interactive: quality control questions for interactive prompts. The default value is:
  ```
  - Does the prompt encourage meaningful engagement?
  - Have I set clear boundaries for the interaction?
  - Is the scenario or game logic easy to understand?
  - Have I clarified the AI’s role in the interaction?
  - Did I specify how long or detailed the responses should be?
  - Is there room for creativity within the interaction?
  - Did I avoid overly rigid instructions that hinder flexibility?
  - Can the interaction adapt to user responses dynamically?
  - Does the prompt ensure a smooth flow of conversation?
  - Could this interaction keep the user engaged over multiple turns?
  ```
- prompt_improvement_questions_comparative: quality control questions for comparative prompts. The default value is:
  ```
  - Have I clearly stated what is being compared?
  - Did I specify the criteria for comparison?
  - Is the comparison limited to relevant aspects?
  - Have I avoided bias in framing the comparison?
  - Does the prompt require a balanced perspective?
  - Is the purpose of the comparison clearly explained?
  - Are there examples to illustrate the comparison?
  - Have I asked for similarities, differences, or both?
  - Is the scope of the comparison manageable and focused?
  - Does the prompt encourage analytical reasoning?
  ```
- prompt_improvement_questions_problem-solving: quality control questions for problem-solving prompts. The default value is:
  ```
  - Is the problem clearly defined and unambiguous?
  - Have I included all relevant details or constraints?
  - Did I specify the type of solution I’m looking for?
  - Is the problem statement concise but comprehensive?
  - Have I ruled out unnecessary complexity?
  - Does the prompt encourage logical reasoning or creativity?
  - Have I provided examples or context if needed?
  - Is the problem solvable with the given information?
  - Did I specify the format of the solution (e.g., steps, code, summary)?
  - Does the prompt avoid leading to a single expected answer?
  ```
- prompt_improvement_questions_exploratory: quality control questions for exploratory prompts. The default value is:
  ```
  - Does the prompt invite open-ended exploration?
  - Have I made the topic or idea clear?
  - Is the scope broad enough for diverse responses?
  - Have I avoided narrowing the focus too early?
  - Does the prompt encourage creativity or brainstorming?
  - Are there examples or hints to spark ideas?
  - Have I clarified the type of output desired (list, narrative, etc.)?
  - Is the prompt free of restrictive assumptions?
  - Did I specify whether the exploration should be speculative or factual?
  - Could this prompt lead to innovative or unique ideas?
  ```
- prompt_improvement_questions_evaluation: quality control questions for evaluation prompts. The default value is:
  ```
  - Is the content being evaluated clearly defined?
  - Have I explained the criteria for evaluation?
  - Is the evaluation prompt free of bias?
  - Did I specify the depth of feedback needed?
  - Have I asked for constructive and actionable feedback?
  - Is the purpose of the evaluation clear?
  - Does the prompt include examples for reference?
  - Have I limited the scope to avoid overwhelming responses?
  - Is the tone neutral and objective?
  - Could the evaluation lead to measurable improvements?
  ```

### 3\. LLM endpoint selection and configuration
**Graphical user interface**
- Display the graphical user interface for LLM endpoint selection and configuration on the side bar. The whole LLM endpoint selection and configuration can be collapsed and is expanded by default.
- Get the list of supported LLM platforms from llm_platform.
- User will be able to configure the main LLM platform and the alternative LLM platform for purposes such as performance comparision.
- For configuring the main LLM platform, first follow the default values for LLM endpoint and check if a connection with the default endpoint can be made. If not, follow the common steps for configuring LLM endpoint.
- Common steps for configuring LLM endpoint
  - Can be applied to configure both the main and the alternative LLM platforms
  - First, ask user to select a platform from a list of supported platforms.
  - For a selected platform, present the user with options to properly configure the platform API.
  - Once connection is successfully established with the selected LLM endpoint, fetch a list of LLMs supported by the platform, allow the user to select which supported LLM model to use.
- At anytime, user can use the interface to change the LLM platform and/or LLMs.
- Use proper mechanisms to sustain/persist user-selected values and configurations until user decide to change them.

**Configuring Ollama**
- The default endpoint is "Localhost": "http://127.0.0.1:11434"
- An alternative endpoint is "Docker Internal": "http://host.docker.internal:8000"
- User also has nother option to input custom Ollama endpoint.
- Once endpoint is configured and confirmed, connect to the endpoint and provide error message if connection is unsuccessful
- Upon successful connection, fetch available models in Olllama. If there is no model available, instruct the user to load at least an LLM in Ollama.
- Upon successfully fetch model, ask the user to select a model.
- Test the model by submiting a prompt. If the model does not respond, display an error message.

**Configuring OpenAI**
- Get openAI API key from the user.
- Load a list of allowed openAI models (allowed_openai_models).
- Fetch available openAI models and only allow the models that are in allowed_openai_models.
- Upon successfully fetch model, ask the user to select a model.
- Test the model by submiting a prompt. If the model does not respond, display an error message.

**Configuring Anthropic**
- Ask the user to input  Anthropic API Key
- Load a list of allowed Anthropic models (allowed_anthropic_models)
- Fetch available openAI models and only allow the models that are in allowed_anthropic_models.
- Upon successfully fetch model, ask the user to select a model.
- Test the model by submiting a prompt. If the model does not respond, display an error message.

**Configuring Google Vertex AI**
- Ask user to input Google Cloud Project ID
- Ask user to input cloud location
- Ask user to upload Service Account JSON Key File
- Initialize the AI platform
- Try to fetch available models from the platform
- Only allow the models that are in allowed_vertex_models
- Upon successfully fetch model, ask the user to select a model.
- Test the model by submiting a prompt. If the model does not respond, display an error message.

**Configuring Amazon Bedrock**
- Ask user to input AWS Access Key ID
- Ask user to input AWS Secret Access Key
- Ask user to input AWS Session Token (optional)
- Ask user to input AWS Region
- Initialize boto3 client
- Fetch available models that are allowed in allowed_bedrock_models
- Upon successfully fetch model, ask the user to select a model.
- Test the model by submiting a prompt. If the model does not respond, display an error message.

### 4\. The main application graphical user interface
The Simple Chat application graphical user interface contains the side bar and the main application graphical user interfaces. The main application graphical user interface can be described as follows:

#### 4a\. The Prompt Composer section
- The Promp Composer section is in the same row with the Prompt Variable Management section and occupies 60% of the row width.
- The title of the section is "Craft a question".
- Below the section title is a text area (multi line input text box) containing user's input for prompt.
- Below the input text area is the Prompt Infomatic Area.
- Below the Prompt Infomatic Area is the Prompt Action Area.
- A user can reference a prompt variable by enclosing the prompt variable name within {{ and }}. A prompt variable contains a chunk of texts which may contain other prompt variables. In such a case, we call the prompt variable is referencing other prompt variables.
- A referenced prompt variable may or may not exist in a selected prompt variable file. If a referenced prompt variable does not exist, it will be shown in the Prompt Infomatic Area.
- No special character is allowed in the text area except for {,},$,&,%,(,),+,-,=,*,/.
- **Prompt Infomatic Area**
  - Context window: display the context window size in tokens from context_window
  - Prompt tokens (prompt_tokens): display the total token number based on all texts within the user input prompt, and the texts in all of the prompt variables referenced by the prompt and the referencing prompt variables. The user input prompt token number is updated as user types the prompt. The prompt variable token number is updated after the related prompt variable(s) is modified and saved.
  - Prompt size warning: Warn user if prompt_tokens/context_window is greater than the specified prompt_ratio. 
  - Empty variables: display the name of referenced prompt variables that are empty or non-exist. If an empty variable is referenced by parent prompt variables, display the the prompt chain. For example, if an empty var3 is referenced by var2 which was referenced by var1, then var3 should be displayed at var1 > var2 > var3.
  - Token integrity: display "Pass" or "Fail". Display "Pass" if there is no token failing the integrity check.
- **Prompt Action Area**
  - Run prompt: a button for user to send the prompt to the LLM. This button should have the color Green.
  - Improve prompt: a button for user to ask LLM for potential prompt improvements. Click this button will open the prompt improvement graphical user interface.
  - Save prompt: a button for user to save prompt to a prompt variable. Click this button will open the Prompt variable creation from prompt graphical user interface.
  - All these buttons should be in the same row.
- **Prompt variable creation from prompt graphical user interface**
  - The prompt variable creation from prompt graphical user interface is within a modal dialog.
  - Ask the user to input variable name.
  - The prompt variable type will be "Question".
  - Follow section 6\. Promp Variable Management for procedures to properly create the prompt variable of "Question" type.
  - Display error or informational message to the user.
  - Allow the user to close out the prompt variable creation interface.
- **Prompt improvement graphical user interface**
  - The prompt improvement graphical user interface is within a modal dialog.
  - Ask user to clarify which type is the user's prompt by selecting one type from a list of supported prompt types which are:
    - Instructional: user prompt instructs the AI to perform a task, answer to a question, or generate specific content
    - Interactive: user prompt creates a back-and-forth interaction
    - Comparative: user prompt compares two or more ideas, concepts, or items
    - Problem solving: user prompt tries to solve a relatively complex problem (more complex than instructional prompt)
    - Exploratory: user prompt is trying to explore ideas or brainstorm a solution
    - Evaluation: user prompt asks the AI to provide constructive feedback or evaluate content
  - Suggest Prompt Improvements: this is a button which executes the following upon click:
    - Load prompt_improvement_instruction to the `prompt_improvement_instruction` program variable.
    - Load quality control questions for the selected prompt type to the `prompt_improvement_questions` program variable.
    - Load current text area input text box content to the `user_prompt` program variable.
    - Build a prompt improvement prompt with the following
      ```
      We have the following prompt:
      `user_prompt`

      Please improve the prompt using the following prompt improvement instructions:
      `prompt_improvement_instruction`
      while thinking carefully about the following questions:
      `prompt_improvement_questions`
      ```
    - Send the prompt improvement prompt to the main LLM for response.
    - Close out of the modal dialog so that the user can see the LLM's response.

#### 4b\. The Prompt Variable Management section
- The title of the section is "Prompt Variable Management".
- Below the title is a prompt variable file selection box with the default prompt variable file selected.
- Below the prompt variable file selection box are Prompt variable display tabs.
- Click any of the displayed variables will open up the View/update prompt variable interface.
- Below the prompt variable display tabs is a row of "New prompt variable" and "Clone prompt variable" buttons.
- Clicking the "New prompt variable" button will open the Create prompt variable interface.
- Clicking the "Clone prompt variable" button will open the Clone prompt variable interface.
- **Prompt variable types**
  - Question: the variable of this type was created from user's question. It should contain an inquiry.
  - Answer: the variable of this type was created from an LLM's answer. It should not contain an inquiry.
  - File: variables of this type was automatically created by crawlwing a user-specified local directory.
  - Web: the variable of this type was created from extracting content from a user-specified website. 
  - API: the variable of this type was created from extracting content from a user-specified API request.
- **Prompt variable file selection box**:
  - Prompt variable files are loaded, ordered alphabetically and displayed within a drop down box in the application side bar. User selects one prompt variable file to use.
  - When a new prompt variable file was successfully created and saved, update the drop down box.
  - User can click the "Create new prompt variable file" button to create new prompt variable file. Once clicked, a streamlit dialog box appears with options for user to create a new prompt file (see section 5\. Promp Variable File Management for more details).
- **Prompt variable display tabs**
  - There are tabs of "Questions", "Answers", "Files", "Web sites", and "APIs" respectively display prompt variables of type Question, Answer, File, Web, and API.
  - Each prompt variable is displayed as a button. Upon click, the View/update prompt variable interface is displayed.
  - In each tab, prompt variables are displayed in rows of maximum 3 prompt variables per row.
  - In each tab, prompt variable rows will be put inside a collapsed expander entitled "Expand to see prompt variables" when the number of rows exceed 4.
- **View/update prompt variable interface**
  - The View/update prompt variable interface is within a modal dialog.
  - Display the components of the prompt variable.
  - Display Integrity check result.
  - Display Dependency check
  - Display a row of "Update" and "Close" buttons.
  - If "Close" is clicked, close out the modal dialog.
  - Display the Update prompt variable option appropriate for the prompt variable type. The detailed processes are in section 6\. Promp Variable Management.
- **Create prompt variable interface**
  - The Create prompt variable interface is within a modal dialog.
  - Support the creation of "Questions", "Answers", "Web sites", and "APIs" variables.
  - Ask the user to select which type of prompt to be created.
  - Provide the input options necessary for user to type in values for certain prompt variable components.
  - Follow the type-specific prompt variable creation processes described in section 6\. Promp Variable Management.
  - Provide a "Create variable" button. Upon click, the variable will be properly saved and the modal dialog will be closed out.
- **Clone prompt variable interface**
  - The Clone prompt variable interface is within a modal dialog.
  - Ask the user to type in the name of the of the variable to be cloned (variable_A).
  - Check to see if variable_A exist within the current namespace and is not empty. If varible_A does not exist or is empty, ask the user to type another name for variable_A
  - Ask the user to type in the name of the new variable (variable_B).
  - Check to see if variable_B exist within the current namespace. If variable_B exist, ask the user tro type another name for variable_B.
  - If both the names for variable_A and variable_B are good to go, display the "Clone variable" button.
  - Once the "Clone variable" button is clicked, save variable_A with variable_B name and close out the interface.
#### 4c\. The LLM Response Section
- The section has a title of "LLM Response(s)"
- Below the title, there is a "Performance comparision" check box. By default, this box is unchecked and there is only one "LLM Response sub-section" using the main LLM platform and its selected model. Once the box is checked, there is another "LLM Response sub-section" displayed next to the earlier one, using the alternate LLM platform and its selected model.
- **LLM Response sub-sections**:
  - Display LLM response texts to the sent prompt.
  - Display "Save response to prompt variable" button. Once clicked, it opens the Create prompt variable interface with the prompt type of "Answer" preselected.
#### 4d\. User feedback Section**
- This section has the title of "Giving feedback"
- Read the feedback form url from feedback_form
- Integrate the form and display it.

### 5\. Promp Variable File Management
**Create new prompt variable file**:
- Ask user to put in the prompt variable file name.
- If the file already exists, ask the user for another name.
- Ask the user to set a custom namespace (optional). The default namespace is a combination of `prompt variable file name` and `local user name`.
- User will then be able to choose whether to create a new blank file or from an existing prompt variable file.
- If user chose to create a new file from an existing prompt variable file, allow the user to chose which file.
- A prompt variable file begins with the namespace information (namespace key) to be followed by prompt variable details.
- Save the file to the prompt variable folder (promptvariable_filepath)
**Load and save prompt variable files**:
- User selects a prompt variable file name (json file)
- Load the file from the prompt variable folder (promptvariable_filepath)
- When saveing a prompt varible file, saves the file as a json with indent=4 to the prompt variable folder (promptvariable_filepath)

### 6\. Promp Variable Management
**Components of a prompt variable**
- Variable name: the name of the variable, must be all lower case with no space, must have no special character. Except for variables of type "File", variable names must not have leading numbers and must not be more than 12 characters.
- Variable author: the user who created the variable (local_user_name)
- Variable type: the variable's type
- Variable content: the value to of the variable with one or more of the following sub values
  - Texts: the textual content assigned to the variable.
  - Size: the number of tokens from the Texts.
  - Source: the source of the Texts. For the "Question" type, this value is the local_user_name. For the "Answer" type, this value is the user selected LLM model within the user selected LLM platform. For the "File" type, this value is the path to a folder or a file. For the "Web" type, this value is a url. For the "API" type, this value is the API endpoint.
- Creation time: The time when the prompt variable was first created.
- Latest time: The time when the prompt variable was last updated. The default value is the Creation time.
- Hash: The hash of the content of Variable value - Texts and Salt.
- Update logs: A comma-separated list of time values. The default value is the Creation time. 
**Prompt variable types**
- Question: the variable of this type was created from user's question. It should contain an inquiry.
- Answer: the variable of this type was created from an LLM's answer. It should not contain an inquiry.
- File: variables of this type was automatically created by crawlwing a user-specified local directory.
- Web: the variable of this type was created from extracting content from a user-specified website. 
- API: the variable of this type was created from extracting content from a user-specified API request.
**Prompt variable naming and renaming**
- Namespace is used to make sure there is no collision in prompt variable names.
- A user can manually set a custom namespace. In this case, few prompt variable files may share the same custom namespace.
- A user can only rename the prompt variables that s/he authored, within the namespace that the variable resides.
- Once a renaming is confirmed, the variable name will be changed and updated in all places where other variables referenced the variable within the same namespace.
**Create prompt variables of "File" type**
- Variable name:
  - The variable name is based on the file name without the file extension.
  - If the file name is more than 11 characters, the variable name is `first 5 characters of the file name`_`last 2 characters of the file name`.`the file extension`
  - If the file name is less than 12 characters, the variable name is `the file name`.`the file extension`
- The process is initiated automatically when user opens the application and is independent from the user's selected prompt variable file.
- Read and traverse all folders and files including shortcuts or symbolic links within data_filepath.
- Create a prompt variable for each folder follwing the format of `folder level`_`folder name`_folder. The folder level number starts with 1 (top level) and reflects the folder level in the overall folder hierarchy within data_filepath.
- Create a prompt variable for each file follwing the format of `folder level`_`file name`. The folder level value is the same folder level value of the folder hosting the files.
- Supported file types are txt, rtf, wps, pdf, doc, docx, xls, tiff, xml, htm, html, .msg, .wpd.
- The variables are saved to memory, not to any prompt variable file.
- Save the variable with the following additional values:
  - Variable value:
    - Texts: 
      - If it is a folder, the texts include the variables representing the folders and/or files within the folder.
      - If it is a file, the texts include the textual content of the file following this template:
        ```
        My current `file name` is:
        `extracted textual content of the file`
        ```
      - If it is a file, the textual content is extracted only when the variable was referenced by a user prompt or by another variable at run time. Before that, the default value is "pending extraction"
    - Source: The path to the folder or the file
  - Creation time: The time right before the variable was first saved to a variable file.
  - Latest time: The time right after the Texts were successfuly extracted and the variable is successfully updated. The default value is the Creation time.
  - Hash: The hash of the content of Variable value - Texts and Salt.
  - Update logs: when there is a new "Latest time" value, append the value to this updated logs comma-separated list.
**Create prompt variables of "Web" type**
- Ask user to put in the name of the variable.
- User can optionally provide multiple div tags.
- Crawl and extract a website content using user-provided url and the optional div tags. If div tags are provided, only extract html content within the div tags.
- Clean up the extracted texts.
- Create a Source object that contains the  user-provided url and the optional div tags. The program can later use this Source object to revisit the website and extract the contents again.
- Create a prompt variable of type "Web" with the user-provided variable name.
- Save the variable with the following additional values
  - Variable value:
    - Texts: the cleaned up extracted texts
    - Source: the Source object
  - Creation time: The time right before the variable was first saved to a variable file.
  - Latest time: The time when the url was last visited, its content was successfully extracted, and the variable is successfully updated. The default value is the Creation time.
  - Hash: The hash of the content of Variable value - Texts and Salt.
  - Update logs: when there is a new "Latest time" value, append the value to this updated logs comma-separated list.
- Upon successful saving, append the variable name enclosed within {{ and }} to the user's current text area if promptvariable_autoinclusion is True.
**Create prompt variables of "API" type**
- Ask user to put in the name of the variable.
- Present the user with the options to establish the API connection and query per further details provided in section 7\. External API Integration. 
- A successful API query should return a query object and a result object.
- The query object contains all details needed to repeat the same API call again.
- The result object will be parsed and converted to API texts.
- Save the variable with the following additional values
  - Variable value:
    - Texts: the cleaned up API texts
    - Source: the API query object
  - Creation time: The time right before the variable was first saved to a variable file.
  - Latest time: The time when the API query object was last executed. The default value is the Creation time.
  - Hash: The hash of the content of Variable value - Texts and Salt.
  - Update logs: when there is a new "Latest time" value, append the value to this updated logs comma-separated list.
  - Upon successful saving, append the variable name enclosed within {{ and }} to the user's current text area if promptvariable_autoinclusion is True.
**Create prompt variables of Question or Answer types**
- Ask user to put in the name of the variable.
- Save the variable with the following additional values
  - Variable value:
    - Texts: This text is copied over from the user prompt text area (if creating a Question prompt variable) or from the LLM response texts (if creating an Answer prompt variable). The user is able to make correction and/or addition to the texts.
    - Source: the user (if creating a Question prompt variable) or the selected LLM model (if creating an Answer prompt variable)
  - Creation time: The time right before the variable was first saved to a variable file.
  - Latest time: The last time the variable was saved to a variable file. The default value is the Creation time.
  - Hash: The hash of the content of Variable value - Texts and Salt.
  - Update logs: when there is a new "Latest time" value, append the value to this updated logs comma-separated list.
- Upon successful saving of "Answer" type variable, append the variable name enclosed within {{ and }} to the user's current text area if promptvariable_autoinclusion is True.
**Integrity check**
- Can only be performed by the author of the variables. Assuming the salt is well-kept in secret by each user, each user can verify if the user indeed authored a variable and if the content of the variable was changed.
- Read the Variable value - Texts of a selected variable within a prompt variable file.
- Append the user's salt to the Texts.
- Hash the appended result.
- Compare the hash result with the prompt variable's hash.
- Integrity check is passed if the two hash values are the same.
**Dependency check**
- To be performed when a prompt variable is referenced by the user. The prompt variable can be referenced by other parent prompt variables and/or referencing other child prompt variables in its Variable value - Texts.
- The Dependency Check will check and report any identified issues with both parent and child prompt variables.
- The potential issues to be checked are:
  - The parent/child variables do not exist.
  - The parent/child variables are empty.
  - The parent/child variables reference prompt variables that are either empty or do not exist. 
**Update prompt variables of "File" type**
- This process is done automatically each time a prompt variable of "File" type is referenced by the user's prompt.
- The "File" type variable value is updated following the same process in Create prompt variables of "File" type.
- Only update the variable and its child variables when there are changes in folder structures, folder/file names, folder/file contents.
**Update prompt variables of "Web" type**
- In the View/update prompt variable interface, when user click the "Update" button, the Variable value - Source object will be parsed. The application will visit the website and perform proper content extraction of either the whole website or the content within the div tags.
- If there are issues, report the issues to user and do not update the Variable value - Texts.
- Potential issues are:
  - Website refuses to serve the expected content.
  - Website requires bot verification.
  - Website is temporarily unavailable.
  - Website takes too long to load.
  - The specified div tags are no longer available.
- If there is no issue, update the variable with the following:
  - Variable value:
    - Texts: will be updated if the extracted texts are different from the existing texts.
    - Source: the Source object should remain the same.
  - Creation time: remain the same
  - Latest time: The time immediately before the variable was updated on the variable file.
  - Hash: The hash of the content of newly extracted Variable value - Texts and Salt.
  - Update logs: Append the Latest time
**Update prompt variables of "API" type**
- In the View/update prompt variable interface, when user click the "Update" button, the Variable value - Source object (the API query object) will be parsed. Based on the parsed result, the application will properly connect to the API endpoint and query the endpoint to gather a result object.
- If there are issues, report the issues to user and do not update the Variable value - Texts.
- Potential issues are:
  - Authentication and authorization issues.
  - Request formating errors which can happen due to changes/upgrades on the API host.
  - Network issues such as connnection timeout.
  - Exceeded API rate limit.
  - API deprecation or changes.
  - Data related issues such as requesting too much data in a single query.
- If there is no issue, update the variable with the following:
- Variable value:
  - Texts: the updated cleaned up API texts
  - Source: remain the same
- Creation time: remain the same
- Latest time: The time immediately before the variable was updated on the variable file.
- Hash: The hash of the content of newly extracted Variable value - Texts and Salt.
- Update logs: Append the Latest time
**Update prompt variables of Question or Answer types**
- In the View/update prompt variable interface, the user is able to make changes to the variable Value - Texts box.
- After the user made the changes and when user click the "Update" button, update the variable with the following values
  - Variable value:
    - Texts: the user updated texts
    - Source: remain the same
  - Creation time: remain the same
  - Latest time: The time immediately before the variable was updated on the variable file.
  - Hash: The hash of the content of newly extracted Variable value - Texts and Salt.
  - Update logs: Append the Latest time

### 7\. External API Integration
- tba
#### 7a\. Threat Intelligence
- **Government Sources**
  - National Vulnerability Database 	U.S. National Vulnerability Database https://nvd.nist.gov/vuln/Data-Feeds/JSON-feed-changelog
  - 
- **Industry Sources**
  - AlienVault Open Threat Exchange (OTX) 	https://otx.alienvault.com/api 	IP/domain/URL reputation 	FREE
  - FullHunt 	Searchable attack surface database of the entire internet https://api-docs.fullhunt.io/#introduction
  - PhishStats 	Phishing database https://phishstats.info/#apidoc
  - Spamhaus https://www.spamhaus.com/product/intelligence-api/
  - Cisco PSIRT https://developer.cisco.com/psirt/
- **Community Sources**
  - [Bugcrowd](https://docs.bugcrowd.com/api/getting-started/) 	Bugcrowd API for interacting and tracking the reported issues programmatically
  - HackerNews 	https://github.com/HackerNews/API 	Social news for CS and entrepreneurship 	FREE
  - Bing Web Search API 	https://www.microsoft.com/en-us/bing/apis/bing-web-search-api 	Search in Bing (+instant answers and location) 	1000 transactions per month FREE
  - Google Custom Search JSON API 	https://developers.google.com/custom-search/v1/overview 	Search in Google 	100 requests FREE

#### 7b\. Malware
- VirusTotal 	https://developers.virustotal.com/reference 	files and urls analyze 	Public API is FREE
- Malpedia - https://malpedia.caad.fkie.fraunhofer.de/usage/api
#### 7c\. Network Intelligence
- **Network Operations**
  - Shodan 	Search engine for Internet connected devices
  - Cloudflare Trace 	https://github.com/fawazahmed0/cloudflare-trace-api 	Get IP Address, Timestamp, User Agent, Country Code, IATA, HTTP Version, TLS/SSL Version & More 	FREE
  - Shodan 	https://developer.shodan.io 
  - Censys.io 	https://censys.io/api
  - Host.io 	https://host.io/ 	Get info about domain 	FREE
  - BeVigil OSINT API 	https://bevigil.com/osint-api 	provides access to millions of asset footprint data points including domain intel, cloud services, API information, and third party assets extracted from millions of mobile apps being continuously uploaded and scanned by users on bevigil.com 	50 credits free/1000 credits/$50
  - EVA 	https://eva.pingutil.com/ 	Measuring email deliverability & quality 	FREE
  - Kickbox 	https://open.kickbox.com/ 	Email verification API 	FREE
  - FachaAPI 	https://api.facha.dev/ 	Allows checking if an email domain is a temporary email domain 	FREE
- **Network Archive**
  - Wayback Machine API (Memento API, CDX Server API, Wayback Availability JSON API) 	https://archive.org/help/wayback_api.php 	Retrieve information about Wayback capture data 	FREE
  - TROVE (Australian Web Archive) API 	https://trove.nla.gov.au/about/create-something/using-api 	Retrieve information about TROVE capture data 	FREE
  - UK Web Archive API 	https://ukwa-manage.readthedocs.io/en/latest/#api-reference 	Retrieve information about UK Web Archive capture data 	FREE
  - Library Of Congress archive API 	https://www.loc.gov/apis/ 	Provides structured data about Library of Congress collections 	FREE
  - BotsArchive 	https://botsarchive.com/docs.html 	JSON formatted details about Telegram Bots available in database 	FREE
- **Crypto Networks**
  - BTC.com 	https://btc.com/btc/adapter?type=api-doc 	get information about addresses and transanctions 	FREE
  - Bitcointabyse 	https://www.bitcoinabuse.com/api-docs 	Lookup bitcoin addresses that have been linked to criminal activity 	FREE
  - Bitcoinwhoswho 	https://www.bitcoinwhoswho.com/api 	Scam reports on the Bitcoin Address 	FREE
  - Etherscan 	https://etherscan.io/apis 	Ethereum explorer API 	FREE
  - BlockFacts 	https://blockfacts.io/ 	Real-time crypto data from multiple exchanges via a single unified API, and much more 	FREE
  - Brave NewCoin 	https://bravenewcoin.com/developers 	Real-time and historic crypto data from more than 200+ exchanges 	FREE
  - WalletLabels 	https://www.walletlabels.xyz/docs 	Labels for 7,5 million Ethereum wallets 	FREE

#### 7d\. News and Geo-Political Intelligence
- **Cybersecurity News**
  - tba
- **US Government News**
  - tba
  - sources on policies and legislation?
  - FDIC Bank Data API 	https://banks.data.fdic.gov/docs/ 	institutions, locations and history events 	FREE
- **World News**
  - tba
- **Geo-Social-Intelligence**
  - Linkedin company search API 	https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/organizations/company-search?context=linkedin%2Fcompliance%2Fcontext&tabs=http 	Find companies using keywords, industry, location, and other criteria 	FREE
  - US Street Address 	https://smartystreets.com/docs/cloud/us-street-api 	Validate and append data for any US postal address 	FREE
  - Zipcodebase 	https://zipcodebase.com 	Lookup postal codes, calculate distances and much more 	5000 requests FREE
  - Veriphone 	https://veriphone.io/ 	Phone number validation & carrier lookup 	1000 requests/month FREE
  - Twillo 	https://www.twilio.com/docs/lookup/api 	Provides a way to retrieve additional information about a phone number 	Free or $0.01 per request (for caller lookup)
  - Ipstack 	https://ipstack.com 	Detect country, region, city and zip code 	FREE
  - Alpaca 	https://alpaca.markets/docs/api-documentation/api-v2/market-data/alpaca-data-api-v2/ 	Realtime and historical market data on all US equities and ETFs 	FREE
  - Genderize.io 	https://genderize.io 	Instantly answers the question of how likely a certain name is to be male or female and shows the popularity of the name. 	1000 names/day free
  - Nataonalize.io 	https://nationalize.io 	Predicts the nationality of a person given their name 	1000 names/day free

#### 7e\. Social Networks
- Twitter API 	https://developer.twitter.com/en 		
- Linkedin API 	https://docs.microsoft.com/en-us/linkedin/ 		
- All Facebook and Instagram API 	https://developers.facebook.com/docs/
- Reddit 	https://www.reddit.com/dev/api/
- Telegram and Telegram Bot API 	https://core.telegram.org 		
- Weibo API 	https://open.weibo.com/wiki/API文档/en 		
- XING 	https://dev.xing.com/partners/job_integration/api_docs 		
- Viber 	https://developers.viber.com/docs/api/rest-bot-api/ 		
- Discord 	https://discord.com/developers/docs
- Blogger 	https://developers.google.com/blogger/ 	The Blogger APIs allows client applications to view and update Blogger content 	FREE
- Disqus 	https://disqus.com/api/docs/auth/ 	Communicate with Disqus data 	FREE
- Foursquare 	https://developer.foursquare.com/ 	Interact with Foursquare users and places (geolocation-based checkins, photos, tips, events, etc) 	FREE
- Kakao 	https://developers.kakao.com/ 	Kakao Login, Share on KakaoTalk, Social Plugins and more 	FREE
- Line 	https://developers.line.biz/ 	Line Login, Share on Line, Social Plugins and more 	FRE
- Social Links 	https://sociallinks.io/products/sl-api (paid)

#### 7f\. Research & Development
- tba

### 8\. LLM Monitoring and Guard
- >>>>>>>tba - decorator based

### 9\. Supports for API Interface
- The python code must support the building of a robust API interface based on FastAPI and Kong Gateway.
- The API will be RESTful.
- The API can be divided into service categories.
- The API uses OpenAPI specification.
- >>>>>>>tba

### 10\. Supports for Apache AirFlow
- >>>>>>>tba

### 11\. Supports for Cybersecurity Continuous Monitoring
#### a\. Continuous Penetration testing of AI features
**Executable benchmarks**
- >>>>>>>tba - benchmark datasets (including benchmarking guard and security features) for both local and cloud based LLMs
**Agent-based penetration testing**
- >>>>>>>tba - API for continuous automatic agent-based penetration testing
#### b\. Continuous Penetration testing of non-AI features
**Unit Testing**
- Develop unit tests for each function and component.
- Use test-driven development practices where feasible.
**Performance Testing**
- Evaluate performance with datasets of varying sizes and complexities.
- Optimize algorithms based on profiling results.
- >>>>>>>tba - test cases, web-based pen-test, etc.
#### c\. Compliance checks
- >>>>>>>tba - how to generate structured compliance details from program codes and documentations

### 12\. User Interface and Experience Improvements
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

### 13\. Testing, Validation, Documentation, and Extensibility
**To ensure reliability and future-proofing:**
- Extensibility:
  - Design the system to handle multiple datasets beyond just two.
  - Support additional data formats (e.g., JSON, XML) and database connections.
  - Modularize components to allow for easy updates and feature additions.

**To aid users and developers:**
- Comprehensive Documentation:
  - Provide professional github md files.
  - Provide a detailed user manual with step-by-step instructions.
  - Include technical documentation for developers, outlining system architecture and codebase.
  - Use Swagger UI for API documentation.
  - >>>>>>>>>>>>> TBA
- Logging and Auditability:
  - Implement detailed logging of user actions and system processes.
  - Store logs securely and provide access for audit purposes if needed.
  - Provide robust undo and revert options can be challenging to implement effectively.
- Support Resources:
  - Offer support channels such as email, chat, or forums.
  - Regularly update documentation with FAQs and troubleshooting tips.

### 14\. Other Considerations
**Performance Considerations**
Processing large datasets, especially in a web-based application like Streamlit, can lead to performance bottlenecks.

Recommendations:
- Data Chunking: Process data in chunks to manage memory usage efficiently.
- Asynchronous Processing: Use asynchronous programming to prevent the UI from freezing during long operations.
- Resource Limits: Set limits on the size of files that can be uploaded or provide warnings for large files.

**Streamlit Execution Flow Optimization**
Reruns are a central part of every Streamlit app. When users interact with widgets, our script reruns from top to bottom, and our app's frontend is updated. Streamlit provides several features to help us develop our app within this execution model. Streamlit version 1.37.0 introduced fragments to allow rerunning a portion of our code instead of our full script. As our app grows larger and more complex, these fragment reruns help our app be efficient and performant. Fragments give us finer, easy-to-understand control over our app's execution flow.

Streamlit provides a decorator (st.fragment) to turn any function into a fragment function. When we call a fragment function that contains a widget function, a user triggers a fragment rerun instead of a full rerun when they interact with that fragment's widget. During a fragment rerun, only our fragment function is re-executed. Anything within the main body of our fragment is updated on the frontend, while the rest of our app remains the same. 

Please use the decorator "@st.fragment", st.session_state variables, "Refresh" and "Reset" buttons properly on and within UI component functions to optimize the application's execution flow.