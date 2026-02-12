"""Application configuration management."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    environment: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # GitHub
    github_app_id: Optional[str] = Field(default=None, description="GitHub App ID")
    github_webhook_secret: Optional[str] = Field(default=None, description="GitHub webhook secret")
    github_private_key_path: Optional[str] = Field(
        default=None, description="Path to GitHub private key"
    )

    # LLM APIs
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")

    # Databases
    qdrant_url: Optional[str] = Field(default=None, description="Qdrant instance URL")
    qdrant_api_key: Optional[str] = Field(default=None, description="Qdrant API key")
    neo4j_uri: Optional[str] = Field(default=None, description="Neo4j URI")
    neo4j_user: Optional[str] = Field(default="neo4j", description="Neo4j username")
    neo4j_password: Optional[str] = Field(default=None, description="Neo4j password")
    supabase_url: Optional[str] = Field(default=None, description="Supabase URL")
    supabase_key: Optional[str] = Field(default=None, description="Supabase API key")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
