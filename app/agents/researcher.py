"""研究型 Agent。

它读取用户请求和长期记忆，产出后续写作所需的研究摘要。
这里适合教学展示“模型并不是直接读数据库”，而是先把长期
记忆整理成 prompt 上下文，再交给模型理解。
"""

from app.schemas.task import ResearchOutput


def run_researcher(model, user_input: str, memory_text: str) -> ResearchOutput:
    """结合长期记忆产出研究摘要。"""
    chain = model.with_structured_output(ResearchOutput)
    prompt = (
        "请根据用户任务和长期记忆整理研究摘要，并返回结构化结果。\n"
        f"用户任务：{user_input}\n"
        f"长期记忆：{memory_text}"
    )
    return chain.invoke(prompt)
