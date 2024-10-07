# utils/eda_utils.py

import os
import networkx as nx
from networkx import DiGraph, draw
import matplotlib.pyplot as plt
import pandas as pd
from ydata_profiling import ProfileReport
from data_unificator.utils.logging_utils import log_error,log_event

def perform_eda(df, file_path):
    """
    Performs exploratory data analysis and returns an HTML report.
    The report is saved in the 'eda_report' folder at the same level as the file_path.
    """
    try:
        # Create the 'eda_report' folder at the same directory level as file_path
        base_dir = os.path.dirname(file_path)
        eda_report_dir = os.path.join(base_dir, 'eda_report')
        os.makedirs(eda_report_dir, exist_ok=True)

        # Generate the EDA report
        profile = ProfileReport(df, title='EDA Report', explorative=True)

        # Save the report to the 'eda_report' folder
        file_name = os.path.basename(file_path)
        report_file_name = f"{os.path.splitext(file_name)[0]}_eda_report.html"
        report_file_path = os.path.join(eda_report_dir, report_file_name)
        profile.to_file(report_file_path)

        # Read the report HTML content
        with open(report_file_path, 'r', encoding='utf-8') as f:
            eda_html = f.read()

        return eda_html

    except Exception as e:
        log_error(f"Error performing EDA: {str(e)}")
        return None


def extract_hierarchy(df, column_separator='.'):
    """
    Extracts the hierarchy from a DataFrame based on column names.
    """
    hierarchy = nx.DiGraph()
    if any(column_separator in col for col in df.columns):
        for col in df.columns:
            parts = col.split(column_separator)
            for i in range(1, len(parts)):
                parent = column_separator.join(parts[:i])
                child = column_separator.join(parts[:i+1])
                hierarchy.add_edge(parent, child)
    else:
        log_event("No hierarchy detected in the DataFrame columns.")
    return hierarchy    

def visualize_hierarchy(hierarchy, save_path):
    """
    Visualizes the data hierarchy and saves the visualization to a file.
    """
    try:
        import matplotlib.pyplot as plt
        import networkx as nx

        if len(hierarchy.nodes) == 0:
            log_event("No hierarchy to visualize")
            return

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(hierarchy)
        nx.draw(hierarchy, pos, with_labels=True, node_size=2000, node_color='lightblue', arrows=True)
        plt.savefig(save_path)
        plt.close()
    except Exception as e:
        log_error(f"Error visualizing hierarchy: {str(e)}")


def hierarchy_layout(hierarchy):
    """
    Custom layout function for hierarchy
    """
    return nx.spring_layout(hierarchy)