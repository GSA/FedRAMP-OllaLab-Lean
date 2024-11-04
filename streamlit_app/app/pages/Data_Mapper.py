# Data_Mapper.py

app_version = "0.1"
app_title = "OllaLab - Data Mapper"
app_description = "Construct a graph and perform graph analysis."
app_icon = ":chart:"

import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import io
import json

st.title("NetworkX Graph Visualizer")

# File uploader
uploaded_file = st.file_uploader(
    "Choose a file",
    type=[
        "txt",
        "csv",
        "tsv",
        "xlsx",
        "pajek",
        "graphml",
        "gml",
        "json",
    ],
)

if uploaded_file is not None:
    file_type = uploaded_file.name.split(".")[-1]

    # Initialize an empty graph
    G = nx.Graph()

    # Process based on file type
    if file_type in ["csv", "tsv", "xlsx"]:
        # Read the file into a pandas DataFrame
        if file_type == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_type == "tsv":
            df = pd.read_csv(uploaded_file, sep="\t")
        elif file_type == "xlsx":
            df = pd.read_excel(uploaded_file)

        st.write("Data Preview:")
        st.dataframe(df.head())

        # Ask user to select "from" and "to" columns
        columns = df.columns.tolist()
        from_column = st.selectbox("Select the 'from' column", options=columns)
        to_column = st.selectbox("Select the 'to' column", options=columns)
        delimiter = st.text_input(
            "Enter the delimiter used in 'from' and 'to' columns (default is ',')",
            value=",",
        )

        # Build the graph
        for idx, row in df.iterrows():
            from_nodes = str(row[from_column]).split(delimiter)
            to_nodes = str(row[to_column]).split(delimiter)
            for from_node in from_nodes:
                from_node = from_node.strip()
                for to_node in to_nodes:
                    to_node = to_node.strip()
                    G.add_edge(from_node, to_node)

        st.success("Graph has been created.")

    elif file_type == "txt":
        # Read the file content
        content = uploaded_file.read().decode("utf-8")
        # Assume each line is a node and its neighbors
        G = nx.parse_adjlist(content.split("\n"))
        st.success("Graph has been created from adjacency list.")

    elif file_type == "pajek":
        G = nx.read_pajek(uploaded_file)
        st.success("Graph has been created from Pajek file.")

    elif file_type == "graphml":
        G = nx.read_graphml(uploaded_file)
        st.success("Graph has been created from GraphML file.")

    elif file_type == "gml":
        G = nx.read_gml(uploaded_file)
        st.success("Graph has been created from GML file.")

    elif file_type == "json":
        data = json.load(uploaded_file)
        G = nx.node_link_graph(data)
        st.success("Graph has been created from JSON file.")

    else:
        st.error("Unsupported file type.")

    # Function to plot the graph
    def plot_graph(G):
        pos = nx.spring_layout(G)
        edge_x = []
        edge_y = []

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=0.5, color="#888"),
            hoverinfo="none",
            mode="lines",
        )

        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(str(node))

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            hoverinfo="text",
            text=node_text,
            textposition="top center",
            marker=dict(showscale=False, color="blue", size=10, line=dict(width=2)),
        )

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )
        return fig

    # Plot the original graph
    st.subheader("Original Graph")
    fig = plot_graph(G)
    st.plotly_chart(fig)

    # Compute node degrees
    degrees = dict(G.degree())
    degree_df = pd.DataFrame.from_dict(degrees, orient="index", columns=["Degree"])

    # Allow users to filter the graph
    st.subheader("Filter Graph")
    degree_threshold = st.slider(
        "Select minimum degree of nodes to display",
        min_value=int(degree_df["Degree"].min()),
        max_value=int(degree_df["Degree"].max()),
        value=int(degree_df["Degree"].min()),
    )

    # Filter nodes based on degree
    nodes_to_keep = [node for node, deg in degrees.items() if deg >= degree_threshold]
    G_filtered = G.subgraph(nodes_to_keep)

    # Plot the filtered graph
    st.subheader("Filtered Graph")
    fig_filtered = plot_graph(G_filtered)
    st.plotly_chart(fig_filtered)

    # Compute graph statistics
    st.subheader("Node Statistics")
    degree_centrality = nx.degree_centrality(G_filtered)
    betweenness_centrality = nx.betweenness_centrality(G_filtered)
    closeness_centrality = nx.closeness_centrality(G_filtered)

    stats_df = pd.DataFrame({
        "Node": list(G_filtered.nodes()),
        "Degree": [degrees[node] for node in G_filtered.nodes()],
        "Degree Centrality": [degree_centrality[node] for node in G_filtered.nodes()],
        "Betweenness Centrality": [betweenness_centrality[node] for node in G_filtered.nodes()],
        "Closeness Centrality": [closeness_centrality[node] for node in G_filtered.nodes()],
    })

    # Display the sortable table
    st.dataframe(stats_df.sort_values(by="Degree", ascending=False))

