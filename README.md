# UrlDock

**Smart Bookmark & Link Organizer with Semantic Search**

Dump in any URL and UrlDock automatically fetches, cleans, summarizes, tags,
and indexes the page so you can later search your saved links with a natural
language query instead of scrolling an unsorted list.

> "that article about transformer attention I saved last month"

UrlDock runs **100% locally** — no Docker, no cloud APIs. Fetching, LLM
summaries, and semantic search all happen on your machine (via Ollama).

---

## Features (v1)

- **Add a link** — paste a URL; it's fetched, cleaned, and stored
- **Auto-summarize** — one local LLM call produces a short summary
- **Auto-tag** — the same call generates 3–6 relevant tags
- **Semantic search** — natural-language search over your saved links
- **Browse / filter** — card grid filterable by tag, sorted by date saved
- **Delete** — simple confirmed removal from DB + vector store

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
├── main/                 # The application (FastAPI + Jinja2)
│   ├── app/
│   │   ├── api/          # Route handlers (REST + HTML endpoints)
│   │   ├── services/     # fetcher, llm, embedder, pipeline
│   │   ├── templates/    # Jinja2 HTML (warm/organic UI)
│   │   ├── static/       # CSS + JS
│   │   └── main.py       # FastAPI entrypoint
│   ├── requirements.txt
│   ├── .env.example
│   └── pyproject.toml
├── scripts/              # Utilities (e.g. models comparison runner)
└── testing/              # pytest suite + fixtures
```

---

## API

| Method | Endpoint       | Purpose                                      |
|--------|----------------|----------------------------------------------|
| POST   | `/links`       | Add a URL (triggers the full pipeline)       |
| GET    | `/links`       | List links, optional `?tag=` filter          |
| GET    | `/links/{id}`  | Get one link                                 |
| DELETE | `/links/{id}`  | Remove a link                                |
| GET    | `/search`      | Semantic search, `?q=...`                    |
| GET    | `/tags`        | All tags                                     |
| GET    | `/health`      | Health check                                 |

Interactive API docs at **http://127.0.0.1:8000/docs**.

---

## Testing

```bash
cd main
pytest ../testing          # run the suite (uses temp DB, no network)
```

---

## License

MIT