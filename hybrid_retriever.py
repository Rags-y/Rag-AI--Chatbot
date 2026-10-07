from retriever import retrieve
from graph import graph_search


def graph_expand_from_chunks(chunk_ids, limit=4):

    if not chunk_ids:
        return []

    from graph import driver
    from langchain_core.documents import Document

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

            ORDER BY size(shared_concepts) DESC, related.page

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
                    "concept": ", ".join(record["shared_concepts"]),
                    "retrieval": "graph",
                },
            )
        )

    return docs


def hybrid_retrieve(query: str, k: int = 4):

    vector_docs = retrieve(query, k=k)

    vector_chunk_ids = [
        doc.metadata.get("chunk_id")
        for doc in vector_docs
        if doc.metadata.get("chunk_id") is not None
    ]

    graph_docs = graph_search(
        query,
        limit=k,
    )

    if len(graph_docs) < k:

        expanded_docs = graph_expand_from_chunks(
            vector_chunk_ids,
            limit=k,
        )

        graph_docs.extend(expanded_docs)

    combined_docs = []

    seen = set()

    for doc in vector_docs + graph_docs:

        chunk_id = doc.metadata.get("chunk_id")

        if chunk_id is not None:

            if chunk_id in seen:
                continue

            seen.add(chunk_id)

        combined_docs.append(doc)

    return combined_docs


if __name__ == "__main__":

    question = input("\nEnter a question: ")

    docs = hybrid_retrieve(
        question,
        k=4,
    )

    print()

    for i, doc in enumerate(docs, 1):

        print(f"--- Hybrid Result {i} ---")

        print(
            f"Retrieval: "
            f"{doc.metadata.get('retrieval', 'vector')}"
        )

        print(
            f"Page: "
            f"{doc.metadata.get('page')}"
        )

        print(
            f"Chunk ID: "
            f"{doc.metadata.get('chunk_id')}"
        )

        if doc.metadata.get("concept"):
            print(
                f"Concept: "
                f"{doc.metadata.get('concept')}"
            )

        print(doc.page_content[:400])
        print()