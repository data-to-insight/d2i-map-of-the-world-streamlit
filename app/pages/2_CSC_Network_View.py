import streamlit as st
import yaml
import os
from pyvis.network import Network
from collections import defaultdict

st.set_page_config(page_title="Network Graph", layout="wide")
st.title("Network Graph")

data_dir = "data" # retained outside the streamlit structure

folders = [
    # naming/spelling in line with SCCM
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

# === Read filters from session ===
filters = st.session_state.get("filters", {})

# === Filter logic ===
def match_filters(data, kind):
    if filters.get("folder") not in ["All", None] and filters["folder"] != kind:
        return False
    if filters.get("tag") and filters["tag"].lower() not in [t.lower() for t in data.get("tags", [])]:
        return False
    if filters.get("region") and filters["region"].lower() not in data.get("region", "").lower():
        return False
    if filters.get("search") and filters["search"].lower() not in data.get("name", "").lower():
        return False
    return True

# Track node degrees for sizing
node_degrees = defaultdict(int)

# Load YAML nodes
included_nodes = set()

node_metadata = {}

def load_entities(folder_name, node_type):
    folder_path = os.path.join(data_dir, folder_name)
    if not os.path.isdir(folder_path):
        return
    for file in os.listdir(folder_path):
        if file.endswith(".yaml") and not file.startswith("0_template"):
            with open(os.path.join(folder_path, file)) as f:
                data = yaml.safe_load(f)
                if not match_filters(data, folder_name):
                    continue
                node_id = file.replace(".yaml", "")
                label = data.get("name", node_id)
                included_nodes.add(node_id)
                node_metadata[node_id] = {
                    "label": label,
                    "title": f"{node_type}: {label}",
                    "group": node_type
                }

# Load edges from relationships
edges = []

def load_relationships(path):
    for file in os.listdir(path):
        if file.endswith(".yaml") and not file.startswith("0_template"):
            with open(os.path.join(path, file)) as f:
                data = yaml.safe_load(f)
                source = data.get("source")
                target = data.get("target")
                label = data.get("relationship_type", "relatesTo")
                if source in included_nodes and target in included_nodes:
                    node_degrees[source] += 1
                    node_degrees[target] += 1
                    edges.append((source, target, label, data.get("description", "")))

# Build graph
for folder, label in folders:
    load_entities(folder, label)
load_relationships(rels_dir)

if included_nodes:
    # Add nodes with size scaling
    for node_id, meta in node_metadata.items():
        degree = node_degrees.get(node_id, 1)
        size = 10 + degree * 2
        G.add_node(node_id, label=meta["label"], title=meta["title"], group=meta["group"], size=size)

    # Add edges
    for source, target, label, desc in edges:
        G.add_edge(source, target, label=label, title=desc)

    G.write_html(graph_file, notebook=False)

    st.markdown("### Interactive Network Graph") # sub heading on page
    with open(graph_file, 'r', encoding='utf-8') as f:
        graph_html = f.read()

    st.components.v1.html(graph_html, height=750, scrolling=True)
else:
    st.warning("No matching entities found for current filters. Try adjusting your search.")
