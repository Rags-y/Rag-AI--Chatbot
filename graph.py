from typing import TypedDict

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

from retriever import retrieve
from config import GOOGLE_API_KEY


llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=GOOGLE_API_KEY,
    temperature=0,
)


class GraphState(TypedDict):
    question: str
    context: str
    answer: str


def retrieve_node(state):

    docs = retrieve(
        state["question"],
        k=8,
    )

    print("\nQUESTION:", state["question"])

    for i, doc in enumerate(docs, start=1):
        print("=" * 70)
        print(
            f"Chunk {i} | Page {doc.metadata.get('page_label', doc.metadata.get('page'))}"
        )
        print(doc.page_content[:300])

    context = "\n\n".join(
        f"Page {doc.metadata.get('page_label', doc.metadata.get('page'))}\n"
        f"{doc.page_content}"
        for doc in docs
    )

    return {
        "context": context
    }


def generate(state):

    prompt = f"""
You are an AI assistant answering questions from a PDF.

Use ONLY the supplied context.

The answer may be spread across multiple chunks.

Combine information from all relevant chunks into one complete answer.

If the answer is not present in the context, reply exactly:

I couldn't find that information in the provided document.

Context
--------
{state["context"]}

Question
--------
{state["question"]}

Answer
"""

    response = llm.invoke(prompt)

    if isinstance(response.content, str):
        answer = response.content
    else:
        answer = ""
        for part in response.content:
            if isinstance(part, dict):
                answer += part.get("text", "")

    return {
        "answer": answer
    }


builder = StateGraph(GraphState)

builder.add_node("retrieve", retrieve_node)
builder.add_node("generate", generate)

builder.set_entry_point("retrieve")

builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)

graph = builder.compile()