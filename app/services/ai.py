import os

from openai import AsyncAzureOpenAI, AsyncOpenAI


def get_ai_client() -> AsyncAzureOpenAI | AsyncOpenAI | None:
    """Return AsyncAzureOpenAI if Azure creds are present, AsyncOpenAI if only
    OPENAI_API_KEY is set, or None if no credentials are configured."""
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if azure_endpoint and azure_api_key:
        return AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        )
    openai_api_key = os.getenv("OPENAI_API_KEY")
    print(
        f"AI client config — Azure: {bool(azure_endpoint and azure_api_key)}, "
        f"OpenAI: {bool(openai_api_key)}"
    )
    if openai_api_key:
        return AsyncOpenAI(api_key=openai_api_key)
    return None
