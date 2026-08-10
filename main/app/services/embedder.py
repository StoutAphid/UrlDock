import json
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import get_settings
from app.database import get_chroma_client, get_chroma_collection
from typing import List, Optional
import numpy as np


settings = get_settings()

_embedder_model: Optional[SentenceTransformer] = None


def get_embedder() -> SentenceTransformer:
    global _embedder_model
    if _embedder_model is None:
        _embedder_model = SentenceTransformer(settings.embedding_model)
    return _embedder_model


def generate_embedding(text: str) -> List[float]:
    model = get_embedder()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def _prepare_metadata(metadata: dict) -> dict:
    """Convert metadata values to ChromaDB-compatible types (str, int, float, bool)."""
    prepared = {}
    for key, value in metadata.items():
        if isinstance(value, list):
            prepared[key] = json.dumps(value)
        elif isinstance(value, (str, int, float, bool)) or value is None:
            prepared[key] = value
        else:
            prepared[key] = str(value)
    return prepared


async def store_embedding(link_id: int, text: str, metadata: dict) -> Optional[str]:
    try:
        client = get_chroma_client()
        collection = get_chroma_collection(client)
        
        embedding = generate_embedding(text)
        prepared_metadata = _prepare_metadata(metadata)
        
        collection.upsert(
            ids=[str(link_id)],
            embeddings=[embedding],
            metadatas=[prepared_metadata],
            documents=[text]
        )
        return str(link_id)
    except Exception as e:
        print(f"Error storing embedding: {e}")
        return None


async def delete_embedding(link_id: int) -> bool:
    try:
        client = get_chroma_client()
        collection = get_chroma_collection(client)
        collection.delete(ids=[str(link_id)])
        return True
    except Exception as e:
        print(f"Error deleting embedding: {e}")
        return False


async def search_similar(query: str, limit: int = 10) -> List[dict]:
    try:
        client = get_chroma_client()
        collection = get_chroma_collection(client)
        
        query_embedding = generate_embedding(query)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            include=["metadatas", "documents", "distances"]
        )
        
        formatted = []
        if results["ids"] and results["ids"][0]:
            for i, link_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                document = results["documents"][0][i] if results["documents"] else ""
                distance = results["distances"][0][i] if results["distances"] else 1.0
                
                # Parse tags back from JSON string if needed
                if "tags" in metadata and isinstance(metadata["tags"], str):
                    try:
                        metadata["tags"] = json.loads(metadata["tags"])
                    except json.JSONDecodeError:
                        metadata["tags"] = []
                
                formatted.append({
                    "link_id": int(link_id),
                    "metadata": metadata,
                    "document": document,
                    "score": 1.0 - distance
                })
        
        return formatted
    except Exception as e:
        print(f"Error searching: {e}")
        return []