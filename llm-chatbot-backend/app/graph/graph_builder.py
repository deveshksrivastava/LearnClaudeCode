# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This file assembles all the node functions into a simple sequential pipeline.
# It replaced the previous LangGraph StateGraph implementation with plain Python.
#
# PIPELINE FLOW (with tool calling):
#
#   receive_input → retrieve_context → build_prompt → call_llm
#                                                          │
#                                          ┌──────────────┴─────────────┐
#                                          │ tool_calls present?        │
#                                          │ YES                        │ NO
#                                          ▼                            ▼
#                                    execute_tools              format_response
#                                          │
#                                          ▼
#                               call_llm (second pass,
#                               with tool results in prompt)
#                                          │
#                                          ▼
#                                   format_response
#
# HOW IT WORKS:
#   ConversationPipeline holds a list of node functions.
#   When .invoke(state) is called, each node runs in order, merging its
#   returned dict back into the shared state — exactly what LangGraph did,
#   but without the external dependency.
#
#   The tool execution step is handled by ConversationPipeline.invoke() itself:
#   after call_llm, it checks state["tool_calls"] and conditionally runs
#   execute_tools + a second call_llm pass before format_response.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from llama_index.core import VectorStoreIndex

from app.graph.state import ConversationState
from app.graph.nodes import (
    make_receive_input_node,
    make_retrieve_context_node,
    make_build_prompt_node,
    make_call_llm_node,
    make_execute_tools_node,
    make_format_response_node,
)
from app.config import Settings

logger = logging.getLogger(__name__)


class ConversationPipeline:
    """
    A sequential pipeline that replaces LangGraph's StateGraph, now with
    conditional tool execution support.

    Each node is a function (state: dict) -> dict that returns only the
    fields it changed. After each node runs, its result is merged into
    the shared state dict — the same contract LangGraph used.

    The .invoke() method mirrors LangGraph's compiled graph API so that
    the rest of the codebase (chat_router, conftest mocks) needs no changes.

    TOOL CALLING BRANCH:
      The pipeline has a special step after call_llm. If the LLM requested
      tool calls (state["tool_calls"] is non-empty), the pipeline:
        1. Runs execute_tools to execute them and collect results
        2. Appends the AIMessage + ToolMessages to built_prompt
        3. Runs call_llm again so the LLM can answer using the tool results
      Then format_response runs as normal.
    """

    def __init__(
        self,
        pre_llm_nodes: list,
        call_llm_fn,
        execute_tools_fn,
        format_response_fn,
    ):
        self._pre_llm_nodes = pre_llm_nodes          # receive_input, retrieve_context, build_prompt
        self._call_llm = call_llm_fn                  # call_llm node function
        self._execute_tools = execute_tools_fn         # execute_tools node function (may be None)
        self._format_response = format_response_fn    # format_response node function

    def invoke(self, state: dict) -> dict:
        """
        Run the pipeline, branching through tool execution if the LLM requests it.

        Args:
            state: Initial ConversationState dict.

        Returns:
            dict: Final state after all nodes have run.
        """
        current_state = dict(state)

        # ── Phase 1: pre-LLM nodes (input → retrieval → prompt building) ──
        for name, node_fn in self._pre_llm_nodes:
            logger.debug(f"[pipeline] Running node: {name}")
            updates = node_fn(current_state)
            current_state.update(updates)

        # ── Phase 2: first LLM call ────────────────────────────────────────
        logger.debug("[pipeline] Running node: call_llm")
        updates = self._call_llm(current_state)
        current_state.update(updates)

        # ── Phase 3: tool execution branch (only if LLM requested tools) ──
        tool_calls = current_state.get("tool_calls") or []
        if tool_calls and self._execute_tools is not None:
            # 3a. Execute the tool calls and collect results
            logger.debug("[pipeline] Running node: execute_tools")
            updates = self._execute_tools(current_state)
            current_state.update(updates)

            # 3b. Append the LLM's tool-call message + tool results to the prompt.
            #     This is required by the OpenAI API: the conversation must contain
            #     the AIMessage (with tool_calls) followed by ToolMessages, so the
            #     LLM understands what it asked for and what the answers were.
            llm_response: AIMessage = current_state.get("llm_response")
            tool_results: list = current_state.get("tool_results", [])

            if llm_response is not None and tool_results:
                existing_prompt = list(current_state.get("built_prompt") or [])
                current_state["built_prompt"] = existing_prompt + [llm_response] + tool_results

            # 3c. Second LLM call — now the model has tool results and can answer
            logger.debug("[pipeline] Running node: call_llm (second pass with tool results)")
            updates = self._call_llm(current_state)
            # Clear tool_calls so format_response doesn't re-enter the branch
            updates["tool_calls"] = []
            current_state.update(updates)

        # ── Phase 4: format and return the final response ──────────────────
        logger.debug("[pipeline] Running node: format_response")
        updates = self._format_response(current_state)
        current_state.update(updates)

        return current_state


def build_conversation_graph(
    llm: BaseChatModel,
    index: Optional[VectorStoreIndex],
    settings: Settings,
    tools: Optional[list] = None,
) -> ConversationPipeline:
    """
    Builds a ConversationPipeline by wiring up all node functions.

    Args:
        llm:      A LangChain chat model (ChatOpenAI or AzureChatOpenAI).
        index:    The LlamaIndex VectorStoreIndex (or None if no docs indexed).
        settings: Application settings.
        tools:    Optional list of LangChain @tool functions. When provided,
                  the LLM can call them to fetch live data from the e-commerce API.

    Returns:
        ConversationPipeline: Ready to call .invoke() on.
    """
    logger.info("Building conversation pipeline...")

    if tools:
        logger.info(f"Tool calling enabled: {[t.name for t in tools]}")
    else:
        logger.info("Tool calling disabled (no tools provided)")

    pre_llm_nodes = [
        ("receive_input",    make_receive_input_node()),
        ("retrieve_context", make_retrieve_context_node(index=index, settings=settings)),
        ("build_prompt",     make_build_prompt_node()),
    ]

    pipeline = ConversationPipeline(
        pre_llm_nodes=pre_llm_nodes,
        call_llm_fn=make_call_llm_node(llm=llm, tools=tools),
        execute_tools_fn=make_execute_tools_node(tools) if tools else None,
        format_response_fn=make_format_response_node(),
    )

    logger.info("Conversation pipeline built successfully")
    return pipeline


def run_conversation_graph(
    compiled_graph: ConversationPipeline,
    session_id: str,
    user_input: str,
    message_history: list[dict],
) -> dict:
    """
    Runs the pipeline for one conversation turn.

    Args:
        compiled_graph:  The ConversationPipeline from build_conversation_graph().
        session_id:      Unique ID for this conversation session.
        user_input:      The user's latest message.
        message_history: List of previous messages (dicts with 'role' and 'content').

    Returns:
        dict: Final state after all nodes have run.
              Key fields: 'final_response', 'sources', 'messages', 'error'.
    """
    initial_state: ConversationState = {
        "session_id": session_id,
        "messages": message_history,
        "user_input": user_input,
        "retrieved_context": "",
        "sources": [],
        "built_prompt": None,
        "final_response": "",
        "error": None,
        "llm_response": None,
        "tool_calls": [],
        "tool_results": [],
    }

    logger.info(f"Running conversation pipeline for session '{session_id}'")
    return compiled_graph.invoke(initial_state)
