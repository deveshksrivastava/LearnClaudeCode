# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This file contains each "node" in the LangGraph conversation graph.
# A node is just a Python function that:
#   1. Receives the current state (a dict with all conversation data)
#   2. Does some work (validate, retrieve, build prompt, call LLM, etc.)
#   3. Returns a dict with only the fields it changed (LangGraph merges this back)
#
# The graph runs nodes in sequence: receive_input → retrieve_context →
# build_prompt → call_llm → format_response → END
# ─────────────────────────────────────────────────────────────────────────────

import logging
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from app.graph.state import ConversationState
from app.llm.prompt_templates import get_rag_prompt, get_simple_chat_prompt
from app.rag.retriever import retrieve_context, RetrievalResult
from llama_index.core import VectorStoreIndex

logger = logging.getLogger(__name__)


def make_receive_input_node():
    """
    Factory function that returns the 'receive_input' node function.

    WHY A FACTORY PATTERN?
      LangGraph nodes must be simple functions with signature: (state) -> dict.
      If a node needs dependencies (like an LLM client), we use factories —
      closures that capture the dependency and return a plain function.
      This keeps the graph definition clean and makes nodes easy to test.

    Returns:
        Callable: A node function with signature (ConversationState) -> dict.
    """
    def receive_input(state: ConversationState) -> dict:
        """
        Node 1: Validates and logs the incoming user message.

        WHAT DOES THIS NODE DO?
          - Checks that user_input is not empty
          - Logs the incoming message for debugging
          - If invalid, sets error so downstream nodes can skip

        Args:
            state: The current conversation state.

        Returns:
            dict: Updated fields — only 'error' if validation fails,
                  or empty dict if everything is fine.
        """
        user_input = state.get("user_input", "").strip()
        session_id = state.get("session_id", "unknown")

        logger.info(f"[receive_input] Session '{session_id}': received message '{user_input[:80]}'")

        # Validate that the message is not empty after stripping whitespace
        if not user_input:
            logger.warning(f"[receive_input] Session '{session_id}': empty user input received")
            return {"error": "User input cannot be empty"}

        # No error — continue to next node with no state changes
        # (user_input and session_id were already set before graph execution)
        return {"error": None}

    return receive_input


def make_retrieve_context_node(
    index: Optional[VectorStoreIndex],
    settings,
):
    """
    Factory that returns the 'retrieve_context' node function.

    Args:
        index:    The LlamaIndex VectorStoreIndex wrapping ChromaDB.
                  Can be None if no documents have been indexed.
        settings: Application settings (contains rag_top_k).

    Returns:
        Callable: A node function with signature (ConversationState) -> dict.
    """
    def retrieve_context_node(state: ConversationState) -> dict:
        """
        Node 2: Queries ChromaDB to find relevant document chunks.

        WHAT DOES THIS NODE DO?
          - Converts the user's question into an embedding vector
          - Searches ChromaDB for the most similar stored chunks
          - Returns the chunks as plain text to inject into the LLM prompt

        WHY SKIP IF ERROR?
          If Node 1 set an error, there's no valid user_input to search with.
          Skipping prevents cascading failures.

        Args:
            state: The current conversation state.

        Returns:
            dict: Updated 'retrieved_context' and 'sources' fields.
        """
        # Short-circuit: if a previous node encountered an error, skip this step
        if state.get("error"):
            logger.warning("[retrieve_context] Skipping due to previous error")
            return {"retrieved_context": "", "sources": []}

        user_input = state["user_input"]

        # Delegate to the retriever module
        result: RetrievalResult = retrieve_context(
            query=user_input,
            index=index,
            settings=settings,
        )

        logger.info(
            f"[retrieve_context] Found {result.chunks_found} chunks "
            f"from sources: {result.sources}"
        )

        return {
            "retrieved_context": result.context_text,
            "sources": result.sources,
        }

    return retrieve_context_node


