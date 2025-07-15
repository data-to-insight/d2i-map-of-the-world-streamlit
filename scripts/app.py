import streamlit as st
import duckdb
import os, yaml

st.set_page_config(page_title="Children's Services Knowledge Base", layout="wide")
st.title("Children's Services Knowledge Base")

# Load YAML and build DuckDB index
def load_yaml_records(folder):
    records = []
    for subfolder in os.listdir(folder):
        subpath = os.path.join(folder, subfolder)
        for file in os.listdir(subpath):
            with open(os.path.join(subpath, file), 'r') as f:
                data = yaml.safe_load(f)
                data['filename'] = file
                data['folder'] = subfolder
                records.append(data)
    return records

def build_duckdb_index(records):
    con = duckdb.connect()
    con.execute("DROP TABLE IF EXISTS index_data")
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

records = load_yaml_records("data")
con = build_duckdb_index(records)

# Sidebar filters
st.sidebar.header("🔍 Search Filters")
search_text = st.sidebar.text_input("Search (name/tags/org):", "")
folder_filter = st.sidebar.selectbox("Entity Type", ["All", "people", "projects", "orgs"])
region_filter = st.sidebar.text_input("Region contains:", "")
tag_filter = st.sidebar.text_input("Tag contains:", "")

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

st.markdown(f"### Found {len(results)} results")
for row in results:
    r = dict(zip(cols, row))
    with st.expander(f"🔗 {r['name']} ({r['type']})"):
        st.markdown(f"**Type:** {r['type']}")
        st.markdown(f"**Subtype:** {r['subtype']}")
        st.markdown(f"**Organisation:** {r['organisation']}")
        st.markdown(f"**Region:** {r['region']}")
        st.markdown(f"**Tags:** `{r['tags']}`")
        st.markdown(f"**Projects:** `{r['projects']}`")
        st.markdown(f"**Filename:** `{r['filename']}`")
        st.markdown(f"**Folder:** `{r['folder']}`")
