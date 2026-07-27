from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

from config import PINECONE_INDEX

print("Loading PDF...")

loader = PyPDFLoader("data/Agentic AI.pdf")
documents = loader.load()
for i in range(8):
    


print(f"Loaded {len(documents)} pages")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=150
)

chunks = text_splitter.split_documents(documents)

for chunk in chunks:
    chunk.metadata["source"] = "Agentic AI.pdf"

print(f"Created {len(chunks)} chunks")

print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    encode_kwargs={"normalize_embeddings": True}
)

print("Uploading to Pinecone...")

PineconeVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    index_name=PINECONE_INDEX,
)

print("✅ All chunks uploaded successfully!")