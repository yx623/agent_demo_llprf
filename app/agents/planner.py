"""规划型 Agent。

它把用户的一句话需求转换成结构化计划，供后续 researcher 和
writer 使用。这里演示的是 LangChain 的“结构化输出”能力，
不是多 Agent 编排能力。
"""

from app.schemas.task import PlanOutput


def run_planner(model, user_input: str) -> PlanOutput:
    """生成结构化计划。

    输入是用户原始请求，输出是 `PlanOutput`。这样工作流层
    不需要再去猜模型返回的文本格式。
    """
    chain = model.with_structured_output(PlanOutput)
    prompt = (
        "请把下面的用户任务改写成教学型执行计划，并返回结构化结果。\n"
        f"用户任务：{user_input}"
    )
    return chain.invoke(prompt)
