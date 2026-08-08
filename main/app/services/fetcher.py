import httpx
import trafilatura
from trafilatura.settings import use_config
from app.config import get_settings
from typing import Optional
import re
from bs4 import BeautifulSoup


settings = get_settings()

trafilatura_config = use_config()
trafilatura_config.set("DEFAULT", "EXTRACTION_TIMEOUT", "30")


def extract_title_from_html(html: str) -> Optional[str]:
    """Fallback: extract title from HTML <title> tag or og:title meta."""
    try:
        soup = BeautifulSoup(html, "html.parser")
        # Try og:title first (often more descriptive)
        og_title = soup.find("meta", attrs={"property": "og:title"})
        if og_title and og_title.get("content"):
            return og_title["content"].strip()
        # Try twitter:title
        twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
        if twitter_title and twitter_title.get("content"):
            return twitter_title["content"].strip()
        # Fallback to <title> tag
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            return title_tag.string.strip()
    except Exception:
        pass
    return None


async def fetch_page_content(url: str) -> tuple[str, Optional[str], Optional[str]]:
    """
    Fetch and extract clean article content from a URL.
    Returns: (cleaned_text, title, error_message)
    """
    try:
        async with httpx.AsyncClient(
            timeout=settings.fetcher_timeout,
            headers={"User-Agent": settings.fetcher_user_agent},
            follow_redirects=True
        ) as client:
            response = await client.get(str(url))
            response.raise_for_status()
            
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type.lower():
                return "", None, f"Unsupported content type: {content_type}"
            
            html = response.text
            
    except httpx.TimeoutException:
        return "", None, "Request timed out"
    except httpx.HTTPStatusError as e:
        return "", None, f"HTTP {e.response.status_code}: {e.response.reason_phrase}"
    except httpx.RequestError as e:
        return "", None, f"Request failed: {str(e)}"
    except Exception as e:
        return "", None, f"Fetch error: {str(e)}"

    try:
        extracted = trafilatura.extract(
            html,
            config=trafilatura_config,
            include_comments=False,
            include_tables=False,
            no_fallback=False,
            favor_recall=True,
            with_metadata=True,
        )
        
        if not extracted:
            return "", None, "Failed to extract content from page"
        
        if isinstance(extracted, dict):
            text = extracted.get("text", "")
            title = extracted.get("title", None)
        else:
            text = extracted
            title = None
        
        # Fallback: if trafilatura didn't find a title, try HTML meta tags
        if not title:
            title = extract_title_from_html(html)
        
        text = clean_extracted_text(text)
        
        if len(text) < 100:
            return "", title, "Extracted content too short"
            
        if len(text) > settings.max_content_length:
            text = text[:settings.max_content_length]
        
        return text, title, None
        
    except Exception as e:
        return "", None, f"Extraction error: {str(e)}"


def clean_extracted_text(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = text.strip()
    return text


def get_content_snippet(text: str, max_chars: int = 500) -> str:
    if len(text) <= max_chars:
        return text
    snippet = text[:max_chars]
    last_period = snippet.rfind('.')
    if last_period > max_chars * 0.5:
        return snippet[:last_period + 1]
    return snippet + "..."