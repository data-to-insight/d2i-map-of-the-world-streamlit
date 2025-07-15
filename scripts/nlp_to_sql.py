# Stub example for natural language to SQL
# In production this could call an LLM or map basic queries

def nlp_to_sql(text):
    text = text.lower()
    if "safeguarding" in text and "north west" in text:
        return "SELECT name, organisation FROM index_data WHERE tags ILIKE '%safeguarding%' AND region ILIKE '%north west%' AND type = 'AGENT';"
    elif "projects by townville" in text:
        return "SELECT name, description FROM index_data WHERE organisation = 'townville-council' AND folder = 'projects';"
    else:
        return "SELECT * FROM index_data LIMIT 5"

if __name__ == "__main__":
    q = input("Enter your query: ")
    print("Generated SQL:")
    print(nlp_to_sql(q))
