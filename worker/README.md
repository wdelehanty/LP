# Status rail Worker

Serves `GET /api/status` for the rail under the site nav.

Response:

```json
{
  "workflows_active": 35,
  "last_morning_round": "Wed 07:00",
  "last_morning_round_at": "2026-09-02T11:00:48.027Z",
  "generated_at": "2026-09-02T13:10:00.000Z"
}
```

The page maps each `data-rail="<key>"` element to the key of the same name.
Anything missing or non-200 is ignored and the baked values stay.

## How the data flows

The Worker holds no secrets. It reads the n8n webhook
`https://n8n.stedd.ai/webhook/portfolio-status`, served by the workflow
"Portfolio: Status Endpoint v2" (id akNgYXFop16grmqY), which counts active
workflows and finds the last successful Morning Round v2 run through the
n8n API using the credential "n8n API - Stedd" stored inside n8n. The
Worker adds the 15 minute cache and the CORS header for the site origin.

## State on 2026-09-02

Deployed at `https://wd-status.wdelehanty.workers.dev/api/status`. It
answers 502 until the n8n side is live, and every page keeps its baked
values, so nothing on the site breaks.

The n8n workflow was created through the MCP connection, which refuses to
attach header credentials to HTTP Request nodes. Two clicks in the n8n UI
finish it:

1. Open the workflow, open "Count Workflows", pick the credential
   "n8n API - Stedd". Do the same on "Last Success". Save.
2. Activate the workflow.

Do not activate it before step 1: the HTTP nodes would fail on every poll
and the Stedd Error Alerting workflow would email about each one.

Public API keys created for the Worker were rejected by n8n as
unauthorized (identical response to a bogus key), which is why the design
moved the credential to the n8n side. The older "Portfolio: Status
Endpoint" workflow (v1) is inactive and can be archived.

## Same-origin route

The commented `routes` entry in `wrangler.toml` binds the Worker to
`williamdelehanty.com/api/status` instead. The zone is on Cloudflare but
the apex record is DNS-only, so that route would not match. Turn the proxy
on for the apex, uncomment the route, run `wrangler deploy`, and set each
page's `data-status` back to `/api/status`. GitHub Pages keeps serving the
site either way.

## Refreshing the baked values

`scripts/release.sh vX.Y.Z` stamps every page and then runs
`scripts/bake_status.py`, which fetches this endpoint and writes the live
values into the markup so the no-JS and Worker-down cases show real, recent
numbers.
