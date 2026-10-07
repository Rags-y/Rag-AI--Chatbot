from neo4j import GraphDatabase
from langchain_core.documents import Document

from config import (
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
)


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
)


def graph_search(query: str, limit: int = 4):
    """
    Search the Neo4j knowledge graph using concept matching.
    """

    query_lower = query.lower()

    with driver.session() as session:

        result = session.run(
            """
            MATCH (concept:Concept)

            WHERE toLower($search_text) CONTAINS toLower(concept.name)
               OR toLower(concept.name) CONTAINS toLower($search_text)

            MATCH (chunk:Chunk)-[:MENTIONS]->(concept)

            RETURN DISTINCT
                chunk.id AS chunk_id,
                chunk.content AS content,
                chunk.page AS page,
                concept.name AS concept

            ORDER BY chunk.page

            LIMIT $limit
            """,
            search_text=query_lower,
            limit=limit,
        )

        records = list(result)

    docs = []

    for record in records:

        doc = Document(
            page_content=record["content"],
            metadata={
                "chunk_id": record["chunk_id"],
                "page": record["page"],
                "concept": record["concept"],
                "retrieval": "graph",
            },
        )

        docs.append(doc)

    return docs


def close_driver():
    driver.close()


if __name__ == "__main__":

    question = input("Enter a question: ")

    docs = graph_search(question)

    print(f"\nGraph retrieved {len(docs)} chunks.\n")

    for i, doc in enumerate(docs, 1):

        print(f"--- Graph Result {i} ---")
        print(f"Concept: {doc.metadata.get('concept')}")
        print(f"Page: {doc.metadata.get('page')}")
        print(doc.page_content[:500])
        print()