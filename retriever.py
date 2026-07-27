from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

from config import PINECONE_INDEX

print(f"Using index: {PINECONE_INDEX}")

# Load embedding model only once
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    encode_kwargs={"normalize_embeddings": True},
)

# Connect to Pinecone
vectorstore = PineconeVectorStore(
    index_name=PINECONE_INDEX,
    embedding=embeddings,
)


def retrieve(query: str, k: int = 4):
    """
    Retrieve the most relevant documents from Pinecone.

    Args:
        query: User question
        k: Number of chunks to retrieve

    Returns:
        List of Documents
    """

    print(f"\nSearching: {query}")

    docs = vectorstore.similarity_search(
        query=query,
        k=k,
    )

    print(f"Retrieved {len(docs)} documents.\n")

    return docs