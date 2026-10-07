from neo4j import GraphDatabase

from config import (
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
)


print("Connecting to Neo4j...")

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
)

try:
    driver.verify_connectivity()

    print("Neo4j connection successful!")

finally:
    driver.close()