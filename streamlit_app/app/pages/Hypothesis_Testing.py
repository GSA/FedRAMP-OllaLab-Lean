# Hypothesis_Testing.py

app_version = "0.1"
app_title = "OllaLab - Hypothesis Testing"
app_description = "Test hypotheses with SEM."
app_icon = ":chart:"

import streamlit as st
import pandas as pd
import numpy as np
from semopy import Model
from semopy.inspector import inspect
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor

if 'result' not in st.session_state:
        st.session_state['result'] = None

def main():
    st.title("Interactive Structural Equation Modeling App")

    # Step 1: Upload File
    data = upload_file_step()
    if data is not None:
        # Step 2: Confirm Numerical Columns
        data = confirm_numerical_columns_step(data)
        if data is not None:
            # Step 3: Handle Missing Values
            data = handle_missing_values_step(data)
            if data is not None:
                # Step 4: Select Columns of Interest
                data = select_columns_of_interest_step(data)
                if data is not None:
                    # Step 5: Check Normality and Multicollinearity
                    check_data_assumptions_step(data)
                    # Step 6: Build Measurement Model
                    measurement_model, latent_vars_list = build_measurement_model_step(data)
                    # Step 7: Build Regression Model
                    regression_model = build_regression_model_step(data.columns.tolist(), latent_vars_list)
                    # Step 8: Build Residual Correlations
                    residual_correlations = build_residual_correlations_step(data.columns.tolist(), latent_vars_list)
                    # Step 9: Select SEM Parameters
                    objective, optimizer = select_sem_parameters_step()
                    # Combine all model specifications
                    model_spec = measurement_model + regression_model + "\n" + residual_correlations
                    # Step 10: Estimate the Model
                    result = estimate_model_step(model_spec, data, objective, optimizer)
                    if st.session_state['result'] is not None:
                        # Step 11: Evaluate Model Parameters
                        evaluate_model_parameters_step(result)
                        # Step 12: Plot the SEM Model
                        plot_sem_model_step(model_spec, data)
                        # Step 13: Restart Option
                        restart_app_step()

def upload_file_step():
    st.header("1. Upload Data File")
    uploaded_file = st.file_uploader("Upload your tabular data file (csv, tsv, xlsx, etc.)", type=['csv', 'tsv', 'xlsx'])
    if uploaded_file is not None:
        data = read_uploaded_file(uploaded_file)
        if data is not None:
            st.write("Preview of the dataset:")
            st.dataframe(data.head())
            return data
    return None

@st.cache_data
def read_uploaded_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.tsv'):
            data = pd.read_csv(uploaded_file, sep='\t')
        elif uploaded_file.name.endswith('.xlsx'):
            data = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format!")
            return None
        return data
    except Exception as e:
        st.error(f"Error reading the file: {e}")
        return None

@st.fragment()
def confirm_numerical_columns_step(data):
    st.header("2. Confirm Numerical Columns")
    numeric_cols = data.select_dtypes(include=np.number).columns.tolist()
    selected_numeric_cols = st.multiselect("Select the numerical columns to use:", numeric_cols, default=numeric_cols)
    if selected_numeric_cols:
        data = data[selected_numeric_cols]
        return data
    else:
        st.warning("Please confirm the numerical columns to proceed.")
        return None

@st.fragment()
def handle_missing_values_step(data):
    st.header("3. Handle Missing Values")
    missing_values = data.isnull().sum()
    if missing_values.any():
        st.warning("Missing values detected!")
        st.write(missing_values[missing_values > 0])
        fix_option = st.radio("Choose how to handle missing values:", ["Remove rows with missing values", "Fill with mean", "Fill with median"])
        data = fix_missing_values(data, fix_option)
        st.success("Missing values handled.")
    else:
        st.success("No missing values detected.")
    return data

def fix_missing_values(data, fix_option):
    if fix_option == "Remove rows with missing values":
        data = data.dropna()
    elif fix_option == "Fill with mean":
        data = data.fillna(data.mean())
    elif fix_option == "Fill with median":
        data = data.fillna(data.median())
    return data

def select_columns_of_interest_step(data):
    st.header("4. Select Columns of Interest")
    selected_cols = st.multiselect("Select at least 2 columns of interest:", data.columns.tolist())
    if len(selected_cols) >= 2:
        data = data[selected_cols]
        return data
    else:
        st.warning("Please select at least 2 columns of interest.")
        return None

@st.fragment()
def check_data_assumptions_step(data):
    st.header("5. Check Normality and Multicollinearity")
    normality_df = perform_normality_tests(data)
    st.subheader("Normality Tests (Shapiro-Wilk Test)")
    st.dataframe(normality_df)
    vif_data = calculate_vif(data)
    st.subheader("Variance Inflation Factor (VIF)")
    st.dataframe(vif_data)

@st.cache_data
def perform_normality_tests(data):
    normality_results = {}
    for col in data.columns:
        stat, p = stats.shapiro(data[col])
        normality_results[col] = {'Statistic': stat, 'p-value': p}
    normality_df = pd.DataFrame(normality_results).T
    return normality_df

