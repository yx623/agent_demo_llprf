from app.schemas.task import ReviewOutput


def run_reviewer(model, draft_markdown: str) -> ReviewOutput:
    """对草稿进行结构化审校。"""
    chain = model.with_structured_output(ReviewOutput)
    prompt = (
        "请判断草稿是否可直接交付，并给出结构化意见。\n"
        f"草稿内容：\n{draft_markdown}"
    )
    return chain.invoke(prompt)
