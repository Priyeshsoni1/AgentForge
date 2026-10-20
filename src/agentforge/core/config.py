
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AgentForge"
    app_version: str = "0.7.0"
    environment: str = "development"

    openrouter_api_key: SecretStr | None = None
    openrouter_model: str = "openrouter/free"
    openrouter_timeout_seconds: float = 30.0
    openrouter_max_tokens: int = 500

    tavily_api_key: SecretStr | None = None
    allowed_api_hosts: str = ""

    python_sandbox_image: str = "python:3.12-alpine"
    python_sandbox_timeout_seconds: int = 5
    file_reader_root: str = "workspace"

    database_url: SecretStr | None = None
    redis_url: SecretStr | None = None

    # JSON object mapping owner IDs to API keys.
    # Example: {"local":"a-long-random-secret"}
    app_api_keys: SecretStr | None = None

    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def api_host_allowlist(self) -> set[str]:
        return {
            host.strip().lower().rstrip(".")
            for host in self.allowed_api_hosts.split(",")
            if host.strip()
        }


settings = Settings()
