# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This file defines the prompt templates used when talking to the LLM.
# A PromptTemplate is like a form letter with blanks to fill in.
# For example: "You are a helpful assistant. Context: {context}. Question: {question}"
# LangChain fills in the blanks at runtime with real data.
# Having templates here (not scattered in code) makes them easy to tune.
# ─────────────────────────────────────────────────────────────────────────────

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def get_rag_prompt() -> ChatPromptTemplate:
    """
    Returns the prompt template used for RAG (Retrieval-Augmented Generation) chat.

    ANATOMY OF THIS PROMPT:
      - System message: Sets the chatbot's persona and rules.
      - {context}: Will be replaced with relevant text chunks from ChromaDB.
      - {chat_history}: Will be replaced with previous messages in this session.
      - {question}: Will be replaced with the user's latest message.

    WHY A SYSTEM MESSAGE?
      The system message is invisible to end users but sets the behaviour rules
      for the LLM. It's the most powerful part of prompt engineering.

    Returns:
        ChatPromptTemplate: A LangChain prompt object ready for .format_messages()
    """
    system_message = (
        "You are a helpful, knowledgeable assistant. "
        "Use the following retrieved context to answer the user's question accurately. "
        "If the context does not contain enough information to answer, say so clearly "
        "rather than making something up. "
        "Always be concise and cite the source if you use context information.\n\n"
        "Retrieved Context:\n"
        "─────────────────\n"
        "{context}\n"
        "─────────────────"
    )

    return ChatPromptTemplate.from_messages([
        # "system" role: instructions to the LLM about how to behave
        ("system", system_message),
        # MessagesPlaceholder: inserts the full chat history here as a list of messages
        # This is how multi-turn memory works — LangChain serialises old messages here
        MessagesPlaceholder(variable_name="chat_history"),
        # "human" role: the user's latest question
        ("human", "{question}"),
    ])


def get_simple_chat_prompt() -> ChatPromptTemplate:
    """
    Returns a simple chat prompt template (no RAG context).

    Used as a fallback when no documents have been indexed yet,
    or when the retriever returns no relevant results.

    Returns:
        ChatPromptTemplate: A simple prompt with just history + question.
    """
    system_message = (
        "You are a helpful and friendly assistant. "
        "Answer the user's questions clearly and concisely. "
        "If you don't know something, say so honestly."
    )

    return ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])
