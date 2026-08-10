from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from typing import Optional, List
from app.models import Link


class LinkCreate(BaseModel):
    url: HttpUrl

    @field_validator("url", mode="before")
    @classmethod
    def validate_url(cls, v):
        url_str = str(v)
        if not url_str.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return url_str


class LinkRead(BaseModel):
    id: int
    url: str
    title: Optional[str]
    summary: Optional[str]
    tags: List[str]
    content_snippet: Optional[str]
    date_saved: datetime
    fetch_status: str

    @classmethod
    def from_model(cls, link: Link) -> "LinkRead":
        return cls(
            id=link.id,
            url=link.url,
            title=link.title,
            summary=link.summary,
            tags=link.get_tags_list(),
            content_snippet=link.content_snippet,
            date_saved=link.date_saved,
            fetch_status=link.fetch_status,
        )


class LinkList(BaseModel):
    links: List[LinkRead]
    total: int


class SearchResult(BaseModel):
    id: int
    url: str
    title: Optional[str]
    summary: Optional[str]
    tags: List[str]
    score: float


class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    total: int