# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This file defines the "state" that flows through the LangGraph conversation graph.
# State is the shared data that every node in the graph can read and write.
# Think of it as a baton passed between runners in a relay race — each runner
# (node) adds information to the baton before passing it to the next runner.
# ─────────────────────────────────────────────────────────────────────────────

from typing import TypedDict, Optional, Any


class ConversationState(TypedDict):
    """
    The state object that flows through the LangGraph StateGraph.

    WHAT IS TypedDict?
      TypedDict is a Python type hint that describes a dictionary with specific keys.
      LangGraph requires state to be a TypedDict so it can track what changed
      between node executions and support checkpointing (saving/restoring state).

    FIELDS (in order of population through the graph):
      session_id:        Unique ID for this conversation (from the API request).
                         Used to look up conversation history and maintain continuity.

      messages:          Full conversation history as a list of dicts.
                         Format: [{"role": "human", "content": "..."}, {"role": "assistant", "content": "..."}]
                         This is what gives the LLM "memory" of previous turns.

      user_input:        The user's latest message (from the API request).
                         Set by the "receive_input" node.

      retrieved_context: The text chunks retrieved from ChromaDB that are relevant
                         to the user's question. Set by the "retrieve_context" node.
                         Empty string if no documents are indexed.

      sources:           List of source document names used in RAG retrieval.
                         Populated alongside retrieved_context.

      final_response:    The LLM's formatted response to the user.
                         Set by the "format_response" node (last node before END).

      error:             If any node encounters an error, it sets this field.
                         Other nodes check this field and can skip if there's an error.
                         None means "no error so far".

      llm_response:      The raw AIMessage object returned by the LLM.
                         May contain .tool_calls if the model wants to use a tool.
                         Set by the call_llm node.

      tool_calls:        List of tool call requests from the LLM (populated after
                         call_llm if the model chose to use one or more tools).
                         Each entry: {"name": str, "args": dict, "id": str}

      tool_results:      List of ToolMessage objects containing the results after
                         our code executed the tool calls (populated by execute_tools).
                         These are fed back into the prompt for the second LLM call.
    """
    session_id: str
    messages: list[dict]
    user_input: str
    retrieved_context: str
    sources: list[str]
    built_prompt: Optional[list]
    final_response: str
    error: Optional[str]
    llm_response: Optional[Any]
    tool_calls: Optional[list]
    tool_results: Optional[list]
