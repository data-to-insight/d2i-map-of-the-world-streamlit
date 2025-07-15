# app/pages/1_Relationships.py
import streamlit as st
import yaml
import os
from pathlib import Path

st.set_page_config(page_title="Entity Relationships", layout="wide")
st.title("🔗 Entity Relationships")

# === Path Setup ===
ROOT = Path(__file__).resolve().parents[2]
REL_DIR = ROOT / "data" / "relationships"

# === Load YAML Relationship Files ===
def load_relationships(path):
    relationships = []
    for file in os.listdir(path):
        if file.endswith(".yaml"):
            with open(path / file, "r") as f:
                data = yaml.safe_load(f)
                relationships.append(data)
    return relationships

relationships = load_relationships(REL_DIR)
st.markdown(f"### Found {len(relationships)} defined relationships")

# === Display ===
for rel in relationships:
    st.markdown("----")
    st.subheader(rel.get("name", "Unnamed relationship"))
    st.markdown(f"**Source:** `{rel['source']}`")
    st.markdown(f"**Target:** `{rel['target']}`")
    st.markdown(f"**Type:** `{rel['relationship_type']}`")
    st.markdown(f"**Tags:** `{', '.join(rel.get('tags', []))}`")
    st.markdown(f"**Description:** {rel.get('description', '')}")
