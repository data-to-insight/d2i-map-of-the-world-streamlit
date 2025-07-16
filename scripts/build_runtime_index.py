
# build_runtime_index.py updated for SCCM-aligned folders

import os
import yaml
import duckdb
import pandas as pd

# SCCM folder to @type mapping
FOLDER_TYPE_MAP = {
    "organizations": "ORGANIZATION",
    "services": "SERVICE",
    "plans": "PLAN",
    "events": "EVENT",
    "collections": "COLLECTION",
    "items": "ITEM",
    "resources": "RESOURCE",
    "relationships": "RELATIONSHIP"
}

index_records = []

for folder, type_value in FOLDER_TYPE_MAP.items():
    folder_path = os.path.join("data", folder)
    if not os.path.isdir(folder_path):
        continue

    for file in os.listdir(folder_path):
        if file.endswith(".yaml"):
            full_path = os.path.join(folder_path, file)
            with open(full_path, "r") as f:
                try:
                    data = yaml.safe_load(f)
                except Exception as e:
                    print(f"Error loading {full_path}: {e}")
                    continue

            index_records.append({
                "file_path": full_path,
                "folder": folder,
                "filename": file,
                "name": data.get("name", file.replace(".yaml", "")),
                "@type": data.get("@type", type_value),
                "subtype": data.get("subtype", ""),
                "tags": ", ".join(data.get("tags", [])),
                "organisation": data.get("organisation", ""),
                "region": data.get("region", ""),
                "projects": ", ".join(data.get("projects", [])) if data.get("projects") else ""
            })

# Write to CSV
index_df = pd.DataFrame(index_records)
index_df.to_csv("index_data.csv", index=False)

# Save to DuckDB
db_path = "index.db"
con = duckdb.connect(db_path)
con.execute("DROP TABLE IF EXISTS index_data")
con.execute("CREATE TABLE index_data AS SELECT * FROM index_df")

print("✅ DuckDB + CSV index rebuilt using SCCM folder structure")
