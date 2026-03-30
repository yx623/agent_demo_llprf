"""长期记忆服务。"""

from sqlalchemy import select

from app.db.models import MemoryItem


class LongTermMemoryService:
    """负责保存和读取长期记忆。

    这一层把“数据库如何存”隐藏起来，对上层暴露的是“怎么保存一条记忆”
    和“怎么把记忆渲染成 prompt 文本”。
    """

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
        """写入一条长期记忆。"""
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
        """按时间倒序列出指定用户的长期记忆。"""
        with self.session_factory() as session:
            stmt = (
                select(MemoryItem)
                .where(MemoryItem.user_id == user_id)
                .order_by(MemoryItem.created_at.desc(), MemoryItem.id.desc())
            )
            return list(session.scalars(stmt))

    def render_for_prompt(self, user_id: str) -> str:
        """把长期记忆渲染成可直接拼进 prompt 的文本。

        这一步体现了一个重要教学点：数据库记录不一定适合直接给模型看，
        需要先整理成紧凑、稳定的上下文格式。
        """
        memories = self.list_by_user(user_id)
        if not memories:
            return "暂无长期记忆。"

        return "\n".join(
            f"- [{item.namespace}] {item.key}: {item.content}"
            for item in memories[:10]
        )
