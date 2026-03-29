from langchain_core.tools import tool

from app.memory.long_term import LongTermMemoryService


def build_memory_lookup_tool(memory_service: LongTermMemoryService):
    @tool("memory_lookup")
    def memory_lookup(user_id: str) -> str:
        """读取指定用户的长期记忆摘要。"""
        return memory_service.render_for_prompt(user_id)

    return memory_lookup
