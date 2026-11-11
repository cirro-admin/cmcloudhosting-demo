# CM Cloud PHP starter

A small PHP app that exists to show the deployment path working, end to end. PHP serves it under this app's own user account, with `public/` as the document root — the same layout Laravel expects — and nginx in front.

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
| Build command | _(leave empty — `composer install --no-dev` runs for you when there is a `composer.json`)_ |
| Start command | _(leave empty — the server is started for you)_ |
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
- For a real Laravel app the platform also builds the `.env` from your `.env.example`
  with production defaults (`APP_ENV=production`, `APP_DEBUG=false`), keeps one
  `APP_KEY` for the app across deploys, keeps the default SQLite database outside
  the release, and runs `php artisan migrate --force` before traffic moves. A failed
  migration stops the deploy and leaves the previous release serving.
- For managed PostgreSQL set `DB_CONNECTION=pgsql` and `DB_URL` to the `DATABASE_URL`
  from your service's Database tab.
