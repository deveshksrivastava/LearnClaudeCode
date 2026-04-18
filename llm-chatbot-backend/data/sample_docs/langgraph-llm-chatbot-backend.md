# LangGraph in llm-chatbot-backend

## The Core Concept: State + Nodes

LangGraph's fundamental idea is **state-driven pipelines**: data flows through a series of nodes as a shared dictionary. Each node reads from it, does one job, and returns only the fields it changed.

```
User Request
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│                   ConversationState                      │
│  session_id, messages, user_input, retrieved_context,   │
│  sources, built_prompt, llm_response, tool_calls,        │
│  tool_results, final_response, error                     │
└─────────────────────────────────────────────────────────┘
     │
     ▼  receive_input    → validates user message
     ▼  retrieve_context → queries ChromaDB for docs
     ▼  build_prompt     → formats history + context into LangChain messages
     ▼  call_llm         → sends to LLM (with tools bound)
     ▼  execute_tools    → (only if LLM called a tool)
     ▼  call_llm again   → (second pass with tool results)
     ▼  format_response  → extracts text, updates message history
     │
     ▼
  API Response
```

---

## 1. The State — `app/graph/state.py`

```python
class ConversationState(TypedDict):
    session_id: str        # Which user session
    messages: list[dict]   # Full history: [{"role": "human", "content": "..."}]
    user_input: str        # Current question
    retrieved_context: str # RAG chunks from ChromaDB
    sources: list[str]     # Which docs were retrieved
    built_prompt: list     # Final LangChain message list for LLM
    llm_response: Any      # Raw AIMessage (may contain .tool_calls)
    tool_calls: list       # Tools the LLM wants to call
    tool_results: list     # Results of executing those tools
    final_response: str    # Final text sent back to user
    error: str             # Any error that occurred
```

> Think of this as the **relay baton** — every node receives the full state and adds its contribution.

---

## 2. The Nodes — `app/graph/nodes.py`

Each node is a plain function `(state) -> dict`. The factory pattern is used so nodes can receive dependencies (like the LLM or index) without global variables.

| Node | Job | Key Output |
|---|---|---|
| `make_receive_input_node` | Validates message isn't empty | `error` |
| `make_retrieve_context_node` | Queries ChromaDB for relevant docs | `retrieved_context`, `sources` |
| `make_build_prompt_node` | Formats history + context into LangChain messages | `built_prompt` |
| `make_call_llm_node(llm, tools)` | Calls LLM; detects tool call requests | `llm_response`, `tool_calls` |
| `make_execute_tools_node(tools)` | Runs requested tools, wraps in `ToolMessage` | `tool_results` |
| `make_format_response_node` | Extracts text, saves to history | `final_response`, `messages` |

### Tool Calling Hook — `nodes.py:223`

```python
llm_to_use = llm.bind_tools(tools) if tools else llm
```

`.bind_tools()` tells the LLM what functions are available. The model's response then either contains `tool_calls` (use a tool) or just `.content` (answer directly).

---

## 3. The Pipeline — `app/graph/graph_builder.py`

This project replaced LangGraph's `StateGraph` with a plain Python class that does the same thing:

```python
class ConversationPipeline:
    def invoke(self, state):
        # Run receive_input → retrieve_context → build_prompt
        for name, node_fn in self._pre_llm_nodes:
            updates = node_fn(current_state)
            current_state.update(updates)   # ← merge partial dict into state

        # First LLM call
        current_state.update(self._call_llm(current_state))

        # Tool calling branch (only if LLM requested tools)
        if current_state.get("tool_calls"):
            current_state.update(self._execute_tools(current_state))

            # Append AIMessage + ToolMessages to prompt, then call LLM again
            current_state["built_prompt"] += [llm_response] + tool_results
            current_state.update(self._call_llm(current_state))

        # Final formatting
        current_state.update(self._format_response(current_state))
        return current_state
```

> The tool branch is why there are sometimes **two LLM calls**: first to decide which tool to use, second to answer after seeing the tool results.

---

## 4. The Full Request Flow

```
POST /api/v1/chat-llm
   │
   ├─ chat_router.py retrieves compiled_graph from app.state
   ├─ run_conversation_graph() builds the initial state dict
   ├─ compiled_graph.invoke(state) runs the pipeline
   │     ├─ receive_input:    validates "What products do you sell?"
   │     ├─ retrieve_context: finds return_policy.txt from ChromaDB
   │     ├─ build_prompt:     formats into [SystemMessage, HumanMessage]
   │     ├─ call_llm:         LLM responds with tool_call: list_all_products()
   │     ├─ execute_tools:    calls GET /products → returns product list
   │     ├─ call_llm again:   LLM sees products, answers naturally
   │     └─ format_response:  saves to session history
   └─ Returns {"response": "We sell: Laptop $999, Mouse $29..."}
```

> The graph is built **once at startup** (`main.py:133-141`) with LLM + ChromaDB index + tools all wired in, then reused for every request.

---

## 5. Why LangGraph (this pattern)?

| Without LangGraph | With This Pattern |
|---|---|
| Spaghetti function passing variables around | Clean state flows through typed dict |
| Hard to add new steps | Add a new node, insert it in the list |
| Hard to test individual steps | Each node is testable in isolation |
| No conditional branching | `if tool_calls:` branch is explicit |
| No error propagation | Any node sets `error`, others skip |

---

## Further Deep-Dives

- How the tool calling two-pass flow works in detail
- How RAG retrieval connects to ChromaDB
- How to add a new node to the pipeline
- How session memory works across turns
