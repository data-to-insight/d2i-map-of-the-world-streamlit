# Updated graph_viewer.py to support SCCM-aligned folders with filters, sizing by degree, and empty-state warning

import streamlit as st
import yaml
import os
from pyvis.network import Network
from collections import defaultdict
from pathlib import Path

st.set_page_config(page_title="Children's Services Map of the World (SCCM)", layout="wide")
st.title("Children's Services Map of the World")

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RELS_DIR = DATA_DIR / "relationships"
GRAPH_FILE = ROOT / "relationship_graph.html"

G = Network(height="700px", width="100%", directed=True, notebook=False)
G.force_atlas_2based()

# === Sidebar filters with default ===
st.sidebar.header("🔍 Search Filters")
search_text = st.sidebar.text_input("Search (name/tags/org):", st.session_state.get("filters", {}).get("search", ""))
folder_filter = st.sidebar.selectbox("Entity Type", [
    "All",
    "organizations",
    "services",
    "plans",
    "events",
    "relationships",
    "collections",
    "items",
    "resources"
], index=0 if "filters" not in st.session_state else [
    "All",
    "organizations",
    "services",
    "plans",
    "events",
    "relationships",
    "collections",
    "items",
    "resources"
].index(st.session_state.get("filters", {}).get("folder", "All")))
region_filter = st.sidebar.text_input("Region contains:", st.session_state.get("filters", {}).get("region", ""))
tag_filter = st.sidebar.text_input("Tag contains:", st.session_state.get("filters", {}).get("tag", ""))

# === Reset Filters Button ===
if st.sidebar.button("Reset Filters"):
    st.session_state["filters"] = {
        "tag": "",
        "region": "",
        "folder": "All",
        "search": ""
    }
    st.rerun()

# === Default filters on first load ===
if "filters" not in st.session_state:
    st.session_state["filters"] = {
        "tag": "",
        "region": "",
        "folder": "organizations",
        "search": "data_to_insight"
    }

# === Sync filters with input ===
st.session_state["filters"].update({
    "search": search_text,
    "folder": folder_filter,
    "region": region_filter,
    "tag": tag_filter
})

filters = st.session_state["filters"]

# === Load filtered nodes ===
node_degrees = defaultdict(int)
included_nodes = set()
node_metadata = {}
edges = []

folder_map = {
    "organizations": "Organization",
    "services": "Service",
    "plans": "Plan",
    "events": "Event",
    "collections": "Collection",
    "items": "Item",
    "resources": "Resource"
}

for folder, label in folder_map.items():
    folder_path = DATA_DIR / folder
    if not folder_path.exists():
        continue
    for file in os.listdir(folder_path):
        if file.endswith(".yaml") and not file.startswith("0_template"):
            path = folder_path / file
            with open(path) as f:
                data = yaml.safe_load(f)
                node_id = file.replace(".yaml", "")
                label_val = data.get("name", node_id)
                search_target = ' '.join([
                    label_val,
                    node_id,
                    data.get("organisation", ""),
                    ', '.join(data.get("tags", []))
                ]).lower()

                # Apply filters
                if filters.get("folder") not in ["All", None] and filters["folder"] != folder:
                    continue
                if filters.get("tag") and filters["tag"].lower() not in ', '.join(data.get("tags", [])).lower():
                    continue
                if filters.get("region") and filters["region"].lower() not in data.get("region", "").lower():
                    continue
                if filters.get("search") and filters["search"].lower() not in search_target:
                    continue

                included_nodes.add(node_id)
                node_metadata[node_id] = {
                    "label": label_val,
                    "title": f"{label}: {label_val}",
                    "group": label
                }

# === Load and filter relationships ===
for file in os.listdir(RELS_DIR):
    if file.endswith(".yaml") and not file.startswith("0_template"):
        with open(RELS_DIR / file) as f:
            data = yaml.safe_load(f)
            source = data.get("source")
            target = data.get("target")
            label = data.get("relationship_type", "relatesTo")
            if source in included_nodes or target in included_nodes:
                node_degrees[source] += 1
                node_degrees[target] += 1
                included_nodes.add(source)
                included_nodes.add(target)
                edges.append((source, target, label, data.get("description", "")))

# === Render Graph ===
if included_nodes:
    for node_id in included_nodes:
        meta = node_metadata.get(node_id, {
            "label": node_id,
            "title": node_id,
            "group": "Unclassified"
        })
        degree = node_degrees.get(node_id, 1)
        size = 10 + degree * 2
        title = f"{meta['title']}<br>Degree: {degree}"
        G.add_node(node_id, label=meta["label"], title=title, group=meta["group"], size=size)

    for source, target, label, desc in edges:
        G.add_edge(source, target, label=label, title=desc)

    G.show_buttons(filter_=['physics'])
    G.toggle_physics(True)
    G.set_options("""
    {
    "nodes": {
        "scaling": {
        "min": 10,
        "max": 30
        }
    },
    "interaction": {
        "navigationButtons": true,
        "zoomView": true
    },
    "layout": {
        "improvedLayout": true
    },
    "physics": {
        "forceAtlas2Based": {
        "gravitationalConstant": -50,
        "centralGravity": 0.01,
        "springLength": 100,
        "springConstant": 0.08
        },
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {
        "iterations": 150
        }
    }
    }
    """)

    G.write_html(str(GRAPH_FILE), notebook=False)
    st.markdown(f"### Interactive Network Graph ({len(included_nodes)} nodes, {len(edges)} edges)")
    with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
        st.components.v1.html(f.read(), height=750, scrolling=True)
else:
    st.warning("No matching entities found for current filters.")

# === Home page content ===
with st.expander("ℹ️ About the Map", expanded=False):
    st.markdown("""
            
    Data connections within the Children’s Services ecosystem.

    tbc - some project desc still to come here.
        
                
    """)
