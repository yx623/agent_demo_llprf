"""封装 LangChain 聊天模型的统一构造入口。

这个文件只解决一件事：把散落在环境变量里的 OpenAI 配置
收拢成一个可复用的 `ChatOpenAI` 实例。这样其它 Agent 文件
可以只关心 prompt 和结构化输出，而不用重复处理配置校验。
"""

from langchain_openai import ChatOpenAI

from app.core.config import Settings


def build_chat_model(settings: Settings) -> ChatOpenAI:
    """根据配置创建 LangChain 聊天模型。

    这里显式校验关键配置，而不是把错误留到真正发请求时才暴露。
    对教学项目来说，这样更容易让读者看清“模型构造失败”和
    “模型调用失败”是两类不同问题。
    """
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
        # 教学项目默认关闭随机性，方便稳定观察结构化输出。
        temperature=0,
    )
