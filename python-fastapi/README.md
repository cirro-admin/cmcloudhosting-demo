# CM Cloud FastAPI starter

A small FastAPI app that exists to show the deployment path working, end to end. Uvicorn runs it under systemd in its own Python virtual environment and its own user account, reached through nginx.

Runtime: **`python_fastapi`**

## Deploy it

1. In the portal, open your **App Hosting** service and start a deploy.
2. Fill the form:

| field | value |
|---|---|
| Repository | `https://github.com/cirro-admin/cmcloudhosting-demo` |
| Branch | `main` |
| Subdirectory | `python-fastapi` |
| Runtime | `python_fastapi` |
| Build command | `venv/bin/pip install -r requirements.txt` |
| Start command | `venv/bin/uvicorn app:app --host 127.0.0.1 --port $PORT` |
| Health check path | `/_runtime/health` |

3. Deploy, then open the app URL. Add a couple of entries, then redeploy: they are gone. The list lives in the process, which is exactly why durable state belongs in a managed database service.

4. **Redeploy** and watch the swap. The new colour starts, the health check has to pass,
   nginx switches over, and the previous colour retires. A failed health check rolls back
   and leaves the running version serving.
5. **Put configuration in environment variables** in the portal, not in the repository.
6. **Need a database?** Add a managed PostgreSQL service, or a Pocketbase Backend
   service. Each is a service of its own, not part of this app.

## Routes

| path | what it shows |
|---|---|
| `/` | this description and the walkthrough |
| `/_runtime/health` | the path the platform polls before swapping traffic |
| `/api/info` | Python version, resident memory, vCPU, uptime |
| `/api/docs` | FastAPI's own OpenAPI UI |
| `/api/entries` | list the in-memory entries |
| `POST /api/entries` | add one — `{"message":"hello"}` |

## Notes

- Versions are pinned in `requirements.txt`. The platform builds the venv and installs into it.
- `python_fastapi` also runs Flask — expose `app` from `app.py` and point the start command at your WSGI/ASGI server.
