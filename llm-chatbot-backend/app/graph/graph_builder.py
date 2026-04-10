# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This file assembles all the node functions into a simple sequential pipeline.
# It replaced the previous LangGraph StateGraph implementation with plain Python.
#
# PIPELINE FLOW:
#   receive_input → retrieve_context → build_prompt → call_llm → format_response
#
# HOW IT WORKS:
#   ConversationPipeline holds a list of node functions.
#   When .invoke(state) is called, each node runs in order, merging its
#   returned dict back into the shared state — exactly what LangGraph did,
#   but without the external dependency.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from llama_index.core import VectorStoreIndex

from app.graph.state import ConversationState
from app.graph.nodes import (
    make_receive_input_node,
    make_retrieve_context_node,
    make_build_prompt_node,
    make_call_llm_node,
    make_format_response_node,
)
from app.config import Settings

logger = logging.getLogger(__name__)


class ConversationPipeline:
    """
    A simple sequential pipeline that replaces LangGraph's StateGraph.

    Each node is a function (state: dict) -> dict that returns only the
    fields it changed. After each node runs, its result is merged into
    the shared state dict — the same contract LangGraph used.

    The .invoke() method mirrors LangGraph's compiled graph API so that
    the rest of the codebase (chat_router, conftest mocks) needs no changes.
    """

    def __init__(self, nodes: list):
        # nodes is a list of (name, fn) tuples for logging clarity
        self._nodes = nodes

    def invoke(self, state: dict) -> dict:
        """
        Run all nodes in sequence, accumulating state changes.

        Args:
            state: Initial ConversationState dict.

        Returns:
            dict: Final state after all nodes have run.
        """
        current_state = dict(state)
        for name, node_fn in self._nodes:
            logger.debug(f"[pipeline] Running node: {name}")
            updates = node_fn(current_state)
            current_state.update(updates)
        return current_state


def build_conversation_graph(
    llm: BaseChatModel,
    index: Optional[VectorStoreIndex],
    settings: Settings,
) -> ConversationPipeline:
    """
    Builds a ConversationPipeline by wiring up all node functions.

    Args:
        llm:      A LangChain chat model (ChatOpenAI or AzureChatOpenAI).
        index:    The LlamaIndex VectorStoreIndex (or None if no docs indexed).
        settings: Application settings.

    Returns:
        ConversationPipeline: Ready to call .invoke() on.
    """
    logger.info("Building conversation pipeline...")

    nodes = [
        ("receive_input",    make_receive_input_node()),
        ("retrieve_context", make_retrieve_context_node(index=index, settings=settings)),
        ("build_prompt",     make_build_prompt_node()),
        ("call_llm",         make_call_llm_node(llm=llm)),
        ("format_response",  make_format_response_node()),
    ]

    pipeline = ConversationPipeline(nodes)
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
    }

    logger.info(f"Running conversation pipeline for session '{session_id}'")
    return compiled_graph.invoke(initial_state)
