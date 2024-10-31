app_version = "0.2"
app_title = "OllaLab - Simple Chat"
app_description = "A simple chat application with your selected LLM."
app_icon = ":robot_face:"

import os
import streamlit as st
import requests
import ollama
from ollama import Client
import glob
import json
from datetime import datetime
import time
import re
import shutil

# Streamlit application configuration
st.set_page_config(
    page_title=app_title,
    page_icon=app_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application Header
st.title(app_title)
st.write(app_description)

# Initialize session state
if 'prompt_variable_file' not in st.session_state:
    st.session_state['prompt_variable_file'] = None
if 'variable_source' not in st.session_state:
    st.session_state['variable_source'] = ''
if 'full_response' not in st.session_state:
    st.session_state['full_response'] = ''
if 'show_create_file_modal' not in st.session_state:
    st.session_state['show_create_file_modal'] = False
if 'show_create_var_from_prompt' not in st.session_state:
    st.session_state['show_create_var_from_prompt'] = False
if 'show_create_var_from_response' not in st.session_state:
    st.session_state['show_create_var_from_response'] = False
if 'current_variable_name' not in st.session_state:
    st.session_state['current_variable_name'] = ''
if 'show_duplicate_file_modal' not in st.session_state:
    st.session_state['show_duplicate_file_modal'] = False


# Check for existing prompt variable files
prompt_variable_files = glob.glob('*_promptvariables.json')

if not prompt_variable_files:
    # No existing prompt variable files, create default
    default_file = 'default_promptvariables.json'
    with open(default_file, 'w') as f:
        json.dump({}, f)
    prompt_variable_files.append(default_file)

# Function to load prompt variables from a file
def load_prompt_variables(file_name):
    try:
        with open(file_name, 'r') as f:
            data = json.load(f)
        return data
    except:
        return {}

# Function to save prompt variables to a file
def save_prompt_variables(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

@st.dialog("Create New Prompt Variable File")
def create_new_prompt_variable_file():
    new_file_name = ""
    new_file_name_input = st.text_input("Enter new prompt variable file name (without extension)")
    create_file_submit = st.button("Create file")
    if create_file_submit:
        new_file_name = f"{new_file_name_input}_promptvariables.json"
        if new_file_name not in prompt_variable_files:
            # Create new file
            with open(new_file_name, 'w') as f:
                json.dump({}, f)
            st.success(f"Created new prompt variable file: {new_file_name}")
            st.session_state['show_create_file_modal'] = False
        else:
            st.warning("File already exists.")
    return new_file_name

@st.dialog("Prompt Variable Details")
def view_prompt_variable(var_name, var_data):
    st.write(f"**Variable Name:** {var_name}")
    st.write(f"**Number of Tokens:** {var_data.get('num_tokens', 'N/A')}")
    st.write(f"**Timestamp:** {var_data.get('timestamp', 'N/A')}")
    st.text_area("Variable Value:", value=var_data.get('value', ''), height=200)

with st.sidebar:
    # Sidebar for Ollama Endpoint Selection
    st.header("Chat Endpoint")

    # Predefined endpoints
    default_endpoints = {
        "Docker Internal": "http://host.docker.internal:8000",
        "Localhost": "http://127.0.0.1:11434",
        "Other": ""
    }

    endpoint_option = st.selectbox(
        "Select Ollama Endpoint",
        options=list(default_endpoints.keys()),
        index=1  # Default selection is "Localhost"
    )

    if endpoint_option == "Other":
        custom_endpoint = st.text_input("Enter Ollama Endpoint URL", value="http://")
        selected_endpoint = custom_endpoint
    else:
        selected_endpoint = default_endpoints[endpoint_option]

    # Set OLLAMA_HOST environment variable
    if selected_endpoint:
        os.environ['OLLAMA_HOST'] = selected_endpoint

        # Fetch available models
        try:
            models_response = requests.get(f"{selected_endpoint}/v1/models")
            if models_response.status_code == 200:
                available_models_data = models_response.json()
                # assume the response contains a list of models under 'data' key
                model_names = [model['id'] for model in available_models_data.get('data',[])]
                if not model_names:
                    st.error("No model available for the selected endpoint.")
                    st.stop()
            else:
                st.error(f"Failed to retrieve models - status code {models_response.status_code}")
                st.stop()
        except Exception as e:
            st.error(f"Error connecting to Ollama endpoint: {e}")
            st.stop()
    else:
        st.error("Please select or enter a valid Ollama endpoint.")
        st.stop()

    selected_model = st.selectbox(
        "Choose a Model",
        options=model_names,
        index=0
    )

# Handle Create Prompt Variable Modal
@st.dialog("Create Prompt Variable")
def create_prompt_variable(content, origin):
    variable_name = st.text_input("Enter variable name:")
    variable_value = st.text_area("Variable content:",content)
    submit = st.button("Save Variable")
    if submit:
        # Load existing variables
        prompt_variable_file = st.session_state['prompt_variable_file']
        prompt_variables = load_prompt_variables(prompt_variable_file)
        if variable_name in prompt_variables:
            st.error("Variable name already exists. Please choose another name.")
        else:
            # Calculate number of tokens
            num_tokens = len(variable_value.split())
            # Get current time
            current_time = datetime.now().isoformat()
            # Save variable with metadata
            prompt_variables[variable_name] = {
                'value': variable_value,
                'num_tokens': num_tokens,
                'timestamp': current_time,
                'origin': origin
            }
            save_prompt_variables(prompt_variable_file, prompt_variables)
            st.success(f"Variable '{variable_name}' saved successfully.")

            if (origin=="response"):
                st.session_state['show_create_var_from_response'] = False
            else:
                st.session_state['show_create_var_from_prompt'] = False

@st.dialog("Duplicate Prompt Variable File")
def duplicate_prompt_variable_file():
    file_to_duplicate = st.selectbox("Select a file to duplicate", options=prompt_variable_files)
    new_file_name_input = st.text_input("Enter new file name (without extension)")
    duplicate_submit = st.button("Duplicate")
    if duplicate_submit:
        new_file_name = f"{new_file_name_input}_promptvariables.json"
        if new_file_name in prompt_variable_files:
            st.warning("File with this name already exists.")
        else:
            shutil.copy(file_to_duplicate, new_file_name)
            st.success(f"File duplicated to {new_file_name}")
            st.session_state['show_duplicate_file_modal'] = False
            prompt_variable_files.append(new_file_name)

# Sidebar for Prompt Variable File Selection
with st.sidebar:
    st.header("Prompt Variables")

    if st.button("Create New Prompt Variable File"):
        st.session_state['show_create_file_modal'] = True
        st.session_state['show_duplicate_file_modal'] = False
        st.session_state['show_create_var_from_prompt'] = False
        st.session_state['show_create_var_from_response'] = False

    if st.session_state.get('show_create_file_modal', False):
        new_file = create_new_prompt_variable_file()
        prompt_variable_files.append(new_file)

    if st.button("Duplicate a Prompt Variable File"):
        st.session_state['show_duplicate_file_modal'] = True
        st.session_state['show_create_file_modal'] = False
        st.session_state['show_create_var_from_prompt'] = False
        st.session_state['show_create_var_from_response'] = False

    if st.session_state.get('show_duplicate_file_modal', False):
        duplicate_prompt_variable_file()

    # Option to select existing prompt variable file
    selected_file = st.selectbox("Select Prompt Variable File", options=prompt_variable_files)
    st.session_state['prompt_variable_file'] = selected_file

    # Load prompt variables from the selected file
    prompt_variables = {}
    if st.session_state.get('prompt_variable_file'):
        prompt_variables = load_prompt_variables(st.session_state['prompt_variable_file'])
    else:
        prompt_variables = {}

# Input text from user
st.subheader("Enter your prompt:")
user_input = st.text_area("")

col1, col2, col3 = st.columns([2,3,5])
with col1:
    generate_response = st.button("Generate Response")
with col2:
    if st.button("Create Prompt Variable from This Prompt"):
        create_prompt_variable(user_input,"prompt")
with col3:
    if st.button("Create Prompt Variable from Recent Response"):
        create_prompt_variable(st.session_state['full_response'],"response")

# Prompt variables display
if st.session_state.get('prompt_variable_file'):
    prompt_variables = load_prompt_variables(st.session_state['prompt_variable_file'])
    if prompt_variables:
        with st.expander("PROMPT VARIABLES", expanded=False):
            cols = st.columns(3)
            for idx, var_name in enumerate(prompt_variables.keys()):
                col = cols[idx % 3]
                if col.button(var_name):
                    # Launch View Prompt Variable Modal
                    prompt_variable_file = st.session_state['prompt_variable_file']
                    prompt_variables = load_prompt_variables(prompt_variable_file)
                    var_data = prompt_variables.get(var_name, {})
                    view_prompt_variable(var_name, var_data)

    else:
        st.write("No variable in the current file.")
else:
    st.write("No prompt variable file selected.")
    
ollama_client = Client(host=selected_endpoint)

if generate_response:
    if user_input:
        try:
            # Process prompt variables in user_input
            pattern = r"\{\{(\w+)\}\}"
            variable_names = re.findall(pattern, user_input)
            missing_vars = []
            for var in variable_names:
                if var in prompt_variables:
                    user_input = user_input.replace(f"{{{{{var}}}}}", prompt_variables[var]['value'])
                else:
                    user_input = user_input.replace(f"{{{{{var}}}}}", "")
                    missing_vars.append(var)
            if missing_vars:
                st.warning(f"Prompt variables not found: {', '.join(missing_vars)}")
            # Generate response using Ollama
            with st.spinner("Generating response..."):
                response = ollama_client.chat(model=selected_model, messages=[
                    {
                        'role': 'user',
                        'content': user_input,
                    },
                ])
            st.session_state['full_response'] = response["message"]["content"]
            st.write("**Response:**")
            st.markdown(st.session_state['full_response'])
        except Exception as e:
            st.error(f"Error generating response: {e}")
    else:
        st.warning("Please enter a prompt.")