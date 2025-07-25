import streamlit as st
import yaml
import os
import pandas as pd
from pyvis.network import Network
from collections import defaultdict
from pathlib import Path

st.set_page_config(page_title="Map of the World", layout="wide")
st.title("Map of the World - Children's Social Care")

# === Home page content ===
with st.expander("ℹ️ About...", expanded=False):
    st.markdown("""
    D2I project to map the data connections within the Children’s Social Care(CSC) ecosystem.
    (in progress)
    Inspired in part by the work within www.childrensservices.network/network.html
                
    *Key aims*
    
    """)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RELS_DIR = DATA_DIR / "relationships"
PARQUET_FILE = DATA_DIR / "index_data.parquet"
GRAPH_FILE = ROOT / "relationship_graph.html"

G = Network(height="700px", width="100%", directed=True, notebook=False)
G.force_atlas_2based()

# === Function to parse YAMLs and save as Parquet ===
def load_yaml_records(folder: Path):
    records = []
    for subfolder in folder.iterdir():
        if subfolder.is_dir():
            for file in subfolder.glob("*.yaml"):
                if file.name.startswith("0_template"):
                    continue
                with open(file, "r") as f:
                    data = yaml.safe_load(f)
                    data["filename"] = file.name
                    data["folder"] = subfolder.name
                    records.append(data)
    return records

def build_dataframe(records: list[dict]) -> pd.DataFrame:
    rows = []
    for r in records:
        rows.append({
            "name": r.get("name"),
            "type": r.get("@type"),
            "subtype": r.get("subtype", ""),
            "tags": ', '.join(r.get("tags", [])),
            "organisation": r.get("organisation", ""),
            "region": r.get("region", ""),
            "projects": ', '.join(r.get("projects", [])) if r.get("projects") else '',
            "folder": r.get("folder"),
            "filename": r.get("filename")
        })
    return pd.DataFrame(rows)

# === Create Parquet if missing ===
if not PARQUET_FILE.exists():
    with st.spinner("Building Parquet cache from YAMLs..."):
        records = load_yaml_records(DATA_DIR)
        df = build_dataframe(records)
        df.to_parquet(PARQUET_FILE, index=False)

# === Load Parquet and filter to 'data to insight' ===
df = pd.read_parquet(PARQUET_FILE)
df_subset = df[df["name"].str.lower().str.contains("data to insight", na=False)]

# === Load filtered nodes ===
node_degrees = defaultdict(int)
included_nodes = set()
node_metadata = {}
edges = []

# We no longer need folder_map – the label can come from type
for _, row in df_subset.iterrows():
    node_id = row["filename"].replace(".yaml", "")
    label_val = row["name"]
    label_type = row["type"] or "Unknown"
    included_nodes.add(node_id)
    node_metadata[node_id] = {
        "label": label_val,
        "title": f"{label_type}: {label_val}",
        "group": label_type
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

    G.set_options("""
    {
        "nodes": {
            "scaling": { "min": 10, "max": 30 },
            "font": { "size": 14 }
        },
        "edges": {
            "arrows": { "to": { "enabled": true } },
            "smooth": false
        },
        "interaction": {
            "navigationButtons": true,
            "zoomView": true
        },
        "layout": {
            "improvedLayout": true
        },
        "physics": {
            "enabled": true,
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 100,
                "springConstant": 0.08
            },
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": { "enabled": true, "iterations": 150 }
        }
    }
    """)

    G.write_html(str(GRAPH_FILE), notebook=False)
    st.markdown(f"### D2I Network View ({len(included_nodes)} nodes, {len(edges)} edges)")
    with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
        st.components.v1.html(f.read(), height=750, scrolling=False)
else:
    st.warning("No matching entities found for current filters.")
