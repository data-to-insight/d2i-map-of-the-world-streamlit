# app/Home.py
import streamlit as st
import duckdb
import os, yaml
from pathlib import Path

st.set_page_config(page_title="Children's Services Map of the World (SCCM)", layout="wide")
st.title("Children's Services Map of the World")



# === Path Setup ===
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

# === Load YAML Files ===
def load_yaml_records(folder):
    records = []
    for subfolder in os.listdir(folder):
        subpath = folder / subfolder
        for file in os.listdir(subpath):
            if file.endswith(".yaml"):
                with open(subpath / file, 'r') as f:
                    data = yaml.safe_load(f)
                    data['filename'] = file
                    data['folder'] = subfolder
                    records.append(data)
    return records

def build_duckdb_index(records):
    con = duckdb.connect()
    con.execute("""
        CREATE TABLE index_data (
            name TEXT,
            type TEXT,
            subtype TEXT,
            tags TEXT,
            organisation TEXT,
            region TEXT,
            projects TEXT,
            folder TEXT,
            filename TEXT
        );
    """)
    for r in records:
        con.execute("""
            INSERT INTO index_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            r.get("name"),
            r.get("@type"),
            r.get("subtype"),
            ', '.join(r.get("tags", [])),
            r.get("organisation"),
            r.get("region"),
            ', '.join(r.get("projects", [])) if r.get("projects") else '',
            r.get("folder"),
            r.get("filename")
        ))
    return con

records = load_yaml_records(DATA_DIR)
con = build_duckdb_index(records)

# === Sidebar filters ===
st.sidebar.header("Search Filters")
search_text = st.sidebar.text_input("Search (name/tags/org):", "")
folder_filter = st.sidebar.selectbox("Entity Type", ["All", "people", "projects", "orgs"])
region_filter = st.sidebar.text_input("Region contains:", "")
tag_filter = st.sidebar.text_input("Tag contains:", "")

# Persist filters
# st.session_state["search_text"] = search_text
# st.session_state["tag_filter"] = tag_filter
# st.session_state["region_filter"] = region_filter
# st.session_state["folder_filter"] = folder_filter

st.session_state["filters"] = {
    "tag": tag_filter,
    "region": region_filter,
    "folder": folder_filter,
    "search": search_text
}


# === Query building ===
query = "SELECT * FROM index_data WHERE 1=1"
if search_text:
    query += f" AND (name ILIKE '%{search_text}%' OR tags ILIKE '%{search_text}%' OR organisation ILIKE '%{search_text}%')"
if folder_filter != "All":
    query += f" AND folder = '{folder_filter}'"
if region_filter:
    query += f" AND region ILIKE '%{region_filter}%'"
if tag_filter:
    query += f" AND tags ILIKE '%{tag_filter}%'"

results = con.execute(query).fetchall()
cols = ["name", "type", "subtype", "tags", "organisation", "region", "projects", "folder", "filename"]

# === Output ===
st.markdown(f"### Found {len(results)} results")
for row in results:
    r = dict(zip(cols, row))
    with st.expander(f"🔗 {r['name']} ({r['type']})"):
        for k, v in r.items():
            if v:
                st.markdown(f"**{k.capitalize()}:** {v}")



## direct download option
# CSV Download
csv_path = Path("index_data.csv")
if csv_path.exists():
    with open(csv_path, "rb") as f:
        st.download_button(
            label="📥 Download Full Index (CSV)",
            data=f,
            file_name="index_data.csv",
            mime="text/csv"
        )
else:
    st.warning("No CSV found. Run `scripts/build_runtime_index.py` to generate it.")
