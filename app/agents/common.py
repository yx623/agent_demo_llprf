from langchain_openai import ChatOpenAI

from app.core.config import Settings


def build_chat_model(settings: Settings) -> ChatOpenAI:
    missing_fields = []
    if not settings.openai_model:
        missing_fields.append("OPENAI_MODEL")
    if not settings.openai_api_key:
        missing_fields.append("OPENAI_API_KEY")
    if not settings.openai_base_url:
        missing_fields.append("OPENAI_BASE_URL")

    if missing_fields:
        missing_text = ", ".join(missing_fields)
        raise ValueError(f"缺少 OpenAI 配置: {missing_text}")

    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=0,
    )
