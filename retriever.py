from supabase import create_client
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from config import SUPABASE_URL, SUPABASE_KEY


print("Connecting to Supabase...")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)


# Load embedding model only once
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    encode_kwargs={"normalize_embeddings": True},
)


def retrieve(query: str, k: int = 4):
    """
    Retrieve relevant documents from Supabase using RPC vector search.
    """

    print(f"\nSearching: {query}")

    # Convert the query into a vector
    query_embedding = embeddings.embed_query(query)

    # Call Supabase RPC search function
    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_count": k,
        },
    ).execute()

    results = response.data

    print(f"Retrieved {len(results)} documents.\n")

    # Convert Supabase results into LangChain Documents
    docs = []

    for i, result in enumerate(results, 1):

        metadata = result.get("metadata") or {}

        # Include similarity score in metadata
        metadata["similarity"] = result.get("similarity")

        doc = Document(
            page_content=result["content"],
            metadata=metadata,
        )

        docs.append(doc)

        print(f"--- Retrieved Chunk {i} ---")
        print(f"Page: {metadata.get('page')}")
        print(f"Similarity: {metadata.get('similarity'):.4f}")
        print(doc.page_content[:500])
        print()

    return docs