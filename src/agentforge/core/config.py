
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AgentForge"
    app_version: str = "0.3.0"
    environment: str = "development"

    openrouter_api_key: SecretStr | None = None
    openrouter_model: str = "openrouter/free"
    openrouter_timeout_seconds: float = 30.0
    openrouter_max_tokens: int = 500

    tavily_api_key: SecretStr | None = None

    # Comma-separated list of approved HTTPS API hostnames.
    allowed_api_hosts: str = ""

    python_sandbox_image: str = "python:3.12-alpine"
    python_sandbox_timeout_seconds: int = 5

    # Only files inside this directory can be read.
    file_reader_root: str = "workspace"

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
