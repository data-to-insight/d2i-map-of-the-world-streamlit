# scripts/build_runtime_index.py
import os, yaml
import duckdb
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

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
    con = duckdb.connect("index_data.db")
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

    # Export to CSV
    con.execute("""
        COPY index_data TO 'index_data.csv' (HEADER, DELIMITER ',');
    """)
    print("Exported index_data.csv")

    return con

if __name__ == "__main__":
    records = load_yaml_records(DATA_DIR)
    con = build_duckdb_index(records)
    results = con.execute("SELECT * FROM index_data").fetchall()
    for row in results:
        print(row)
