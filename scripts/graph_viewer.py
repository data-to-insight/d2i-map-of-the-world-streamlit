# streamlit run scripts/graph_viewer.py
# Updated graph_viewer.py to support SCCM-aligned folders

import streamlit as st
import yaml
import os
from pyvis.network import Network

st.set_page_config(page_title="Network Graph", layout="wide")
st.title("🕸️ Relationship Graph Viewer")

data_dir = "data"
folders = [
    ("organizations", "Organization"),
    ("services", "Service"),
    ("plans", "Plan"),
    ("events", "Event"),
    ("collections", "Collection"),
    ("items", "Item"),
    ("resources", "Resource")
]
rels_dir = os.path.join(data_dir, "relationships")
graph_file = "relationship_graph.html"

G = Network(height="700px", width="100%", directed=True, notebook=False)
G.force_atlas_2based()

# Load YAML nodes
def load_entities(folder_name, node_type):
    folder_path = os.path.join(data_dir, folder_name)
    if not os.path.isdir(folder_path):
        return
    for file in os.listdir(folder_path):
        if file.endswith(".yaml"):
            with open(os.path.join(folder_path, file)) as f:
                data = yaml.safe_load(f)
                node_id = file.replace(".yaml", "")
                label = data.get("name", node_id)
                G.add_node(node_id, label=label, title=f"{node_type}: {label}", group=node_type)

# Load edges from relationships
def load_relationships(path):
    for file in os.listdir(path):
        if file.endswith(".yaml"):
            with open(os.path.join(path, file)) as f:
                data = yaml.safe_load(f)
                source = data.get("source")
                target = data.get("target")
                label = data.get("relationship_type", "relatesTo")
                if source and target:
                    G.add_edge(source, target, label=label, title=data.get("description", ""))

# Build graph
for folder, label in folders:
    load_entities(folder, label)
load_relationships(rels_dir)

G.write_html(graph_file, notebook=False)

st.markdown("### Interactive Network Graph")
with open(graph_file, 'r', encoding='utf-8') as f:
    graph_html = f.read()

st.components.v1.html(graph_html, height=750, scrolling=True)
