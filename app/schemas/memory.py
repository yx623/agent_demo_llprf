from datetime import datetime

from pydantic import BaseModel


class MemoryView(BaseModel):
    id: int
    namespace: str
    key: str
    content: str
    created_at: datetime
