from neo4j import GraphDatabase
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from config import (
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
)


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(
        NEO4J_USERNAME,
        NEO4J_PASSWORD,
    ),
)


embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    encode_kwargs={
        "normalize_embeddings": True
    },
)


def vector_search(
    query: str,
    k: int = 4,
):
    """
    Search Neo4j's vector index for the
    most semantically similar chunks.
    """

    query_embedding = embeddings.embed_query(
        query
    )

    with driver.session() as session:

     records = session.run(
    """
    MATCH (node:Chunk)
    SEARCH node IN (
        VECTOR INDEX chunk_embedding_index
        FOR $query_embedding
        LIMIT $k
    )
    SCORE AS score

    RETURN
        node.id AS chunk_id,
        node.content AS content,
        node.page AS page,
        score

    ORDER BY score DESC
    """,
    k=k,
    query_embedding=query_embedding,
).data()

    docs = []

    for record in records:

        docs.append(
            Document(
                page_content=record["content"],
                metadata={
                    "chunk_id": record["chunk_id"],
                    "page": record["page"],
                    "similarity": record["score"],
                    "retrieval": "neo4j_vector",
                },
            )
        )

    return docs


def graph_expand(
    chunk_ids,
    limit: int = 4,
):
    """
    Expand vector-retrieved chunks through
    Neo4j concept relationships.
    """

    if not chunk_ids:
        return []

    with driver.session() as session:

        result = session.run(
            """
            MATCH (source:Chunk)-[:MENTIONS]->(concept:Concept)

            WHERE source.id IN $chunk_ids

            MATCH (related:Chunk)-[:MENTIONS]->(concept)

            WHERE NOT related.id IN $chunk_ids

            WITH
                related,
                collect(DISTINCT concept.name) AS shared_concepts

            RETURN
                related.id AS chunk_id,
                related.content AS content,
                related.page AS page,
                shared_concepts

            ORDER BY
                size(shared_concepts) DESC,
                related.page

            LIMIT $limit
            """,
            chunk_ids=chunk_ids,
            limit=limit,
        )

        records = list(result)

    docs = []

    for record in records:

        docs.append(
            Document(
                page_content=record["content"],
                metadata={
                    "chunk_id": record["chunk_id"],
                    "page": record["page"],
                    "concept": ", ".join(
                        record["shared_concepts"]
                    ),
                    "retrieval": "neo4j_graph",
                },
            )
        )

    return docs


def neo4j_retrieve(
    query: str,
    vector_k: int = 4,
    graph_k: int = 4,
):
    """
    Neo4j-centered retrieval.

    1. Vector search finds relevant starting chunks.
    2. Graph traversal expands those chunks.
    3. Results are combined and deduplicated.
    """

    vector_docs = vector_search(
        query,
        k=vector_k,
    )

    vector_chunk_ids = [
        doc.metadata.get("chunk_id")
        for doc in vector_docs
        if doc.metadata.get("chunk_id")
    ]

    graph_docs = graph_expand(
        vector_chunk_ids,
        limit=graph_k,
    )

    combined_docs = []

    seen_chunk_ids = set()

    for doc in vector_docs + graph_docs:

        chunk_id = doc.metadata.get(
            "chunk_id"
        )

        if chunk_id in seen_chunk_ids:
            continue

        seen_chunk_ids.add(chunk_id)

        combined_docs.append(doc)

    return combined_docs


if __name__ == "__main__":

    question = input(
        "\nEnter a question: "
    ).strip()

    docs = neo4j_retrieve(
        question,
        vector_k=4,
        graph_k=4,
    )

    print(
        f"\nRetrieved {len(docs)} unique chunks.\n"
    )

    for i, doc in enumerate(
        docs,
        1,
    ):

        print(
            f"--- Result {i} ---"
        )

        print(
            f"Retrieval: "
            f"{doc.metadata.get('retrieval')}"
        )

        print(
            f"Chunk ID: "
            f"{doc.metadata.get('chunk_id')}"
        )

        print(
            f"Page: "
            f"{doc.metadata.get('page')}"
        )

        if doc.metadata.get("similarity") is not None:

            print(
                f"Similarity: "
                f"{doc.metadata.get('similarity'):.4f}"
            )

        if doc.metadata.get("concept"):

            print(
                f"Concepts: "
                f"{doc.metadata.get('concept')}"
            )

        print()

        print(
            doc.page_content[:500]
        )

        print()