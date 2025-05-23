import os
import json
from neo4j import GraphDatabase

# --- Konfiguration ---
JSON_DIR = r"C:/Users/matti/GNR8 AB/GNR8 AB - Konsultprofiler"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

# --- Räkna i JSON-filer ---
consultant_counts = {}
total_assignments_json = 0
for root, dirs, files in os.walk(JSON_DIR):
    for file in files:
        if file.endswith('.json'):
            try:
                with open(os.path.join(root, file), encoding='utf-8') as f:
                    data = json.load(f)
                    name = data.get('name', 'UNKNOWN')
                    assignments = data.get('assignments', [])
                    consultant_counts[name] = len(assignments)
                    total_assignments_json += len(assignments)
            except Exception as e:
                print(f"[JSON ERROR] {file}: {e}")

print("\n[JSON] Konsulter:", len(consultant_counts))
print("[JSON] Assignments per konsult:")
for k, v in consultant_counts.items():
    print(f"  {k}: {v}")
print("[JSON] Totalt assignments:", total_assignments_json)

# --- Räkna i Neo4j ---
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
with driver.session() as session:
    antal_konsulter = session.run("MATCH (c:Consultant) RETURN count(c)").single()[0]
    print("\n[Neo4j] Konsulter:", antal_konsulter)

    res = session.run("""
        MATCH (c:Consultant)
        OPTIONAL MATCH (c)-[:PERFORMED]->(a:Assignment)
        RETURN c.name, count(a) AS antal_assignments
    """)
    print("[Neo4j] Assignments per konsult:")
    for row in res:
        print(f"  {row['c.name']}: {row['antal_assignments']}")

    total_assignments = session.run("MATCH (a:Assignment) RETURN count(a)").single()[0]
    print("[Neo4j] Totalt assignments:", total_assignments)
driver.close() 