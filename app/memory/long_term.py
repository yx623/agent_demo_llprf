from sqlalchemy import select

from app.db.models import MemoryItem


class LongTermMemoryService:
    """负责保存和读取长期记忆。"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def save(
        self,
        *,
        user_id: str,
        namespace: str,
        key: str,
        content: str,
        source_run_id: str | None,
    ) -> MemoryItem:
        with self.session_factory() as session:
            item = MemoryItem(
                user_id=user_id,
                namespace=namespace,
                key=key,
                content=content,
                source_run_id=source_run_id,
            )
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    def list_by_user(self, user_id: str) -> list[MemoryItem]:
        with self.session_factory() as session:
            stmt = (
                select(MemoryItem)
                .where(MemoryItem.user_id == user_id)
                .order_by(MemoryItem.created_at.desc(), MemoryItem.id.desc())
            )
            return list(session.scalars(stmt))

    def render_for_prompt(self, user_id: str) -> str:
        memories = self.list_by_user(user_id)
        if not memories:
            return "暂无长期记忆。"

        return "\n".join(
            f"- [{item.namespace}] {item.key}: {item.content}"
            for item in memories[:10]
        )
