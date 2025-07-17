# import streamlit as st
# import duckdb
# import os
# import yaml
# from pathlib import Path

# st.set_page_config(page_title="Map of the World (SCCM)", layout="wide")
# st.title("Organisations, Tools, Services, Relations")

# # === Path Setup ===
# ROOT = Path(__file__).resolve().parents[2] # jump back 2 levels to get /data 
# DATA_DIR = ROOT / "data"


# # === Load YAML Files ===
# def load_yaml_records(folder):
#     records = []
#     for subfolder in os.listdir(folder):
#         subpath = folder / subfolder
#         if not subpath.is_dir():
#             continue
#         for file in os.listdir(subpath):
#             if file.endswith(".yaml") and not file.startswith("0_template"):
#                 with open(subpath / file, 'r') as f:
#                     data = yaml.safe_load(f)
#                     data['filename'] = file
#                     data['folder'] = subfolder
#                     records.append(data)
#     return records

# # === Build DuckDB Index ===
# def build_duckdb_index(records):
#     con = duckdb.connect()
#     con.execute("DROP TABLE IF EXISTS index_data")
#     con.execute("""
#         CREATE TABLE index_data (
#             name TEXT,
#             type TEXT,
#             subtype TEXT,
#             tags TEXT,
#             organisation TEXT,
#             region TEXT,
#             projects TEXT,
#             folder TEXT,
#             filename TEXT
#         );
#     """)
#     for r in records:
#         con.execute("""
#             INSERT INTO index_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#         """, (
#             r.get("name"),
#             r.get("@type"),
#             r.get("subtype", ""),
#             ', '.join(r.get("tags", [])),
#             r.get("organisation", ""),
#             r.get("region", ""),
#             ', '.join(r.get("projects", [])) if r.get("projects") else '',
#             r.get("folder"),
#             r.get("filename")
#         ))
#     return con

# with st.spinner("🔄 Loading YAML records and building index..."):
#     records = load_yaml_records(DATA_DIR)
#     con = build_duckdb_index(records)


# # === Sidebar filters ===
# st.sidebar.header("🔍 Search Filters")
# search_text = st.sidebar.text_input("Search (name/tags/org):", "")
# folder_filter = st.sidebar.selectbox("Entity Type", [
#     # naming/spelling in line with SCCM
#     "All",
#     "organizations",
#     "services",
#     "plans",
#     "events",
#     "relationships",
#     "collections",
#     "items",
#     "resources"
# ])
# region_filter = st.sidebar.text_input("Region contains:", "")
# tag_filter = st.sidebar.text_input("Tag contains:", "")

# # === Persist filters to session ===
# st.session_state["filters"] = {
#     "tag": tag_filter,
#     "region": region_filter,
#     "folder": folder_filter,
#     "search": search_text
# }

# # === Query building ===
# query = "SELECT * FROM index_data WHERE 1=1"
# if search_text:
#     query += f" AND (name ILIKE '%{search_text}%' OR tags ILIKE '%{search_text}%' OR organisation ILIKE '%{search_text}%')"
# if folder_filter != "All":
#     query += f" AND folder = '{folder_filter}'"
# if region_filter:
#     query += f" AND region ILIKE '%{region_filter}%'"
# if tag_filter:
#     query += f" AND tags ILIKE '%{tag_filter}%'"

# results = con.execute(query).fetchall()
# cols = ["name", "type", "subtype", "tags", "organisation", "region", "projects", "folder", "filename"]

# # === Output ===
# st.markdown(f"### Found {len(results)} result(s)")
# for row in results:
#     r = dict(zip(cols, row))
#     with st.expander(f"🔗 {r['name']} ({r['type']})"):
#         for k, v in r.items():
#             if v:
#                 st.markdown(f"**{k.capitalize()}:** {v}")

