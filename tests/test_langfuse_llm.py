"""Tests for backend.llm module (Langfuse-wrapped OpenAI client)."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = MagicMock()
    settings.openai_api_key = "test-openai-key"
    settings.query_agent_model = "gpt-4o-mini"
    settings.langfuse_secret_key = ""
    settings.langfuse_public_key = ""
    settings.langfuse_host = "https://cloud.langfuse.com"
    return settings


@pytest.fixture
def mock_settings_with_langfuse():
    """Create mock settings with Langfuse enabled."""
    settings = MagicMock()
    settings.openai_api_key = "test-openai-key"
    settings.query_agent_model = "gpt-4o-mini"
    settings.langfuse_secret_key = "sk-lf-test"
    settings.langfuse_public_key = "pk-lf-test"
    settings.langfuse_host = "https://cloud.langfuse.com"
    return settings


class TestLangfuseClientConfiguration:
    """Test client configuration and initialization."""

    def test_langfuse_disabled_when_keys_empty(self, mock_settings, monkeypatch):
        """When Langfuse keys are empty, tracing should be disabled."""
        monkeypatch.setattr("mcp.config.settings", mock_settings)

        # Clear any existing env vars
        for key in ["LANGFUSE_SECRET_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_TRACING_ENABLED"]:
            monkeypatch.delenv(key, raising=False)

        # Import after patching settings
        import importlib

        import backend.llm.client as client_module

        importlib.reload(client_module)

        # Should set LANGFUSE_TRACING_ENABLED to false when keys are empty
        assert os.environ.get("LANGFUSE_TRACING_ENABLED") == "false"

    def test_langfuse_enabled_when_keys_set(self, mock_settings_with_langfuse, monkeypatch):
        """When Langfuse keys are set, they should be configured."""
        monkeypatch.setattr("mcp.config.settings", mock_settings_with_langfuse)

        # Clear env vars first
        for key in ["LANGFUSE_SECRET_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_TRACING_ENABLED"]:
            monkeypatch.delenv(key, raising=False)

        import importlib

        import backend.llm.client as client_module

        importlib.reload(client_module)

        # Should set Langfuse keys in env
        assert os.environ.get("LANGFUSE_SECRET_KEY") == "sk-lf-test"
        assert os.environ.get("LANGFUSE_PUBLIC_KEY") == "pk-lf-test"


class TestCreateChatCompletion:
    """Test the create_chat_completion wrapper function."""

    @pytest.mark.asyncio
    async def test_create_chat_completion_calls_openai(self, monkeypatch):
        """Test that create_chat_completion calls the OpenAI API with correct params."""
        # Create a mock completion response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content="Test response"))]

        # Create async mock for create method
        mock_create = AsyncMock(return_value=mock_completion)

        # Mock the AsyncOpenAI client
        mock_client = MagicMock()
        mock_client.chat.completions.create = mock_create

        # Patch get_openai_client to return our mock
        with patch("backend.llm.client.get_openai_client", return_value=mock_client):
            from backend.llm import create_chat_completion

            result = await create_chat_completion(
                name="test-completion",
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello"},
                ],
                metadata={"correlation_id": "test-123"},
            )

            # Verify the mock was called with expected arguments
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["model"] == "gpt-4o-mini"
            assert call_kwargs["name"] == "test-completion"
            assert len(call_kwargs["messages"]) == 2
            assert call_kwargs["metadata"] == {"correlation_id": "test-123"}
            assert result == mock_completion

    @pytest.mark.asyncio
    async def test_create_chat_completion_empty_metadata(self, monkeypatch):
        """Test that create_chat_completion handles None metadata."""
        mock_completion = MagicMock()
        mock_create = AsyncMock(return_value=mock_completion)
        mock_client = MagicMock()
        mock_client.chat.completions.create = mock_create

        with patch("backend.llm.client.get_openai_client", return_value=mock_client):
            from backend.llm import create_chat_completion

            await create_chat_completion(
                name="test",
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hi"}],
                metadata=None,
            )

            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["metadata"] == {}


class TestAgentLangfuseIntegration:
    """Test Langfuse integration in the query agent."""

    def test_get_langfuse_handler_returns_none_when_disabled(self, mock_settings, monkeypatch):
        """When Langfuse keys are empty, handler should be None."""
        import importlib

        import mcp.langgraphs.agent as agent_module

        monkeypatch.setattr("mcp.config.settings", mock_settings)
        # Reload to pick up mocked settings
        importlib.reload(agent_module)

        handler = agent_module._get_langfuse_handler()
        assert handler is None

    def test_get_langfuse_handler_returns_handler_when_enabled(
        self, mock_settings_with_langfuse, monkeypatch
    ):
        """When Langfuse keys are set, handler should be created."""
        import importlib

        import mcp.langgraphs.agent as agent_module

        monkeypatch.setattr("mcp.config.settings", mock_settings_with_langfuse)
        importlib.reload(agent_module)

        # Mock Langfuse and CallbackHandler at the module level
        mock_langfuse_client = MagicMock()
        mock_handler = MagicMock()

        with (
            patch.object(agent_module, "Langfuse", mock_langfuse_client, create=True),
        ):
            # Patch the imports within the function using the module's namespace
            with patch.dict(
                "sys.modules",
                {
                    "langfuse": MagicMock(
                        Langfuse=MagicMock(return_value=mock_langfuse_client)
                    ),
                    "langfuse.langchain": MagicMock(
                        CallbackHandler=MagicMock(return_value=mock_handler)
                    ),
                },
            ):
                importlib.reload(agent_module)
                handler = agent_module._get_langfuse_handler()
                # Handler should be returned when Langfuse is mocked
                assert handler is not None


class TestIntegrationWithRealAPI:
    """Integration tests that require real API keys (skipped when not available)."""

    @pytest.mark.skipif(
        not os.environ.get("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set - skipping real API test",
    )
    @pytest.mark.asyncio
    async def test_real_completion_does_not_crash(self):
        """Test that a real API call works (when API key is available)."""
        from backend.llm import create_chat_completion

        try:
            result = await create_chat_completion(
                name="test-real-completion",
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say 'test' and nothing else."}],
                max_tokens=10,
            )
            assert result is not None
            assert len(result.choices) > 0
        except Exception as e:
            # Only fail if it's not an API key or rate limit issue
            error_str = str(e).lower()
            if "api key" not in error_str and "rate limit" not in error_str:
                raise
