from fastapi import APIRouter, Request, Query, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.services.pipeline import process_link, search_links, get_links
from app.schemas import SearchResult


router = APIRouter()
_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


@router.post("/_ui/links", response_class=HTMLResponse)
async def ui_add_link(request: Request, url: str = Form(...)):
    link, error = await process_link(str(url).strip())
    if error:
        return templates.TemplateResponse(
            request, "partials/save_message.html",
            {"status": "error", "error": error, "url": str(url)},
            status_code=200,
        )
    return templates.TemplateResponse(
        request, "partials/save_message.html",
        {"status": "success", "link": link},
        status_code=200,
    )


@router.get("/_ui/search", response_class=HTMLResponse)
async def ui_search(request: Request, q: str = Query(default="", min_length=0)):
    if not q or not q.strip():
        return templates.TemplateResponse(
            request, "partials/search_results.html",
            {"results": [], "query": q},
        )
    results = await search_links(q, limit=8)
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
    return templates.TemplateResponse(
        request, "partials/search_results.html",
        {"results": result_models, "query": q},
    )


@router.get("/_ui/links-grid", response_class=HTMLResponse)
async def ui_links_grid(request: Request, sort: str = "newest"):
    links = await get_links(limit=50, sort=sort)
    return templates.TemplateResponse(
        request, "partials/links_grid.html",
        {"links": links},
    )