from app.schemas.task import PlanOutput


def run_planner(model, user_input: str) -> PlanOutput:
    """生成结构化计划。"""
    chain = model.with_structured_output(PlanOutput)
    return chain.invoke(
        {
            "instruction": "请把用户任务改写成教学型执行计划。",
            "user_input": user_input,
        }
    )
