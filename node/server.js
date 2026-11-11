// CM Cloud node starter.
//
// Two things here are not decoration:
//   * it binds 127.0.0.1, never 0.0.0.0 — nginx is the only thing that should
//     be reachable from outside, and the platform proxies to this port.
//   * the entries list is deliberately IN MEMORY. Add some, redeploy, and they
//     are gone. That is the point: state in a process does not survive a
//     release, which is why a database is a separate managed service.
const express = require('express');

const app = express();
const port = process.env.PORT || 3000;
const started = Date.now();
const entries = [];

app.use(express.json());

// The path the platform polls before it moves traffic to a new release.
app.get('/_runtime/health', (_req, res) => {
  res.type('text/plain').send('cmcloud-node:ready\n');
});

app.get('/api/info', (_req, res) => {
  const mem = process.memoryUsage();
  res.json({
    node: process.version,
    // Counted against this plan's MemoryMax cgroup cap, not the node's RAM.
    heapUsedMb: Math.round(mem.heapUsed / 1048576),
    rssMb: Math.round(mem.rss / 1048576),
    vcpu: require('os').cpus().length,
    uptimeSeconds: Math.round((Date.now() - started) / 1000),
    entries: entries.length
  });
});

app.get('/api/entries', (_req, res) => res.json(entries));

app.post('/api/entries', (req, res) => {
  const message = (req.body && req.body.message || '').toString().trim();
  if (!message) return res.status(400).json({ error: 'message is required' });
  const entry = { id: entries.length + 1, message, createdAt: new Date().toISOString() };
  entries.push(entry);
  res.status(201).json(entry);
});

app.get('/', (_req, res) => {
  res.type('html').send(`<!doctype html>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CM Cloud node starter</title>
<style>
 body{margin:0;font-family:Inter,system-ui,sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh;display:grid;place-items:center}
 main{max-width:720px;padding:40px}h1{margin:0 0 8px;font-size:34px}
 p,li{line-height:1.65}code{background:#1e293b;padding:2px 6px;border-radius:5px}
 a{color:#7dd3fc}
</style>
<main>
  <h1>Node starter</h1>
  <p>An Express app on the CM Cloud <code>node</code> runtime, started by systemd under
     its own user account and reached through nginx.</p>
  <ol>
    <li><code>/_runtime/health</code> — the path the platform polls before it moves
        traffic to a new release.</li>
    <li><code>/api/info</code> — the Node version, heap in use and uptime this process
        actually has. The heap counts against your plan's memory cap, not the node's RAM.</li>
    <li><code>POST /api/entries</code> with <code>{"message":"hello"}</code>, then
        <code>GET /api/entries</code>. Now redeploy: they are gone. The list is in memory,
        and that is why a database is a separate managed service.</li>
    <li>Redeploy and watch the swap — the new colour starts, health has to pass, nginx
        switches over, the previous colour retires.</li>
    <li>Put configuration in environment variables in the portal, not in the repository.</li>
  </ol>
</main>`);
});

// Express's default error page is HTML with a stack trace in it, which leaks
// absolute paths and is the wrong thing to hand anyone looking at a starter.
// A JSON API should answer malformed JSON with JSON.
app.use((err, _req, res, _next) => {
  const status = err && err.status ? err.status : 500;
  res.status(status).json({
    error: status === 400 ? 'invalid JSON body' : 'internal error'
  });
});

app.listen(port, '127.0.0.1', () => {
  console.log(`cmcloud-node-starter listening on 127.0.0.1:${port}`);
});
