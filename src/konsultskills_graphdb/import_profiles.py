import json
import os
from typing import Dict, List, Any
from neo4j import GraphDatabase
from dotenv import load_dotenv
from tqdm import tqdm

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
            title: $title,
            expertise: $expertise,
            employment_type: $employment_type,
            employment_by: $employment_by
        })
        """
        session.run(consultant_query, {
            "name": data["name"],
            "title": data["title"],
            "expertise": data["expertise"],
            "employment_type": data["employment_type"],
            "employment_by": data["employment_by"]
        })

        # Create and connect technologies
        for tech in data["technologies"]:
            tech_query = """
            MERGE (t:Technology {name: $name, category: $category})
            WITH t
            MATCH (c:Consultant {name: $consultant_name})
            MERGE (c)-[r:KNOWS_TECHNOLOGY]->(t)
            """
            session.run(tech_query, {
                "name": tech["name"],
                "category": tech["category"],
                "consultant_name": data["name"]
            })

        # Create and connect methods
        for method in data["methods"]:
            method_query = """
            MERGE (m:Method {name: $name, category: $category})
            WITH m
            MATCH (c:Consultant {name: $consultant_name})
            MERGE (c)-[r:USES_METHOD]->(m)
            """
            session.run(method_query, {
                "name": method["name"],
                "category": method["category"],
                "consultant_name": data["name"]
            })

        # Create and connect tools
        for tool in data["tools"]:
            tool_query = """
            MERGE (t:Tool {name: $name, category: $category})
            WITH t
            MATCH (c:Consultant {name: $consultant_name})
            MERGE (c)-[r:USES_TOOL]->(t)
            """
            session.run(tool_query, {
                "name": tool["name"],
                "category": tool["category"],
                "consultant_name": data["name"]
            })

        # Create and connect languages
        for lang in data["languages"]:
            lang_query = """
            MERGE (l:Language {name: $name})
            WITH l
            MATCH (c:Consultant {name: $consultant_name})
            MERGE (c)-[r:SPEAKS {proficiency: $proficiency}]->(l)
            """
            session.run(lang_query, {
                "name": lang["name"],
                "proficiency": lang["proficiency"],
                "consultant_name": data["name"]
            })

        # Create and connect education
        for edu in data["education"]:
            edu_query = """
            MERGE (e:Education {name: $name, institution: $institution})
            WITH e
            MATCH (c:Consultant {name: $consultant_name})
            MERGE (c)-[r:HAS_EDUCATION]->(e)
            """
            session.run(edu_query, {
                "name": edu["name"],
                "institution": edu["institution"],
                "consultant_name": data["name"]
            })

def main():
    # Connect to Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        # Create constraints
        create_constraints(driver)
        
        # Load and process JSON files
        json_files = [f for f in os.listdir() if f.endswith('.json') and f != 'schema.json']
        
        for json_file in tqdm(json_files, desc="Processing files"):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                create_consultant(driver, data)
                
    finally:
        driver.close()

if __name__ == "__main__":
    main() 