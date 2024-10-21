app_version = "0.1"
app_title = "OllaLab - Chat with Local Folder"
app_description = "Chat with documents in a local folder."
app_icon = ":open_file_folder:"

import os
import streamlit as st
from pathlib import Path

from langchain.chains import RetrievalQA
from PyPDF2 import PdfReader
from docx import Document
from langchain.callbacks.base import BaseCallbackHandler
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Neo4jVector
from streamlit.logger import get_logger

# Import local embeddings and Ollama LLM
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import Ollama

st.set_page_config(
    page_title=app_title,
    page_icon=app_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

NEO4J_URI="bolt://host.docker.internal:7687"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your_secure_password"

logger = get_logger(__name__)

# Initialize Ollama client
#ollama_client = Client(host=f"http://host.docker.internal:8000")

# Define base directory for data storage
BASE_DIR = 'folder_chat'

# Ensure base directory exists
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

@st.fragment
def chat_fragment(qa):
    # Load local embeddings and Ollama LLM
    query = st.text_input("Ask a question about your documents")
    if query:
        # Define StreamHandler for real-time output
        class StreamHandler(BaseCallbackHandler):
            def __init__(self, container, initial_text=""):
                self.container = container
                self.text = initial_text

            def on_llm_new_token(self, token: str, **kwargs) -> None:
                self.text += token
                self.container.markdown(self.text)

        stream_handler = StreamHandler(st.empty())
        qa.run(query, callbacks=[stream_handler])

# START OF MAIN APP
st.title(app_title)
st.write(app_description)

# Folder management
st.subheader("Folder Management")

# Create a new folder
new_folder_name = st.text_input("Create a new folder")
if st.button("Create Folder"):
    if new_folder_name:
        folder_path = os.path.normpath(os.path.join(BASE_DIR, new_folder_name))
        if not folder_path.startswith(os.path.abspath(BASE_DIR)):
            st.error("Invalid folder name. Please try again.")
        elif not os.path.exists(folder_path):
            os.makedirs(folder_path)
            st.success(f"Folder '{new_folder_name}' created.")
        else:
            st.warning(f"Folder '{new_folder_name}' already exists.")
    else:
        st.error("Please enter a folder name.")

# List existing folders
folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]
if folders:
    selected_folder = st.selectbox("Select a folder", folders)
else:
    st.warning("No folders available. Please create a new folder.")
    selected_folder = None

# File upload
st.subheader("Upload Files")
if selected_folder:
    uploaded_files = st.file_uploader(
        "Upload your documents",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True
    )
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.size > 10 * 1024 * 1024:  # Limit file size to 10MB
                st.error(f"File {uploaded_file.name} is too large. Maximum size is 10MB.")
                continue
            file_path = os.path.join(BASE_DIR, selected_folder, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
        st.success("Files uploaded successfully.")

# Chat Interface
st.subheader("Chat Interface")

if selected_folder:
    folder_path = os.path.join(BASE_DIR, selected_folder)
    files_in_folder = os.listdir(folder_path)

    if files_in_folder:
        # Process documents
        st.write("Processing the following documents:")

        all_text = ""
        for file_name in files_in_folder:
            file_path = os.path.join(folder_path, file_name)
            try:
                if file_name.lower().endswith('.pdf'):
                    pdf_reader = PdfReader(file_path)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    all_text += text
                elif file_name.lower().endswith('.docx'):
                    doc = Document(file_path)
                    text = ""
                    for para in doc.paragraphs:
                        text += para.text
                    all_text += text
                elif file_name.lower().endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    all_text += text
                else:
                    st.warning(f"Unsupported file format: {file_name}")
            except Exception as e:
                st.error(f"Error processing {file_name}: {e}")
            st.write(file_name)
        if all_text:
            # Text splitting
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200, length_function=len
            )

            chunks = text_splitter.split_text(text=all_text)

            # Load local embeddings and Ollama LLM
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            llm = Ollama(model="llama3.1:8b", base_url="http://host.docker.internal:8000")

            # Neo4j configuration
            neo4j_url = NEO4J_URI
            neo4j_username = NEO4J_USERNAME
            neo4j_password = NEO4J_PASSWORD

            # Store the chunks in Neo4j vector database
            vectorstore = Neo4jVector.from_texts(
                chunks,
                url=neo4j_url,
                username=neo4j_username,
                password=neo4j_password,
                embedding=embeddings,
                index_name=f"{selected_folder}_index",
                node_label="DocumentChunk",
                pre_delete_collection=True,  # Delete existing data for this collection
            )

            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever()
            )

            # Chat interface
            st.write("You can now chat with your documents.")
            chat_fragment(qa)
        else:
            st.warning("No text found in the documents.")
    else:
        st.warning("No files in the selected folder. Please upload documents.")