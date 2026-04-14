# ─────────────────────────────────────────────────────────────────────────────
# WHAT IS THIS FILE?
# Tests for the application configuration in app/config.py.
# These tests verify that Settings loads correctly from environment variables,
# applies defaults, and validates field constraints (min/max values).
# ─────────────────────────────────────────────────────────────────────────────

import pytest
import os
from unittest.mock import patch

from app.config import Settings


class TestSettings:
    """Tests for the Settings pydantic-settings class."""

    def test_default_values_are_applied(self):
        """
        WHAT: Tests that all settings have sensible defaults.
        WHY:  Defaults let the app start without a complete .env file.
              Missing defaults would require every developer to set every variable.
        """
        settings = Settings(
            openai_api_key="sk-test",  # Provide minimum required value
        )
        assert settings.llm_provider == "openai"
        assert settings.llm_temperature == 0.7
        assert settings.llm_max_tokens == 1024
        assert settings.chroma_collection_name == "chatbot_docs"
        assert settings.app_version == "1.0.0"
        assert settings.rag_top_k == 3

    def test_custom_values_override_defaults(self):
        """
        WHAT: Tests that explicitly set values override the defaults.
        WHY:  Overriding defaults is the primary way to configure the app.
              If overrides were silently ignored, production configs would be wrong.
        """
        settings = Settings(
            openai_api_key="sk-test",
            llm_temperature=0.2,
            llm_max_tokens=512,
            chroma_collection_name="my_custom_collection",
            rag_top_k=5,
        )
        assert settings.llm_temperature == 0.2
        assert settings.llm_max_tokens == 512
        assert settings.chroma_collection_name == "my_custom_collection"
        assert settings.rag_top_k == 5

    def test_temperature_validation_rejects_negative(self):
        """
        WHAT: Tests that a negative temperature raises a ValidationError.
        WHY:  Temperature < 0 is not meaningful for LLMs and would cause API errors.
              Catching this at config load is better than failing during inference.
        """
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            Settings(openai_api_key="sk-test", llm_temperature=-0.1)

    def test_temperature_validation_rejects_above_two(self):
        """
        WHAT: Tests that temperature > 2.0 raises a ValidationError.
        WHY:  Values above 2.0 exceed the OpenAI API's supported range.
        """
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            Settings(openai_api_key="sk-test", llm_temperature=2.1)

    def test_max_tokens_must_be_positive(self):
        """
        WHAT: Tests that max_tokens=0 raises a ValidationError.
        WHY:  Zero or negative tokens would mean the LLM generates nothing.
              This is always a misconfiguration.
        """
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            Settings(openai_api_key="sk-test", llm_max_tokens=0)

    def test_loads_from_environment_variables(self):
        """
        WHAT: Tests that settings are loaded from environment variables.
        WHY:  In production (Azure), config comes from environment variables,
              not a .env file. This must work correctly.
        """
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "sk-from-env",
            "LLM_TEMPERATURE": "0.3",
            "LLM_MAX_TOKENS": "2048",
        }):
            settings = Settings()
            assert settings.openai_api_key == "sk-from-env"
            assert settings.llm_temperature == 0.3
            assert settings.llm_max_tokens == 2048

    def test_llm_provider_defaults_to_openai(self):
        """
        WHAT: Tests that the default provider is 'openai'.
        WHY:  Most users will use standard OpenAI, not Azure OpenAI.
              The default should match the most common use case.
        """
        settings = Settings(openai_api_key="sk-test")
        assert settings.llm_provider == "openai"

    def test_azure_settings_can_be_set(self):
        """
        WHAT: Tests that Azure OpenAI settings are accepted.
        WHY:  Enterprise users need Azure OpenAI support.
              If these fields were rejected, Azure deployment would fail.
        """
        settings = Settings(
            llm_provider="azure",
            azure_openai_api_key="azure-key",
            azure_openai_endpoint="https://myresource.openai.azure.com/",
            azure_openai_deployment_name="gpt-4o",
        )
        assert settings.llm_provider == "azure"
        assert settings.azure_openai_endpoint == "https://myresource.openai.azure.com/"
        assert settings.azure_openai_deployment_name == "gpt-4o"

    def test_case_insensitive_env_vars(self):
        """
        WHAT: Tests that environment variable names are case-insensitive.
        WHY:  Some shells normalise env var names to uppercase, some don't.
              The settings must handle both to work across different OS/CI environments.
        """
        with patch.dict(os.environ, {"openai_api_key": "sk-lowercase"}):
            settings = Settings()
            assert settings.openai_api_key == "sk-lowercase"

    def test_chroma_in_memory_defaults_false(self):
        """
        WHAT: Tests that chroma_in_memory defaults to False.
        WHY:  By default, we use persistent ChromaDB with disk storage.
              In-memory mode must be explicitly enabled for stateless deployments.
        """
        os.environ.pop("CHROMA_IN_MEMORY", None)
        settings = Settings()
        assert settings.chroma_in_memory is False

    def test_chroma_in_memory_env_var(self):
        """
        WHAT: Tests that chroma_in_memory can be set via CHROMA_IN_MEMORY env var.
        WHY:  Azure Container Apps uses environment variables for configuration.
              This must work to enable in-memory mode in production.
        """
        with patch.dict(os.environ, {"CHROMA_IN_MEMORY": "true"}):
            settings = Settings()
            assert settings.chroma_in_memory is True
