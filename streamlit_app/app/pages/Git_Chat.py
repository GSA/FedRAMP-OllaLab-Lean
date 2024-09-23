app_version = "0.1"
app_title = "OllaLab - Chat with Git Repositories"
app_description = "Application to chat with data from Git repositories"
app_icon = ":books:"

import os
import streamlit as st
import ollama
from ollama import Client

# Initialize Ollama client
ollama_client = Client(host=f"http://host.docker.internal:8000")

st.set_page_config(
    page_title=app_title,
    page_icon=app_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Streamlit application code
st.title(app_title)
st.write(app_description)

st.warning('This application is still under construction', icon="⚠️")
