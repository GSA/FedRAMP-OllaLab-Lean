import streamlit as st

def select_processing_option():
    """
    Displays a radio button for the user to choose the processing path.

    Returns:
        str: The selected processing option.
    """
    st.header("Select Processing Option")
    options = [
        "Process Serialized data",
        "Process Tabular data",
        "Process Unstructured data"
    ]
    choice = st.radio("Choose a processing path:", options)
    return choice

def display_eda_results(eda_results):
    """
    Displays the Exploratory Data Analysis (EDA) results in the Streamlit app.

    Args:
        eda_results (dict): The results of the EDA.
            Expected keys may include 'dataframe', 'statistics', 'plots', 'wordcloud', etc.
    """
    st.header("Exploratory Data Analysis Results")

    if 'dataframe' in eda_results:
        st.subheader("Dataframe Sample")
        st.write(eda_results['dataframe'])

    if 'statistics' in eda_results:
        st.subheader("Descriptive Statistics")
        st.write(eda_results['statistics'])

    if 'plots' in eda_results:
        st.subheader("Plots")
        for plot in eda_results['plots']:
            st.pyplot(plot)

    if 'wordcloud' in eda_results:
        st.subheader("Word Cloud")
        st.image(eda_results['wordcloud'])

    if 'text_summary' in eda_results:
        st.subheader("Text Summary")
        st.write(eda_results['text_summary'])

    # Add other EDA results as needed

def schema_builder_interface():
    """
    Provides an interface for the user to build and customize the data schema.

    Returns:
        dict: The user-defined schema.
    """
    st.header("Schema Builder")

    # Initialize schema in session state if not already present
    if 'schema' not in st.session_state:
        st.session_state['schema'] = {
            'title': '',
            'description': '',
            'type': 'object',
            'properties': {}
        }
        st.session_state['current_object'] = st.session_state['schema']
        st.session_state['object_stack'] = []

    # Display current object path for clarity
    current_path = '/'.join(
        [obj.get('name', 'root') for obj in st.session_state['object_stack']]
    )
    st.write(f"Current Object Path: `{current_path or 'root'}`")

    # Schema title and description
    st.session_state['schema']['title'] = st.text_input(
        "Schema Title",
        value=st.session_state['schema']['title']
    )
    st.session_state['schema']['description'] = st.text_area(
        "Schema Description",
        value=st.session_state['schema']['description']
    )

    st.write("### Add Properties to the Schema:")

    # Form for adding new properties
    with st.form("add_property_form", clear_on_submit=True):
        prop_name = st.text_input("Property Name")
        prop_type = st.selectbox(
            "Property Type",
            ["string", "number", "integer", "boolean", "array", "object"]
        )
        prop_description = st.text_area("Property Description")

        # Handle property details based on type
        prop_details = {}

        if prop_type == 'array':
            item_type = st.selectbox(
                "Item Type",
                ["string", "number", "integer", "boolean", "object"]
            )
            prop_details = {
                'type': 'array',
                'description': prop_description,
                'items': {}
            }
            if item_type == 'object':
                prop_details['items'] = {'type': 'object', 'properties': {}}
                st.info("You can add properties to the items in this array after adding this property.")
            else:
                prop_details['items']['type'] = item_type

        elif prop_type == 'object':
            prop_details = {
                'type': 'object',
                'description': prop_description,
                'properties': {}
            }
            st.info("You can add properties to this object after adding it to the schema.")

        else:
            # Simple types
            prop_details = {
                'type': prop_type,
                'description': prop_description
            }

        # Submit button for adding the property
        submit_button = st.form_submit_button("Add Property")

        if submit_button and prop_name:
            # Add property to the current object
            st.session_state['current_object']['properties'][prop_name] = prop_details
            st.success(f"Property '{prop_name}' added to schema.")

    # Display current schema structure
    st.write("### Current Schema Structure:")
    display_schema_structure(st.session_state['schema'])

    # Options to navigate into nested objects
    navigate_nested_objects()

    # Option to finish schema building
    finish_button = st.button("Finish Schema and Save")

    if finish_button:
        st.success("Schema building completed.")
        return st.session_state['schema']

    return None

def navigate_nested_objects():
    """
    Provides navigation options for editing nested objects within the schema.
    """
    current_properties = st.session_state['current_object'].get('properties', {})

    # Buttons for navigating into nested objects
    for prop_name, prop_details in current_properties.items():
        if prop_details.get('type') == 'object' or (
            prop_details.get('type') == 'array' and
            prop_details['items'].get('type') == 'object'
        ):
            if prop_details['type'] == 'array':
                object_to_edit = prop_details['items']
                label = f"Edit properties of items in array '{prop_name}'"
            else:
                object_to_edit = prop_details
                label = f"Edit object '{prop_name}'"

            if st.button(label):
                st.session_state['object_stack'].append({
                    'name': prop_name,
                    'object': st.session_state['current_object']
                })
                st.session_state['current_object'] = object_to_edit
                st.experimental_rerun()

    # Option to go back to parent object
    if st.session_state['object_stack']:
        if st.button("Go Back to Parent Object"):
            parent_info = st.session_state['object_stack'].pop()
            st.session_state['current_object'] = parent_info['object']
            st.experimental_rerun()

def display_schema_structure(schema, level=0):
    """
    Recursively displays the schema structure.

    Args:
        schema (dict): The schema to display.
        level (int): Current level of nesting.
    """
    indent = '  ' * level
    for prop_name, prop_details in schema.get('properties', {}).items():
        st.markdown(f"{indent}- **{prop_name}** (_{prop_details.get('type')}_)")
        if prop_details.get('type') == 'object':
            display_schema_structure(prop_details, level + 1)
        elif prop_details.get('type') == 'array' and prop_details['items'].get('type') == 'object':
            st.markdown(f"{indent}  - items (_{prop_details['items'].get('type')}_)")
            display_schema_structure(prop_details['items'], level + 2)

def display_validation_results(is_valid, errors=None):
    """
    Displays the results of the schema validation.

    Args:
        is_valid (bool): Whether the data is valid against the schema.
        errors (list or str, optional): Validation errors, if any.
    """
    st.header("Schema Validation Results")
    if is_valid:
        st.success("Data is valid against the schema.")
    else:
        st.error("Data is not valid against the schema.")
        if errors:
            st.write("#### Errors:")
            if isinstance(errors, list):
                for error in errors:
                    st.markdown(f"- {error}")
            else:
                st.write(errors)