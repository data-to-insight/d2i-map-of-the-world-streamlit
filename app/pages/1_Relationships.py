import streamlit as st
import yaml
import os
from pathlib import Path

st.set_page_config(page_title="Sector Relations", layout="wide")
st.title("🔗 Sector Relations")

# === Path Setup ===
ROOT = Path(__file__).resolve().parents[2]
REL_DIR = ROOT / "data" / "relationships"

# === Get filters from session state ===
filters = st.session_state.get("filters", {})
folder_filter = filters.get("folder")
search = filters.get("search", "").lower()
region = filters.get("region", "").lower()
tag = filters.get("tag", "").lower()

# === Load and filter relationship files ===
def load_filtered_relationships(path):
    relationships = []
    for file in os.listdir(path):
        if file.endswith(".yaml") and not file.startswith("0_template"):
            with open(path / file, "r") as f:
                try:
                    data = yaml.safe_load(f)
                    data["__filename"] = file

                    # === Apply filters
                    if search and search not in data.get("name", "").lower():
                        continue
                    if tag and tag not in [t.lower() for t in data.get("tags", [])]:
                        continue
                    if region and region not in data.get("description", "").lower():
                        continue
                    if folder_filter and folder_filter != "All":
                        # Attempt to infer from source/target
                        if not (folder_filter in data.get("source", "") or folder_filter in data.get("target", "")):
                            continue

                    relationships.append(data)
                except Exception as e:
                    st.warning(f"Error reading {file}: {e}")
    return relationships

relationships = load_filtered_relationships(REL_DIR)

# === Output
st.markdown(f"### Found {len(relationships)} matching relationships")

if relationships:
    for rel in relationships:
        st.markdown("----")
        st.subheader(rel.get("name", "Unnamed relationship"))
        st.markdown(f"**Filename:** `{rel.get('__filename', '')}`")
        st.markdown(f"**Source:** `{rel.get('source', 'N/A')}`")
        st.markdown(f"**Target:** `{rel.get('target', 'N/A')}`")
        st.markdown(f"**Type:** `{rel.get('relationship_type', 'unspecified')}`")
        st.markdown(f"**Tags:** `{', '.join(rel.get('tags', []))}`")
        st.markdown(f"**Description:** {rel.get('description', '')}")
else:
    st.warning("No relationships match your current filters.")
