"""把长期记忆服务包装成 LangChain Tool。"""

from langchain_core.tools import tool

from app.memory.long_term import LongTermMemoryService


def build_memory_lookup_tool(memory_service: LongTermMemoryService):
    """返回可注入 Agent 的长期记忆查询工具。

    LangChain 的 tool 机制要求外部能力暴露成一个可调用函数。
    这里故意保持最小实现，让读者把注意力放在“工具如何接入 Agent”
    而不是复杂业务逻辑上。
    """
    @tool("memory_lookup")
    def memory_lookup(user_id: str) -> str:
        """读取指定用户的长期记忆摘要。"""
        return memory_service.render_for_prompt(user_id)

    return memory_lookup
