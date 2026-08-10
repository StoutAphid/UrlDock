# UrlDock

**Smart Bookmark & Link Organizer with Semantic Search**

Dump in any URL and UrlDock automatically fetches, cleans, summarizes, tags,
and indexes the page so you can later search your saved links with a natural
language query instead of scrolling an unsorted list.

> "that article about transformer attention I saved last month"

UrlDock runs **100% locally** — no Docker, no cloud APIs. Fetching, LLM
summaries, and semantic search all happen on your machine (via Ollama).

---

## Features

- **Add a link** — paste a URL; it's fetched, cleaned, and stored
- **Auto-summarize** — one local LLM call produces a 2–4 sentence summary
- **Auto-tag** — the same call generates 2–4 specific, relevant tags
- **Semantic search** — natural-language search over your saved links
- **Sort** — newest first, oldest first, or title (A–Z)
- **Delete** — simple confirmed removal from the DB + vector store
- **Save feedback** — live "Processing link…" indicator, success/error states
- **Retry failed links** — re-saving a failed URL reprocesses it from scratch

---

## Quick Start

```bash
# 1. Install Ollama and pull a model
ollama pull llama3.2:latest
ollama serve            # keep running in another terminal

# 2. Setup the app
cd main
pip install -r requirements.txt
cp .env.example .env

# 3. Run it
uvicorn app.main:app --reload --port 8000
```

Open **<http://127.0.0.1:8000>**.

---

## Requirements

- Python 3.11+
- [Ollama](https://ollama.com/download) running locally

No virtual environment required — `pip install -r requirements.txt` works globally.

---

## Project Structure

```
UrlDock/
└── main/                      # The application (FastAPI + Jinja2)
    ├── app/
    │   ├── api/               # Route handlers (REST + HTML endpoints)
    │   ├── services/          # fetcher, llm, embedder, pipeline
    │   ├── templates/         # Jinja2 HTML (base, index + partials)
    │   │   └── partials/      # link cards, grid, search results, save messages
    │   ├── static/
    │   │   ├── css/           # styles (responsive, dark/light themes)
    │   │   └── js/            # small vanilla-JS enhancements
    │   ├── main.py            # FastAPI entrypoint
    │   ├── database.py        # SQLite (SQLModel) + ChromaDB setup
    │   ├── config.py          # .env settings
    │   ├── models.py          # Link model
    │   └── schemas.py         # Pydantic schemas
    ├── requirements.txt
    ├── .env.example
    └── pyproject.toml
```

---

## UI Features

### Save Link Feedback
- **Processing** — "Processing link, Please wait..." shows immediately when you click Save
- **Success** — "Link Processed Successfully... Please reload the page" on success
- **Duplicate** — "Link Already Exists" when the URL is already saved
- **Error** — "Not able to process link, please try a different link" on failure (Cloudflare, paywalls, JS-rendered sites, etc.)

---

## API

| Method | Endpoint       | Purpose                                      |
|--------|----------------|----------------------------------------------|
| POST   | `/links`       | Add a URL (triggers the full pipeline)       |
| GET    | `/links`       | List saved links                             |
| GET    | `/links/{id}`  | Get one link                                 |
| DELETE | `/links/{id}`  | Remove a link                                |
| GET    | `/search`      | Semantic search, `?q=...`                    |
| GET    | `/tags`        | All tags                                     |
| GET    | `/health`      | Health check                                 |

Interactive API docs at **http://127.0.0.1:8000/docs**.

---

## Data Storage

- **SQLite** (`urldock.db`) — link metadata, summaries, tags
- **ChromaDB** (`chroma_db/`) — embeddings for semantic search

Both live next to the app and are ignored by git.

---

## License

MIT