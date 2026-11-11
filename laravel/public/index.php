<?php
/**
 * CM Cloud laravel/PHP starter.
 *
 * nginx serves public/ as the document root — the same layout Laravel expects —
 * so nothing outside this directory is reachable over HTTP. Keep .env and
 * vendor/ above it, as Laravel already does.
 *
 * The entries list is deliberately per-request (PHP shares nothing between
 * requests), which is the same lesson the other starters make with a restart:
 * durable state belongs in a managed database service, not in the app.
 */
declare(strict_types=1);

$started = microtime(true);
$path = strtok($_SERVER['REQUEST_URI'] ?? '/', '?');
$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';

// The path the platform polls before it moves traffic to a new release.
if ($path === '/_runtime/health') {
    header('Content-Type: text/plain');
    echo "cmcloud-laravel:ready\n";
    exit;
}

if ($path === '/api/info') {
    header('Content-Type: application/json');
    echo json_encode([
        'php' => PHP_VERSION,
        'sapi' => PHP_SAPI,
        // memory_limit is PHP's own ceiling; the plan's MemoryMax cgroup cap
        // sits above it and applies to the whole pool.
        'memoryUsedMb' => (int) round(memory_get_usage(true) / 1048576),
        'memoryLimit' => ini_get('memory_limit'),
        'extensions' => count(get_loaded_extensions()),
        'requestMs' => (int) round((microtime(true) - $started) * 1000),
    ], JSON_PRETTY_PRINT);
    exit;
}

if ($path === '/api/echo' && $method === 'POST') {
    $body = json_decode(file_get_contents('php://input') ?: '[]', true);
    $message = trim((string) ($body['message'] ?? ''));
    header('Content-Type: application/json');
    if ($message === '') {
        http_response_code(400);
        echo json_encode(['error' => 'message is required']);
        exit;
    }
    http_response_code(201);
    echo json_encode([
        'message' => $message,
        'note' => 'Not stored. PHP shares nothing between requests — durable state needs a managed database service.',
    ]);
    exit;
}

header('Content-Type: text/html');
?><!doctype html>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CM Cloud PHP starter</title>
<style>
 body{margin:0;font-family:Inter,system-ui,sans-serif;background:#450a0a;color:#fee2e2;min-height:100vh;display:grid;place-items:center}
 main{max-width:720px;padding:40px}h1{margin:0 0 8px;font-size:34px}
 p,li{line-height:1.65}code{background:#7f1d1d;padding:2px 6px;border-radius:5px}
</style>
<main>
  <h1>PHP starter</h1>
  <p>PHP-FPM on the CM Cloud <code>laravel</code> runtime, under this app's own user
     account, with nginx serving <code>public/</code> as the document root.</p>
  <ol>
    <li><code>/_runtime/health</code> — the path the platform polls before it moves
        traffic to a new release.</li>
    <li><code>/api/info</code> — the PHP version, memory in use and limits this process
        actually has.</li>
    <li><code>POST /api/echo</code> with <code>{"message":"hello"}</code>. Nothing is
        stored: PHP shares nothing between requests, so durable state needs a managed
        database service.</li>
    <li>Push a real Laravel repository over this one — <code>artisan</code> plus
        <code>public/index.php</code> — and the platform runs composer install for you.</li>
    <li>Put configuration in environment variables in the portal, not in the repository.</li>
  </ol>
</main>
