# 0_README_events.md

This folder captures real-world happenings — inspections, reports, summits, publication dates.
Use `'@type': EVENT` or `'@type': OBSERVATION`.

Maps to SCCM concept: **EVENT**, **OBSERVATION**


## Folder Structure (SCCM-Aligned)

| Folder                     | SCCM Concept         | Notes                                                                 |
|----------------------------|----------------------|-----------------------------------------------------------------------|
| `data/organizations/`      | `ORGANIZATION`       | For public bodies, networks, partnerships, etc                        |
| `data/services/`           | `SERVICE`, `FUNCTION`| For initiatives, tools, and capabilities delivered by organisations   |
| `data/plans/`              | `PLAN`               | For strategies, roadmaps, coordinated actions (e.g. NVEST roadmap)    |
| `data/events/`             | `EVENT`              | For past/present activities such as launches, reviews, inspections    |
| `data/relationships/`      | `RELATIONSHIP`       | One file per relationship (e.g. org–org, person–org)                 |
| `data/collections/`        | `COLLECTION`         | For logical groupings like datasets, tools, dashboards                |
| `data/items/` *(optional)* | `ITEM`, `OBJECT`     | Physical things like forms, dashboards, data files                    |
| `data/rules/` *(optional)* | `RULE`               | Towards possible modelling of governance or validation logic          |
