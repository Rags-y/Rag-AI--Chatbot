# Hybrid RAG AI Chatbot

A document-grounded RAG chatbot that answers questions from a PDF using semantic vector retrieval, graph-based retrieval, and a Groq LLM.

The project combines Supabase pgvector for semantic search with Neo4j for graph-based relationships between document chunks and concepts.



## Architecture

```text
                         User Question
                              │
                              ▼
                     ┌─────────────────┐
                     │ Hybrid Retriever│
                     └────────┬────────┘
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        ┌─────────────────┐       ┌─────────────────┐
        │    Supabase     │       │     Neo4j       │
        │    pgvector     │       │   Graph DB      │
        │                 │       │                 │
        │ Semantic Search │       │ Concepts/Chunks │
        └────────┬────────┘       └────────┬────────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                       Retrieved Context
                              │
                              ▼
                     ┌─────────────────┐
                     │    Groq LLM     │
                     │  GPT-OSS-20B    │
                     └────────┬────────┘
                              │
                              ▼
                       Grounded Answer
                              │
                              ▼
                         Page Sources
                         
                         
```
## How It Works

The PDF document is loaded and split into smaller chunks.
Each chunk is converted into an embedding using:
BAAI/bge-base-en-v1.5
The embeddings are stored in Supabase PostgreSQL with pgvector.
The same document chunks are stored in Neo4j.
Important concepts are connected to relevant chunks using graph relationships.
When a user asks a question:
Vector search retrieves semantically similar chunks.
Neo4j retrieves graph-related chunks and concepts.
The results are combined and deduplicated.
The retrieved context is passed to Groq's GPT-OSS-20B model.
The LLM generates an answer using only the retrieved document context.
The response includes the relevant document page numbers as sources.

## Features

PDF-based question answering
Semantic vector search
Graph-based retrieval
Hybrid RAG pipeline
Supabase pgvector vector database
Neo4j graph database
Groq LLM generation
Hugging Face BGE embeddings
Context deduplication
Document-grounded responses
Page-level source citations
Hallucination protection through context-only prompting

## Tech Stack

| Component              | Technology                     |
| ---------------------- | ------------------------------ |
| Language               | Python                         |
| LLM                    | Groq - GPT-OSS-20B             |
| Embeddings             | BAAI/bge-base-en-v1.5          |
| Vector Database        | Supabase PostgreSQL + pgvector |
| Graph Database         | Neo4j                          |
| RAG Framework          | LangChain                      |
| PDF Processing         | PyPDF                          |
| UI                     | Streamlit                      |
| Environment Management | python-dotenv                  |

## Project Structure 

Rag AI  Chatbot/
│
├── app.py
├── config.py
├── generator.py
├── graph.py
├── hybrid_retriever.py
├── ingest.py
├── retriever.py
│
├── data/
│   └── Agentic AI.pdf
│
├── scripts/
│   ├── add_concepts.py
│   ├── check_chunks.py
│   ├── check_chunk_concepts.py
│   ├── check_index.py
│   ├── clear_index.py
│   ├── ingest_neo4j.py
│   ├── setup_neo4j.py
│   └── test_neo4j.py
│
├── supabase/
│   └── schema.sql
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt

## Setup

1. Clone the repository
git clone https://github.com/Rags-y/Rag-AI--Chatbot.git
cd Rag-AI--Chatbot
2. Create a virtual environment
python -m venv .venv

Activate it on Windows:

.venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt
Environment Variables

Create a .env file in the project root.

Use .env.example as a template:

SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_secret_key

NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password

GROQ_API_KEY=your_groq_api_key

Never commit .env or API keys to GitHub.

## Supabase Setup

The project uses PostgreSQL with the vector extension.

Run the SQL in:

supabase/schema.sql

The database contains a documents table with:

document content
metadata
vector embeddings

A PostgreSQL RPC function is used to perform similarity search against the stored embeddings.

## Neo4j Setup

Create a Neo4j Aura database and configure the following variables:

NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password

Run:

python scripts/test_neo4j.py

Then create the graph schema:

python scripts/setup_neo4j.py
Ingestion
Vector Database

Run:

python ingest.py

This:

Loads the PDF.
Splits it into chunks.
Generates embeddings.
Stores the chunks and embeddings in Supabase.
Neo4j Graph

Run:

python scripts/ingest_neo4j.py

This creates:

(:Document)-[:CONTAINS]->(:Chunk)

Then create concept relationships:

python scripts/add_concepts.py

This creates relationships such as:

(:Chunk)-[:MENTIONS]->(:Concept)

Example:

Chunk ──MENTIONS──> Agentic AI
Chunk ──MENTIONS──> Planning
Chunk ──MENTIONS──> RAG
Running the Chatbot

Run:

python generator.py

Ask a question:

What is Agentic AI?

The system retrieves relevant information from both the vector and graph layers before generating the answer.

Example
Question
What is Agentic AI?
Answer
Agentic AI refers to systems capable of autonomous decision-making
and action in pursuit of specific objectives.
Sources
- Page 17
- Page 53
- Page 1
- Page 3

## Hallucination Protection

The generator is explicitly instructed to answer only from the retrieved document context.

For example, asking:

What is the capital of France?

when the information is not present in the PDF produces:

I could not find this information in the document.

This prevents the LLM from answering using outside knowledge.

Hybrid Retrieval

The retrieval pipeline combines two approaches.

Vector Retrieval

Supabase pgvector finds chunks that are semantically similar to the user's question.

Question
   │
   ▼
Embedding
   │
   ▼
Supabase pgvector
   │
   ▼
Similar document chunks
Graph Retrieval

Neo4j connects document chunks through concepts.

Question
   │
   ▼
Relevant concepts/chunks
   │
   ▼
Neo4j graph
   │
   ▼
Related document chunks

The results are combined and duplicate chunks are removed before being passed to the LLM.

Data

The included document is:

data/Agentic AI.pdf

The current dataset contains:

60 PDF pages
153 unique document chunks
13 graph concepts
155 concept-to-chunk relationships

## Future Improvements

Possible future improvements include:

Better automatic concept extraction
Graph-based query understanding
Retrieval reranking
Hybrid retrieval scoring
Conversational memory
Evaluation benchmarks
Streaming responses
Improved source attribution
More advanced graph traversal

## Author
Raghav Kumar
