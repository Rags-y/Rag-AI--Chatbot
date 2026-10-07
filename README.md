# Neo4j-Centered RAG AI Chatbot

A document-grounded RAG chatbot that answers questions from a PDF using semantic vector retrieval, graph-based context expansion, and a Groq LLM.

The system uses Neo4j as the central retrieval layer. Document chunks are stored in Neo4j together with their embeddings and relationships to concepts. Vector search first identifies semantically relevant chunks, and Neo4j graph traversal then expands the context using related concepts and chunks.

The retrieved context is passed to Groq's GPT-OSS-20B model to generate a grounded answer.

## Architecture

```text
                         User Question
                              │
                              ▼
                    BGE Query Embedding
                              │
                              ▼
                    ┌───────────────────┐
                    │       Neo4j       │
                    │                   │
                    │  Vector Search    │
                    │       │           │
                    │       ▼           │
                    │ Relevant Chunks   │
                    │       │           │
                    │       ▼           │
                    │ Graph Expansion   │
                    │       │           │
                    │       ▼           │
                    │ Related Chunks    │
                    │   & Concepts      │
                    └────────┬──────────┘
                             │
                             ▼
                     Unified Context
                             │
                             ▼
                    ┌───────────────────┐
                    │     Groq LLM      │
                    │    GPT-OSS-20B    │
                    └────────┬──────────┘
                             │
                             ▼
                     Grounded Answer
                             │
                             ▼
                       Page Sources
```

## How It Works

1. The PDF document is loaded and split into smaller chunks.
2. Each chunk is converted into an embedding using `BAAI/bge-base-en-v1.5`.
3. The chunks, embeddings, and document relationships are stored in Neo4j.
4. Important concepts are connected to relevant document chunks.
5. When a user asks a question:

   * The question is converted into a BGE embedding.
   * Neo4j performs vector similarity search to find relevant chunks.
   * The retrieved chunks become the starting points for graph traversal.
   * Neo4j follows concept relationships to find related chunks.
   * Vector and graph results are combined and deduplicated.
6. The unified context is passed to Groq's GPT-OSS-20B model.
7. The LLM generates an answer using only the retrieved document context.
8. The response includes the relevant PDF page numbers as sources.

This creates a single Neo4j-centered retrieval flow rather than maintaining separate vector and graph retrieval systems.

## Features

* PDF-based question answering
* Semantic vector search
* Neo4j vector index
* Graph-based context expansion
* Concept-to-chunk relationships
* Unified vector + graph retrieval
* Groq LLM generation
* Hugging Face BGE embeddings
* Context deduplication
* Document-grounded responses
* Page-level source attribution
* Hallucination protection through context-only prompting

## Tech Stack

| Component              | Technology            |
| ---------------------- | --------------------- |
| Language               | Python                |
| LLM                    | Groq - GPT-OSS-20B    |
| Embeddings             | BAAI/bge-base-en-v1.5 |
| Vector Database        | Neo4j Vector Index    |
| Graph Database         | Neo4j                 |
| RAG Framework          | LangChain             |
| PDF Processing         | PyPDF                 |
| UI                     | Streamlit             |
| Environment Management | python-dotenv         |

## Project Structure

```text
Rag AI  Chatbot/
│
├── app.py
├── config.py
├── generator.py
├── graph.py
├── neo4j_retriever.py
│
├── data/
│   └── Agentic AI.pdf
│
├── scripts/
│   ├── add_concepts.py
│   ├── check_chunks.py
│   ├── check_chunk_concepts.py
│   ├── check_neo4j_version.py
│   ├── check_supabase_legacy.py
│   ├── clear_index.py
│   ├── embed_neo4j_chunks.py
│   ├── ingest_neo4j.py
│   ├── setup_neo4j.py
│   ├── test_neo4j.py
│   └── test_neo4j_vector.py
│
├── hybrid_retriever_legacy.py
├── ingest_supabase_legacy.py
├── retriever_legacy.py
│
├── supabase/
│   └── schema.sql
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

The files ending in `_legacy.py` contain the previous Supabase-based retrieval implementation and are retained for reference and rollback during the migration.

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Rags-y/Rag-AI--Chatbot.git
cd Rag-AI--Chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root.

Use `.env.example` as a template:

```text
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password

GROQ_API_KEY=your_groq_api_key
```

Never commit `.env` or API keys to GitHub.

## Neo4j Setup

Create a Neo4j Aura database and configure:

```text
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

