# components/validation_ui.py

import streamlit as st
from streamlit.logger import get_logger
from data_unificator.modules.data_validation import DataValidator
from data_unificator.audits.audit_trail import record_action
from data_unificator.utils.data_utils import perform_eda
import traceback

logger = get_logger(__name__)

def initialize_session_state():
    if 'validated_data' not in st.session_state:
        st.session_state['validated_data'] = None
    if 'validation_actions' not in st.session_state:
        st.session_state['validation_actions'] = []

@st.fragment
def render_validation():
    st.header("Data Validation and Export")
    st.write("Validate your data for completeness, correctness, and consistency.")

    initialize_session_state()

    try:
        consolidated_data = st.session_state.get('consolidated_data', None)
        if consolidated_data is None:
            st.warning("No consolidated data available for validation. Please complete the Data Deduplication step or upload data.")
        
        data_validator = DataValidator(consolidated_data)

        # Step 1: Perform Validation
        if st.button("Perform Data Validation"):
            try:
                data_validator.perform_validation()
                st.session_state['validated_data'] = consolidated_data
                st.success("Data validation completed.")
                record_action("User performed data validation.")
                st.session_state['validation_actions'].append("Performed data validation.")

                # Display validation results
                st.subheader("Validation Results")
                for category, issues in data_validator.validation_results.items():
                    if issues:
                        with st.expander(f"Issues found in {category.replace('_', ' ').title()}"):
                            st.write(issues)
                    else:
                        st.write(f"No issues found in {category.replace('_', ' ').title()}.")
            except Exception as e:
                logger.error(f"Error performing data validation: {str(e)}", exc_info=True)
                st.error("Failed to perform data validation.")
                st.exception(e)

        # Step 2: Manual Review of Sample Records
        st.subheader("Manual Review of Sample Records")
        sample_size = st.slider("Select number of records to review", min_value=1, max_value=100, value=5)
        if st.button("Review Sample Records"):
            try:
                sample_records = consolidated_data.sample(sample_size)
                st.dataframe(sample_records)
                record_action(f"User reviewed a sample of {sample_size} records.")
                st.session_state['validation_actions'].append(f"Reviewed {sample_size} sample records.")
            except Exception as e:
                logger.error(f"Error reviewing sample records: {str(e)}", exc_info=True)
                st.error("Failed to review sample records.")
                st.exception(e)

        # Step 3: Exploratory Data Analysis (EDA)
        st.subheader("Exploratory Data Analysis (EDA)")
        if st.button("Perform EDA"):
            try:
                eda_report = perform_eda(consolidated_data, "Consolidated Data")
                with st.expander("EDA Report"):
                    st.write(eda_report)
                st.success("EDA completed.")
                record_action("User performed EDA on the consolidated data.")
                st.session_state['validation_actions'].append("Performed EDA.")
            except Exception as e:
                logger.error(f"Error performing EDA: {str(e)}", exc_info=True)
                st.error("Failed to perform EDA.")
                st.exception(e)

        # Step 4: Statistical Analysis for Anomalies
        st.subheader("Statistical Analysis for Anomalies")
        if st.button("Analyze Statistical Anomalies"):
            try:
                anomalies = data_validator.detect_statistical_anomalies()
                if anomalies:
                    with st.expander("Anomalies Detected"):
                        st.write(anomalies)
                    record_action("User reviewed statistical anomalies.")
                    st.session_state['validation_actions'].append("Reviewed statistical anomalies.")
                else:
                    st.write("No statistical anomalies detected.")
            except Exception as e:
                logger.error(f"Error analyzing statistical anomalies: {str(e)}", exc_info=True)
                st.error("Failed to analyze statistical anomalies.")
                st.exception(e)

        # Step 5: Apply Business Rules
        st.subheader("Apply Business Rules")
        if st.button("Apply Business Rules"):
            try:
                business_rule_issues = data_validator.apply_business_rules()
                if business_rule_issues:
                    with st.expander("Business Rule Violations"):
                        st.write(business_rule_issues)
                    record_action("User reviewed business rule violations.")
                    st.session_state['validation_actions'].append("Reviewed business rule violations.")
                else:
                    st.write("No business rule violations detected.")
            except Exception as e:
                logger.error(f"Error applying business rules: {str(e)}", exc_info=True)
                st.error("Failed to apply business rules.")
                st.exception(e)

        # Step 6: Export Validated Data
        st.subheader("Export Validated Data")
        output_format = st.selectbox("Select output format", ["CSV", "Excel", "JSON", "SQL Database"])
        db_connection_info = None
        if output_format == "SQL Database":
            db_connection_info = st.text_input("Enter database connection string")
        output_path = st.text_input("Enter output file path", 
                                    st.session_state.get('validation_output_path', "output/validated_data.csv"))

        if st.button("Export Data"):
            try:
                if output_format == "CSV":
                    consolidated_data.to_csv(output_path, index=False)
                elif output_format == "Excel":
                    consolidated_data.to_excel(output_path, index=False)
                elif output_format == "JSON":
                    consolidated_data.to_json(output_path, orient='records')
                elif output_format == "SQL Database":
                    if not db_connection_info:
                        st.error("Please provide a valid database connection string.")
                        st.stop()
                    data_validator.export_to_sql(db_connection_info, output_path)
                st.session_state['validation_output_path'] = output_path
                st.success(f"Data exported successfully to {output_path}.")
                record_action(f"User exported data to '{output_path}' in {output_format} format.")
                st.session_state['validation_actions'].append(f"Exported data to {output_path} as {output_format}.")
            except Exception as e:
                logger.error(f"Error exporting data: {str(e)}", exc_info=True)
                st.error("Failed to export data.")
                st.exception(e)

    except Exception as e:
        logger.error(f"Error in Data Validation: {str(e)}", exc_info=True)
        st.error("An error occurred during data validation. Please check the logs for details.")
        st.exception(e)
        st.stop()
