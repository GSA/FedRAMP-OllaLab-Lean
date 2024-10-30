app_version = "0.1"
app_title = "OllaLab - Simple Chat"
app_description = "A simple chat application with your selected LLM."
app_icon = ":robot_face:"

import os
import streamlit as st
import requests
import ollama
from ollama import Client

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

# Sidebar for Ollama Endpoint Selection
st.sidebar.header("Ollama Endpoint Configuration")

# Predefined endpoints
default_endpoints = {
    "Docker Internal": "http://host.docker.internal:8000",
    "Localhost": "http://127.0.0.1:11434",
    "Other": ""
}

endpoint_option = st.sidebar.selectbox(
    "Select Ollama Endpoint",
    options=list(default_endpoints.keys()),
    index=0
)

if endpoint_option == "Other":
    custom_endpoint = st.sidebar.text_input("Enter Ollama Endpoint URL", value="http://")
    selected_endpoint = custom_endpoint
else:
    selected_endpoint = default_endpoints[endpoint_option]

# Initialize Ollama client based on selected endpoint
if selected_endpoint:
    #try:
    ollama_client = Client(host=selected_endpoint)
    # Fetch available models
    models_response = requests.get(f"{selected_endpoint}/v1/models")
    if models_response.status_code == 200:
        available_models_data = models_response.json()
        # assume the response contains a  list of models under 'data' key
        model_names = [model['id'] for model in available_models_data.get('data',[])]
        if not model_names:
            st.error("No model available for the selected endpoint.")
            st.stop
    else:
        st.error(f"Failed to retrieve model - status code {models_response.status_code}")
        st.stop

else:
    st.error("Please select or enter a valid Ollama endpoint.")
    st.stop()

# Sidebar for Model Selection
st.sidebar.header("Model Selection")
selected_model = st.sidebar.selectbox(
    "Choose a Model",
    options=model_names,
    index=0
)

# Input text from user
user_input = st.text_area("Enter your prompt:")

if st.button("Generate Response"):
    if user_input:
        try:
            # Generate response using Ollama
            response = ollama_client.chat(model=selected_model, messages=[
                {
                    'role': 'user',
                    'content': user_input,
                },
            ])
            st.write("**Response:**")
            st.write(response["message"]["content"])
        except Exception as e:
            st.error(f"Error generating response: {e}")
    else:
        st.warning("Please enter a prompt.")
