# utils/eda_utils.py

from autoviz.AutoViz_Class import AutoViz_Class
import networkx as nx
from networkx import DiGraph, draw
import matplotlib.pyplot as plt
import pandas as pd
from data_unificator.utils.logging_utils import log_error,

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
        return eda_report # display logistics will be handled by the caller function
    except Exception as e:
        log_error(f"EDA - {str(e)} - {title}")
        return f"Error generating EDA report: {str(e)}"

def extract_hierarchy(df, column_separator='.'):
    """
    Extract and visualize the hierarchy
    from a dataframe with data that may or may not been flattened
    """
    hierarchy = DiGraph()
    if any(column_separator in col for col in df.columns):
        for col in df.columns:
            parts = col.split(column_separator)
            for i in range(1,len(parts)):
                parent, child = column_separator.join(parts[:i]), column_separator.join[parts[:i+1]]
                hierarchy.add_edge(parent,child)
    return hierarchy # len() will be zero if no hierarchy detected           

def visualize_hierarchy(hierarchy, save_path=None):
    """
    Visualize and optionally save the hierarchy
    """
    plt.figure(figsize=(10,10))
    pos = hierarchy_layout(hierarchy)
    draw(hierarchy, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=10)
    if save_path:
        plt.savefig(save_path)
    plt.show()

def hierarchy_layout(hierarchy):
    """
    Custom layout function for hierarchy
    """
    return nx.spring_layout(hierarchy)