import streamlit as st
import pandas as pd
from pyvis.network import Network
from collections import defaultdict
from pathlib import Path
import yaml
import os

st.set_page_config(page_title="Network Graph", layout="wide")
st.title("Children's Social Care Network Graph")

# === Paths ===
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RELS_DIR = DATA_DIR / "relationships"
PARQUET_FILE = DATA_DIR / "index_data.parquet"
GRAPH_FILE = ROOT / "relationship_graph.html"


# === Paths ===
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RELS_DIR = DATA_DIR / "relationships"
PARQUET_FILE = DATA_DIR / "index_data.parquet"

# # === Optional toggle: D2I-only filter ===
# use_d2i_filter = st.sidebar.checkbox("Limit to Data to Insight?", value=False)

# # === Read filters from session ===
filters = st.session_state.get("filters", {})
# if use_d2i_filter:
#     filters["search"] = "data to insight"

# === Load Parquet data ===
if not PARQUET_FILE.exists():
    st.error("Parquet file not found. Run Home page first to (re)generate it.")
    st.stop()
else:
    df = pd.read_parquet(PARQUET_FILE)

# === Apply filters ===
if filters.get("search"):
    df = df[df.apply(lambda r: filters["search"].lower() in (
        str(r["name"]) + str(r["tags"]) + str(r["organisation"])
    ).lower(), axis=1)]

if filters.get("folder") not in [None, "All"]:
    df = df[df["folder"] == filters["folder"]]

if filters.get("region"):
    df = df[df["region"].str.lower().str.contains(filters["region"].lower(), na=False)]

if filters.get("tag"):
    df = df[df["tags"].str.lower().str.contains(filters["tag"].lower(), na=False)]

# === Build graph ===
G = Network(height="700px", width="100%", directed=True, notebook=False)
G.force_atlas_2based()
included_nodes = set()
node_metadata = {}
node_degrees = defaultdict(int)
edges = []

# === Add nodes from filtered dataframe ===
for _, row in df.iterrows():
    node_id = row["filename"].replace(".yaml", "")
    label = row["name"] or node_id
    included_nodes.add(node_id)
    node_metadata[node_id] = {
        "label": label,
        "title": f"{row['type']}: {label}",
        "group": row["type"]
    }

# === Add edges if both source/target present ===
for file in os.listdir(RELS_DIR):
    if file.endswith(".yaml") and not file.startswith("0_template"):
        with open(RELS_DIR / file) as f:
            data = yaml.safe_load(f)
            source = data.get("source")
            target = data.get("target")
            label = data.get("relationship_type", "relatesTo")
            if source in included_nodes and target in included_nodes:
                node_degrees[source] += 1
                node_degrees[target] += 1
                edges.append((source, target, label, data.get("description", "")))

if included_nodes:
    for node_id, meta in node_metadata.items():
        degree = node_degrees.get(node_id, 1)
        size = 10 + degree * 2
        G.add_node(node_id, label=meta["label"], title=meta["title"], group=meta["group"], size=size)

    for source, target, label, desc in edges:
        G.add_edge(source, target, label=label, title=desc)

    G.write_html(str(GRAPH_FILE), notebook=False)
    st.markdown(f"### Interactive Network Graph ({len(included_nodes)} nodes, {len(edges)} edges)")
    with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
        st.components.v1.html(f.read(), height=750, scrolling=False)
else:
    st.warning("No matching entities found for current filters.")
