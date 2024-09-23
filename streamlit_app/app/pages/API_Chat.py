app_version = "0.1"
app_title = "OllaLab - Chat with API"
app_description = "Application to chat with data from API requests"
app_icon = ":electric_plug:"

import os
import streamlit as st
import ollama
from ollama import Client
import requests
import pandas as pd
import re
from cryptography.fernet import Fernet
import base64
import json
import asyncio
import httpx
import spacy

# Initialize Ollama client
ollama_client = Client(host=f"http://host.docker.internal:8000")

st.set_page_config(
    page_title=app_title,
    page_icon=app_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize encryption key for the session
if 'encryption_key' not in st.session_state:
    st.session_state['encryption_key'] = Fernet.generate_key()

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Initialize API credentials
if 'api_credentials' not in st.session_state:
    st.session_state['api_credentials'] = {}

# Initialize retrieved data
if 'api_data' not in st.session_state:
    st.session_state['api_data'] = None

# Initialize processed data
if 'processed_data' not in st.session_state:
    st.session_state['processed_data'] = None

# Functions

def validate_credentials(api_url, api_key, client_id, client_secret):
    try:
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        response = requests.get(api_url, headers=headers, timeout=10)
        return response.status_code == 200
    except Exception as e:
        return False

def api_setup():
    st.header("API Setup")
    api_url = st.text_input("API URL or Endpoint", "")
    api_key = st.text_input("API Key", "", type="password")
    oauth_client_id = st.text_input("OAuth Client ID", "")
    oauth_client_secret = st.text_input("OAuth Client Secret", type="password")
    # Add more fields as necessary

    if st.button("Validate Credentials"):
        # Implement credential validation
        is_valid = validate_credentials(api_url, api_key, oauth_client_id, oauth_client_secret)
        if is_valid:
            st.success("Credentials are valid!")
            st.session_state['api_credentials'] = {
                'api_url': api_url,
                'api_key': api_key,
                'oauth_client_id': oauth_client_id,
                'oauth_client_secret': oauth_client_secret
            }
        else:
            st.error("Invalid credentials. Please check and try again.")

def data_retrieval():
    st.header("Data Retrieval")
    search_query = st.text_input("Enter your search query", "")
    
    # Allow users to input additional API parameters
    st.subheader("Additional API Parameters")
    additional_params = {}
    num_params = st.number_input("Number of additional parameters", min_value=0, step=1, value=0)
    for i in range(int(num_params)):
        param_key = st.text_input(f"Parameter {i+1} Key", key=f"param_key_{i}")
        param_value = st.text_input(f"Parameter {i+1} Value", key=f"param_value_{i}")
        if param_key and param_value:
            additional_params[param_key] = param_value

    if st.button("Retrieve Data"):
        data = retrieve_data(search_query, additional_params)
        if data is not None:
            st.session_state['api_data'] = data
            st.success("Data retrieved successfully!")
            display_data(data)
        else:
            st.error("Failed to retrieve data.")

def retrieve_data(query, additional_params):
    try:
        credentials = st.session_state.get('api_credentials', {})
        api_url = credentials.get('api_url')
        api_key = credentials.get('api_key')
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        params = {'query': query} if query else {}
        
        # Merge additional parameters
        params.update(additional_params)

        response = requests.get(api_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Store processed data in session state
        st.session_state['processed_data'] = process_data(data)
        return data
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def store_data(data):
    if 'processed_data' not in st.session_state:
        st.session_state['processed_data'] = process_data(data)

def process_data(data):
    # Assuming data is a list of dictionaries
    if isinstance(data, dict):
        data = [data]
    df = pd.DataFrame(data)
    return df

def display_data(data):
    df = st.session_state.get('processed_data')
    if df is not None:
        st.dataframe(df)
        st.download_button(
            label="Download Data as CSV",
            data=df.to_csv(index=False),
            file_name='api_data.csv',
            mime='text/csv',
        )
    else:
        st.error("No data to display.")

def process_chat_input(user_input):
    # Simple NLP processing

    df = st.session_state.get('processed_data')
    if df is None:
        return "No data available to chat with. Please retrieve data first."

    # Basic keyword matching
    if re.search(r'show.*severity.*high', user_input, re.IGNORECASE):
        if 'severity' in df.columns:
            filtered_df = df[df['severity'].str.lower() == 'high']
            if not filtered_df.empty:
                return filtered_df.to_string(index=False)
            else:
                return "No records found with high severity."
        else:
            return "Severity information not available in the data."
    elif re.search(r'list.*vulnerabilities.*2023', user_input, re.IGNORECASE):
        if 'publishedDate' in df.columns:
            filtered_df = df[df['publishedDate'].str.contains('2023')]
            if not filtered_df.empty:
                return filtered_df.to_string(index=False)
            else:
                return "No vulnerabilities found from 2023."
        else:
            return "Publication date information not available in the data."
    else:
        return "I'm sorry, I didn't understand your request."

def chat_interface():
    st.header("Chat with Your Data")
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    user_input = st.text_input("You:", key="chat_input")
    if st.button("Send", key="send_button"):
        response = process_chat_input(user_input)
        st.session_state['chat_history'].append(("You", user_input))
        st.session_state['chat_history'].append(("Bot", response))

    for sender, message in st.session_state['chat_history']:
        st.write(f"**{sender}:** {message}")

def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_data(token, key):
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()

def sanitize_input(user_input):
    # Remove any potentially harmful characters or patterns
    return re.sub(r'[^\w\s\-\.]', '', user_input)

def logout():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.success("Session is cleared.")
    st.experimental_rerun()

def retrieve_data_with_pagination(query):
    credentials = st.session_state.get('api_credentials', {})
    api_url = credentials.get('api_url')
    api_key = credentials.get('api_key')
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    params = {'query': query, 'page': 1}
    all_data = []

    while True:
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data.get('results'):
            break
        all_data.extend(data['results'])
        params['page'] += 1

        if params['page'] > data.get('total_pages', 1):  # Assuming total_pages is provided
            break

    return all_data

async def retrieve_data_async(query):
    credentials = st.session_state.get('api_credentials', {})
    api_url = credentials.get('api_url')
    api_key = credentials.get('api_key')
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    params = {'query': query}

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data

nlp = spacy.load('en_core_web_sm')

def process_chat_input_advanced(user_input):
    doc = nlp(user_input)
    # Extract entities and intents
    # Implement more sophisticated parsing

# Streamlit application code
st.title(app_title)
st.write(app_description)

st.warning('This application is still under construction', icon="⚠️")

steps = ["API Setup", "Data Retrieval", "Chat with Data", "Clear Session"]
choice = st.selectbox("Steps", steps)
if choice == "API Setup":
    api_setup()
elif choice == "Data Retrieval":
    data_retrieval()
elif choice == "Chat with Data":
    chat_interface()
elif choice == "Clear Session":
    logout()
