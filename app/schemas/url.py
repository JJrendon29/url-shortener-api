from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field


class URLCreate(BaseModel):
    original_url: HttpUrl
    expires_in_hours: Optional[int] = Field(default=1, ge=1, le=168)


class URLResponse(BaseModel):
    code: str
    original_url: str
    short_url: str
    clicks: int
    created_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True}


class URLStats(BaseModel):
    code: str
    original_url: str
    short_url: str
    clicks: int
    created_at: datetime
    expires_at: datetime

    model_config = {"from_attributes": True}
