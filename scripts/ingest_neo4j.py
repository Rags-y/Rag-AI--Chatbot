from neo4j import GraphDatabase

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
)


PDF_PATH = "data/Agentic AI.pdf"


print("Loading PDF...")

loader = PyPDFLoader(PDF_PATH)
documents = loader.load()

print(f"Loaded {len(documents)} pages")


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=150,
)

chunks = text_splitter.split_documents(documents)

chunks = [
    chunk
    for chunk in chunks
    if len(chunk.page_content.strip()) >= 100
]


# Remove duplicate chunks
unique_chunks = []
seen = set()

for chunk in chunks:

    content = chunk.page_content.strip()

    if content not in seen:
        seen.add(content)
        unique_chunks.append(chunk)


chunks = unique_chunks

print(f"Created {len(chunks)} unique chunks")


print("Connecting to Neo4j...")

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
)


def create_document(tx):
    tx.run(
        """
        MERGE (d:Document {id: $id})
        SET d.name = $name
        """,
        id="agentic-ai-pdf",
        name="Agentic AI.pdf",
    )


def create_chunk(tx, chunk_id, content, page):
    tx.run(
        """
        MATCH (d:Document {id: $document_id})

        MERGE (c:Chunk {id: $chunk_id})

        SET
            c.content = $content,
            c.page = $page

        MERGE (d)-[:CONTAINS]->(c)
        """,
        document_id="agentic-ai-pdf",
        chunk_id=chunk_id,
        content=content,
        page=page,
    )


try:

    driver.verify_connectivity()

    print("Neo4j connection successful!")

    with driver.session() as session:

        print("Creating document node...")

        session.execute_write(create_document)

        print("Uploading chunks...")

        for i, chunk in enumerate(chunks):

            page = chunk.metadata.get("page")

            session.execute_write(
                create_chunk,
                i,
                chunk.page_content.strip(),
                page,
            )

            print(
                f"Uploaded chunk {i + 1}/{len(chunks)}"
            )

    print("\nNeo4j graph ingestion completed successfully!")

finally:

    driver.close()