from app.schemas.task import ReviewOutput


def run_reviewer(model, draft_markdown: str) -> ReviewOutput:
    """对草稿进行结构化审校。"""
    chain = model.with_structured_output(ReviewOutput)
    return chain.invoke(
        {
            "instruction": "请判断草稿是否可直接交付，并给出结构化意见。",
            "draft_markdown": draft_markdown,
        }
    )
