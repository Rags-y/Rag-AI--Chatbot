import streamlit as st

from rag_graph import generate_answer


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Agentic AI Assistant",
    page_icon="🤖",
    layout="centered",
)


# --------------------------------------------------
# Custom styling
# --------------------------------------------------

st.markdown(
    """
    <style>

    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #777;
        margin-bottom: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🤖 Agentic AI Assistant</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Ask questions about the Agentic AI document'
    '</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header("About")

    st.write(
        """
        This assistant answers questions using the
        **Agentic AI document** as its source of truth.
        """
    )

    st.divider()

    st.markdown("### Retrieval")

    st.write(
        """
        **Neo4j**

        • Vector search  
        • Graph expansion  
        • Concept relationships
        """
    )

    st.markdown("### Generation")

    st.write(
        """
        **Groq**

        Model: `GPT-OSS-20B`
        """
    )

    st.divider()

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.rerun()


# --------------------------------------------------
# Welcome message
# --------------------------------------------------

if not st.session_state.messages:

    with st.chat_message("assistant"):

        st.markdown(
            """
            👋 **Hello!**

            I'm an AI assistant that answers questions from
            the **Agentic AI document**.

            You can ask me things like:

            - What is Agentic AI?
            - What is planning?
            - What are AI agents?
            - How do agents use memory?
            - What are multi-agent systems?
            """
        )


# --------------------------------------------------
# Display previous messages
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        # Display sources separately
        if message["role"] == "assistant":

            sources = message.get("sources", [])

            if sources:

                st.markdown("**📚 Sources**")

                source_text = " · ".join(
                    f"Page {page}"
                    for page in sources
                )

                st.caption(source_text)


# --------------------------------------------------
# User input
# --------------------------------------------------

question = st.chat_input(
    "Ask a question about the document..."
)


if question:

    # --------------------------------------------------
    # User message
    # --------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):

        st.markdown(question)


    # --------------------------------------------------
    # Generate answer
    # --------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching the document and generating an answer..."
        ):

            try:

                result = generate_answer(
    question,
    chat_history=st.session_state.messages,
)

                answer = result["answer"]
                sources = result["sources"]

                st.markdown(answer)

                if sources:

                    st.markdown("**📚 Sources**")

                    source_text = " · ".join(
                        f"Page {page}"
                        for page in sources
                    )

                    st.caption(source_text)

            except Exception as e:

                answer = (
                    "Sorry, I couldn't generate an answer "
                    "right now."
                )

                sources = []

                st.error(answer)

                st.exception(e)


    # --------------------------------------------------
    # Save assistant message
    # --------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
        }
    )