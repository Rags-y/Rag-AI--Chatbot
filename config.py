import os
from dotenv import load_dotenv

load_dotenv()


PINECONE_INDEX = "agentic-ai"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")