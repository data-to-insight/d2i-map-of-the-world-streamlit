# streamlit run scripts/graph_viewer.py

import streamlit as st
import yaml
import os
from pyvis.network import Network


st.set_page_config(page_title="Network Graph", layout="wide")
st.title("🕸️ Relationship Graph Viewer")

# Define folders
data_dir = "data"
people_dir = os.path.join(data_dir, "people")
orgs_dir = os.path.join(data_dir, "orgs")
proj_dir = os.path.join(data_dir, "projects")
rels_dir = os.path.join(data_dir, "relationships")
graph_file = "relationship_graph.html"

# Create network
G = Network(height="700px", width="100%", directed=True, notebook=False)
G.force_atlas_2based()

# Load YAML nodes
def load_entities(path, node_type):
    for file in os.listdir(path):
        if file.endswith(".yaml"):
            with open(os.path.join(path, file)) as f:
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
load_entities(people_dir, "Person")
load_entities(orgs_dir, "Organisation")
load_entities(proj_dir, "Project")
load_relationships(rels_dir)

# G.show(graph_file) # issue with pyvis 0.3.2+ when run outside .ipynb context
G.write_html(graph_file, notebook=False)

# Embed the HTML graph in Streamlit
st.markdown("### Interactive Network Graph")
with open(graph_file, 'r', encoding='utf-8') as f:
    graph_html = f.read()

st.components.v1.html(graph_html, height=750, scrolling=True)

