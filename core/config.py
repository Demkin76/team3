from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "GitHub Doppelgänger Hunter API"
    APP_VERSION: str = "0.4-github"

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/doppel"

    REDIS_URL: str | None = "redis://localhost:6379/0"
    USE_REDIS_QUEUE: bool = True

    # GitHub
    GITHUB_TOKEN: str | None = None
    GITHUB_API_BASE: str = "https://api.github.com"

    # Limits
    FETCH_TIMEOUT_SEC: int = 12
    MAX_FILES_PER_PROFILE: int = 25
    MAX_FILE_BYTES: int = 120_000
    CODE_EXTENSIONS: str = ".py,.js,.ts,.java,.go,.rs,.cpp,.c,.cs,.php,.rb,.swift,.kt,.scala,.sql,.html,.css,.md"

    # Cache (exact set match)
    CACHE_HIT_THRESHOLD: float = 1.0

    # Search limits
    SEARCH_FILES_LIMIT: int = 15
    SEARCH_LINES_PER_FILE: int = 3

    # Repo-level similarity labels (percent)
    REPO_STRONG_THRESHOLD: float = 60.0
    REPO_COPY_THRESHOLD: float = 80.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