def make_build_prompt_node():
    """
    Factory that returns the 'build_prompt' node function.

    Returns:
        Callable: A node function with signature (ConversationState) -> dict.
    """
    def build_prompt(state: ConversationState) -> dict:
        """
        Node 3: Assembles the full prompt using LangChain PromptTemplate.

        WHAT DOES THIS NODE DO?
          - Formats chat history into LangChain message objects
          - Selects the right prompt template (RAG vs simple)
          - Stores the formatted prompt in state for the next node

        WHY STORE PROMPT IN STATE?
          The call_llm node needs the formatted messages.
          Storing in state keeps nodes decoupled — each node does one thing.

        Args:
            state: The current conversation state.

        Returns:
            dict: Updated state with 'built_prompt' key (list of LangChain messages).
        """
        if state.get("error"):
            logger.warning("[build_prompt] Skipping due to previous error")
            return {}

        # Convert stored message dicts back to LangChain message objects
        # State stores messages as plain dicts for serialisation compatibility
        chat_history = []
        for msg in state.get("messages", []):
            role = msg.get("role", "human")
            content = msg.get("content", "")
            if role == "human":
                chat_history.append(HumanMessage(content=content))
            elif role == "assistant":
                chat_history.append(AIMessage(content=content))
            elif role == "system":
                chat_history.append(SystemMessage(content=content))

        retrieved_context = state.get("retrieved_context", "")
        has_context = bool(retrieved_context and "No " not in retrieved_context[:10])

        # Choose template based on whether we have RAG context
        if has_context:
            prompt_template = get_rag_prompt()
            prompt_messages = prompt_template.format_messages(
                context=retrieved_context,
                chat_history=chat_history,
                question=state["user_input"],
            )
        else:
            prompt_template = get_simple_chat_prompt()
            prompt_messages = prompt_template.format_messages(
                chat_history=chat_history,
                question=state["user_input"],
            )

        logger.info(f"[build_prompt] Built prompt with {len(prompt_messages)} messages")

        # Store formatted messages in state for the call_llm node
        return {"built_prompt": prompt_messages}

    return build_prompt


def make_call_llm_node(llm: BaseChatModel, tools: Optional[list] = None):
    """
    Factory that returns the 'call_llm' node function.

    TOOL CALLING:
      If tools are provided, the LLM is bound to them via .bind_tools().
      This means the model's response may include tool_calls — requests to
      execute one of the provided functions before giving a final answer.
      The execute_tools node handles those calls; this node just detects them.

    Args:
        llm:   A LangChain chat model (ChatOpenAI or AzureChatOpenAI).
        tools: Optional list of LangChain @tool functions to make available.

    Returns:
        Callable: A node function with signature (ConversationState) -> dict.
    """
    # Bind tools to the LLM once at construction time — not on every call.
    # .bind_tools() wraps the LLM so the tool schemas are included in every
    # request to the model. The model then decides whether to use a tool.
    llm_to_use = llm.bind_tools(tools) if tools else llm

    def call_llm(state: ConversationState) -> dict:
        """
        Node 4: Sends the formatted prompt to the LLM and gets a response.

        WHAT DOES THIS NODE DO?
          - Calls llm.invoke() with the built prompt messages
          - If tools are bound, checks whether the LLM requested tool calls
          - Returns tool_calls list (may be empty) alongside the raw llm_response

        WHY STORE tool_calls IN STATE?
          The pipeline checks this field after call_llm to decide whether to
          run execute_tools. Keeping it in state avoids coupling the pipeline
          logic to the node implementation.

        Args:
            state: The current conversation state (must have 'built_prompt').

        Returns:
            dict: Updated state with 'llm_response' and 'tool_calls'.
        """
        if state.get("error"):
            logger.warning("[call_llm] Skipping due to previous error")
            return {"llm_response": None, "tool_calls": []}

        built_prompt = state.get("built_prompt")
        if not built_prompt:
            error_msg = "build_prompt node did not produce a prompt"
            logger.error(f"[call_llm] {error_msg}")
            return {"error": error_msg, "llm_response": None, "tool_calls": []}

        try:
            logger.info("[call_llm] Sending prompt to LLM...")
            response = llm_to_use.invoke(built_prompt)

            # Check if the LLM decided to call a tool.
            # response.tool_calls is a list of dicts like:
            #   [{"name": "search_products", "args": {"query": "laptop"}, "id": "call_abc123"}]
            tool_calls = getattr(response, "tool_calls", []) or []

            if tool_calls:
                logger.info(f"[call_llm] LLM requested {len(tool_calls)} tool call(s): "
                            f"{[tc['name'] for tc in tool_calls]}")
            else:
                logger.info("[call_llm] LLM responded directly (no tool calls)")

            return {"llm_response": response, "tool_calls": tool_calls}

        except Exception as e:
            logger.error(f"[call_llm] LLM call failed: {e}")
            return {
                "error": f"LLM call failed: {str(e)}",
                "llm_response": None,
                "tool_calls": [],
            }

    return call_llm


