# CM Cloud Flask starter

A small Flask app that shows the deployment path working, end to end. It runs
under systemd in its own Python virtual environment and its own user account,
reached through nginx.

Runtime: **`python_flask`**

## Deploy it

1. In the portal, open your **App Hosting** service and start a deploy.
2. Fill the form:

| field | value |
|---|---|
| Repository | `https://github.com/cirro-admin/cmcloudhosting-demo` |
| Branch | `main` |
| Subdirectory | `python-flask` |
| Runtime | `python_flask` |
| Build command | _(leave empty)_ |
| Start command | `venv/bin/gunicorn app:app --bind 127.0.0.1:$PORT --workers 3` |
| Health check path | `/_runtime/health` |

3. Deploy, then open the app URL.
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

## Notes

- **Set the Start command.** Without one the platform runs `python app.py`, which is
  Flask's development server: one process, and not meant for production traffic.
  gunicorn is in `requirements.txt` for that reason.
- The platform builds the venv and installs `requirements.txt` into it.
- The app binds `127.0.0.1`, never `0.0.0.0`. The platform passes the port as `PORT`
  and nginx is the only thing reachable from outside.
- The `__main__` block in `app.py` is for running it locally: `python app.py`.
