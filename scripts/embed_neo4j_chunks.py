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

    with driver.session() as session:

        result = session.run(
            """
            MATCH (c:Chunk)
            RETURN c.id AS chunk_id, c.content AS content
            ORDER BY c.id
            """
        )

        chunks = list(result)

    print(f"Found {len(chunks)} chunks.")

    if not chunks:
        raise RuntimeError(
            "No Chunk nodes found in Neo4j."
        )

    print("Generating embeddings...")

    texts = [
        record["content"]
        for record in chunks
    ]

    vectors = embeddings.embed_documents(texts)

    print(
        f"Generated {len(vectors)} embeddings."
    )

    with driver.session() as session:

        for i, (record, vector) in enumerate(
            zip(chunks, vectors),
            start=1,
        ):

            session.run(
                """
                MATCH (c:Chunk {id: $chunk_id})
                SET c.embedding = $embedding
                """,
                chunk_id=record["chunk_id"],
                embedding=vector,
            )

            if i % 10 == 0 or i == len(chunks):

                print(
                    f"Updated {i}/{len(chunks)} chunks"
                )

    print(
        "\nNeo4j chunk embeddings added successfully!"
    )

finally:

    driver.close()