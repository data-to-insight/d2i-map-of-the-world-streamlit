# Children's Services Knowledge Base

[![Open Source](https://img.shields.io/badge/Open%20Source-Yes-brightgreen)](https://opensource.org)
[![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b)](https://streamlit.io)
[![DuckDB Powered](https://img.shields.io/badge/Database-DuckDB-blueviolet)](https://duckdb.org)

A lightweight, open-source, Git-native 'map of the world' or knowledge base for connected **people**, **projects**, and **organisations** in the **children’s services sector**, aligned to the [Smart City Concept Model (SCCM)](http://www.smartcityconceptmodel.com/).

---

## Structure

```
childrens_knowledge_base/
├── data/
│   ├── people/       # Individual agents
│   ├── projects/     # Services or events
│   └── orgs/         # Organisations
├── scripts/
│   ├── app.py               # Streamlit UI
│   ├── build_runtime_index.py  # Build DuckDB index from YAML
│   ├── validate_schema.py  # Validate YAMLs against schema
│   └── nlp_to_sql.py        # Stub for natural-language to SQL
└── README.md
```

---

## Getting Started

### Install dependencies

You’ll need Python 3.9+ and the following packages:

```bash
pip install streamlit duckdb pyyaml cerberus
```

### Run the Streamlit App

```bash
streamlit run app/Home.py
```

This will launch local UI in browser for exploring people, projects, and orgs.

---

## Dev Notes

### Validate YAML Structure

Use the built-in schema validation script:

```bash
python scripts/validate_schema.py
```

This checks for required fields and types based on a lightweight SCCM-aligned schema.

### Rebuild Search Index

DuckDB is used as a fast in-memory index:

```bash
python scripts/build_runtime_index.py
```

You’ll see all records loaded and printed to terminal. If you’re running streamlit run app/Home.py you don't need to do this as build_duckdb_index(records) is automatically called — no need to run it separately.

### Text-to-SQL (Prototype)

You can simulate natural language queries:

```bash
python scripts/nlp_to_sql.py
```

Example input:
```
Who worked on safeguarding in the North West?
```

---

## Future Plans

- SCCM-compliant JSON-LD export
- GitHub Pages + search index
- Relationship mapping (RELATIONSHIP, EVENT)
- Collaborative edit + merge workflow

---

© D2I
