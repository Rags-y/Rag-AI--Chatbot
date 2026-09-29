from langchain_groq import ChatGroq

from retriever import retrieve
from config import GROQ_API_KEY


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=GROQ_API_KEY,
    temperature=0.2,
)


def generate_answer(question: str):

    docs = retrieve(question, k=4)

    context = "\n\n".join(
        f"Page {doc.metadata.get('page')}:\n{doc.page_content}"
        for doc in docs
    )

    pages = []

    for doc in docs:
        page = doc.metadata.get("page")

        if page is not None and page not in pages:
            pages.append(page)

    prompt = f"""
You are a helpful document question-answering assistant.

Answer ONLY using the provided context.

Rules:
- Do not use outside knowledge.
- If the answer is partially available, answer only what is present.
- If the answer is not found, reply exactly:
I could not find this information in the document.

Context:
--------------------
{context}
--------------------

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    # Extract text safely
    if isinstance(response.content, str):
        answer = response.content

    elif isinstance(response.content, list):
        answer = ""

        for part in response.content:

            if isinstance(part, dict):
                answer += part.get("text", "")

            elif hasattr(part, "text"):
                answer += part.text

            else:
                answer += str(part)

    else:
        answer = str(response.content)

    # Add citations
    citation = "\n\nSources:\n"

    for page in pages:
        citation += f"- Page {page}\n"

    return answer + citation


if __name__ == "__main__":

    while True:

        question = input("\nAsk a question (or type 'exit'): ")

        if question.lower() in ["exit", "quit"]:
            break

        print("\nGenerating answer...\n")

        answer = generate_answer(question)

        print("=" * 80)
        print(answer)
        print("=" * 80)
        from langchain_groq import ChatGroq

from retriever import retrieve
from config import GROQ_API_KEY


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    groq_api_key=GROQ_API_KEY,
    temperature=0.2,
)


def generate_answer(question: str):

    docs = retrieve(question, k=4)

    context = "\n\n".join(
        f"Page {doc.metadata.get('page')}:\n{doc.page_content}"
        for doc in docs
    )

    pages = []

    for doc in docs:
        page = doc.metadata.get("page")

        if page is not None and page not in pages:
            pages.append(page)

    prompt = f"""
You are a helpful document question-answering assistant.

Answer ONLY using the provided context.

Rules:
- Do not use outside knowledge.
- If the answer is partially available, answer only what is present.
- If the answer is not found, reply exactly:
I could not find this information in the document.

Context:
--------------------
{context}
--------------------

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    # Extract text safely
    if isinstance(response.content, str):
        answer = response.content

    elif isinstance(response.content, list):
        answer = ""

        for part in response.content:

            if isinstance(part, dict):
                answer += part.get("text", "")

            elif hasattr(part, "text"):
                answer += part.text

            else:
                answer += str(part)

    else:
        answer = str(response.content)

    # Add citations
    citation = "\n\nSources:\n"

    for page in pages:
        citation += f"- Page {page}\n"

    return answer + citation


if __name__ == "__main__":

    while True:

        question = input("\nAsk a question (or type 'exit'): ")

        if question.lower() in ["exit", "quit"]:
            break

        print("\nGenerating answer...\n")

        answer = generate_answer(question)

        print("=" * 80)
        print(answer)
        print("=" * 80)