from langchain_groq import ChatGroq

from neo4j_retriever import neo4j_retrieve
from config import GROQ_API_KEY


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=GROQ_API_KEY,
    temperature=0.2,
)


def generate_answer(question: str):

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

    docs = unique_docs[:4]

    context_parts = []

    for doc in docs:
        page = doc.metadata.get("page")

        context_parts.append(
            f"[Page {page}]\n"
            f"{doc.page_content}"
        )

    context = "\n\n".join(context_parts)

    pages = []

    for doc in docs:
        page = doc.metadata.get("page")

        if page is not None and page not in pages:
            pages.append(page)

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
                answer += part.get("text", "")
            elif hasattr(part, "text"):
                answer += part.text
            else:
                answer += str(part)

        answer = answer.strip()

    else:
        answer = str(response.content).strip()

    citation = "\n\nSources:\n"

    for page in pages:
        citation += f"- Page {page}\n"

    return answer + citation


if __name__ == "__main__":

    while True:

        try:
            question = input(
                "\nAsk a question (or type 'exit'): "
            ).strip()

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if question.lower() in ["exit", "quit"]:
            print("Exiting...")
            break

        if not question:
            continue

        print("\nGenerating answer...\n")

        try:
            answer = generate_answer(question)

            print("=" * 80)
            print(answer)
            print("=" * 80)

        except Exception as e:
            print("\nError while generating answer:")
            print(e)