# CM Cloud App Hosting starters

One small, working app per runtime, ready to deploy on
[CM Cloud App Hosting](https://cmcloudhosting.com). Pick the runtime closest to
your project, deploy its folder as it is, and check that the URL works. Then push
your own code the same way.

Each folder has its own README with the exact deploy-form values.

| Folder | Runtime | What it is | Needs |
|---|---|---|---|
| [`static`](static) | `static` | Plain HTML and CSS served by nginx. No server process | any plan |
| [`node`](node) | `node` | Express API with a page | any plan |
| [`python-fastapi`](python-fastapi) | `python_fastapi` | FastAPI with an OpenAPI page | any plan |
| [`python-flask`](python-flask) | `python_flask` | Flask served by gunicorn | any plan |
| [`python-django`](python-django) | `python_django` | Django 5.2 with admin, static files and PostgreSQL | any plan; PostgreSQL optional |
| [`laravel`](laravel) | `laravel` | PHP front controller in `public/` | any plan |
| [`java`](java) | `java` | Spring Boot 3.3 with a Vue UI built into the jar | App Business or higher, plus managed PostgreSQL |

PocketBase needs no code, so it has no folder. Choose the `pocketbase` runtime
in the portal and the platform installs it for you.

## Deploying a folder

1. In the portal, open your **App Hosting** service and go to the deploy form.
2. Set **Repository** to `https://github.com/cirro-admin/cmcloudhosting-demo`
   and **Branch** to `main`.
3. Set **Subdirectory** to the folder name, for example `python-flask`. For Java
   it is `java/backend`.
4. Choose the **Runtime** from the table, and fill the other fields from that
   folder's README.
5. Click **Redeploy App** and follow the deploy log.

**Moving on to your own code.** The deploy form keeps Subdirectory and Start
command from the last deploy; leaving a field empty does not clear it. When you
switch Repository to your own project, type a single dot (`.`) in Subdirectory
if your app sits at the root of your repository, and check the Start command.

This repository is public, so no GitHub token is needed. For your own private
repository, save a token with `repo` scope in Deploy settings first.

## What every starter shows

- `/_runtime/health` is the path the platform checks before it moves traffic to
  a new release. A release that never turns healthy is rolled back, and the
  previous one keeps serving.
- `/api/info` (not in `static`) shows the runtime version, memory and uptime the
  process actually has.
- The app listens on `127.0.0.1` on the port the platform passes as `PORT`.
  nginx in front of it handles TLS and is the only thing reachable from outside.

## Guides

- [All App Deployment guides](https://cmcloudhosting.com/knowledge-base/app-deployment)
- [Which environment variables does my app need?](https://cmcloudhosting.com/knowledge-base/app-deployment/which-env-vars-does-my-app-need)
- [Connect your app to PostgreSQL](https://cmcloudhosting.com/knowledge-base/databases/connect-your-app-to-postgres)
- [Deploy a PocketBase backend](https://cmcloudhosting.com/knowledge-base/app-deployment/deploy-pocketbase-app)

Questions the guides don't answer go to support from the portal.
