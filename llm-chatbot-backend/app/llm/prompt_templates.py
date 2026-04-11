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
        "You are ShopFast Assistant, an AI shopping assistant for the ShopFast online store.\n\n"
        "## TOOL USAGE — MANDATORY RULES\n"
        "You have tools to access live store data. Follow these rules strictly:\n"
        "- User asks what products exist / what's for sale → call list_all_products\n"
        "- User wants to find or search for a product → call search_products\n"
        "- User wants details about a specific product → call get_product_details\n"
        "- User wants to see their cart or total → call view_cart\n"
        "- User wants to buy / add something to cart → call add_to_cart\n\n"
        "IMPORTANT: NEVER answer questions about products, prices, or the cart from the "
        "knowledge base context below. That context is ONLY for store policies and FAQs. "
        "For all product and cart queries, you MUST call the appropriate tool.\n\n"
        "## KNOWLEDGE BASE CONTEXT (policies and FAQs only)\n"
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

    TOOL CALLING NOTE:
      Even in simple mode, the LLM may still call tools (e.g. to search products).
      The system message instructs it to use tools for live data.

    Returns:
        ChatPromptTemplate: A simple prompt with just history + question.
    """
    system_message = (
        "You are ShopFast Assistant, an AI shopping assistant for the ShopFast online store.\n\n"
        "## TOOL USAGE — MANDATORY RULES\n"
        "You have tools to access live store data. Follow these rules strictly:\n"
        "- User asks what products exist / what's for sale → call list_all_products\n"
        "- User wants to find or search for a product → call search_products\n"
        "- User wants details about a specific product → call get_product_details\n"
        "- User wants to see their cart or total → call view_cart\n"
        "- User wants to buy / add something to cart → call add_to_cart\n\n"
        "NEVER answer questions about products, prices, or the cart from memory or guessing. "
        "Always call the appropriate tool to get live, accurate data. Be friendly and concise."
    )

    return ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])
