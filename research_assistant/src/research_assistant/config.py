"""Configuration management for the research assistant."""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    """Raised when configuration is invalid."""

    pass


@dataclass
class Settings:
    """Application settings loaded from environment."""

    ANTHROPIC_API_KEY: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    CLAUDE_MODEL: str = field(default_factory=lambda: os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"))
    # Web search configuration
    # SEARCH_PROVIDER: "tavily" (default) or "serper"
    SEARCH_PROVIDER: str = field(default_factory=lambda: (os.getenv("SEARCH_PROVIDER", "tavily") or "tavily").strip())
    SEARCH_API_KEY: str | None = field(default_factory=lambda: (os.getenv("SEARCH_API_KEY") or "").strip() or None)
    MAX_ITERATIONS: int = field(default_factory=lambda: int(os.getenv("MAX_ITERATIONS", "10")))
    TIMEOUT: int = field(default_factory=lambda: int(os.getenv("TIMEOUT", "30")))


settings = Settings()


def validate_config() -> None:
    """Validate required configuration is present."""
    if not settings.ANTHROPIC_API_KEY:
        raise ConfigError(
            "ANTHROPIC_API_KEY environment variable is required.\n"
            "Set it in .env or export it in your shell:\n"
            "  export ANTHROPIC_API_KEY=sk-ant-..."
        )