# # === CSV Download ===
# csv_path = Path("index_data.csv")
# if csv_path.exists():
#     with open(csv_path, "rb") as f:
#         st.download_button(
#             label="📥 Download Full Index (CSV)",
#             data=f,
#             file_name="index_data.csv",
#             mime="text/csv"
#         )
# else:
#     st.warning("No CSV found. Run `scripts/build_runtime_index.py` to generate it.")




## First time: YAMLs → Pandas Df → saved to Parquet
## Next runs: Parquet → fast Pandas filter → results

import streamlit as st
import pandas as pd
import os, yaml
from pathlib import Path

st.set_page_config(page_title="Map of the World (SCCM)", layout="wide")
st.title("Organisations, Tools, Services, Relations")

# === Path Setup ===
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
PARQUET_FILE = DATA_DIR / "index_data.parquet"


# === Load YAML Files and Cache as Parquet ===
@st.cache_data(show_spinner=False)
def load_and_cache_yaml(folder, parquet_path):
    """Load YAML files, flatten key fields, and write to Parquet for speedup"""
    records = []
    for subfolder in os.listdir(folder):
        subpath = folder / subfolder
        if not subpath.is_dir():
            continue
        for file in os.listdir(subpath):
            if file.endswith(".yaml") and not file.startswith("0_template"):
                with open(subpath / file, 'r') as f:
                    data = yaml.safe_load(f)
                    data['filename'] = file
                    data['folder'] = subfolder
                    records.append({
                        "name": data.get("name"),
                        "type": data.get("@type"),
                        "subtype": data.get("subtype", ""),
                        "tags": ', '.join(data.get("tags", [])),
                        "organisation": data.get("organisation", ""),
                        "region": data.get("region", ""),
                        "projects": ', '.join(data.get("projects", [])) if data.get("projects") else '',
                        "folder": data.get("folder"),
                        "filename": data.get("filename")
                    })
    df = pd.DataFrame(records)
    df.to_parquet(parquet_path, index=False)  # Save for fast future access
    return df

with st.spinner("🔄 Loading and caching records..."):
    if PARQUET_FILE.exists():
        df = pd.read_parquet(PARQUET_FILE)
    else:
        df = load_and_cache_yaml(DATA_DIR, PARQUET_FILE)

# === Sidebar filters ===
st.sidebar.header("🔍 Search Filters")
search_text = st.sidebar.text_input("Search (name/tags/org):", "")
folder_filter = st.sidebar.selectbox("Entity Type", [
    "All", "organizations", "services", "plans", "events", 
    "relationships", "collections", "items", "resources"
])
region_filter = st.sidebar.text_input("Region contains:", "")
tag_filter = st.sidebar.text_input("Tag contains:", "")

st.session_state["filters"] = {
    "tag": tag_filter,
    "region": region_filter,
    "folder": folder_filter,
    "search": search_text
}

# === Filter Query ===
query_df = df.copy()

if search_text:
    query_df = query_df[
        query_df["name"].str.contains(search_text, case=False, na=False) |
        query_df["tags"].str.contains(search_text, case=False, na=False) |
        query_df["organisation"].str.contains(search_text, case=False, na=False)
    ]

if folder_filter != "All":
    query_df = query_df[query_df["folder"] == folder_filter]

if region_filter:
    query_df = query_df[query_df["region"].str.contains(region_filter, case=False, na=False)]

if tag_filter:
    query_df = query_df[query_df["tags"].str.contains(tag_filter, case=False, na=False)]

# === Output ===
st.markdown(f"### Found {len(query_df)} result(s)")
for _, row in query_df.iterrows():
    with st.expander(f"🔗 {row['name']} ({row['type']})"):
        for k, v in row.items():
            if pd.notna(v) and v != "":
                st.markdown(f"**{k.capitalize()}:** {v}")

# === CSV Download ===
if PARQUET_FILE.exists():
    st.download_button(
        label="📥 Download Full Index (CSV)",
        data=df.to_csv(index=False),
        file_name="index_data.csv",
        mime="text/csv"
    )
else:
    st.warning("No Parquet file found. YAMLs must be loaded first.")
