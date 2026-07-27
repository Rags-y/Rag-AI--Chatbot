#  RAG AI Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that answers questions from a PDF document using semantic search and Google's Gemini model.

The chatbot retrieves the most relevant document sections from Pinecone and generates grounded answers using Gemini, ensuring responses are based only on the uploaded document.



## Features

- PDF document ingestion
- Semantic search using Hugging Face embeddings
- Pinecone vector database integration
- Retrieval-Augmented Generation (RAG)
- Google Gemini for answer generation
- Source page citations
- Interactive command-line chatbot
- Prevents hallucinations by answering only from the document



## Tech Stack

- Python
- LangChain
- Google Gemini API
- Pinecone
- Hugging Face Embeddings (BAAI/bge-base-en-v1.5)
- PyPDF
- Recursive Character Text Splitter



## Project Structure

text
RAG-AI-Chatbot/
│
├── data/
│   └── Agentic AI.pdf
│
├── ingest.py
├── retriever.py
├── generator.py
├── config.py
│
├── requirements.txt
├── README.md
├── .gitignore
└── .env




## Installation

### Clone the repository


git clone https://github.com/yourusername/RAG-AI-Chatbot.git

cd RAG-AI-Chatbot




### Create a virtual environment

Windows



### Install dependencies


pip install -r requirements.txt


### Configure environment variables

Create a `.env` file.


GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX=agentic-ai




## Upload the PDF

Place your PDF inside


data/


Example


data/Agentic AI.pdf




## Ingest the document


python ingest.py


This will:

- Load the PDF
- Split it into chunks
- Generate embeddings
- Upload vectors to Pinecone



## Run the chatbot


python generator.py


Example


Ask a question:

> What is Agentic AI?

Agentic AI refers to systems capable of autonomous decision-making and action in pursuit of specific objectives.

Sources:
Page 3
Page 18



## Example Questions

- What is Agentic AI?
- Explain the BDI model.
- What are Multi-Agent Systems?
- What industries use Agentic AI?
- What are the benefits of Agentic AI?
- Explain the architecture of Agentic AI.



## Sample Output

Ask a question:

What is Agentic AI?

Agentic AI refers to systems capable of autonomous decision-making and action in pursuit of specific objectives.

Sources:
Page 3
Page 18




## How It Works


          PDF
           │
           ▼
     PyPDF Loader
           │
           ▼
 Text Chunking
           │
           ▼
 Hugging Face Embeddings
           │
           ▼
     Pinecone Index
           │
           ▼
     User Question
           │
           ▼
 Semantic Retrieval
           │
           ▼
     Gemini LLM
           │
           ▼
 Final Answer + Sources




## Future Improvements

- Streamlit web interface
- Chat history
- Multiple PDF support
- Hybrid search (BM25 + Vector Search)
- Conversation memory
- Docker support
- Deployment on Render or Hugging Face Spaces



## Author

**Raghav Kumar**
