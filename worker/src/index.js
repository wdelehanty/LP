/* GET /api/status for the williamdelehanty.com status rail.
   Reads the "Portfolio: Status Endpoint" n8n webhook, which counts active
   workflows and finds the last successful Morning Round v2 run using a
   credential kept inside n8n. Cached 15 minutes at the edge and in the
   isolate. Any failure returns 502 with no-store, and the page keeps the
   values baked in at build time. */

const DEFAULT_TTL = 900;
let memo = { at: 0, body: null };

export default {
  async fetch(request, env, ctx) {
    const cors = {
      'access-control-allow-origin': env.ALLOW_ORIGIN || '*',
      'access-control-allow-methods': 'GET, OPTIONS',
      'vary': 'origin',
    };
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    if (request.method !== 'GET') return json({ error: 'method not allowed' }, 0, cors, 'error', 405);

    const ttl = Number(env.CACHE_SECONDS) || DEFAULT_TTL;
    const now = Date.now();
    if (memo.body && now - memo.at < ttl * 1000) return json(memo.body, ttl, cors, 'memory');

    const cache = caches.default;
    const key = new Request('https://williamdelehanty.com/api/status', { method: 'GET' });
    const hit = await cache.match(key);
    if (hit) {
      const body = await hit.json();
      memo = { at: now, body };
      return json(body, ttl, cors, 'edge');
    }

    let body;
    try {
      body = await build(env);
    } catch (err) {
      return json({ error: String((err && err.message) || err) }, 0, cors, 'error', 502);
    }
    memo = { at: now, body };
    const res = json(body, ttl, cors, 'origin');
    ctx.waitUntil(cache.put(key, res.clone()));
    return res;
  },
};

async function build(env) {
  /* The n8n side does the counting: the "Portfolio: Status Endpoint"
     workflow reads the n8n API with a credential stored in n8n itself, so
     no API key lives in this Worker. This Worker adds the cache and CORS. */
  const src = env.STATUS_SOURCE_URL;
  if (!src) throw new Error('STATUS_SOURCE_URL is not set');
  const r = await fetch(src, { headers: { accept: 'application/json' } });
  if (!r.ok) throw new Error('status source returned ' + r.status);
  const s = await r.json();
  if (typeof s.workflows_active !== 'number') throw new Error('status source returned no workflows_active');
  const at = s.last_morning_round_at || null;
  return {
    workflows_active: s.workflows_active,
    last_morning_round: s.last_morning_round || (at ? label(at) : null),
    last_morning_round_at: at,
    generated_at: new Date().toISOString(),
  };
}

/* "Wed 07:00" in New York time, matching the baked format in the markup */
function label(iso) {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/New_York',
    weekday: 'short',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  }).formatToParts(new Date(iso));
  const get = (type) => (parts.find((p) => p.type === type) || {}).value || '';
  return get('weekday') + ' ' + get('hour') + ':' + get('minute');
}

function json(body, ttl, cors, source, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: Object.assign(
      {
        'content-type': 'application/json; charset=utf-8',
        'cache-control': ttl ? 'public, max-age=' + ttl + ', s-maxage=' + ttl : 'no-store',
        'x-status-source': source,
      },
      cors
    ),
  });
}
