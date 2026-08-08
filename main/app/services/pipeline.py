from sqlmodel import Session, select
from app.database import engine, get_chroma_client, get_chroma_collection
from app.models import Link
from app.schemas import LinkCreate, LinkRead
from app.services.fetcher import fetch_page_content, get_content_snippet
from app.services.llm import generate_summary_and_tags
from app.services.embedder import store_embedding, delete_embedding, search_similar
from app.config import get_settings
from typing import Optional, List
from datetime import datetime


settings = get_settings()


async def process_link(url: str) -> tuple[Optional[Link], Optional[str]]:
    """
    Full pipeline: fetch -> summarize -> tag -> embed -> store
    Returns: (Link object, error_message)
    """
    with Session(engine) as session:
        existing = session.exec(select(Link).where(Link.url == url)).first()
        if existing:
            return existing, "Link already exists"
        
        link = Link(url=url, fetch_status="processing")
        session.add(link)
        session.commit()
        session.refresh(link)
    
    try:
        content, extracted_title, fetch_error = await fetch_page_content(url)
        
        if fetch_error:
            with Session(engine) as session:
                link = session.get(Link, link.id)
                if link:
                    link.fetch_status = "failed"
                    session.add(link)
                    session.commit()
            return None, fetch_error
        
        summary, tags, llm_error = await generate_summary_and_tags(content)
        
        if llm_error:
            with Session(engine) as session:
                link = session.get(Link, link.id)
                if link:
                    link.fetch_status = "failed"
                    session.add(link)
                    session.commit()
            return None, llm_error
        
        title = extracted_title or "Untitled"
        snippet = get_content_snippet(content)
        
        embed_text = f"{title}\n{summary}\n{content[:2000]}"
        metadata = {
            "link_id": link.id,
            "title": title,
            "url": url,
            "tags": tags
        }
        
        await store_embedding(link.id, embed_text, metadata)
        
        with Session(engine) as session:
            link = session.get(Link, link.id)
            if link:
                link.title = title
                link.summary = summary
                link.set_tags_list(tags)
                link.content_snippet = snippet
                link.fetch_status = "ok"
                session.add(link)
                session.commit()
                session.refresh(link)
        
        return link, None
        
    except Exception as e:
        with Session(engine) as session:
            link = session.get(Link, link.id)
            if link:
                link.fetch_status = "failed"
                session.add(link)
                session.commit()
        return None, f"Pipeline error: {str(e)}"


async def get_link(link_id: int) -> Optional[LinkRead]:
    with Session(engine) as session:
        link = session.get(Link, link_id)
        if link:
            return LinkRead.from_model(link)
    return None


async def get_links(tag: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[LinkRead]:
    with Session(engine) as session:
        query = select(Link).order_by(Link.date_saved.desc())
        
        if tag:
            all_links = session.exec(query).all()
            filtered = [l for l in all_links if tag in l.get_tags_list()]
            filtered = filtered[offset:offset + limit]
            return [LinkRead.from_model(l) for l in filtered]
        
        query = query.offset(offset).limit(limit)
        links = session.exec(query).all()
        return [LinkRead.from_model(l) for l in links]


async def delete_link(link_id: int) -> bool:
    with Session(engine) as session:
        link = session.get(Link, link_id)
        if not link:
            return False
        session.delete(link)
        session.commit()
    
    await delete_embedding(link_id)
    return True


async def search_links(query: str, limit: int = 10) -> List[dict]:
    results = await search_similar(query, limit)
    return results


async def get_all_tags() -> List[str]:
    with Session(engine) as session:
        links = session.exec(select(Link)).all()
        all_tags = set()
        for link in links:
            all_tags.update(link.get_tags_list())
        return sorted(all_tags)