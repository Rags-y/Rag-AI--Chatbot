from neo4j import GraphDatabase
from langchain_huggingface import HuggingFaceEmbeddings

from config import (
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
)


print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    encode_kwargs={
        "normalize_embeddings": True
    },
)


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(
        NEO4J_USERNAME,
        NEO4J_PASSWORD,
    ),
)


try:

    driver.verify_connectivity()

    print("Neo4j connection successful!")

    question = input(
        "\nEnter a question: "
    ).strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    print("\nGenerating query embedding...")

    query_embedding = embeddings.embed_query(
        question
    )

    print("Searching Neo4j vector index...")

    with driver.session() as session:

        result = session.run(
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
    node.page AS page,
    node.content AS content,
    score

ORDER BY score DESC
            """,
            k=4,
            query_embedding=query_embedding,
        )

        records = list(result)

    print(
        f"\nRetrieved {len(records)} chunks.\n"
    )

    for i, record in enumerate(records, 1):

        print(
            f"--- Neo4j Vector Result {i} ---"
        )

        print(
            f"Chunk ID: "
            f"{record['chunk_id']}"
        )

        print(
            f"Page: "
            f"{record['page']}"
        )

        print(
            f"Similarity: "
            f"{record['score']:.4f}"
        )

        print(
            record["content"][:500]
        )

        print()

finally:

    driver.close()