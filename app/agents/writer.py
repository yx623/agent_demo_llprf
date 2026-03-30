"""写作型 Agent。

writer 的职责是把“计划 + 研究摘要”整理成面向教学的 Markdown 草稿。
这一步依然属于单 Agent 能力，不涉及工作流跳转。
"""

from app.schemas.task import PlanOutput, ResearchOutput, WriterOutput


def run_writer(model, plan: PlanOutput, research: ResearchOutput) -> WriterOutput:
    """把计划与研究摘要转成中文 Markdown 草稿。"""
    chain = model.with_structured_output(WriterOutput)
    prompt = (
        "请输出面向教学的中文 Markdown 草稿，并返回结构化结果。\n"
        f"目标：{plan.objective}\n"
        f"步骤：{plan.steps}\n"
        f"研究摘要：{research.summary}\n"
        f"关键要点：{research.bullet_points}"
    )
    return chain.invoke(prompt)