def make_execute_tools_node(tools: list):
    """
    Factory that returns the 'execute_tools' node function.

    WHAT IS THIS NODE?
      After call_llm, if the LLM requested tool calls, this node:
        1. Maps each tool call name to the actual Python function
        2. Executes the function with the LLM-provided arguments
        3. Wraps each result in a ToolMessage (LangChain's format for tool output)
        4. Stores the results in state so call_llm can use them in the next pass

    WHY ToolMessage?
      The OpenAI API requires tool results to be returned as messages with a
      specific format (role="tool", tool_call_id matching the request).
      LangChain's ToolMessage handles this serialisation automatically.

    Args:
        tools: List of LangChain @tool functions available to the LLM.

    Returns:
        Callable: A node function with signature (ConversationState) -> dict.
    """
    # Build a name → tool lookup for fast access
    tool_map = {t.name: t for t in tools}

    def execute_tools(state: ConversationState) -> dict:
        """
        Node 4b: Executes tool calls requested by the LLM.

        Args:
            state: Must have 'tool_calls' (list of dicts from LLM).

        Returns:
            dict: Updated 'tool_results' (list of ToolMessage objects).
        """
        if state.get("error"):
            logger.warning("[execute_tools] Skipping due to previous error")
            return {"tool_results": []}

        tool_calls = state.get("tool_calls", [])
        if not tool_calls:
            return {"tool_results": []}

        results = []
        for call in tool_calls:
            tool_name = call["name"]
            tool_args = call.get("args", {})
            tool_call_id = call.get("id", "unknown")

            if tool_name not in tool_map:
                logger.error(f"[execute_tools] Unknown tool: {tool_name!r}")
                result_str = f"Error: tool '{tool_name}' not found."
            else:
                try:
                    logger.info(f"[execute_tools] Calling {tool_name}({tool_args})")
                    result = tool_map[tool_name].invoke(tool_args)
                    result_str = str(result)
                    logger.info(f"[execute_tools] {tool_name} returned {len(result_str)} chars")
                except Exception as e:
                    logger.error(f"[execute_tools] {tool_name} raised: {e}")
                    result_str = f"Error executing {tool_name}: {str(e)}"

            # Wrap result in a ToolMessage so LangChain can include it
            # in the conversation as the tool's "reply" to the LLM's request.
            results.append(
                ToolMessage(content=result_str, tool_call_id=tool_call_id)
            )

        return {"tool_results": results}

    return execute_tools


def make_format_response_node():
    """
    Factory that returns the 'format_response' node function.

    Returns:
        Callable: A node function with signature (ConversationState) -> dict.
    """
    def format_response(state: ConversationState) -> dict:
        """
        Node 5 (final): Cleans and structures the LLM response.

        WHAT DOES THIS NODE DO?
          - Extracts text content from the AIMessage object
          - Appends the user message and bot reply to conversation history
          - Sets 'final_response' which the API endpoint will return

        WHY UPDATE MESSAGES HERE?
          Conversation history must include the current turn so the NEXT
          request has access to this exchange. We update it at the end
          because we don't know the response until after call_llm runs.

        Args:
            state: The current conversation state.

        Returns:
            dict: Updated 'final_response' and 'messages' (with this turn appended).
        """
        # If there was an error at any point, return a user-friendly error message
        if state.get("error"):
            error_msg = state["error"]
            logger.error(f"[format_response] Returning error response: {error_msg}")
            return {
                "final_response": f"I encountered an error: {error_msg}",
                "messages": state.get("messages", []),
            }

        llm_response = state.get("llm_response")
        if llm_response is None:
            return {
                "final_response": "I was unable to generate a response. Please try again.",
                "messages": state.get("messages", []),
            }

        # Extract plain text from the LangChain AIMessage object
        response_text = llm_response.content.strip()

        # Append this turn to conversation history for future turns
        updated_messages = list(state.get("messages", []))
        updated_messages.append({"role": "human", "content": state["user_input"]})
        updated_messages.append({"role": "assistant", "content": response_text})

        logger.info(f"[format_response] Final response: '{response_text[:100]}...'")

        return {
            "final_response": response_text,
            "messages": updated_messages,
        }

    return format_response
