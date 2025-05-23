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

        # Only use 'assignment' key for assignments, warn if 'assignments' is present
        if "assignments" in data:
            print(f"[WARNING] 'assignments' key found in {data.get('name', 'unknown')}, but only 'assignment' is supported. Please update the JSON.")
        assignments = data.get("assignment", [])
        for assignment in assignments:
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
                    "name": approach.get("name", "") if isinstance(approach, dict) else approach,
                    "description": approach.get("description", "") if isinstance(approach, dict) else "",
                    "client": assignment.get("client", ""),
                    "role": assignment.get("role", "")
                })

def validate_all_files(directory_path: str) -> tuple[bool, list[tuple[str, str]]]:
    """Validate all JSON files in a directory and its subdirectories.
    Returns a tuple of (is_valid, list of (file_path, error_message))"""
    validation_errors = []
    
    # Load schema
    with open("schema.json", "r", encoding="utf-8") as schema_file:
        schema = json.load(schema_file)

    def validate_directory(dir_path: str) -> None:
        # Process all JSON files in current directory
        json_files = [f for f in os.listdir(dir_path) if f.endswith('.json')]
        
        for json_file in json_files:
            file_path = os.path.join(dir_path, json_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    try:
                        jsonschema.validate(instance=data, schema=schema)
                        # Check for 'assignments' key (should be 'assignment')
                        if "assignments" in data:
                            validation_errors.append((file_path, "Uses 'assignments' key instead of 'assignment'"))
                    except jsonschema.ValidationError as e:
                        validation_errors.append((file_path, str(e)))
            except Exception as e:
                validation_errors.append((file_path, f"Failed to read/parse JSON: {str(e)}"))

        # Process all subdirectories
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isdir(item_path):
                validate_directory(item_path)

    validate_directory(directory_path)
    return len(validation_errors) == 0, validation_errors

def process_directory(driver: GraphDatabase.driver, directory_path: str) -> None:
    """Process all JSON files in a directory and its subdirectories."""
    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return

    # First validate all files
    is_valid, validation_errors = validate_all_files(directory_path)
    
    if not is_valid:
        print("\n[VALIDATION ERRORS] The following files have issues:")
        for file_path, error in validation_errors:
            print(f"\n  {os.path.basename(file_path)}:")
            print(f"    {error}")
        print("\nPlease fix these issues before importing.")
        return

    # If all files are valid, proceed with import
    def process_directory_recursive(dir_path: str) -> None:
        # Process all JSON files in current directory
        json_files = [f for f in os.listdir(dir_path) if f.endswith('.json')]
        
        for json_file in tqdm(json_files, desc=f"Processing files in {os.path.basename(dir_path)}"):
            file_path = os.path.join(dir_path, json_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    create_consultant(driver, data)
                    print(f"\n[SUCCESS] Processed {json_file}")
            except Exception as e:
                print(f"\n[ERROR] Failed to process {json_file}: {str(e)}")

        # Process all subdirectories
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isdir(item_path):
                print(f"\nProcessing subdirectory: {item}")
                process_directory_recursive(item_path)

    process_directory_recursive(directory_path)

def main():
    # Connect to Neo4j
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        # Create constraints
        create_constraints(driver)
        
        # Process OneDrive directory
        onedrive_path = r"C:\Users\matti\GNR8 AB\GNR8 AB - Konsultprofiler"
        process_directory(driver, onedrive_path)
                
    finally:
        driver.close()

if __name__ == "__main__":
    main() 