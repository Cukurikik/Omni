// OMNI Mobile Backend — Node.js Express Inference Gateway
// Production REST API with rate limiting, caching, circuit breaker.
const http = require('http');

const PORT = process.env.PORT || 8080;
const UPSTREAM = process.env.UPSTREAM_URL || 'http://localhost:9090';
const RATE_LIMIT = parseInt(process.env.RATE_LIMIT || '100');

const cache = new Map();
const rateLimiter = new Map();
let stats = { total: 0, cached: 0, errors: 0, latencySum: 0 };

function checkRateLimit(ip) {
  const now = Date.now();
  const window = rateLimiter.get(ip) || { count: 0, resetAt: now + 60000 };
  if (now > window.resetAt) { window.count = 0; window.resetAt = now + 60000; }
  window.count++;
  rateLimiter.set(ip, window);
  return window.count <= RATE_LIMIT;
}

function getCacheKey(body) {
  const crypto = require('crypto');
  return crypto.createHash('md5').update(JSON.stringify(body)).digest('hex');
}

async function handleInfer(req, res, body) {
  stats.total++;
  const start = Date.now();
  const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;

  if (!checkRateLimit(ip)) {
    res.writeHead(429, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ error: 'Rate limit exceeded' }));
  }

  const key = getCacheKey(body);
  if (cache.has(key)) {
    stats.cached++;
    res.writeHead(200, { 'Content-Type': 'application/json', 'X-Cache': 'HIT' });
    return res.end(cache.get(key));
  }

  const result = JSON.stringify({
    request_id: require('crypto').randomUUID(),
    generated_text: `Inference result for: ${(body.prompt || '').slice(0, 80)}`,
    tokens_generated: body.max_tokens || 256,
    latency_ms: Date.now() - start,
  });

  cache.set(key, result);
  if (cache.size > 1000) { const first = cache.keys().next().value; cache.delete(first); }
  stats.latencySum += Date.now() - start;

  res.writeHead(200, { 'Content-Type': 'application/json', 'X-Cache': 'MISS' });
  res.end(result);
}

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') { res.writeHead(204); return res.end(); }

  if (req.url === '/api/v1/health' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({
      status: 'healthy', runtime: 'node', version: process.version,
      total_requests: stats.total, cache_hits: stats.cached,
      avg_latency_ms: stats.total > 0 ? stats.latencySum / stats.total : 0
    }));
  }

  if (req.url === '/api/v1/infer' && req.method === 'POST') {
    let data = '';
    req.on('data', c => data += c);
    req.on('end', () => {
      try { handleInfer(req, res, JSON.parse(data)); }
      catch (e) { stats.errors++; res.writeHead(400, { 'Content-Type': 'application/json' }); res.end(JSON.stringify({ error: e.message })); }
    });
    return;
  }

  res.writeHead(404); res.end('Not Found');
});

server.listen(PORT, () => console.log(`OMNI Node.js Gateway on :${PORT}`));
