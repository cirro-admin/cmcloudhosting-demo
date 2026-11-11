import os
import time

_STARTED = time.time()

from flask import Flask, Response, jsonify

app = Flask(__name__)

def _info():
    import os, sys, time, resource
    return {
        "python": sys.version.split()[0],
        # ru_maxrss is KB on Linux. The ceiling it counts against is the plan's
        # MemoryMax cgroup cap, not the node's RAM.
        "rssMb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024,
        "vcpu": os.cpu_count(),
        "uptimeSeconds": int(time.time() - _STARTED),
    }


@app.get("/_runtime/health")
def health():
    return Response("cmcloud-flask:ready\n", mimetype="text/plain")


@app.get("/api/info")
def info():
    return jsonify(_info())


@app.get("/")
def home():
    return '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CM Cloud Flask starter</title><style>body{margin:0;font-family:Inter,system-ui,sans-serif;background:linear-gradient(135deg,#312e81,#0891b2);color:white;min-height:100vh;display:grid;place-items:center}main{max-width:760px;padding:42px;border-radius:26px;background:rgba(15,23,42,.72);box-shadow:0 30px 90px rgba(0,0,0,.32)}h1{font-size:clamp(34px,7vw,76px);margin:0 0 12px}p{font-size:18px;line-height:1.6}</style></head><body><main><h1>Flask app ready</h1><p>CM Cloud Flask starter</p><p>This is the CM Cloud Flask sample: one Flask app under systemd in its own Python virtual environment and its own user account, reached through nginx.<br><br><strong>Walk it through</strong><br>1. <code>/_runtime/health</code> &mdash; the path the platform polls before it moves traffic to a new release.<br>2. <code>/api/info</code> &mdash; the Python version, resident memory and uptime this process actually has.<br>3. Push your own repository over this one: <code>app.py</code> exposing <code>app</code>, plus a <code>requirements.txt</code>. The platform builds the venv and installs it.<br>4. Redeploy and watch the swap: the new colour starts, health has to pass, nginx switches over, the previous colour retires. A failed health check rolls back and leaves the running version serving.<br>5. Put configuration in environment variables in the portal, not in the repository.<br>6. Need a database? Add a managed PostgreSQL service, or a Pocketbase Backend service — each is a service of its own, not part of this app.</p></main></body></html>'


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "3000")))