Test the connection:

```bash
python scripts/test_neo4j.py
```

Check the Neo4j version:

```bash
python scripts/check_neo4j_version.py
```

Create the graph schema:

```bash
python scripts/setup_neo4j.py
```

## Ingestion

### Ingest Document Chunks

Run:

```bash
python scripts/ingest_neo4j.py
```

This loads the PDF and creates the document and chunk structure:

```text
(:Document)-[:CONTAINS]->(:Chunk)
```

### Generate Chunk Embeddings

Run:

```bash
python scripts/embed_neo4j_chunks.py
```

This generates normalized BGE embeddings and stores them on the `Chunk` nodes.

Each embedding contains 768 dimensions.

### Create the Neo4j Vector Index

The vector index used by the retriever is:

```text
chunk_embedding_index
```

The index uses cosine similarity over the 768-dimensional BGE embeddings.

### Add Concept Relationships

Run:

```bash
python scripts/add_concepts.py
```

This creates relationships such as:

```text
(:Chunk)-[:MENTIONS]->(:Concept)
```

Example:

```text
Chunk ──MENTIONS──> Agentic AI
Chunk ──MENTIONS──> Planning
Chunk ──MENTIONS──> RAG
```

## Neo4j-Centered Retrieval

The main retrieval implementation is:

```text
neo4j_retriever.py
```

The retrieval flow is:

```text
Question
   │
   ▼
BGE Embedding
   │
   ▼
Neo4j Vector Search
   │
   ▼
Relevant Chunk Nodes
   │
   ▼
Concept Relationships
   │
   ▼
Related Chunk Nodes
   │
   ▼
Deduplicated Context
```

The important design decision is that graph expansion starts from the chunks returned by vector search.

Neo4j therefore acts as the common retrieval layer for both semantic and graph-based retrieval.

## Running the Retriever

Run:

```bash
python neo4j_retriever.py
```

Enter a question such as:

```text
What is Agentic AI?
```

The retriever returns the relevant vector-search chunks followed by graph-expanded chunks.

## Running the Chatbot

Run:

```bash
python generator.py
```

Example question:

```text
What is Agentic AI?
```

The system retrieves relevant context from Neo4j and generates a grounded response using Groq's GPT-OSS-20B model.

Example:

```text
Agentic AI refers to systems that can autonomously make decisions
and take actions to pursue specific objectives.

Sources:
- Page 17
- Page 53
- Page 16
- Page 7
```

## Hallucination Protection

The generator is explicitly instructed to answer only from the retrieved document context.

For example, asking:

```text
What is the capital of France?
```

when the information is not present in the PDF produces:

```text
I could not find this information in the document.
```

This prevents the LLM from answering using outside knowledge.

## Data

The included document is:

```text
data/Agentic AI.pdf
```

Current dataset:

* 60 PDF pages
* 153 unique document chunks
* 13 graph concepts
* 155 concept-to-chunk relationships
* 153 stored chunk embeddings
* 768-dimensional BGE embeddings

## Retrieval Validation

The Neo4j vector retrieval has been tested using the `chunk_embedding_index`.

For the question:

```text
What is Agentic AI?
```

Neo4j returned highly relevant chunks, including:

```text
Chunk 30 — Page 17
Chunk 140 — Page 53
Chunk 29 — Page 16
Chunk 8 — Page 7
```

Graph expansion then retrieved additional chunks connected through shared concepts such as `Agentic AI` and `Planning`.

The complete retrieval pipeline has also been tested through the Groq generator, including an out-of-document question to verify the hallucination fallback.

## Legacy Supabase Implementation

The project previously used Supabase PostgreSQL with pgvector for vector retrieval and Neo4j separately for graph retrieval.

Those files are retained as legacy references:

```text
retriever_legacy.py
hybrid_retriever_legacy.py
ingest_supabase_legacy.py
scripts/check_supabase_legacy.py
supabase/schema.sql
```

They are no longer part of the active chatbot retrieval pipeline.

The current implementation uses:

```text
Neo4j Vector Search
        +
Neo4j Graph Expansion
        ↓
Unified Context
        ↓
Groq LLM
```

## Future Improvements

Possible future improvements include:

* Better automatic concept extraction
* Retrieval reranking
* Conversational memory
* Evaluation benchmarks
* Streaming responses
* Improved source attribution
* More advanced graph traversal

## Author
Raghav Kumar
