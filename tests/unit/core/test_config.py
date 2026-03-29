from app.core.config import Settings


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-demo-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv(
        "POSTGRES_DSN",
        "postgresql+psycopg://postgres:postgres@localhost:5432/agent_demo_llprf",
    )
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

    settings = Settings()

    assert settings.openai_model == "gpt-4o-mini"
    assert settings.max_revision_rounds == 2
    assert settings.redis_url.startswith("redis://")
