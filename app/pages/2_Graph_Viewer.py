# app/pages/2_Graph_Viewer.py
import streamlit as st
import yaml
import os
from pathlib import Path
from pyvis.network import Network

st.set_page_config(page_title="Network Graph", layout="wide")
st.title("🕸️ Relationship Graph Viewer")

# === Paths
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
graph_file = ROOT / "relationship_graph.html"

G = Network(height="700px", width="100%", directed=True)
G.force_atlas_2based()

# === Filters from Home page
filters = st.session_state.get("filters", {})
# show_ssd_only = st.checkbox("Only show SSD-related entities")

# === Filter logic
def match_filters(data, kind):
    if filters.get("folder") not in ["All", None] and filters["folder"] != kind:
        return False
    if filters.get("tag") and filters["tag"].lower() not in [t.lower() for t in data.get("tags", [])]:
        return False
    if filters.get("region") and filters["region"].lower() not in data.get("region", "").lower():
        return False
    if filters.get("search") and filters["search"].lower() not in data.get("name", "").lower():
        return False
    # if show_ssd_only and "standard_safeguarding_dataset" not in data.get("projects", []):
    #     return False
    return True

# === Load Nodes
def load_entities(path, node_type):
    for file in os.listdir(path):
        if file.endswith(".yaml"):
            with open(path / file) as f:
                data = yaml.safe_load(f)
                if match_filters(data, node_type.lower() + "s"):
                    node_id = file.replace(".yaml", "")
                    label = data.get("name", node_id)
                    G.add_node(node_id, label=label, title=f"{node_type}: {label}", group=node_type)

# === Load Edges
def load_relationships(path):
    for file in os.listdir(path):
        if file.endswith(".yaml"):
            with open(path / file) as f:
                data = yaml.safe_load(f)
                source = data.get("source")
                target = data.get("target")
                label = data.get("relationship_type", "relatesTo")
                if source and target:
                    G.add_edge(source, target, label=label, title=data.get("description", ""))

load_entities(DATA_DIR / "people", "Person")
load_entities(DATA_DIR / "orgs", "Organisation")
load_entities(DATA_DIR / "projects", "Project")
load_relationships(DATA_DIR / "relationships")

G.write_html(str(graph_file), notebook=False)

st.markdown("### Interactive Network Graph")
with open(str(graph_file), 'r', encoding='utf-8') as f:
    st.components.v1.html(f.read(), height=750, scrolling=True)
