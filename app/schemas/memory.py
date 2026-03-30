"""长期记忆的只读视图模型。"""

from datetime import datetime

from pydantic import BaseModel


class MemoryView(BaseModel):
    """对外暴露的一条长期记忆。"""

    id: int
    namespace: str
    key: str
    content: str
    created_at: datetime
