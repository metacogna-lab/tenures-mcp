"""Configuration management for MCP Server."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server
    mcp_server_host: str = "0.0.0.0"
    mcp_server_port: int = 8000
    mcp_api_version: str = "v1"

    # Authentication
    bearer_token: str = "dev-token-insecure"  # Required in production via env
    role: str = "agent"  # agent or admin

    # Database
    database_path: str = "./data/tenure_mcp.db"

    # Observability
    langsmith_api_key: str = ""
    langsmith_project: str = "tenure-mcp-mvp"
    opentelemetry_enabled: bool = True
    
    # OpenTelemetry OTLP
    otlp_endpoint: str = ""  # e.g., "http://localhost:4317" for gRPC or "http://localhost:4318" for HTTP
    otlp_headers: dict[str, str] = {}  # Optional headers for OTLP exporter (JSON string in env)

    # Langfuse
    langfuse_secret_key: str = ""
    langfuse_public_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    # Mock Integrations
    vaultre_mock_enabled: bool = True
    ailo_mock_enabled: bool = True
    gmail_mock_enabled: bool = True
    google_drive_mock_enabled: bool = True
    mock_latency_ms: int = 500

    # HITL
    hitl_enabled: bool = True
    hitl_token_secret: str = ""

    # Feature Flags
    multi_tenant_enabled: bool = False
    production_integrations_enabled: bool = False

    # Query agent (LangGraph + LLM)
    openai_api_key: str = ""
    query_agent_model: str = "gpt-4o-mini"
    query_agent_max_steps: int = 5

    # Web Search (Tavily or similar)
    tavily_api_key: str = ""
    web_search_max_results: int = 5

    # MCP transport for langchain-mcp-adapters (base URL when agent connects to self)
    mcp_sse_url: str = "http://127.0.0.1:8000/sse"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
