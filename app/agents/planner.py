from app.schemas.task import PlanOutput


def run_planner(model, user_input: str) -> PlanOutput:
    """生成结构化计划。"""
    chain = model.with_structured_output(PlanOutput)
    prompt = (
        "请把下面的用户任务改写成教学型执行计划，并返回结构化结果。\n"
        f"用户任务：{user_input}"
    )
    return chain.invoke(prompt)
