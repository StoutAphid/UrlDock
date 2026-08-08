from sqlmodel import SQLModel, create_engine, Session
from chromadb import PersistentClient
from chromadb.config import Settings as ChromaSettings
from app.config import get_settings
import os


settings = get_settings()

engine = create_engine(settings.database_url, echo=settings.debug)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    os.makedirs(settings.chroma_db_path, exist_ok=True)


def get_session() -> Session:
    with Session(engine) as session:
        yield session


def get_chroma_client() -> PersistentClient:
    return PersistentClient(
        path=settings.chroma_db_path,
        settings=ChromaSettings(anonymized_telemetry=False)
    )


def get_chroma_collection(client: PersistentClient, name: str = "links"):
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )