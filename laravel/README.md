# CM Cloud PHP starter

A small PHP app that exists to show the deployment path working, end to end. PHP-FPM runs under this app's own user account, with nginx serving `public/` as the document root — the same layout Laravel expects.

Runtime: **`laravel`**

## Deploy it

1. In the portal, open your **App Hosting** service and start a deploy.
2. Fill the form:

| field | value |
|---|---|
| Repository | `https://github.com/cirro-admin/cmcloudhosting-demo` |
| Branch | `main` |
| Subdirectory | `laravel` |
| Runtime | `laravel` |
| Build command | _(leave empty — or `composer install --no-dev` for a real Laravel app)_ |
| Start command | _(leave empty — PHP-FPM is managed for you)_ |
| Health check path | `/_runtime/health` |

3. Deploy, then open the app URL. Nothing it returns is stored: PHP shares nothing between requests, so durable state needs a managed database service.

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
| `/api/info` | PHP version, SAPI, memory in use, memory limit, extension count |
| `POST /api/echo` | echoes a message back — `{"message":"hello"}` |

## Notes

- `public/` is the document root, so nothing outside it is reachable over HTTP. Keep `.env` and `vendor/` above that directory, as Laravel already does.
- Push a real Laravel repository over this one — `artisan` plus `public/index.php` — and the platform runs composer install for you.
