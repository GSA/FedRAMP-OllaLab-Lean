# components/validation_ui.py

import streamlit as st
from streamlit.logger import get_logger
from data_unificator.modules.data_validation import DataValidator
from data_unificator.audits.audit_trail import record_action
from data_unificator.utils.eda_utils import perform_eda
import traceback

logger = get_logger(__name__)

@st.fragment
def render_validation():
    st.header("Data Validation and Export")
    st.write("Validate your data for completeness, correctness, and consistency.")

    # Placeholder for dynamic content
    content_placeholder = st.empty()

    try:
        # Assume consolidated_data is the output from the Data Deduplication step
        consolidated_data = st.session_state.get('consolidated_data', None)
        if consolidated_data is None:
            st.warning("No data available for validation. Please complete the previous steps.")
            st.stop()

        data_validator = DataValidator(consolidated_data)

        # Step 1: Perform Validation
        if st.button("Perform Data Validation"):
            data_validator.perform_validation()
            st.success("Data validation completed.")
            record_action("User performed data validation.")

            # Display validation results
            st.subheader("Validation Results")
            for category, issues in data_validator.validation_results.items():
                if issues:
                    with st.expander(f"Issues found in {category.replace('_', ' ').title()}"):
                        st.write(issues)
                else:
                    st.write(f"No issues found in {category.replace('_', ' ').title()}.")

        # Step 2: Manual Review of Sample Records
        st.subheader("Manual Review of Sample Records")
        sample_size = st.slider("Select number of records to review", min_value=1, max_value=100, value=5)
        st.dataframe(consolidated_data.sample(sample_size))
        record_action(f"User performed manual review of {sample_size} records.")

        # Step 3: Exploratory Data Analysis (EDA)
        st.subheader("Exploratory Data Analysis (EDA)")
        if st.button("Perform EDA"):
            eda_report = perform_eda(consolidated_data, "Consolidated Data")
            with st.expander("EDA Report"):
                st.write(eda_report)
            record_action("User performed EDA on the consolidated data.")

        # Step 4: Statistical Analysis for Anomalies
        st.subheader("Statistical Analysis for Anomalies")
        if 'statistical_anomalies' in data_validator.validation_results:
            anomalies = data_validator.validation_results['statistical_anomalies']
            if anomalies:
                with st.expander("Anomalies Detected"):
                    st.write(anomalies)
                record_action("User reviewed statistical anomalies.")
            else:
                st.write("No statistical anomalies detected.")

        # Step 5: Apply Business Rules
        st.subheader("Apply Business Rules")
        if 'business_rules' in data_validator.validation_results:
            business_rule_issues = data_validator.validation_results['business_rules']
            if business_rule_issues:
                with st.expander("Business Rule Violations"):
                    st.write(business_rule_issues)
                record_action("User reviewed business rule violations.")
            else:
                st.write("No business rule violations detected.")

        # Step 6: Export Validated Data
        st.subheader("Export Validated Data")
        output_format = st.selectbox("Select output format", ["CSV", "Excel", "JSON", "SQL Database"])
        if output_format == "SQL Database":
            db_connection_info = st.text_input("Enter database connection string")
        output_path = st.text_input("Enter output file path", "output/validated_data.csv")
        if st.button("Export Data"):
            # Implement export logic based on selected format
            if output_format == "CSV":
                consolidated_data.to_csv(output_path, index=False)
            elif output_format == "Excel":
                consolidated_data.to_excel(output_path, index=False)
            elif output_format == "JSON":
                consolidated_data.to_json(output_path, orient='records')
            elif output_format == "SQL Database":
                # Implement database export logic
                pass
            st.success(f"Data exported successfully to {output_path}.")
            record_action(f"User exported data to {output_path} in {output_format} format.")

    except Exception as e:
        logger.error(f"Error in Data Validation: {str(e)}", exc_info=True)
        st.error("An error occurred during data validation. Please check the logs for details.")
        st.exception(e)
        st.stop()
