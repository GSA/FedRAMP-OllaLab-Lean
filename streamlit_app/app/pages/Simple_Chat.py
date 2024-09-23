app_version = "0.1"
app_title = "OllaLab - Simple Chat"
app_description = "A simple chat application with Llama3.1:8b"
app_icon = ":robot_face:"

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
# Input text from user
user_input = st.text_area("Enter your prompt:")

if st.button("Generate Response"):
    if user_input:
        # Generate response using Ollama
        response = ollama_client.generate(prompt=user_input, model='llama3.1:8b')
        response = ollama_client.chat(model='llama3.1:8b', messages=[
            {
                'role': 'user',
                'content': user_input,
            },
        ])
        st.write("Response:")
        st.write(response["message"]["content"])
    else:
        st.write("Please enter a prompt.")
