# CM Cloud Django starter

A working Django 5.2 project you can deploy as-is. Follow the steps below and you
get a running Django site with a managed PostgreSQL database behind it.

Everything is done in the portal. There is no SSH step and nothing to install on
a server.

---

## 1 · Get an App Hosting plan

Portal → **Services** → add **App Hosting**.

App Starter is enough (1 app, 1 GB memory, 10 GB disk). The free trial also works.

## 2 · Order a PostgreSQL database

Open the App Hosting service you just created. In the **commerce** section of that
page, find the **Managed PostgreSQL** card, pick a tier (pg_starter, 1 GB) and pay.

The database is created **when the invoice is paid**, not when you click. Once it
is, a **Database** tab appears on the service page.

> Skipping this step is fine for a first look — the starter falls back to SQLite,
> so it will still deploy and run. But that file lives in the release directory
> and is replaced on every deploy, so do not keep anything in it.

## 3 · Check that external access is on

New databases are opened to the public endpoint **automatically**, so this is
already done — Database tab → **Connection** should show it enabled. Confirm it
and move on.

🔑 It is worth knowing why it matters. Apps are placed on whichever runtime node
has room, and only one of those nodes can reach the database's internal port. The
public endpoint works from every node. If external access is ever switched off,
the database refuses every connection even though the credentials are correct.

## 4 · Copy the connection details

Same **Connection** tab. You need five values:

| | Example |
|---|---|
| host | `db.cmcloudhosting.com` |
| port | `5432` |
| database | `app_z15v1kh21e` |
| user | `app_z15v1kh21e` |
| password | shown on the tab |

## 5 · Build the connection string

```
postgres://USER:PASSWORD@db.cmcloudhosting.com:5432/DATABASE
```

For the example above:

```
postgres://app_z15v1kh21e:s3cret@db.cmcloudhosting.com:5432/app_z15v1kh21e
```

⚠️ **Percent-encode the password** if it contains `@`, `/`, `:` or `#` — those
characters end a field in a URL. `@` becomes `%40`, `/` becomes `%2F`.

⚠️ **Use port 5432.** TLS is required there; a connection without it is refused
with `FATAL: SSL required`. This starter already requests TLS, so there is nothing
to add to the URL.

## 6 · Generate a secret key

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(50))'
```

Django needs one, and the platform deliberately does not supply it — a key we
provided would be identical for every deployment while still signing your users'
sessions.

## 7 · Fill in the deploy form

Service page → the deploy form.

| Field | Value |
|---|---|
| Action | `Deploy Python app` |
| Runtime | **`python_django`** |
| Artifact Reference | `https://github.com/cirro-admin/cmcloudhosting-demo` |
| Branch | `main` |
| Subdirectory | `python-django` |
| Build command | *(leave empty)* |
| Start command | *(leave empty)* |
| Health path | `/_runtime/health` |

Environment variables:

| Name | Value |
|---|---|
| `SECRET_KEY` | the value from step 6 |
| `DATABASE_URL` | the connection string from step 5 |

No GitHub token is needed: this repository is public. For your own private
repository, save a token with `repo` scope in Deploy settings first.

## 8 · Deploy

Click **Redeploy App**.

The deploy log shows, in order: the clone, the virtualenv and `pip install`,
`manage.py migrate`, `manage.py collectstatic`, the new release starting on its
own port, the health check, and the traffic swap.

**A failed migration stops the deploy and leaves your previous version serving.**
Nothing is swapped until the new release answers.

## 9 · Check it

| Open | What it tells you |
|---|---|
| `/` | the page renders, and names the database it is actually using |
| `/api/info` | the same as JSON — database vendor and version, static and media paths, `allowed_hosts` |
| `/admin/` | if it loads **styled**, static files are being served correctly |
| `/_runtime/health` | what the platform polls during a deploy |

On `/api/info`, `"vendor": "postgresql"` with a `"version"` confirms the database
is connected. `"vendor": "sqlite"` means `DATABASE_URL` never reached the app.

## 10 · Add an admin login (optional)

The Django admin needs a user. There is no shell access to the app from the
portal, so either commit a small data migration that creates one, or ask support
to run `manage.py createsuperuser` against the release.

---

## Redeploying

Push to `main` and click **Redeploy App** again. Or generate a **deploy hook** on
the service page, add it as a GitHub push webhook, and every push deploys itself.

Environment variables persist across deploys — you only re-enter one to change it.

## If something goes wrong

| What you see | What to do |
|---|---|
| `django_entrypoint_not_found` | no `manage.py` where we looked — set **Subdirectory** to the folder containing it |
| `django_requirements_not_found` | add a `requirements.txt` next to `manage.py` |
| `django_not_installed` | `requirements.txt` does not list `django` |
| `django_migrate_failed` | the database is unreachable or a migration conflicts. Check `DATABASE_URL` and that step 3 was done. Your previous version is still live |
| `FATAL: SSL required` | a port other than 5432, or TLS disabled |
| `password authentication failed` | wrong password, or it needs percent-encoding (step 5) |
| 400 Bad Request on every page | `ALLOWED_HOSTS` does not include your hostname — the deploy log warns about this and prints the line to add |
| `/admin/` loads unstyled | `STATIC_ROOT` unset, or `collectstatic` failed; the log says which |
| `git_auth_missing` / `git_auth_rejected` | the GitHub token is missing, expired, or lacks `repo` scope |

---

## What the platform does on every deploy

| Step | Note |
|---|---|
| `pip install -r requirements.txt` into a fresh virtualenv | `gunicorn` added if you have not pinned it |
| `manage.py migrate --noinput` | **before** the new release starts; a failure aborts the deploy |
| `manage.py collectstatic --noinput --clear` | when `STATIC_ROOT` is set |
| starts `gunicorn <project>.wsgi:application` | the wsgi module is read from your own `manage.py` |
| nginx serves `STATIC_URL` and `MEDIA_URL` from disk | not through Python |
| TLS, custom domain, zero-downtime swap, rollback on failure | automatic |

It also sets `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DJANGO_SETTINGS_MODULE` and
`PORT` in the app's environment. Your own values override them.

**Uploads survive deploys.** Each deploy is a fresh copy of the repository, so the
default `MEDIA_ROOT = BASE_DIR / "media"` would be wiped. The platform moves it to
permanent storage the first time and says so in the log — nothing to change on
your side.

## Using this with your own Django project

Copy three lines from `starter/settings.py`:

```python
ALLOWED_HOSTS = [h for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h]
CSRF_TRUSTED_ORIGINS = [o for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o]
STATIC_ROOT = BASE_DIR / "staticfiles"
```

Plus `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`, because nginx
terminates TLS and forwards plain HTTP to the app.

**A separate frontend** (React, Vue, Svelte) is a second app slot on the same
plan: runtime `static`, its own subdirectory, build command `npm run build`. The
build output is found automatically. Point it at the API's hostname and add that
hostname to the API's `CSRF_TRUSTED_ORIGINS`.

## Local development

```bash
python3 -m venv venv && venv/bin/pip install -r requirements.txt
SECRET_KEY=dev DEBUG=1 venv/bin/python manage.py migrate
SECRET_KEY=dev DEBUG=1 venv/bin/python manage.py runserver
```
