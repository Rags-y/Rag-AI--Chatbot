
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rag_graph import generate_answer


app = FastAPI(
    title="Nexa AI API",
    description="API for the Agentic AI document RAG chatbot",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://rag-ai-chatbot-eta.vercel.app",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10000)
    chat_history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    sources: list[int] = Field(default_factory=list)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Nexa AI API"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    question = request.question.strip()

    if not question:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    history = [
        message.model_dump()
        for message in request.chat_history
    ]

    result = generate_answer(
        question=question,
        chat_history=history,
    )

    return ChatResponse(
        answer=result["answer"],
        sources=[
            int(page)
            for page in result.get("sources", [])
            if str(page).isdigit()
        ],
    )
