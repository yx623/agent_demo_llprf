"""审校型 Agent。

这个 Agent 不负责重写内容，只负责判断当前草稿是否可以直接
通过，还是需要补证据、继续改写。它的输出会直接驱动 LangGraph
 的路由，因此结构化约束尤其重要。
"""

from app.schemas.task import ReviewOutput


def run_reviewer(model, draft_markdown: str) -> ReviewOutput:
    """对草稿进行结构化审校。"""
    chain = model.with_structured_output(ReviewOutput)
    prompt = (
        "请判断草稿是否可直接交付，并给出结构化意见。\n"
        f"草稿内容：\n{draft_markdown}"
    )
    return chain.invoke(prompt)
