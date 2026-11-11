"""CM Cloud FastAPI starter.

The entries list is deliberately IN MEMORY. Add some, redeploy, and they are
gone — state inside a process does not survive a release, which is why a
database is a separate managed service.

The platform starts this with uvicorn bound to 127.0.0.1 on the port it hands
over in PORT; nginx is the only thing reachable from outside.
"""
import os
import resource
import sys
import time

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel

_STARTED = time.time()

app = FastAPI(title="CM Cloud FastAPI starter", docs_url="/api/docs")
_entries: list[dict] = []


class Entry(BaseModel):
    message: str


@app.get("/_runtime/health", response_class=PlainTextResponse)
def health() -> str:
    """The path the platform polls before it moves traffic to a new release."""
    return "cmcloud-fastapi:ready\n"


@app.get("/api/info")
def info() -> dict:
    return {
        "python": sys.version.split()[0],
        # ru_maxrss is KB on Linux. It counts against this plan's MemoryMax
        # cgroup cap, not the node's RAM.
        "rssMb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024,
        "vcpu": os.cpu_count(),
        "uptimeSeconds": int(time.time() - _STARTED),
        "entries": len(_entries),
    }


@app.get("/api/entries")
def list_entries() -> list[dict]:
    return _entries


@app.post("/api/entries", status_code=201)
def add_entry(entry: Entry) -> JSONResponse:
    message = entry.message.strip()
    if not message:
        return JSONResponse({"error": "message is required"}, status_code=400)
    row = {"id": len(_entries) + 1, "message": message, "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    _entries.append(row)
    return JSONResponse(row, status_code=201)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CM Cloud FastAPI starter</title>
<style>
 body{margin:0;font-family:Inter,system-ui,sans-serif;background:#1e1b4b;color:#ede9fe;min-height:100vh;display:grid;place-items:center}
 main{max-width:720px;padding:40px}h1{margin:0 0 8px;font-size:34px}
 p,li{line-height:1.65}code{background:#312e81;padding:2px 6px;border-radius:5px}
</style>
<main>
  <h1>FastAPI starter</h1>
  <p>Uvicorn on the CM Cloud <code>python_fastapi</code> runtime, in its own virtual
     environment and its own user account, reached through nginx.</p>
  <ol>
    <li><code>/_runtime/health</code> — the path the platform polls before it moves
        traffic to a new release.</li>
    <li><code>/api/info</code> — the Python version, resident memory and uptime this
        process actually has. Memory counts against your plan's cap, not the node's RAM.</li>
    <li><code>/api/docs</code> — FastAPI's own OpenAPI UI, no extra setup.</li>
    <li><code>POST /api/entries</code> with <code>{"message":"hello"}</code>, then
        <code>GET /api/entries</code>. Redeploy and they are gone: the list is in memory,
        and that is why a database is a separate managed service.</li>
    <li>Put configuration in environment variables in the portal, not in the repository.</li>
  </ol>
</main>"""