@st.cache_data
def calculate_vif(data):
    vif_data = pd.DataFrame()
    vif_data["Variable"] = data.columns
    vif_data["VIF"] = [variance_inflation_factor(data.values, i) for i in range(len(data.columns))]
    return vif_data

@st.fragment()
def build_measurement_model_step(data):
    st.header("6. Build Measurement Model")
    st.write("Define latent variables and their indicators.")
    measurement_model = ""
    latent_vars = st.text_input("Enter latent variable names (comma-separated):")
    latent_vars_list = [var.strip() for var in latent_vars.split(',') if var.strip()]
    for latent_var in latent_vars_list:
        indicators = st.multiselect(f"Select indicators for latent variable '{latent_var}':", data.columns.tolist())
        if indicators:
            measurement_eq = f"{latent_var} =~ " + " + ".join(indicators)
            measurement_model += measurement_eq + "\n"
    st.code(measurement_model, language='text')
    return measurement_model, latent_vars_list

@st.fragment()
def build_regression_model_step(all_vars, latent_vars_list):
    st.header("7. Build Regression Model")
    dependent_var = st.selectbox("Select the dependent variable:", all_vars + latent_vars_list)
    independent_vars = st.multiselect("Select independent variables:", [var for var in all_vars + latent_vars_list if var != dependent_var])
    regression_model = f"{dependent_var} ~ " + " + ".join(independent_vars) if independent_vars else ""
    st.code(regression_model, language='text')
    return regression_model

@st.fragment()
def build_residual_correlations_step(all_vars, latent_vars_list):
    st.header("8. Build Residual Correlations")
    residual_vars = st.multiselect("Select variables for residual correlations (optional):", all_vars + latent_vars_list)
    residual_correlations = ""
    if residual_vars:
        for i in range(len(residual_vars)):
            for j in range(i+1, len(residual_vars)):
                residual_correlations += f"{residual_vars[i]} ~~ {residual_vars[j]}\n"
        st.code(residual_correlations, language='text')
    return residual_correlations

@st.fragment()
def select_sem_parameters_step():
    st.header("9. Select SEM Parameters")
    objective = st.selectbox("Objective Function:", ["MLW", "FIML", "GLS", "ULS", "DWLS"])
    optimizer = st.selectbox("Optimization Method:", ["SLSQP", "L-BFGS-B", "TNC"])
    return objective, optimizer

@st.fragment()
def estimate_model_step(model_spec, data, objective, optimizer):
    st.header("10. Estimate the Model")
    if st.button("Estimate Model"):
        model = Model(model_spec)
        try:
            res = model.fit(data, obj=objective, solver=optimizer)
            st.success("Model estimation successful.")
            result = inspect_model(model)
            
            # Ensure 'result' is a DataFrame
            if isinstance(result, pd.DataFrame):
                # Replace '-' with NaN
                result.replace('-', np.nan, inplace=True)
                
                # Drop rows with any NaN values
                result.dropna(inplace=True)
                
                st.subheader("Model Inspection Results")
                st.dataframe(result)
                
                # Store the cleaned result in session state
                st.session_state['result'] = result
            else:
                st.error("Inspection result is not a valid DataFrame.")
                st.session_state['result'] = None
        except Exception as e:
            st.error(f"An error occurred during model estimation: {e}")
            st.session_state['result'] = None
    return st.session_state['result']

def inspect_model(model):
    result = pd.DataFrame(inspect(model))
    return result

@st.fragment()
def evaluate_model_parameters_step(result):
    st.header("11. Evaluate Model Parameters")
    p_value_threshold = st.number_input("Set p-value threshold for significance:", value=0.05)
    
    # Ensure that 'result' is a DataFrame
    if not isinstance(result, pd.DataFrame):
        st.error("Invalid result format. Expected a DataFrame.")
        return
    
    # Check if 'pval' exists, else try 'p-value'
    if 'pval' in result.columns:
        p_col = 'pval'
    elif 'p-value' in result.columns:
        p_col = 'p-value'
    else:
        st.error("The result does not contain a 'p-value' or 'pval' column.")
        return
    
    # Ensure that the p-value column contains numeric data
    if not pd.api.types.is_numeric_dtype(result[p_col]):
        st.error(f"The column '{p_col}' must contain numeric p-values.")
        return
    
    # Assign 'Status' based on p-value threshold
    result['Status'] = result[p_col].apply(lambda x: 'fit' if x < p_value_threshold else 'unfit')
    st.dataframe(result)
    
@st.fragment()
def plot_sem_model_step(model_spec, data):
    st.header("12. Plot the SEM Model")
    if st.button("Plot Model"):
        model = Model(model_spec)
        model.fit(data)
        try:
            fig = model.plot_model()
            st.pyplot(fig)
        except Exception as e:
            st.error(f"An error occurred while plotting the model: {e}")

def restart_app_step():
    if st.button("Restart"):
        st.experimental_rerun()

if __name__ == "__main__":
    main()
