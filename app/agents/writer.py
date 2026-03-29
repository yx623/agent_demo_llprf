from app.schemas.task import PlanOutput, ResearchOutput, WriterOutput


def run_writer(model, plan: PlanOutput, research: ResearchOutput) -> WriterOutput:
    """把计划与研究摘要转成中文 Markdown 草稿。"""
    chain = model.with_structured_output(WriterOutput)
    return chain.invoke(
        {
            "instruction": "请输出面向教学的中文 Markdown 草稿。",
            "objective": plan.objective,
            "steps": plan.steps,
            "research_summary": research.summary,
            "bullet_points": research.bullet_points,
        }
    )
