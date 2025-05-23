import time
import sys
from neo4j import GraphDatabase, exceptions

uri = "bolt://localhost:7687"
user = "neo4j"
password = "password"  # Or fetch from env if needed
max_attempts = 30

for i in range(max_attempts):
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
        print('Neo4j is up and accepting Bolt connections!')
        sys.exit(0)
    except exceptions.ServiceUnavailable:
        print('Neo4j Bolt not ready yet, waiting...')
        time.sleep(2)
    except Exception as e:
        print(f'Other error: {e}, waiting...')
        time.sleep(2)
print('Neo4j did not start in time!')
sys.exit(1) 