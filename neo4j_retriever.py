from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

NEO4J_DATABASE = "64205e56"

from neo4j import GraphDatabase


# Neo4j connection
driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
)


# Load the embedding model only when it is first needed.
# Reuse the same model for subsequent searches.
@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def vector_search(query: str, k: int = 4) -> list[Document]:
    """Retrieve relevant document chunks using the Neo4j vector index."""

    query_embedding = get_embeddings().embed_query(query)

    cypher_query = """
    CALL db.index.vector.queryNodes(
        'chunk_embedding_index',
        $k,
        $embedding
    )
    YIELD node, score
    RETURN node, score
    ORDER BY score DESC
    """

    documents = []

    with driver.session(database=NEO4J_DATABASE) as session:
        results = session.run(
            cypher_query,
            k=k,
            embedding=query_embedding,
        )

        for record in results:
            node = record["node"]
            score = record["score"]

            text = node.get("text", "")

            metadata = {
                key: value
                for key, value in dict(node).items()
                if key not in ("text", "embedding")
            }

            metadata["similarity"] = score

            documents.append(
                Document(
                    page_content=text,
                    metadata=metadata,
                )
            )

    return documents


def graph_expand(documents: list[Document]) -> list[Document]:
    """Expand retrieved chunks using connected nodes in the Neo4j graph."""

    if not documents:
        return []

    expanded_documents = list(documents)
    seen_texts = {doc.page_content for doc in expanded_documents}

    cypher_query = """
    MATCH (c:Chunk)-[*1..2]-(related:Chunk)
    WHERE elementId(c) IN $chunk_ids
      AND related.text IS NOT NULL
    RETURN DISTINCT related
    LIMIT 10
    """

    chunk_ids = []

    with driver.session(database=NEO4J_DATABASE) as session:
        for doc in documents:
            page = doc.metadata.get("page")
            source = doc.metadata.get("source")

            if page is None:
                continue

            results = session.run(
                """
                MATCH (c:Chunk)
                WHERE c.page = $page
                  AND ($source IS NULL OR c.source = $source)
                RETURN elementId(c) AS chunk_id
                LIMIT 1
                """,
                page=page,
                source=source,
            )

            for record in results:
                chunk_ids.append(record["chunk_id"])

        if not chunk_ids:
            return expanded_documents

        results = session.run(
            cypher_query,
            chunk_ids=chunk_ids,
        )

        for record in results:
            node = record["related"]
            text = node.get("text", "")

            if not text or text in seen_texts:
                continue

            metadata = {
                key: value
                for key, value in dict(node).items()
                if key not in ("text", "embedding")
            }

            expanded_documents.append(
                Document(
                    page_content=text,
                    metadata=metadata,
                )
            )

            seen_texts.add(text)

    return expanded_documents


def neo4j_retrieve(
    query: str,
    k: int = 4,
    vector_k: int | None = None,
) -> list[Document]:
    if vector_k is not None:
        k = vector_k

    documents = vector_search(query, k=k)
    return graph_expand(documents)
