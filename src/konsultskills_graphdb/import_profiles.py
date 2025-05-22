import json
import os
from typing import Dict, List, Any
from neo4j import GraphDatabase
from dotenv import load_dotenv
from tqdm import tqdm
import jsonschema

# Load environment variables
load_dotenv()

# Neo4j connection details
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def create_constraints(driver: GraphDatabase.driver) -> None:
    """Create constraints for the database."""
    with driver.session() as session:
        # Create constraints for Consultant
        session.run("CREATE CONSTRAINT consultant_name IF NOT EXISTS FOR (c:Consultant) REQUIRE c.name IS UNIQUE")
        
        # Create constraints for Technology
        session.run("CREATE CONSTRAINT technology_name IF NOT EXISTS FOR (t:Technology) REQUIRE t.name IS UNIQUE")
        
        # Create constraints for Method
        session.run("CREATE CONSTRAINT method_name IF NOT EXISTS FOR (m:Method) REQUIRE m.name IS UNIQUE")
        
        # Create constraints for Tool
        session.run("CREATE CONSTRAINT tool_name IF NOT EXISTS FOR (t:Tool) REQUIRE t.name IS UNIQUE")
        
        # Create constraints for Language
        session.run("CREATE CONSTRAINT language_name IF NOT EXISTS FOR (l:Language) REQUIRE l.name IS UNIQUE")
        
        # Create constraints for Education
        session.run("CREATE CONSTRAINT education_name IF NOT EXISTS FOR (e:Education) REQUIRE e.name IS UNIQUE")

def create_consultant(driver: GraphDatabase.driver, data: Dict[str, Any]) -> None:
    """Create a consultant node and its relationships."""
    with driver.session() as session:
        # Create consultant node
        consultant_query = """
        MERGE (c:Consultant {
            name: $name,
            expertise: $expertise,
            employment_type: $employment_type,
            employment_by: $employment_by
        })
        """
        session.run(consultant_query, {
            "name": data.get("name", ""),
            "expertise": data.get("expertise", ""),
            "employment_type": data.get("employment_type", ""),
            "employment_by": data.get("employment_by", "")
        })

        # Create and connect technologies
        for tech in data.get("technologies", []):
            tech_query = """
            MERGE (t:Technology {name: $name, category: $category})
            WITH t
            MATCH (c:Consultant {name: $consultant_name})
            MERGE (c)-[r:KNOWS_TECHNOLOGY]->(t)
            """
            if isinstance(tech, str):
                session.run(tech_query, {
                    "name": tech,
                    "category": "General",
                    "consultant_name": data.get("name", "")
                })
            else:
                session.run(tech_query, {
                    "name": tech["name"],
                    "category": tech["category"],
                    "consultant_name": data.get("name", "")
                })

        # Create and connect methods
        for method in data.get("methods", []):
            method_query = """
            MERGE (m:Method {name: $name, category: $category})
            WITH m
            MATCH (c:Consultant {name: $consultant_name})
            MERGE (c)-[r:USES_METHOD]->(m)
            """
            if isinstance(method, str):
                session.run(method_query, {
                    "name": method,
                    "category": "General",
                    "consultant_name": data.get("name", "")
                })
            else:
                session.run(method_query, {
                    "name": method["name"],
                    "category": method["category"],
                    "consultant_name": data.get("name", "")
                })

        # Create and connect tools
        for tool in data.get("tools", []):
            tool_query = """
            MERGE (t:Tool {name: $name, category: $category})
            WITH t
            MATCH (c:Consultant {name: $consultant_name})
            MERGE (c)-[r:USES_TOOL]->(t)
            """
            if isinstance(tool, str):
                session.run(tool_query, {
                    "name": tool,
                    "category": "General",
                    "consultant_name": data.get("name", "")
                })
            else:
                session.run(tool_query, {
                    "name": tool["name"],
                    "category": tool["category"],
                    "consultant_name": data.get("name", "")
                })

        # Create and connect languages
        for lang in data.get("languages", []):
            lang_query = """
            MERGE (l:Language {name: $name})
            WITH l
            MATCH (c:Consultant {name: $consultant_name})
            MERGE (c)-[r:SPEAKS {proficiency: $proficiency}]->(l)
            """
            if isinstance(lang, str):
                session.run(lang_query, {
                    "name": lang,
                    "proficiency": "Not specified",
                    "consultant_name": data.get("name", "")
                })
            else:
                session.run(lang_query, {
                    "name": lang.get("language", lang.get("name", "")),
                    "proficiency": lang.get("level", lang.get("proficiency", "Not specified")),
                    "consultant_name": data.get("name", "")
                })

        # Create and connect education
        for edu in data.get("education", []):
            edu_query = """
            MERGE (e:Education {name: $name, institution: $institution, period: $period})
            WITH e
            MATCH (c:Consultant {name: $consultant_name})
            MERGE (c)-[r:HAS_EDUCATION]->(e)
            """
            session.run(edu_query, {
                "name": edu.get("focus", ""),
                "institution": edu.get("institution", ""),
                "period": edu.get("period", ""),
                "consultant_name": data.get("name", "")
            })

        # Create and connect assignments with roles
        for assignment in data.get("assignments", []):
            assignment_query = """
            MERGE (a:Assignment {
                client: $client,
                role: $role,
                period: $period,
                description: $description
            })
            WITH a
            MATCH (c:Consultant {name: $consultant_name})
            MERGE (c)-[r:PERFORMED]->(a)
            """
            session.run(assignment_query, {
                "client": assignment.get("client", ""),
                "role": assignment.get("role", ""),
                "period": assignment.get("period", ""),
                "description": assignment.get("description", ""),
                "consultant_name": data.get("name", "")
            })

            # Create and connect approaches
            for approach in assignment.get("approach", []):
                approach_query = """
                MERGE (ap:Approach {name: $name, description: $description})
                WITH ap
                MATCH (a:Assignment {client: $client, role: $role})
                MERGE (a)-[r:USES_APPROACH]->(ap)
                """
                session.run(approach_query, {
                    "name": approach.get("name", ""),
                    "description": approach.get("description", ""),
                    "client": assignment.get("client", ""),
                    "role": assignment.get("role", "")
                })

def main():
    # Connect to Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    # Load schema
    with open("schema.json", "r", encoding="utf-8") as schema_file:
        schema = json.load(schema_file)
    
    try:
        # Create constraints
        create_constraints(driver)
        
        # Load and process JSON files
        json_files = [f for f in os.listdir() if f.endswith('.json') and f != 'schema.json']
        
        for json_file in tqdm(json_files, desc="Processing files"):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                try:
                    jsonschema.validate(instance=data, schema=schema)
                except jsonschema.ValidationError as e:
                    print(f"\n[REJECTED] {json_file}: {e.message}")
                    continue
                create_consultant(driver, data)
                
    finally:
        driver.close()

if __name__ == "__main__":
    main() 