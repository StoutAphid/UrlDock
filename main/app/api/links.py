from fastapi import APIRouter, HTTPException, status, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List
from app.schemas import (
    LinkCreate, LinkRead, LinkList, SearchResponse, SearchResult
)
from app.services.pipeline import (
    process_link, get_link, get_links, delete_link, search_links, get_all_tags
)
from app.config import get_settings


settings = get_settings()
router = APIRouter()

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


@router.post("/links", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
async def create_link(link_data: LinkCreate):
    link, error = await process_link(str(link_data.url))
    if error:
        if error == "Link already exists":
            raise HTTPException(status_code=409, detail=error)
        raise HTTPException(status_code=400, detail=error)
    return link


@router.get("/links", response_model=LinkList)
async def list_links(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    links = await get_links(limit=limit, offset=offset)
    return LinkList(links=links, total=len(links))


@router.get("/links/{link_id}", response_model=LinkRead)
async def get_link_by_id(link_id: int):
    link = await get_link(link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@router.delete("/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link_by_id(link_id: int):
    success = await delete_link(link_id)
    if not success:
        raise HTTPException(status_code=404, detail="Link not found")


@router.get("/search", response_model=SearchResponse)
async def search(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50)):
    results = await search_links(q, limit)
    result_models = []
    for r in results:
        meta = r["metadata"]
        result_models.append(SearchResult(
            id=r["link_id"],
            url=meta.get("url", ""),
            title=meta.get("title", "Untitled"),
            summary=r.get("document", "")[:300],
            tags=meta.get("tags", []),
            score=r["score"],
        ))
    return SearchResponse(
        results=result_models,
        query=q,
        total=len(result_models)
    )


@router.get("/tags", response_model=List[str])
async def list_tags():
    return await get_all_tags()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, sort: str = "newest"):
    links = await get_links(limit=50, sort=sort)
    return templates.TemplateResponse(request, "index.html", {
        "app_name": settings.app_name,
        "links": links,
        "current_sort": sort,
    })