#!/usr/bin/env python3
"""Minimal markdown-to-HTML server for the awesome-selfhosted preview.

Re-reads README.md on every request so edits are visible immediately.
"""
import http.server
import os
import socketserver

import markdown

README_PATH = os.environ.get("README_PATH", "/app/README.md")
STATIC_DIR = os.environ.get("STATIC_DIR", "/app/_static")

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Awesome Self-Hosted</title>
<style>
  :root { color-scheme: light dark; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    max-width: 920px;
    margin: 0 auto;
    padding: 24px 20px 80px;
    line-height: 1.65;
    color: #24292f;
    background: #fff;
  }
  @media (prefers-color-scheme: dark) {
    body { background: #0d1117; color: #c9d1d9; }
    a { color: #58a6ff; }
    h1, h2, h3 { color: #f0f6fc; }
    code { background: #161b22; color: #79c0ff; }
    table th { background: #161b22; }
    td, th { border-color: #30363d; }
  }
  h1, h2, h3 { line-height: 1.25; }
  a { color: #0969da; text-decoration: none; }
  a:hover { text-decoration: underline; }
  table { border-collapse: collapse; width: 100%; margin: 16px 0; }
  td, th { border: 1px solid #d0d7de; padding: 6px 13px; text-align: left; }
  th { background: #f6f8fa; font-weight: 600; }
  img { max-width: 100%; height: auto; }
  code { background: #eff1f3; padding: 2px 6px; border-radius: 6px; font-size: 85%; }
  hr { border: none; border-top: 1px solid #d0d7de; margin: 28px 0; }
  blockquote { border-left: 4px solid #d0d7de; margin: 0; padding: 4px 16px; color: #57606a; }
</style>
</head>
<body>
__BODY__
</body>
</html>
"""


def render() -> str:
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    body = markdown.markdown(
        content, extensions=["tables", "fenced_code", "toc", "sane_lists"]
    )
    # Rewrite relative _static/ image paths to absolute
    body = body.replace('src="_static/', 'src="/_static/')
    return TEMPLATE.replace("__BODY__", body)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve static assets (images, etc.)
        if self.path.startswith("/_static/"):
            rel = self.path[len("/_static/"):]
            filepath = os.path.join(STATIC_DIR, rel)
            if os.path.isfile(filepath):
                self._serve_file(filepath)
            else:
                self.send_error(404)
            return
        # Serve rendered README
        try:
            html = render()
        except Exception as exc:  # noqa: BLE001
            self.send_error(500, str(exc))
            return
        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_file(self, filepath: str):
        with open(filepath, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", self._guess_type(filepath))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    @staticmethod
    def _guess_type(path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        return {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
        }.get(ext, "application/octet-stream")

    def log_message(self, fmt, *args):  # noqa: A002
        # Keep logs clean
        pass


class ReusableTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3000"))
    with ReusableTCPServer(("0.0.0.0", port), Handler) as httpd:
        print(f"Serving awesome-selfhosted on http://0.0.0.0:{port}", flush=True)
        httpd.serve_forever()
