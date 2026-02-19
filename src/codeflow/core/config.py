"""
Application configuration using Pydantic Settings
Loads from environment variables and .env file
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    environment: str = Field(
        default="development", description="Environment: development, staging, production"
    )
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Groq API (LLM)
    groq_api_key: str = Field(..., description="Groq API key for LLM access")
    groq_model: str = Field(default="llama-3.3-70b-versatile", description="Groq model to use")

    # Qdrant Vector Database
    qdrant_url: str = Field(..., description="Qdrant Cloud URL")
    qdrant_api_key: str = Field(..., description="Qdrant API key")
    qdrant_collection_name: str = Field(
        default="code_patterns", description="Qdrant collection name"
    )

    # GitHub App
    github_app_id: Optional[str] = Field(default=None, description="GitHub App ID")
    github_installation_id: Optional[str] = Field(
        default=None, description="GitHub Installation ID"
    )
    github_private_key_path: str = Field(
        default="config/private-key.pem", description="Path to GitHub App private key"
    )
    github_private_key: Optional[str] = Field(
        default=None, description="GitHub App private key content (use instead of path in cloud)"
    )
    github_webhook_secret: Optional[str] = Field(
        default=None, description="GitHub webhook secret for verification"
    )

    # Optional: OpenAI (for comparison/fallback)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")

    # Neo4j (Knowledge Graph) - Optional
    neo4j_uri: Optional[str] = Field(default=None, description="Neo4j connection URI")
    neo4j_user: str = Field(default="neo4j", description="Neo4j username")
    neo4j_password: Optional[str] = Field(default=None, description="Neo4j password")

    # Supabase (Metrics Storage) - Optional
    supabase_url: Optional[str] = Field(default=None, description="Supabase project URL")
    supabase_key: Optional[str] = Field(default=None, description="Supabase API key")

    # Sentry (Error Tracking) - Optional
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
_settings = None


def get_settings() -> Settings:
    """Get application settings (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
