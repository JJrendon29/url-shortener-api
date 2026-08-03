from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class URL(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_url: str
    code: str = Field(unique=True, index=True)
    clicks: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
