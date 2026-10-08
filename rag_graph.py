from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq

from neo4j_retriever import neo4j_retrieve
from config import GROQ_API_KEY


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=GROQ_API_KEY,
    temperature=0.2,
)


class RAGState(TypedDict):
    question: str
    chat_history: list
    standalone_question: str
    context: str
    pages: list
    answer: str


def rewrite_question_node(state: RAGState):
    question = state["question"]
    chat_history = state.get("chat_history", [])

    # No history means the question is already standalone.
    if not chat_history:
        return {
            "standalone_question": question
        }

    history_text = ""

    for message in chat_history[-6:]:
        role = message.get("role", "")
        content = message.get("content", "")

        history_text += (
            f"{role.upper()}: {content}\n"
        )

    prompt = f"""
You are helping a document question-answering system.

Rewrite the user's latest question into a standalone question
that can be searched against the document.

Use the conversation history only to resolve references such as:

- it
- they
- this
- that
- its
- their
- the above
- what about it

Do not answer the question.

Do not add information that is not present in the conversation.

If the question is already standalone, return it unchanged.

CONVERSATION HISTORY
====================
{history_text}

LATEST QUESTION
================
{question}

STANDALONE QUESTION
===================
"""

    response = llm.invoke(prompt)

    if isinstance(response.content, str):
        standalone_question = response.content.strip()

    elif isinstance(response.content, list):
        standalone_question = ""

        for part in response.content:
            if isinstance(part, dict):
                standalone_question += part.get(
                    "text",
                    ""
                )
            elif hasattr(part, "text"):
                standalone_question += part.text
            else:
                standalone_question += str(part)

        standalone_question = standalone_question.strip()

    else:
        standalone_question = str(
            response.content
        ).strip()

    return {
        "standalone_question": standalone_question
    }


def retrieve_node(state: RAGState):
    # Use the rewritten standalone question for retrieval.
    question = state["standalone_question"]

    docs = neo4j_retrieve(
        question,
        vector_k=4,
        graph_k=4,
    )

    unique_docs = []
    seen_content = set()

    for doc in docs:
        content = doc.page_content.strip()

        if not content:
            continue

        if content in seen_content:
            continue

        seen_content.add(content)
        unique_docs.append(doc)

    # Keep all unique vector + graph results.
    docs = unique_docs

    context_parts = []
    pages = []

    for doc in docs:
        page = doc.metadata.get("page")

        context_parts.append(
            f"[Page {page}]\n"
            f"{doc.page_content}"
        )

        if page is not None and page not in pages:
            pages.append(page)

    context = "\n\n".join(context_parts)

    return {
        "context": context,
        "pages": pages,
    }


def generate_node(state: RAGState):
    question = state["question"]
    context = state["context"]

    prompt = f"""
You are a document question-answering assistant.

Your task is to answer the user's question using ONLY the
information contained in the document context below.

IMPORTANT RULES:

1. Carefully read ALL of the provided context before answering.
2. If the answer is present in the context, answer the question.
3. The wording of the question does not need to exactly match
   the wording in the document.
4. You may combine information from multiple pages.
5. Do not use outside knowledge.
6. Do not invent information.
7. If the document contains relevant information, do NOT say
   that the information could not be found.
8. Only use the fallback response if the provided context
   genuinely contains no information that can answer the question.

If the answer genuinely cannot be found in the context, respond exactly:

I could not find this information in the document.

DOCUMENT CONTEXT
================
{context}
================

QUESTION
========
{question}

ANSWER
======
"""

    response = llm.invoke(prompt)

    if isinstance(response.content, str):
        answer = response.content.strip()

    elif isinstance(response.content, list):
        answer = ""

        for part in response.content:
            if isinstance(part, dict):
                answer += part.get(
                    "text",
                    ""
                )
            elif hasattr(part, "text"):
                answer += part.text
            else:
                answer += str(part)

        answer = answer.strip()

    else:
        answer = str(
            response.content
        ).strip()

    return {
        "answer": answer
    }


# --------------------------------------------------
# Build LangGraph
# --------------------------------------------------

builder = StateGraph(RAGState)

builder.add_node(
    "rewrite_question",
    rewrite_question_node,
)

builder.add_node(
    "retrieve",
    retrieve_node,
)

builder.add_node(
    "generate",
    generate_node,
)

builder.add_edge(
    START,
    "rewrite_question",
)

builder.add_edge(
    "rewrite_question",
    "retrieve",
)

builder.add_edge(
    "retrieve",
    "generate",
)

builder.add_edge(
    "generate",
    END,
)

rag_graph = builder.compile()


def generate_answer(
    question: str,
    chat_history: list | None = None,
):
    if chat_history is None:
        chat_history = []

    result = rag_graph.invoke(
        {
            "question": question,
            "chat_history": chat_history,
            "standalone_question": "",
            "context": "",
            "pages": [],
            "answer": "",
        }
    )

    return {
        "answer": result["answer"],
        "sources": result.get(
            "pages",
            []
        ),
    }


if __name__ == "__main__":

    while True:

        try:
            question = input(
                "\nAsk a question (or type 'exit'): "
            ).strip()

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if question.lower() in [
            "exit",
            "quit",
        ]:
            break

        if not question:
            continue

        print("\nGenerating answer...\n")

        try:
            result = generate_answer(question)

            print("=" * 80)

            print(result["answer"])

            print("\nSources:")

            for page in result["sources"]:
                print(f"- Page {page}")

            print("=" * 80)

        except Exception as e:

            print("\nError:")
            print(e)