import httpx
import json
from typing import Optional
from app.config import get_settings


settings = get_settings()

SUMMARY_TAGS_PROMPT = """You are a helpful assistant that summarizes web articles and generates relevant tags.

Given the article content below, provide:
1. A concise summary (2-4 sentences) capturing the main points
2. 2-4 relevant tags (lowercase, hyphenated, e.g. "machine-learning", "tutorial", "python")

Tags should be SPECIFIC to the article's topic, not generic. Avoid: "article", "guide", "tutorial", "introduction", "overview", "basics", "fundamentals", "beginner", "advanced", "tips", "tricks", "best-practices", "how-to", "web", "development", "programming", "software", "technology", "tech", "news", "blog", "post", "read", "reading".

Return ONLY valid JSON in this exact format:
{{"summary": "Your summary here...", "tags": ["tag1", "tag2"]}}

Article content:
{content}"""


async def generate_summary_and_tags(content: str) -> tuple[Optional[str], Optional[list[str]], Optional[str]]:
    """
    Generate summary and tags using Ollama.
    Returns: (summary, tags_list, error_message)
    """
    prompt = SUMMARY_TAGS_PROMPT.format(content=content[:8000])
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            
    except httpx.TimeoutException:
        return None, None, "LLM request timed out"
    except httpx.HTTPStatusError as e:
        return None, None, f"Ollama HTTP error: {e.response.status_code}"
    except httpx.RequestError as e:
        return None, None, f"Cannot connect to Ollama: {str(e)}"
    except Exception as e:
        return None, None, f"LLM error: {str(e)}"
    
    try:
        response_text = result.get("response", "")
        parsed = json.loads(response_text)
        
        summary = parsed.get("summary", "").strip()
        tags = parsed.get("tags", [])
        
        if not summary:
            return None, None, "Empty summary from LLM"
        
        if not isinstance(tags, list):
            tags = []
        
        cleaned_tags = []
        for tag in tags[:settings.max_tags]:
            if isinstance(tag, str):
                cleaned = tag.lower().strip()
                cleaned = cleaned.replace(" ", "-")
                cleaned = "".join(c for c in cleaned if c.isalnum() or c == "-")
                if cleaned and len(cleaned) > 1:
                    cleaned_tags.append(cleaned)
        
        cleaned_tags = list(dict.fromkeys(cleaned_tags))
        
        return summary, cleaned_tags, None
        
    except json.JSONDecodeError as e:
        return None, None, f"Failed to parse LLM response: {str(e)}"
    except Exception as e:
        return None, None, f"Response processing error: {str(e)}"


async def test_ollama_connection() -> tuple[bool, str]:
    """Test if Ollama is running and model is available."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            
            models = [m["name"] for m in data.get("models", [])]
            if settings.ollama_model not in models:
                return False, f"Model '{settings.ollama_model}' not found. Available: {models}"
            
            return True, "OK"
    except Exception as e:
        return False, f"Cannot connect to Ollama: {str(e)}"