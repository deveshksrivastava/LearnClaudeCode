# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# Unit tests for each LangGraph node function in app/graph/nodes.py.
# Each node is tested in isolation — we pass in a state dict and assert
# that the returned dict contains the expected changes.
# ─────────────────────────────────────────────────────────────────────────────

import pytest
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage

from app.graph.nodes import (
    make_receive_input_node,
    make_retrieve_context_node,
    make_build_prompt_node,
    make_call_llm_node,
    make_format_response_node,
)


class TestReceiveInputNode:
    """Tests for the 'receive_input' node — validates and logs incoming messages."""

    def test_valid_input_returns_no_error(self, sample_conversation_state):
        """
        WHAT: Tests that a valid non-empty message passes through without setting an error.
        WHY:  The receive_input node should only set error for invalid inputs.
              Valid inputs should return {'error': None} to allow downstream nodes to run.
        """
        node = make_receive_input_node()
        result = node(sample_conversation_state)

        # Should return no error for valid input
        assert result.get("error") is None

    def test_empty_input_sets_error(self, sample_conversation_state):
        """
        WHAT: Tests that an empty message sets an error in the state.
        WHY:  Empty messages should not be passed to the LLM — they waste API calls
              and would produce meaningless responses.
        """
        node = make_receive_input_node()
        sample_conversation_state["user_input"] = ""  # Empty input

        result = node(sample_conversation_state)

        assert result.get("error") is not None
        assert "empty" in result["error"].lower()

    def test_whitespace_only_input_sets_error(self, sample_conversation_state):
        """
        WHAT: Tests that a message with only spaces/tabs is treated as empty.
        WHY:  Users might accidentally send whitespace — this should be caught
              before calling the LLM.
        """
        node = make_receive_input_node()
        sample_conversation_state["user_input"] = "   \t\n  "

        result = node(sample_conversation_state)

        assert result.get("error") is not None


class TestRetrieveContextNode:
    """Tests for the 'retrieve_context' node — queries ChromaDB for relevant chunks."""

    def test_retrieves_context_when_index_available(
        self, sample_conversation_state, mock_index, test_settings
    ):
        """
        WHAT: Tests that context is retrieved when a VectorStoreIndex is available.
        WHY:  The RAG pipeline depends on this node returning non-empty context
              for queries when documents have been indexed.
        """
        node = make_retrieve_context_node(index=mock_index, settings=test_settings)
        result = node(sample_conversation_state)

        # Should return non-empty context and at least one source
        assert "retrieved_context" in result
        assert len(result["retrieved_context"]) > 0
        assert len(result["sources"]) > 0

    def test_returns_empty_context_when_no_index(
        self, sample_conversation_state, mock_empty_index, test_settings
    ):
        """
        WHAT: Tests that retrieval gracefully handles a None index (no docs indexed yet).
        WHY:  The system must work even before any documents are indexed.
              The LLM should still respond using general knowledge.
        """
        node = make_retrieve_context_node(index=None, settings=test_settings)
        result = node(sample_conversation_state)

        # Should return empty sources (no error)
        assert "sources" in result
        assert result["sources"] == []

    def test_skips_retrieval_when_error_in_state(
        self, sample_conversation_state, mock_index, test_settings
    ):
        """
        WHAT: Tests that this node is skipped when a previous node set an error.
        WHY:  If receive_input found the message invalid, we should not waste
              an expensive ChromaDB query on invalid input.
        """
        sample_conversation_state["error"] = "Previous error"
        node = make_retrieve_context_node(index=mock_index, settings=test_settings)
        result = node(sample_conversation_state)

        # Index's as_retriever should NOT have been called
        mock_index.as_retriever.assert_not_called()
        assert result["retrieved_context"] == ""


