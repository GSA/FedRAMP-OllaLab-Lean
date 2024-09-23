app_version = "0.1"
app_title = "OllaLab - Main"
app_description = "Welcome to OllaLab! Please select a below application to continue."
app_icon = "	:house:"

import os
import streamlit as st

st.set_page_config(
    page_title=app_title,
    page_icon=app_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Streamlit application code
st.title(app_title)
st.write(app_description)
st.text("")

# Function to extract variables from page files
def extract_variables(file_path):
    variables = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('app_version'):
                variables['app_version'] = line.split('=', 1)[1].strip().strip("'\"")
            elif line.startswith('app_title'):
                variables['app_title'] = line.split('=', 1)[1].strip().strip("'\"")
            elif line.startswith('app_description'):
                variables['app_description'] = line.split('=', 1)[1].strip().strip("'\"")
            elif line.startswith('app_icon'):
                variables['app_icon'] = line.split('=', 1)[1].strip().strip("'\"")
            if len(variables) == 4:
                break
    return variables

# Directory containing the page files
pages_dir = 'pages'
page_files = [f for f in os.listdir(pages_dir) if f.endswith('.py') and f != '__init__.py']

# Sort page_files to ensure consistent order
#page_files.sort()

# Define the number of tiles per row
tiles_per_row = 2
cols = st.columns(tiles_per_row)

for idx, file_name in enumerate(page_files):
    file_path = os.path.join(pages_dir, file_name)
    variables = extract_variables(file_path)
    page_name = os.path.splitext(file_name)[0]
    app_icon = variables.get('app_icon', '')
    app_title = variables.get('app_title', '')
    app_version = variables.get('app_version', '')
    app_description = variables.get('app_description', '')

    # Use the emoji short code directly in the button label
    icon = f"{app_icon} " if app_icon else ''
    button_label = f'''{icon}\n**{app_title}** (v. {app_version})\n
    {app_description}'''

    with cols[idx % tiles_per_row]:
        if st.button(button_label, key=page_name):
            st.switch_page(f"pages/{file_name}")


