# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This file defines the "tools" that the LLM can call during a conversation.
#
# WHAT IS A TOOL?
#   A tool is a Python function the LLM can decide to invoke instead of
#   answering directly. When you "bind" tools to an LLM, the model sees their
#   names and docstrings and chooses which one (if any) to use based on the
#   user's message.
#
# HOW TOOL CALLING WORKS (step by step):
#   1. User asks: "Find me a laptop under $1000"
#   2. LLM sees the available tools and picks search_products("laptop")
#   3. Our code calls that function → it hits GET /products/search?q=laptop
#   4. The result (JSON with real products) is returned to the LLM as context
#   5. LLM formulates a natural-language answer using the real data
#
# WHY IS THIS POWERFUL?
#   Without tools, the chatbot can only answer from indexed documents.
#   With tools, it can query live data, take actions, and give up-to-date answers.
#   This is the difference between a Q&A bot and an AI agent.
#
# HOW LANGCHAIN TOOLS WORK:
#   The @tool decorator from LangChain reads the function name, docstring, and
#   type hints to automatically generate a JSON schema. This schema is sent to
#   the LLM so it knows how to call each tool correctly.
# ─────────────────────────────────────────────────────────────────────────────

import json
import logging
from typing import Optional

import httpx
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Base URL for the e-commerce API (port 8000).
# This will be replaced by the configured value from Settings at runtime.
# We use a module-level variable so get_tools() can override it.
_ECOMMERCE_BASE_URL = "http://localhost:8000"


def _get(path: str, params: Optional[dict] = None) -> str:
    """
    Helper: makes a GET request to the e-commerce API and returns a formatted string.

    WHY RETURN A STRING (NOT A DICT)?
      The LLM reads tool results as text context. Returning a human-readable
      string (e.g. JSON-formatted) is clearer to the LLM than a raw dict object.
      The LLM then uses this string to compose its final answer.

    Args:
        path:   URL path (e.g. "/products/search")
        params: Optional query parameters dict (e.g. {"q": "laptop"})

    Returns:
        str: JSON-formatted response body, or an error message string.
    """
    url = f"{_ECOMMERCE_BASE_URL}{path}"
    try:
        response = httpx.get(url, params=params, timeout=5.0)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except httpx.HTTPStatusError as e:
        logger.warning(f"[tool] GET {url} returned {e.response.status_code}")
        return f"Error: the request failed with status {e.response.status_code}."
    except httpx.RequestError as e:
        logger.error(f"[tool] GET {url} connection error: {e}")
        return "Error: could not connect to the e-commerce service. Is it running on port 8000?"


def _post(path: str, body: dict) -> str:
    """
    Helper: makes a POST request to the e-commerce API and returns a formatted string.

    Args:
        path: URL path (e.g. "/cart")
        body: JSON body as a dict.

    Returns:
        str: JSON-formatted response body, or an error message string.
    """
    url = f"{_ECOMMERCE_BASE_URL}{path}"
    try:
        response = httpx.post(url, json=body, timeout=5.0)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except httpx.HTTPStatusError as e:
        logger.warning(f"[tool] POST {url} returned {e.response.status_code}: {e.response.text}")
        try:
            detail = e.response.json().get("detail", e.response.text)
        except Exception:
            detail = e.response.text
        return f"Error: {detail}"
    except httpx.RequestError as e:
        logger.error(f"[tool] POST {url} connection error: {e}")
        return "Error: could not connect to the e-commerce service. Is it running on port 8000?"


# ── Tool Definitions ─────────────────────────────────────────────────────────
#
# IMPORTANT: The docstring IS the tool description.
# The LLM reads it to decide when to call each tool.
# Make docstrings clear and specific — they are part of your prompt engineering.

@tool
def search_products(query: str) -> str:
    """
    Search for products in the ShopFast store by name or keyword.
    Use this when the user asks to find, browse, or look for products.
    Returns a list of matching products with their IDs, names, prices, and stock levels.
    Example: search_products("laptop"), search_products("red sneakers")
    """
    logger.info(f"[tool:search_products] query={query!r}")
    return _get("/products/search", params={"q": query})


@tool
def list_all_products() -> str:
    """
    List all available products in the ShopFast store.
    Use this when the user wants to see everything that's available,
    or when they ask a general question like "what do you sell?" or "show me your products".
    Returns the full product catalogue with IDs, names, prices, and stock.
    """
    logger.info("[tool:list_all_products]")
    return _get("/products")


@tool
def get_product_details(product_id: int) -> str:
    """
    Get detailed information about a specific product by its numeric ID.
    Use this when the user asks about a specific product (e.g. "tell me more about product 3"
    or after finding a product via search and wanting to confirm details).
    Returns the product's ID, name, price, and current stock level.
    """
    logger.info(f"[tool:get_product_details] product_id={product_id}")
    return _get(f"/products/{product_id}")


@tool
def view_cart() -> str:
    """
    View the current shopping cart contents and total price.
    Use this when the user asks to see their cart, check what they've added,
    or asks about their total.
    Returns a list of cart items (product + quantity) and the total price.
    """
    logger.info("[tool:view_cart]")
    return _get("/cart")


@tool
def add_to_cart(product_id: int, quantity: int = 1) -> str:
    """
    Add a product to the shopping cart.
    Use this when the user says they want to buy something, add something to their cart,
    or purchase a product. You must know the product_id (from a prior search).
    If quantity is not specified, default to 1.
    Returns confirmation with product details and quantity added.
    """
    logger.info(f"[tool:add_to_cart] product_id={product_id}, quantity={quantity}")
    return _post("/cart", {"product_id": product_id, "quantity": quantity})


def get_tools(ecommerce_base_url: str = "http://localhost:8000") -> list:
    """
    Returns the list of all e-commerce tools, configured with the correct base URL.

    WHY A FACTORY FUNCTION?
      The base URL may differ between environments (local dev vs production).
      By accepting it as a parameter and patching the module variable, we keep
      the @tool functions simple while still supporting configuration.

    Args:
        ecommerce_base_url: The base URL of the e-commerce API (no trailing slash).

    Returns:
        list: All LangChain tool objects ready to be bound to an LLM.
    """
    global _ECOMMERCE_BASE_URL
    _ECOMMERCE_BASE_URL = ecommerce_base_url.rstrip("/")
    logger.info(f"[tools] E-commerce tools configured for {_ECOMMERCE_BASE_URL}")

    return [
        search_products,
        list_all_products,
        get_product_details,
        view_cart,
        add_to_cart,
    ]
