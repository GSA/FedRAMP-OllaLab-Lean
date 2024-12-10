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

def customize_json_schema(schema):
    """
    Allows the user to customize the JSON schema by setting constraints.

    Args:
        schema (dict): The initial JSON schema.

    Returns:
        dict: The customized JSON schema.
    """
    st.header("Customize JSON Schema")
    properties = schema.get('properties', {})
    required_fields = schema.get('required', [])

    for field_name, field_props in properties.items():
        st.subheader(f"Field: {field_name}")
        field_type = field_props.get('type', 'unknown')
        st.write(f"Type: {field_type}")

        # Required Field Checkbox
        is_required = st.checkbox(f"Is '{field_name}' required?", field_name in required_fields)
        if is_required and field_name not in required_fields:
            required_fields.append(field_name)
        elif not is_required and field_name in required_fields:
            required_fields.remove(field_name)

        # Constraints for String Fields
        if field_type == 'string':
            # Max Length
            max_length = field_props.get('maxLength', None)
            new_max_length = st.number_input(f"Max length for '{field_name}':", value=max_length or 0, min_value=0)
            if new_max_length > 0:
                field_props['maxLength'] = new_max_length
            else:
                field_props.pop('maxLength', None)
            # Enumerated Values
            enum_values = field_props.get('enum', [])
            enum_input = st.text_input(f"Enumerated values for '{field_name}' (comma-separated):", value=', '.join(enum_values))
            if enum_input:
                field_props['enum'] = [v.strip() for v in enum_input.split(',')]
            else:
                field_props.pop('enum', None)

        # Constraints for Numeric Fields
        elif field_type in ['number', 'integer']:
            # Minimum Value
            min_value = field_props.get('minimum', None)
            new_min_value = st.number_input(f"Minimum value for '{field_name}':", value=min_value or 0)
            field_props['minimum'] = new_min_value
            # Maximum Value
            max_value = field_props.get('maximum', None)
            new_max_value = st.number_input(f"Maximum value for '{field_name}':", value=max_value or 0)
            field_props['maximum'] = new_max_value

        properties[field_name] = field_props

    schema['properties'] = properties
    schema['required'] = required_fields if required_fields else None
    return schema

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

def get_user_stopwords():
    """
    Allows the user to input a list of stopwords.

    Returns:
        set: A set of user-defined stopwords.
    """
    st.subheader("Stopwords Configuration")
    user_input = st.text_area("Enter additional stopwords (separated by commas):", value="")
    user_stopwords = set()
    if user_input:
        user_stopwords = {word.strip() for word in user_input.split(',')}
    return user_stopwords

def group_values_interface(bigrams, trigrams, numeric_values):
    """
    Provides an interface for the user to create groups of values.

    Args:
        bigrams (list): List of bigrams.
        trigrams (list): List of trigrams.
        numeric_values (list): List of numeric values.

    Returns:
        dict: Dictionary of groups created by the user.
    """
    st.subheader("Create Groups of Similar Values")
    groups = {}
    num_groups = st.number_input("How many groups do you want to create?", min_value=1, max_value=10, value=1, step=1)
    for i in range(int(num_groups)):
        st.write(f"Group {i+1}")
        group_name = st.text_input(f"Group {i+1} Name", key=f"group_name_{i}")
        group_type = st.selectbox(f"Group {i+1} Type", options=["String", "Numeric"], key=f"group_type_{i}")
        group_description = st.text_area(f"Group {i+1} Description", key=f"group_desc_{i}")
        if group_type == "String":
            # Display options for bigrams and trigrams
            all_ngrams = bigrams + trigrams
            ngram_options = [' '.join(ngram) for ngram in all_ngrams]
            selected_ngrams = st.multiselect(f"Select n-grams for {group_name}", options=ngram_options, key=f"ngrams_{i}")
            groups[group_name] = {
                "type": "string",
                "description": group_description,
                "values": selected_ngrams
            }
        elif group_type == "Numeric":
            # Display options for numeric values
            selected_numbers = st.multiselect(f"Select numeric values for {group_name}", options=sorted(set(numeric_values)), key=f"numbers_{i}")
            groups[group_name] = {
                "type": "number",
                "description": group_description,
                "values": selected_numbers
            }
    return groups

def schema_builder_interface_unstructured(groups):
    """
    Provides a schema builder interface for unstructured data processing.

    Args:
        groups (dict): Dictionary of groups created by the user.

    Returns:
        dict: The user-defined schema.
    """
    st.subheader("Schema Builder")
    schema_title = st.text_input("Schema Title")
    schema_description = st.text_area("Schema Description")
    st.write("Schema type is 'object'.")

    properties = {}
    num_properties = st.number_input("How many properties do you want to add?", min_value=1, max_value=20, value=1, step=1)
    for i in range(int(num_properties)):
        st.write(f"Property {i+1}")
        prop_name = st.text_input(f"Property {i+1} Name", key=f"prop_name_{i}")
        prop_type = st.selectbox(f"Property {i+1} Type", options=["Simple Key-Value", "Array", "Object"], key=f"prop_type_{i}")
        if prop_type == "Simple Key-Value":
            # Options to select from groups or input key name and data type
            use_group = st.checkbox(f"Use a group for property '{prop_name}'?", key=f"use_group_{i}")
            if use_group:
                group_name = st.selectbox(f"Select group for property '{prop_name}'", options=list(groups.keys()), key=f"group_select_{i}")
                group_info = groups[group_name]
                properties[prop_name] = {
                    "type": group_info["type"],
                    "description": group_info["description"]
                }
            else:
                data_type = st.selectbox(f"Select data type for '{prop_name}'", options=["string", "number", "integer", "boolean"], key=f"data_type_{i}")
                description = st.text_area(f"Description for '{prop_name}'", key=f"description_{i}")
                properties[prop_name] = {
                    "type": data_type,
                    "description": description
                }
        elif prop_type == "Array":
            item_type = st.selectbox(f"Select item data type for array '{prop_name}'", options=["string", "number", "integer", "boolean"], key=f"item_type_{i}")
            description = st.text_area(f"Description for '{prop_name}'", key=f"description_{i}")
            properties[prop_name] = {
                "type": "array",
                "description": description,
                "items": {"type": item_type}
            }
        elif prop_type == "Object":
            # Recursive properties for child object
            st.write(f"Define properties for child object '{prop_name}'")
            child_properties = {}
            num_child_props = st.number_input(f"How many properties for '{prop_name}'?", min_value=1, max_value=20, value=1, step=1, key=f"num_child_props_{i}")
            for j in range(int(num_child_props)):
                child_prop_name = st.text_input(f"Property {j+1} Name in '{prop_name}'", key=f"{i}_child_prop_name_{j}")
                child_data_type = st.selectbox(f"Select data type for '{child_prop_name}'", options=["string", "number", "integer", "boolean"], key=f"{i}_child_data_type_{j}")
                child_description = st.text_area(f"Description for '{child_prop_name}'", key=f"{i}_child_description_{j}")
                child_properties[child_prop_name] = {
                    "type": child_data_type,
                    "description": child_description
                }
            properties[prop_name] = {
                "type": "object",
                "properties": child_properties
            }
    schema = {
        "title": schema_title,
        "description": schema_description,
        "type": "object",
        "properties": properties
    }
    st.write("Generated Schema:")
    st.json(schema)
    return schema