# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# This file creates and returns the LLM (Large Language Model) client.
# Think of it as the "adapter" between our app and the AI service.
# It supports both standard OpenAI (api.openai.com) and Azure OpenAI
# (your company's private Azure-hosted GPT instance).
# The choice is controlled by the LLM_PROVIDER environment variable.
# ─────────────────────────────────────────────────────────────────────────────

import logging
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from app.config import Settings

logger = logging.getLogger(__name__)


def get_llm(settings: Settings) -> BaseChatModel:
    """
    Creates and returns a LangChain-compatible LLM client.

    WHY LANGGCHAIN'S ChatOpenAI instead of openai.OpenAI directly?
      LangChain wraps the raw OpenAI SDK and adds:
        - Automatic retry logic
        - Streaming support
        - A standard interface that works with both OpenAI and Azure OpenAI
        - Integration with LangGraph, prompt templates, and chains

    Args:
        settings: The application Settings object from config.py.
                  Contains API keys, model names, temperature, etc.

    Returns:
        BaseChatModel: A LangChain chat model ready to call .invoke() on.
                       The type is BaseChatModel so this function can return
                       either ChatOpenAI or AzureChatOpenAI transparently.

    Raises:
        ValueError: If an unsupported LLM_PROVIDER is configured.
    """
    provider = settings.llm_provider.lower()
    logger.info(f"Initialising LLM provider: {provider}")

    if provider == "azure":
        # Azure OpenAI is your company's private deployment of GPT.
        # It uses different credentials and a different URL format.
        _validate_azure_settings(settings)
        return AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            azure_deployment=settings.azure_openai_deployment_name,
            api_key=settings.azure_openai_api_key,            # type: ignore[arg-type]
            api_version=settings.azure_openai_api_version,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    elif provider == "openai":
        # Standard OpenAI — calls api.openai.com
        _validate_openai_settings(settings)
        return ChatOpenAI(
            model=settings.openai_model_name,
            api_key=settings.openai_api_key,                  # type: ignore[arg-type]
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: '{provider}'. "
            "Expected 'openai' or 'azure'. Check your .env file."
        )


def _validate_azure_settings(settings: Settings) -> None:
    """
    Checks that all required Azure OpenAI settings are present.

    We validate early (at startup) so the developer sees a clear error
    message instead of a cryptic failure during the first API call.

    Args:
        settings: The application Settings object.

    Raises:
        ValueError: If any required Azure setting is missing.
    """
    required = {
        "AZURE_OPENAI_API_KEY": settings.azure_openai_api_key,
        "AZURE_OPENAI_ENDPOINT": settings.azure_openai_endpoint,
        "AZURE_OPENAI_DEPLOYMENT_NAME": settings.azure_openai_deployment_name,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ValueError(
            f"Azure OpenAI selected but these env vars are missing: {', '.join(missing)}"
        )


def _validate_openai_settings(settings: Settings) -> None:
    """
    Checks that all required OpenAI settings are present.

    Args:
        settings: The application Settings object.

    Raises:
        ValueError: If OPENAI_API_KEY is missing.
    """
    if not settings.openai_api_key:
        raise ValueError(
            "LLM_PROVIDER=openai but OPENAI_API_KEY is not set. "
            "Add it to your .env file."
        )