class TestBuildPromptNode:
    """Tests for the 'build_prompt' node — assembles the LLM prompt."""

    def test_builds_rag_prompt_when_context_available(self, sample_conversation_state):
        """
        WHAT: Tests that the RAG prompt template is used when context is available.
        WHY:  The prompt must include retrieved document context so the LLM can
              use it in its answer. This is the core of the RAG pattern.
        """
        sample_conversation_state["retrieved_context"] = (
            "[Source 1: doc.txt (similarity: 0.95)]\nReturn policy is 30 days."
        )
        node = make_build_prompt_node()
        result = node(sample_conversation_state)

        # Should produce a list of prompt messages
        assert "built_prompt" in result
        assert len(result["built_prompt"]) > 0

    def test_builds_simple_prompt_when_no_context(self, sample_conversation_state):
        """
        WHAT: Tests that the simple (non-RAG) prompt is used when context is empty.
        WHY:  When no documents are indexed, the bot should still work using
              general knowledge — just without document citations.
        """
        sample_conversation_state["retrieved_context"] = ""
        node = make_build_prompt_node()
        result = node(sample_conversation_state)

        assert "built_prompt" in result
        assert len(result["built_prompt"]) > 0

    def test_skips_when_error_in_state(self, sample_conversation_state):
        """
        WHAT: Tests that prompt building is skipped when an earlier node errored.
        WHY:  No point building a prompt if the input is invalid.
        """
        sample_conversation_state["error"] = "Upstream error"
        node = make_build_prompt_node()
        result = node(sample_conversation_state)

        # Should return empty dict (no prompt built)
        assert result == {}

    def test_includes_chat_history_in_prompt(self, sample_conversation_state):
        """
        WHAT: Tests that previous conversation messages are included in the prompt.
        WHY:  Multi-turn memory depends on previous messages being passed to the LLM.
              Without this, every message would be a fresh conversation.
        """
        sample_conversation_state["messages"] = [
            {"role": "human", "content": "What is AI?"},
            {"role": "assistant", "content": "AI stands for Artificial Intelligence."},
        ]
        sample_conversation_state["retrieved_context"] = ""
        node = make_build_prompt_node()
        result = node(sample_conversation_state)

        # The prompt should have more messages when history exists
        assert "built_prompt" in result
        # With history, there should be at least 3 messages: system + history msgs + current
        assert len(result["built_prompt"]) >= 3


class TestCallLlmNode:
    """Tests for the 'call_llm' node — calls the LLM API."""

    def test_calls_llm_with_built_prompt(self, sample_conversation_state, mock_llm):
        """
        WHAT: Tests that the node calls llm.invoke() with the built prompt.
        WHY:  The LLM must receive the assembled prompt — this is the central
              action of the entire pipeline.
        """
        mock_prompt = [MagicMock()]
        sample_conversation_state["built_prompt"] = mock_prompt

        node = make_call_llm_node(llm=mock_llm)
        result = node(sample_conversation_state)

        # llm.invoke should have been called exactly once with our prompt
        mock_llm.invoke.assert_called_once_with(mock_prompt)
        assert "llm_response" in result

    def test_returns_error_when_llm_raises(self, sample_conversation_state, mock_llm):
        """
        WHAT: Tests that LLM API errors are caught and stored as state errors.
        WHY:  The LLM API can fail (rate limits, auth errors, network issues).
              We must handle this gracefully rather than letting an unhandled
              exception crash the server and return a 500 to the user.
        """
        mock_llm.invoke.side_effect = Exception("OpenAI API rate limit exceeded")
        sample_conversation_state["built_prompt"] = [MagicMock()]

        node = make_call_llm_node(llm=mock_llm)
        result = node(sample_conversation_state)

        assert result.get("error") is not None
        assert "LLM call failed" in result["error"]

    def test_skips_when_error_in_state(self, sample_conversation_state, mock_llm):
        """
        WHAT: Tests that the LLM is NOT called when an earlier node errored.
        WHY:  We should not make expensive API calls on invalid/failed requests.
        """
        sample_conversation_state["error"] = "Previous error"
        node = make_call_llm_node(llm=mock_llm)
        result = node(sample_conversation_state)

        mock_llm.invoke.assert_not_called()


class TestFormatResponseNode:
    """Tests for the 'format_response' node — formats the LLM output."""

    def test_extracts_text_from_ai_message(self, sample_conversation_state):
        """
        WHAT: Tests that the node correctly extracts text from the AIMessage object.
        WHY:  LangChain returns an AIMessage object, not a plain string.
              The API must return a plain string to the frontend.
        """
        sample_conversation_state["llm_response"] = AIMessage(content="Here is my answer.")
        sample_conversation_state["user_input"] = "What is the policy?"

        node = make_format_response_node()
        result = node(sample_conversation_state)

        assert result["final_response"] == "Here is my answer."

    def test_appends_turn_to_message_history(self, sample_conversation_state):
        """
        WHAT: Tests that this turn (user + bot) is appended to message history.
        WHY:  Multi-turn memory requires that each turn is saved.
              If we don't append here, the next request won't see this conversation.
        """
        sample_conversation_state["messages"] = []  # Fresh conversation
        sample_conversation_state["llm_response"] = AIMessage(content="My answer.")
        sample_conversation_state["user_input"] = "My question."

        node = make_format_response_node()
        result = node(sample_conversation_state)

        # Messages should now contain this turn (human + assistant)
        messages = result["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "human"
        assert messages[0]["content"] == "My question."
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "My answer."

    def test_returns_friendly_error_message_on_state_error(self, sample_conversation_state):
        """
        WHAT: Tests that user-friendly error text is returned when state has an error.
        WHY:  We never want to expose raw Python exceptions to end users.
              The response should always be a readable message.
        """
        sample_conversation_state["error"] = "LLM call failed: rate limit"

        node = make_format_response_node()
        result = node(sample_conversation_state)

        assert "error" in result["final_response"].lower() or "encountered" in result["final_response"].lower()
