# utils/eda_utils.py

from autoviz.AutoViz_Class import AutoViz_Class
import pandas as pd
import streamlit as st

def perform_eda(df, title="EDA Report"):
    """
    Perform EDA using AutoViz and display results.
    """
    AV = AutoViz_Class()
    st.write(f"Generating EDA report for {title}...")
    try:
        eda_report = AV.AutoViz(
            filename="",
            dfte=df,
            depVar='',
            verbose=0,
            lowess=False,
            chart_format='png',
            max_rows_analyzed=150000,
            max_cols_analyzed=30
        )
        st.pyplot(eda_report)
        return "EDA report generated successfully."
    except Exception as e:
        st.error(f"Error generating EDA report: {str(e)}")
        return f"Error generating EDA report: {str(e)}"

