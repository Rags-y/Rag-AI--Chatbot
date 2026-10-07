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


def setup_schema():
    with driver.session() as session:

        print("Creating Neo4j constraints...")

        session.run("""
            CREATE CONSTRAINT document_id_unique IF NOT EXISTS
            FOR (d:Document)
            REQUIRE d.id IS UNIQUE
        """)

        session.run("""
            CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS
            FOR (c:Chunk)
            REQUIRE c.id IS UNIQUE
        """)

        session.run("""
            CREATE CONSTRAINT concept_name_unique IF NOT EXISTS
            FOR (c:Concept)
            REQUIRE c.name IS UNIQUE
        """)

        print("Neo4j schema created successfully!")


try:
    driver.verify_connectivity()
    print("Neo4j connection successful!")

    setup_schema()

finally:
    driver.close()