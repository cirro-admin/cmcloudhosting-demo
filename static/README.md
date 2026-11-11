# CM Cloud static starter

A small static site that exists to show the deployment path working, end to end. nginx serves the files straight from the release; there is no application process, so there is nothing to start and nothing to crash.

Runtime: **`static`**

## Deploy it

1. In the portal, open your **App Hosting** service and start a deploy.
2. Fill the form:

| field | value |
|---|---|
| Repository | `https://github.com/cirro-admin/cmcloudhosting-demo` |
| Branch | `main` |
| Subdirectory | `static` |
| Runtime | `static` |
| Build command | _(leave empty — or your framework's build, e.g. `npm run build`)_ |
| Start command | _(leave empty — there is no process)_ |
| Health check path | `/` |

3. Deploy, then open the app URL. There is no health endpoint to call, because there is no process — nginx either has the file or it does not.

4. **Redeploy** and watch the swap. The new colour starts, the health check has to pass,
   nginx switches over, and the previous colour retires. A failed health check rolls back
   and leaves the running version serving.
5. **Put configuration in environment variables** in the portal, not in the repository.
6. **Need a database?** Add a managed PostgreSQL service, or a Pocketbase Backend
   service. Each is a service of its own, not part of this app.

## Routes

| path | what it shows |
|---|---|
| `/` | the page, with the walkthrough on it |

## Notes

- The platform looks for `index.html` in `dist/`, `build/`, `out/` or `public/`, so a Vite or Next export needs no configuration. This starter keeps `index.html` at the root.
- **There are no runtime environment variables.** Everything shipped in a static release is public, so secrets must stay out of the bundle.
