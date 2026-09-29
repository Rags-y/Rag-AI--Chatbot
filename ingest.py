from supabase import create_client

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from config import SUPABASE_URL, SUPABASE_KEY


print("Connecting to Supabase...")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)

print("Loading PDF...")

loader = PyPDFLoader("data/Agentic AI.pdf")
documents = loader.load()

print(f"Loaded {len(documents)} pages")


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=150,
)

chunks = text_splitter.split_documents(documents)


# Remove very small / low-information chunks
chunks = [
    chunk
    for chunk in chunks
    if len(chunk.page_content.strip()) >= 100
]


# Remove exact duplicate chunks
unique_chunks = []
seen = set()

for chunk in chunks:
    content = chunk.page_content.strip()

    if content not in seen:
        seen.add(content)
        unique_chunks.append(chunk)

chunks = unique_chunks


# Add metadata
for i, chunk in enumerate(chunks):
    chunk.metadata["source"] = "Agentic AI.pdf"
    chunk.metadata["chunk_id"] = i


print(f"Created {len(chunks)} cleaned unique chunks")

print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    encode_kwargs={"normalize_embeddings": True},
)


print("Generating embeddings...")

texts = [chunk.page_content for chunk in chunks]

vectors = embeddings.embed_documents(texts)

print(f"Generated {len(vectors)} embeddings")


print("Uploading chunks to Supabase...")


rows = []

for chunk, vector in zip(chunks, vectors):

    rows.append(
        {
            "content": chunk.page_content,
            "metadata": chunk.metadata,
            "embedding": vector,
        }
    )


# Upload in batches
batch_size = 50

for i in range(0, len(rows), batch_size):

    batch = rows[i:i + batch_size]

    supabase.table("documents").insert(batch).execute()

    print(
        f"Uploaded {min(i + batch_size, len(rows))}/{len(rows)} chunks"
    )


print("All chunks uploaded successfully!")