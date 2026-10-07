from supabase import create_client
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from config import SUPABASE_URL, SUPABASE_KEY


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)


embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    encode_kwargs={
        "normalize_embeddings": True
    },
)


def retrieve(query: str, k: int = 4):

    query_embedding = embeddings.embed_query(query)

    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_count": k,
        },
    ).execute()

    results = response.data

    docs = []

    for result in results:

        metadata = result.get("metadata") or {}

        metadata["similarity"] = result.get(
            "similarity"
        )

        doc = Document(
            page_content=result["content"],
            metadata=metadata,
        )

        docs.append(doc)

    return docs


if __name__ == "__main__":

    question = input(
        "\nEnter a question: "
    )

    docs = retrieve(
        question,
        k=4,
    )

    print(
        f"\nRetrieved {len(docs)} documents.\n"
    )

    for i, doc in enumerate(docs, 1):

        print(
            f"--- Retrieved Chunk {i} ---"
        )

        print(
            f"Page: "
            f"{doc.metadata.get('page')}"
        )

        print(
            f"Similarity: "
            f"{doc.metadata.get('similarity'):.4f}"
        )

        print(
            doc.page_content[:500]
        )

        print()