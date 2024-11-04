# Relationship_Analyzer.py

app_version = "0.1"
app_title = "OllaLab - Relationship Analyzer"
app_description = "Construct a graph and perform graph analysis on provided data."
app_icon = ":chart:"

import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import io
import json

st.title("Relationship Analyzer")

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

        num_pairs = st.number_input(
            "How many relationship pair types you want to specify?",
            min_value = 1,
            value = 1
        )

        edge_list = []
        columns = df.columns.tolist()

        for i in range(int(num_pairs)):
            st.write(f"### Specification for pair {i+1}")
            # Ask user to select "from" and "to" columns
            from_column = st.selectbox(f"Select the 'from' column for pair {i+1}", options=columns, key=f"from_column_{i}")
            to_column = st.selectbox(f"Select the 'to' column for pair {i+1}", options=columns, key=f"to_column_{i}")
            delimiter = st.text_input(
                f"Enter the delimiter used in 'from' and 'to' columns  for pair {i+1} (default is ',')",
                value=",", key=f"delimiter_{i}"
            )

            # Ask user to select "alias" column or upload alias file
            # This action replaces node values with corresponding aliases
            set_aliases_option = st.radio(
                f"Do you want to set aliases for node names for pair {i+1}?",
                options=["No","Select columns from data","Upload alias file"],
                key=f"set_aliases_option_{i}"
            )
            if set_aliases_option == "Select columns from data":
                node_name_column = st.selectbox(
                    f"Select the node name column for pair {i+1}",
                    options=columns, key=f"node_name_column_{i}"
                    )
                alias_column = st.selectbox(
                    f"Select the alias column for pair {i+1}",
                    options=columns, key=f"alias_column_{i}")
                alias_mapping = dict(zip(df[node_name_column].astype(str),df[alias_column].astype(str)))
            elif set_aliases_option == "Upload alias file":
                alias_file = st.file_uploader(
                    f"Upload a file with node names and corresponding aliases for pair {i+1}",
                    type=["csv", "tsv", "xlsx"], key=f"alias_file_{i}")
                if alias_file is not None:
                    alias_file_type = alias_file.name.split(".")[-1]
                    if alias_file_type == "csv":
                        alias_df = pd.read_csv(alias_file)
                    elif alias_file_type == "tsv":
                        alias_df = pd.read_csv(alias_file, sep="\t")
                    elif alias_file_type == "xlsx":
                        alias_df = pd.read_excel(alias_file)
                    else:
                        st.error("Unsupported file type")
                    alias_columns = alias_df.columns.tolist()
                    node_name_column = st.selectbox("Select the node name colum", options=alias_columns)
                    alias_column = st.selectbox("Select the alias column", options=alias_columns)
                    alias_mapping = dict(zip(alias_df[node_name_column].astype(str), alias_df[alias_column].astype(str)))
                else:
                    alias_mapping = {}
            else:
                alias_mapping = {}

            # Build the graph list for this pair
            for idx, row in df.iterrows():
                from_nodes = str(row[from_column]).split(delimiter)
                to_nodes = str(row[to_column]).split(delimiter)

                for from_node in from_nodes:
                    from_node = from_node.strip()
                    from_node = alias_mapping.get(from_node, from_node)
                    for to_node in to_nodes:
                        to_node = to_node.strip()
                        to_node = alias_mapping.get(to_node, to_node)
                        #G.add_edge(from_node, to_node)
                        edge_list.append((from_node, to_node))

        G.add_edges_from(edge_list)
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

    # Compute node degrees
    degrees = dict(G.degree())
    degree_df = pd.DataFrame.from_dict(degrees, orient="index", columns=["Degree"])
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)

    with st.sidebar:
        # Allow users to filter the graph
        st.subheader("Graph Filters")

        # Degree threshold slider
        degree_threshold = st.slider(
            "Minimum Degree",
            min_value=int(degree_df["Degree"].min()),
            max_value=int(degree_df["Degree"].max()),
            value=int(degree_df["Degree"].min()),
        )

        # Degree centrality slider
        degree_centrality_threshold = st.slider(
            "Minimum Degree Centrality",
            min_value = float(min(degree_centrality.values())),
            max_value = float(max(degree_centrality.values())),
            value = float(min(betweenness_centrality.values()))
        )

        # Betweeness centrality slider
        betweeness_centrality_threshold = st.slider(
            "Select minimum betweeness centrality of nodes to display",
            min_value = float(min(betweenness_centrality.values())),
            max_value = float(max(betweenness_centrality.values())),
            value = float(min(betweenness_centrality.values()))
        )

        # Closeness centrality slider
        closeness_centrality_threshold = st.slider(
            "Minimum Closeness Centrality",
            min_value = float(min(closeness_centrality.values())),
            max_value = float(max(closeness_centrality.values())),
            value = float(min(closeness_centrality.values()))
        )

        # Allow users to select nodes to display
        node_list = list(G.nodes())
        selected_nodes = st.multiselect(
            "Select specific nodes to include (leave empty to include all)",
            options=node_list
        )

    # Filter nodes based on filters
    nodes_to_keep = [
        node for node in G.nodes()
        if degrees[node] >= degree_threshold
        and degree_centrality[node] >= degree_centrality_threshold
        and betweenness_centrality[node] >= betweeness_centrality_threshold
        and closeness_centrality[node] >= closeness_centrality_threshold
        and (not selected_nodes or node in selected_nodes)
    ]
    G_filtered = G.subgraph(nodes_to_keep)

    # Plot the filtered graph
    st.subheader("Filtered Graph")
    fig_filtered = plot_graph(G_filtered)
    st.plotly_chart(fig_filtered)

    # Compute graph statistics
    st.subheader("Node Statistics")
    degrees_filtered = dict(G_filtered.degree())
    degree_centrality_filtered = nx.degree_centrality(G_filtered)
    betweenness_centrality_filtered = nx.betweenness_centrality(G_filtered)
    closeness_centrality_filtered = nx.closeness_centrality(G_filtered)

    stats_df = pd.DataFrame({
        "Node": list(G_filtered.nodes()),
        "Degree": [degrees_filtered[node] for node in G_filtered.nodes()],
        "Degree Centrality": [degree_centrality_filtered[node] for node in G_filtered.nodes()],
        "Betweenness Centrality": [betweenness_centrality_filtered[node] for node in G_filtered.nodes()],
        "Closeness Centrality": [closeness_centrality_filtered[node] for node in G_filtered.nodes()],
    })

    # Display the sortable table
    st.dataframe(stats_df.sort_values(by="Degree", ascending=False))

