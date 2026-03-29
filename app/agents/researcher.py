from app.schemas.task import ResearchOutput


def run_researcher(model, user_input: str, memory_text: str) -> ResearchOutput:
    """结合长期记忆产出研究摘要。"""
    chain = model.with_structured_output(ResearchOutput)
    return chain.invoke(
        {
            "instruction": "请根据用户任务和长期记忆整理研究摘要。",
            "user_input": user_input,
            "memory_text": memory_text,
        }
    )
