# Children's Services Knowledge Base

[![Open Source](https://img.shields.io/badge/Open%20Source-Yes-brightgreen)](https://opensource.org)
[![Built with Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b)](https://streamlit.io)
[![DuckDB Powered](https://img.shields.io/badge/Database-DuckDB-blueviolet)](https://duckdb.org)

An open-source, Git-native 'map of the world' or knowledge base for connected **people**, **projects**, and **organisations** in the **children’s services sector**, aligned to the [Smart City Concept Model/framework (SCCM)](http://www.smartcityconceptmodel.com/).

---

## Notes / Dev story

- How can/should we structure the (meta) data about every element within the map (csv, db, flat file, .yml...)
- Can|should we store the names of people around the various initiatives/projects (is that relevant/useful and would they want that)
- How do we store the data for retrieval, as we scale up with larger volumes what impact will this have (esp on load/search times)
- 

## Structure

```
/knowledge_base
├── app/
│   ├── Home.py
│   └── pages/
│       └── 1_relationships.py
│       └── 2_network_view.py
│       └── 3_map_elements.py
├── data/
│   ├── index_data.parquet  ← cached index lives here
│   └── organizations/...   ← sccm framework folder struct with flat files
│   └── relationships/...   
├── scripts/
│   ├── app.py                  # Streamlit UI
│   ├── build_runtime_index.py  # Build DuckDB index from YAML
│   ├── validate_schema.py      # Validate YAMLs against schema
│   └── nlp_to_sql.py           # Stub for natural-language to SQL
└── README.md

```

---

## Dev Notes

### Dependencies

Python 3.9+ and the following packages:

```bash
pip install streamlit duckdb pyyaml cerberus
```

### Run Streamlit App

```bash
streamlit run app/Home.py
```

Will launch local UI in browser for exploring|searching people, projects, and orgs.

---



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
