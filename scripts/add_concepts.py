from neo4j import GraphDatabase

from config import (
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
)


CONCEPTS = [
    "Agentic AI",
    "AI Agent",
    "RAG",
    "LLM",
    "MCP",
    "Memory",
    "Planning",
    "Tool Use",
    "Autonomous Agents",
    "Multi-Agent Systems",
    "Generative AI",
    "Natural Language Processing",
    "Computer Vision",
]


print("Connecting to Neo4j...")

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
)


def add_concepts(tx):
    for concept in CONCEPTS:

        tx.run(
            """
            MERGE (c:Concept {name: $name})
            """,
            name=concept,
        )


def add_mentions(tx):
    result = tx.run(
        """
        MATCH (chunk:Chunk)
        MATCH (concept:Concept)

        WHERE toLower(chunk.content) CONTAINS toLower(concept.name)

        MERGE (chunk)-[:MENTIONS]->(concept)

        RETURN count(*) AS relationships
        """
    )

    return result.single()["relationships"]


try:

    driver.verify_connectivity()

    print("Neo4j connection successful!")

    with driver.session() as session:

        print("Creating concept nodes...")

        session.execute_write(add_concepts)

        print(f"Created/verified {len(CONCEPTS)} concepts")

        print("Creating MENTIONS relationships...")

        relationship_count = session.execute_write(add_mentions)

        print(
            f"Created/verified {relationship_count} "
            "MENTIONS relationships"
        )

    print("\nConcept graph created successfully!")

finally:

    driver.close()