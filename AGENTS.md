# Base44 Dev Environment

## What this repo is

This is the **awesome-selfhosted** repository — a curated Markdown list of self-hosted
software. It has no application server, no `package.json`, and no build system. The only
content is `README.md` (the main list) and `non-free.md`.

## How the preview works

A lightweight Python server (`serve.py`) renders `README.md` to HTML on every request and
serves it on port 3000. The `markdown` Python library is installed at container startup.
Edits to `README.md` are visible immediately (no restart needed) because the file is
re-read on each request.

Static assets in `_static/` are served directly (e.g. `_static/awesome.png`).

## Running

```sh
docker compose -f docker-compose.base44.yml up -d
```

The server uses `python:3.12-slim` as the base image with the repo bind-mounted at `/app`.
No external credentials are needed.
