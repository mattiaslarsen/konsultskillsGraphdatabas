import os
import json
from neo4j import GraphDatabase
from tqdm import tqdm
from typing import Dict, List, Any

class Neo4jImporter:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_constraints(self):
        with self.driver.session() as session:
            # Create constraints for unique properties
            session.run("CREATE CONSTRAINT consultant_name IF NOT EXISTS FOR (c:Consultant) REQUIRE c.name IS UNIQUE")
            session.run("CREATE CONSTRAINT technology_name IF NOT EXISTS FOR (t:Technology) REQUIRE t.name IS UNIQUE")
            session.run("CREATE CONSTRAINT method_name IF NOT EXISTS FOR (m:Method) REQUIRE m.name IS UNIQUE")
            session.run("CREATE CONSTRAINT tool_name IF NOT EXISTS FOR (t:Tool) REQUIRE t.name IS UNIQUE")
            session.run("CREATE CONSTRAINT language_name IF NOT EXISTS FOR (l:Language) REQUIRE l.name IS UNIQUE")
            session.run("CREATE CONSTRAINT education_name IF NOT EXISTS FOR (e:Education) REQUIRE e.name IS UNIQUE")

    def import_profile(self, profile_data: Dict[str, Any]):
        with self.driver.session() as session:
            # Create consultant node
            session.run("""
                MERGE (c:Consultant {
                    name: $name,
                    email: $email,
                    phone: $phone,
                    linkedin: $linkedin,
                    location: $location,
                    role: $role,
                    level: $level,
                    summary: $summary,
                    expertise: $expertise,
                    employment_type: $employment_type,
                    employment_by: $employment_by
                })
            """, profile_data)

            # Import technologies
            for tech in profile_data.get('technologies', []):
                session.run("""
                    MERGE (t:Technology {name: $name})
                    WITH t
                    MATCH (c:Consultant {name: $consultant_name})
                    MERGE (c)-[:KNOWS_TECHNOLOGY]->(t)
                """, {
                    "name": tech,
                    "consultant_name": profile_data.get('name')
                })

            # Import methods
            for method in profile_data.get('methods', []):
                session.run("""
                    MERGE (m:Method {name: $name})
                    WITH m
                    MATCH (c:Consultant {name: $consultant_name})
                    MERGE (c)-[:USES_METHOD]->(m)
                """, {
                    "name": method,
                    "consultant_name": profile_data.get('name')
                })

            # Import tools
            for tool in profile_data.get('tools', []):
                session.run("""
                    MERGE (t:Tool {name: $name})
                    WITH t
                    MATCH (c:Consultant {name: $consultant_name})
                    MERGE (c)-[:USES_TOOL]->(t)
                """, {
                    "name": tool,
                    "consultant_name": profile_data.get('name')
                })

            # Import languages
            for lang in profile_data.get('languages', []):
                session.run("""
                    MERGE (l:Language {name: $name})
                    WITH l
                    MATCH (c:Consultant {name: $consultant_name})
                    MERGE (c)-[r:SPEAKS]->(l)
                    SET r.level = $level
                """, {
                    "name": lang['language'],
                    "level": lang['level'],
                    "consultant_name": profile_data.get('name')
                })

            # Import education
            for edu in profile_data.get('education', []):
                session.run("""
                    MERGE (e:Education {name: $name, institution: $institution})
                    WITH e
                    MATCH (c:Consultant {name: $consultant_name})
                    MERGE (c)-[r:HAS_EDUCATION]->(e)
                    SET r.period = $period
                """, {
                    "name": edu['focus'],
                    "institution": edu['institution'],
                    "period": edu['period'],
                    "consultant_name": profile_data.get('name')
                })

            # Import assignments
            for assignment in profile_data.get('assignments', []):
                session.run("""
                    CREATE (a:Assignment {
                        role: $role,
                        client: $client,
                        period: $period,
                        description: $description
                    })
                    WITH a
                    MATCH (c:Consultant {name: $consultant_name})
                    CREATE (c)-[:PERFORMED]->(a)
                """, {
                    "role": assignment['role'],
                    "client": assignment['client'],
                    "period": assignment['period'],
                    "description": assignment['description'],
                    "consultant_name": profile_data.get('name')
                })

def main():
    # Neo4j connection details
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"

    # Initialize importer
    importer = Neo4jImporter(uri, user, password)
    
    try:
        # Create constraints
        importer.create_constraints()
        
        # Get all JSON files in the current directory
        json_files = [f for f in os.listdir('.') if f.endswith('.json')]
        
        # Import each profile
        for json_file in tqdm(json_files, desc="Importing profiles"):
            with open(json_file, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
                importer.import_profile(profile_data)
                
    finally:
        importer.close()

if __name__ == "__main__":
    main() 