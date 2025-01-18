app_version = "0.6"
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

# Import OpenAI and Anthropic libraries
import openai
from openai import OpenAI
import anthropic

# Import Google Vertex AI libraries
from google.cloud import aiplatform
from google.oauth2 import service_account
from vertexai.preview.language_models import ChatModel

# Import boto3 for Amazon Bedrock
import boto3

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
    st.header("Chat Endpoint Configuration")

    # Provider selection
    providers = ["Ollama", "OpenAI", "Google Vertex AI", "Amazon Bedrock", "Anthropic"]
    selected_provider = st.selectbox("Select Provider", options=providers)

    if selected_provider == "Ollama":
        st.subheader("Ollama Configuration")
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
                        # Allow manual input
                        model_names = []
                else:
                    st.warning(f"Failed to retrieve models - status code {models_response.status_code}")
                    # Allow manual input
                    model_names = []
            except Exception as e:
                st.warning(f"Error connecting to Ollama endpoint: {e}")
                # Allow manual input
                model_names = []
        else:
            st.error("Please select or enter a valid Ollama endpoint.")
            st.stop()

        if model_names:
            selected_model = st.selectbox(
                "Choose a Model",
                options=model_names,
                index=0
            )
        else:
            st.info("Enter model name manually:")
            selected_model = st.text_input("Model Name")
            if selected_model:
                # Test the model by making a small query
                try:
                    ollama_client = Client(host=selected_endpoint)
                    response = ollama_client.generate(model=selected_model, prompt="Hello")
                    st.success("Model is accessible and ready.")
                except Exception as e:
                    st.error(f"Failed to access the model: {e}")
                    st.stop()
            else:
                st.warning("Please enter a model name.")
                st.stop()
    elif selected_provider == "OpenAI":
        # OpenAI API Key
        openai_api_key = st.text_input("Enter OpenAI API Key", type="password")
        if not openai_api_key:
            st.warning("Please enter your OpenAI API Key.")
            st.stop()
        else:
            os.environ['OPENAI_API_KEY'] = openai_api_key
            openai_client = OpenAI(
                api_key = os.getenv('OPENAI_API_KEY')
            )
            # Fetch available models
            try:
                models_response = openai_client.models.list()
                #st.write(str(models_response))
                # Filter models to only include chat models
                allowed_models = ['gpt-4o', 'gpt-4o-mini', 'o1-mini', 'o1-preview', 'o1', 'o3'] # o3 is not available on API yet
                model_names = [model.id for model in models_response.data if model.id in allowed_models]
            except Exception as e:
                st.warning(f"Error retrieving models from OpenAI: {e}")
                model_names = []
            if model_names:
                selected_model = st.selectbox(
                    "Choose a Model",
                    options=model_names,
                    index=0
                )
            else:
                st.stop()
    elif selected_provider == "Google Vertex AI":
        st.subheader("Google Vertex AI Configuration")
        # Get project ID and location
        project_id = st.text_input("Enter Google Cloud Project ID")
        location = st.text_input("Enter Location", value="us-central1")
        # Upload service account JSON key file
        service_account_info = st.file_uploader("Upload Service Account JSON Key File", type="json")
        if not project_id or not location or not service_account_info:
            st.warning("Please enter Project ID, Location, and upload Service Account JSON Key File.")
            st.stop()
        else:
            # Initialize the AI Platform
            try:
                credentials_info = json.load(service_account_info)
                credentials = service_account.Credentials.from_service_account_info(credentials_info)
                aiplatform.init(project=project_id, location=location, credentials=credentials)
                # Get available models
                # For simplicity, we can use predefined model names
                model_names = ["chat-bison@001"]
            except Exception as e:
                st.warning(f"Error initializing Vertex AI: {e}")
                # Allow manual input
                model_names = []
            if model_names:
                selected_model = st.selectbox(
                    "Choose a Model",
                    options=model_names,
                    index=0
                )
            else:
                st.info("Enter model name manually:")
                selected_model = st.text_input("Model Name")
                if selected_model:
                    # Test the model by making a small query
                    try:
                        vertexai.init(project=project_id, location=location, credentials=credentials)
                        chat_model = ChatModel.from_pretrained(selected_model)
                        chat = chat_model.start_chat()
                        response = chat.send_message("Hello")
                        st.success("Model is accessible and ready.")
                    except Exception as e:
                        st.error(f"Failed to access the model: {e}")
                        st.stop()
                else:
                    st.warning("Please enter a model name.")
                    st.stop()
    elif selected_provider == "Amazon Bedrock":
        st.subheader("Amazon Bedrock Configuration")
        # Get AWS credentials
        aws_access_key_id = st.text_input("AWS Access Key ID")
        aws_secret_access_key = st.text_input("AWS Secret Access Key", type="password")
        aws_session_token = st.text_input("AWS Session Token (optional)", type="password")
        region_name = st.text_input("AWS Region", value="us-east-1")
        if not aws_access_key_id or not aws_secret_access_key or not region_name:
            st.warning("Please enter AWS credentials and region.")
            st.stop()
        else:
            # Initialize boto3 client
            try:
                session = boto3.Session(
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token=aws_session_token if aws_session_token else None,
                    region_name=region_name
                )
                bedrock_client = session.client('bedrock-runtime')
                # Get available models
                # For now, we'll hardcode some model names
                model_names = ["anthropic.claude-v2", "ai21.j2-jumbo-instruct"]
            except Exception as e:
                st.warning(f"Error initializing Amazon Bedrock client: {e}")
                # Allow manual input
                model_names = []
            if model_names:
                selected_model = st.selectbox(
                    "Choose a Model",
                    options=model_names,
                    index=0
                )
            else:
                st.info("Enter model name manually:")
                selected_model = st.text_input("Model Name")
                if selected_model:
                    # Test the model by making a small query
                    try:
                        # Make a simple test call
                        test_body = json.dumps({
                            "prompt": "Hello",
                            "maxTokens": 5
                        })
                        response = bedrock_client.invoke_model(
                            modelId=selected_model,
                            accept='application/json',
                            contentType='application/json',
                            body=test_body
                        )
                        st.success("Model is accessible and ready.")
                    except Exception as e:
                        st.error(f"Failed to access the model: {e}")
                        st.stop()
                else:
                    st.warning("Please enter a model name.")
                    st.stop()
    elif selected_provider == "Anthropic":
        st.subheader("Anthropic Configuration")
        # Anthropic API Key
        anthropic_api_key = st.text_input("Enter Anthropic API Key", type="password")
        if not anthropic_api_key:
            st.warning("Please enter your Anthropic API Key.")
            st.stop()
        else:
            os.environ['ANTHROPIC_API_KEY'] = anthropic_api_key
            # Initialize anthropic client
            try:
                anthropic_client = anthropic.Client(api_key=anthropic_api_key)
                # Fetch available models (assuming API provides a way)
                # For now, we'll hardcode some model names
                model_names = ['claude-3-5-sonnet-latest', 'claude-3-5-haiku-latest', 'claude-3-opus-latest', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']
            except Exception as e:
                st.warning(f"Error initializing Anthropic client: {e}")
                # Allow manual input
                model_names = []
            if model_names:
                selected_model = st.selectbox(
                    "Choose a Model",
                    options=model_names,
                    index=0
                )
            else:
                st.info("Enter model name manually:")
                selected_model = st.text_input("Model Name")
                if selected_model:
                    # Test the model by making a small query
                    try:
                        response = client.messages.create(
                            model=selected_model,
                            system="You are a helpful assistant.",
                            messages=[
                                {"role": "user", "content": "Hello"}
                            ],
                            max_tokens=5
                        )

                        st.success("Model is accessible and ready.")
                    except Exception as e:
                        st.error(f"Failed to access the model: {e}")
                        st.stop()
                else:
                    st.warning("Please enter a model name.")
                    st.stop()

# Handle Create Prompt Variable Modal
@st.dialog("Create Prompt Variable")
def create_prompt_variable(content, origin):
    variable_name = st.text_input("Enter variable name:")
    variable_value = st.text_area("Variable content:", content)
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

# Function to resolve nested variables
def resolve_variable(value, prompt_variables, resolved_vars=None):
    if resolved_vars is None:
        resolved_vars = set()
    pattern = r"\{\{(\w+)\}\}"
    variable_names = re.findall(pattern, value)
    if not variable_names:
        return value
    else:
        for var in variable_names:
            if var in resolved_vars:
                raise ValueError(f"Circular dependency detected for variable {var}")
            if var in prompt_variables:
                resolved_vars.add(var)
                var_value = resolve_variable(prompt_variables[var]['value'], prompt_variables, resolved_vars)
                value = value.replace(f"{{{{{var}}}}}", var_value)
                resolved_vars.remove(var)
            else:
                value = value.replace(f"{{{{{var}}}}}", "")
        return value

if generate_response:
    if user_input:
        try:
            # Process prompt variables in user_input
            try:
                user_input_resolved = resolve_variable(user_input, prompt_variables)
            except ValueError as e:
                st.error(str(e))
                st.stop()

            # Now generate the response using the selected provider
            if selected_provider == "Ollama":
                # Use Ollama client
                ollama_client = Client(host=selected_endpoint)
                with st.spinner("Generating response..."):
                    response = ollama_client.chat(model=selected_model, messages=[
                        {
                            'role': 'user',
                            'content': user_input_resolved,
                        },
                    ])
                st.session_state['full_response'] = response["message"]["content"]
                st.write("**Response:**")
                st.markdown(st.session_state['full_response'])
            elif selected_provider == "OpenAI":
                # Use OpenAI API (1.0.0 interface)
                with st.spinner("Generating response..."):
                    response = openai_client.chat.completions.create(
                        model=selected_model,
                        messages=[{"role": "user", "content": user_input_resolved}],
                    )
                st.session_state['full_response'] = response.choices[0].message.content
                st.write("**Response:**")
                st.markdown(st.session_state['full_response'])
            elif selected_provider == "Anthropic":
                # Use Anthropic API with the latest Message API
                client = anthropic.Client(api_key=anthropic_api_key)
                with st.spinner("Generating response..."):
                    response = client.messages.create(
                        model=selected_model,
                        system="You are a helpful assistant.",
                        messages=[
                            {"role": "user", "content": user_input_resolved}
                        ],
                        max_tokens=1000,
                        stop_sequences=["\n\nHuman:"],
                    )
                st.session_state['full_response'] = response.content[0].text
                st.write("**Response:**")
                st.markdown(st.session_state['full_response'])
            elif selected_provider == "Google Vertex AI":
                # Use Vertex AI SDK
                with st.spinner("Generating response..."):
                    try:
                        vertexai.init(project=project_id, location=location, credentials=credentials)
                        chat_model = ChatModel.from_pretrained(selected_model)
                        chat = chat_model.start_chat()
                        response = chat.send_message(user_input_resolved)
                        st.session_state['full_response'] = response.text
                        st.write("**Response:**")
                        st.markdown(st.session_state['full_response'])
                    except Exception as e:
                        st.error(f"Error generating response with Vertex AI: {e}")
            elif selected_provider == "Amazon Bedrock":
                # Use Bedrock client
                with st.spinner("Generating response..."):
                    try:
                        if "ai21" in selected_model:
                            # AI21 model
                            body = json.dumps({
                                "prompt": user_input_resolved,
                                "maxTokens": 512,
                                "temperature": 0.7,
                                "topP": 1,
                                "stopSequences": ["<|END|>"]
                            })
                        elif "anthropic" in selected_model:
                            # Anthropic model via Bedrock
                            body = json.dumps({
                                "prompt": "\n\nHuman: " + user_input_resolved + "\n\nAssistant:",
                                "maxTokens": 512,
                                "temperature": 0.7,
                                "topP": 1,
                                "stopSequences": ["\n\nHuman:"]
                            })
                        else:
                            st.error("Selected model not supported.")
                            st.stop()
                        response = bedrock_client.invoke_model(
                            modelId=selected_model,
                            accept='application/json',
                            contentType='application/json',
                            body=body
                        )
                        response_body = response['body'].read().decode('utf-8')
                        response_json = json.loads(response_body)
                        if "result" in response_json:
                            st.session_state['full_response'] = response_json['result']
                        elif "completion" in response_json:
                            st.session_state['full_response'] = response_json['completion']
                        else:
                            st.error("Unexpected response format from Bedrock.")
                            st.stop()
                        st.write("**Response:**")
                        st.markdown(st.session_state['full_response'])
                    except Exception as e:
                        st.error(f"Error generating response with Amazon Bedrock: {e}")
            else:
                st.error("Selected provider not supported yet.")
        except Exception as e:
            st.error(f"Error generating response: {e}")
    else:
        st.warning("Please enter a prompt.")
