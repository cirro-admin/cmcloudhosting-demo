# CM Cloud Java starter

A working Spring Boot 3.3 + Vue 3 application you can deploy as-is. Follow the
steps below and you get a running Java site with a managed PostgreSQL database
behind it.

It runs on App Hosting's shared `java` runtime and deploys from the portal in
minutes.

One `mvn package` builds the Vue bundle **into the jar**, so the app serves its
own UI from one origin. That is what lets it run on App Hosting at all: the
frontend calls `/api/...` as a relative path, so the UI and the API have to share
a hostname.

---

# Deploy on App Hosting

Everything in the portal. No SSH, nothing to install.

## 1 · Get an App Hosting plan

Portal → **Services** → add **App Hosting**.

⚠️ **App Business or higher.** The `java` runtime needs it — a JVM does not fit
inside App Starter's 1 GB cap, and the platform refuses the runtime below that
tier rather than letting it thrash.

## 2 · Order a PostgreSQL database

On that service page, **commerce** section → **Managed PostgreSQL** card → pick a
tier (pg_starter, 1 GB) → pay. It is created when the invoice is paid, and a
**Database** tab then appears.

⚠️ Unlike the Django starter, this app **will not start without a database**:
`DB_URL`, `DB_USER` and `DB_PASSWORD` have no defaults, and Flyway runs its
migration at startup. Order it before you deploy.

## 3 · Check that external access is on

Database tab → **Connection**. New databases are opened automatically, so this
should already show enabled.

## 4 · Build the JDBC URL

From the Connection tab, take the host, port and database name:

```
jdbc:postgresql://db.cmcloudhosting.com:5432/DATABASE?sslmode=require&prepareThreshold=0
```

⚠️ **Both query parameters are load-bearing** — `sslmode=require` because the
endpoint refuses plaintext, and `prepareThreshold=0` because of the pooler. The
second one bites under load rather than on the first request; see *Connecting to
managed PostgreSQL* below.

## 5 · Fill in the deploy form

| Field | Value |
|---|---|
| Action | `Deploy Java app` |
| Runtime | **`java`** |
| Artifact Reference | `https://github.com/cirro-admin/cmcloudhosting-demo` |
| Branch | `main` |
| Subdirectory | **`java/backend`** |
| Build command | *(leave empty)* |
| Start command | *(leave empty)* |
| Health path | `/api/status` |

Environment variables:

| Name | Value |
|---|---|
| `DB_URL` | the JDBC URL from step 4 |
| `DB_USER` | the database role (same as the database name) |
| `DB_PASSWORD` | from the Connection tab |

Leave the commands empty: the platform runs `mvn clean package` itself, which
builds the Vue bundle into the jar, and starts the jar with a heap sized against
your plan's memory cap.

## 6 · Deploy

Click **Redeploy App**. The log shows the clone, `npm ci` and the Vite build,
Maven packaging the jar, then the new release starting, the health check and the
traffic swap. A Java deploy gets a longer health window than other runtimes — a
JVM is slow to start, not slow to serve.

## 7 · Check it

| Open | What it tells you |
|---|---|
| `/` | the Vue page, served from inside the jar |
| `/api/status` | all three tiers as JSON |

`database.reachable: true` with a `serverVersion` means Flyway ran and the app is
talking to managed PostgreSQL. `web.behindReverseProxy: true` and
`servedBy: nginx → Spring Boot` confirm the platform's nginx is in front.

**Verified end to end 2026-10-05:** deployed on the shared
runtime with a paid managed database — `/` served the Vue UI from the jar, and
`/api/status` reported PostgreSQL 17.11 over TLS with a 2.2 ms round trip.

## If something goes wrong

| What you see | What to do |
|---|---|
| the runtime is refused on your plan | App Starter is too small — App Business or higher |
| `java_jar_not_found` | the build produced no fat jar; read the Maven output in the log |
| `npm ci` fails | `package-lock.json` and `package.json` disagree — commit a regenerated lockfile |
| the app starts then stops | almost always the database: check `DB_URL`, and that step 3 is done |
| `FATAL: SSL required` | `sslmode=require` missing from `DB_URL` |
| `prepared statement S_1 does not exist`, intermittently | `prepareThreshold=0` missing from `DB_URL` |

---

## What the app shows, and why

The page draws the request path with live values read from each tier:

| Tier | What is shown | The point |
|---|---|---|
| **1 · nginx** | whether the request arrived through a reverse proxy, scheme, host, client address | TLS terminates here; the JVM is never exposed directly |
| **2 · Spring Boot** | JDK version, heap used / max, uptime, vCPU, bound address | the app listens on `127.0.0.1` only, and its memory ceiling is a real cap |
| **3 · PostgreSQL** | server version, TLS mode, endpoint dialled, backend that answered, database, role, round-trip latency, row count | the data lives on a managed database, not inside the app |

**Two moments worth planning a walkthrough around:**

1. Add a row, redeploy, reload. Uptime goes back to a few seconds; the
   rows are all still there. That is the whole argument for keeping state in a
   managed database rather than inside the app, and it takes fifteen
   seconds to show.
2. The panel shows the address the app **dialled** and the address of the
   PostgreSQL backend that **answered**. When they differ, the connection pooler
   is on screen — the app holds one cheap connection to the pooler, and the
   pooler shares a small set of real database connections across every client.

## How it runs on App Hosting

- the platform runs the jar under its own unprivileged user, bound to `127.0.0.1`;
  nginx terminates TLS in front of it, so the JVM has no public listener
- your plan's memory is a hard cap, and the JVM sizes its heap against that cap
- every deploy starts the new release beside the old one, waits for the health
  path, then swaps traffic; a release that never turns healthy is rolled back

There is one database migration (`V1__entries.sql`) and one table. Flyway applies
it on startup and records it, so the same jar works against an empty database or
an existing one — schema changes ship with the application instead of being a step
someone has to remember during a release.

## Layout

```
backend/     Spring Boot 3.3, Java 21, Flyway, JPA + JdbcClient
frontend/    Vue 3 + Vite + Tailwind, builds to static files
```

## Running it locally

```bash
# a throwaway database
docker run -d --name pgdemo -e POSTGRES_PASSWORD=demo -e POSTGRES_DB=starter \
  -p 55432:5432 postgres:17

# backend
cd backend
DB_URL="jdbc:postgresql://127.0.0.1:55432/starter?sslmode=disable" \
DB_USER=postgres DB_PASSWORD=demo PORT=11001 \
CORS_ALLOWED_ORIGINS=http://localhost:5173 \
mvn spring-boot:run

# frontend, in another terminal
cd frontend && npm install && npm run dev      # http://localhost:5173
```

Vite proxies `/api` to the backend, so the browser talks to one origin in
development just as it does in production.
