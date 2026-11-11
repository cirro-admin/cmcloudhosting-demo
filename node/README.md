# CM Cloud node starter

A small Express app that exists to show the deployment path working, end to end. It is started by systemd under its own user account and reached through nginx.

Runtime: **`node`**

## Deploy it

1. In the portal, open your **App Hosting** service and start a deploy.
2. Fill the form:

| field | value |
|---|---|
| Repository | `https://github.com/cirro-admin/cmcloudhosting-demo` |
| Branch | `main` |
| Subdirectory | `node` |
| Runtime | `node` |
| Build command | _(leave empty — dependencies are installed for you)_ |
| Start command | _(leave empty — the `start` script in `package.json` is used)_ |
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
| `/api/info` | Node version, heap in use, RSS, vCPU, uptime |
| `/api/entries` | list the in-memory entries |
| `POST /api/entries` | add one — `{"message":"hello"}` |

## Notes

- It binds `127.0.0.1`, never `0.0.0.0`. The platform passes the port as `PORT` and nginx is the only thing that should be reachable from outside.
- `express` is pinned. An unpinned dependency resolves to whatever is newest on the day you deploy.
