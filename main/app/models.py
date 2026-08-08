from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String
from datetime import datetime
from typing import Optional
import json


class Link(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(unique=True, index=True)
    title: Optional[str] = None
    summary: Optional[str] = None
    tags: str = Field(default="[]", sa_column=Column("tags", String(length=1000), nullable=False))
    content_snippet: Optional[str] = None
    date_saved: datetime = Field(default_factory=datetime.utcnow)
    fetch_status: str = Field(default="pending")

    def get_tags_list(self) -> list[str]:
        try:
            return json.loads(self.tags)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_tags_list(self, tags: list[str]) -> None:
        self.tags = json.dumps(tags)