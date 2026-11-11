"""Views that report what the platform actually gave the app, so a deploy can
be checked rather than assumed."""
import json
import os

from django.conf import settings
from django.db import connection
from django.http import HttpResponse, JsonResponse

from .models import Entry


def health(request):
    """What the runtime polls during a blue/green swap. Deliberately touches
    nothing: a health route that queries the database reports the database's
    health, and a release that cannot reach its database should roll back on the
    migration step with a clear message, not on an ambiguous health check."""
    return HttpResponse("cmcloud-django:ready\n", content_type="text/plain")


def api_info(request):
    """Database vendor/version and the asset configuration, read live."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
        version = ""
        if connection.vendor == "postgresql":
            cursor.execute("SHOW server_version")
            version = cursor.fetchone()[0]
    return JsonResponse(
        {
            "app": "cmcloud-django-starter",
            "database": {
                "vendor": connection.vendor,
                "version": version,
                # str(): on SQLite, NAME is a Path (BASE_DIR / "db.sqlite3") and
                # JsonResponse raises "Object of type PosixPath is not JSON
                # serializable" -- a 500 on this route only, so / and /admin/
                # both looked fine.
                "name": str(connection.settings_dict.get("NAME") or ""),
                "host": connection.settings_dict.get("HOST") or "local file",
                "entries": Entry.objects.count(),
            },
            "static": {"url": settings.STATIC_URL, "root": str(settings.STATIC_ROOT or "")},
            "media": {"url": settings.MEDIA_URL, "root": str(settings.MEDIA_ROOT or "")},
            "allowed_hosts": list(settings.ALLOWED_HOSTS),
            "debug": settings.DEBUG,
            "served_host": request.get_host(),
            "forwarded_proto": request.META.get("HTTP_X_FORWARDED_PROTO", ""),
            "is_secure": request.is_secure(),
        },
        json_dumps_params={"indent": 2},
    )


def home(request):
    rows = "".join(
        f"<li><strong>{e.label}</strong> — {e.created_at:%Y-%m-%d %H:%M} UTC</li>"
        for e in Entry.objects.all()[:10]
    ) or "<li><em>No entries yet. Add one in the admin.</em></li>"
    info = json.dumps(
        {
            "database": connection.vendor,
            "host": request.get_host(),
            "static_root_set": bool(settings.STATIC_ROOT),
            "media_root": str(settings.MEDIA_ROOT or ""),
        },
        indent=2,
    )
    return HttpResponse(
        f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Django on CM Cloud</title>
<style>
  :root {{ color-scheme: light dark; --bg:#f8fafc; --fg:#0f172a; --card:#ffffff; --line:#e2e8f0; --accent:#15803d; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#0b1120; --fg:#e2e8f0; --card:#111a2e; --line:#1f2a44; --accent:#4ade80; }}
  }}
  body {{ margin:0; padding:48px 16px; background:var(--bg); color:var(--fg);
         font:16px/1.6 ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif; }}
  main {{ max-width:720px; margin:0 auto; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px;
           padding:24px; margin-bottom:20px; }}
  h1 {{ margin:0 0 8px; font-size:28px; letter-spacing:-.02em; }}
  .ok {{ color:var(--accent); font-weight:600; }}
  pre {{ overflow-x:auto; background:var(--bg); border:1px solid var(--line);
         border-radius:10px; padding:14px; font-size:13px; }}
  ul {{ padding-left:20px; }} a {{ color:var(--accent); }}
</style></head>
<body><main>
  <div class="card">
    <h1>Django is running</h1>
    <p class="ok">gunicorn · own virtual environment · own systemd process account</p>
    <p>Migrations applied and static files collected by the deploy.</p>
  </div>
  <div class="card"><h2>Entries</h2><ul>{rows}</ul></div>
  <div class="card"><h2>Environment</h2><pre>{info}</pre>
    <p><a href="/api/info">/api/info</a> · <a href="/admin/">/admin/</a></p></div>
</main></body></html>
""",
    )
