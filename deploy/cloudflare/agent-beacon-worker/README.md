# SignalBrain Agent Beacon Worker

Tiny Cloudflare Workers endpoint for the public agent beacon.

Free-tier fit:

- Workers Free includes 100,000 requests/day.
- This endpoint has no secrets and no durable state.
- It returns machine-readable links for agents and redirects humans to the
  GitHub beacon issue.

Deploy:

```bash
cd deploy/cloudflare/agent-beacon-worker
npm install -g wrangler
wrangler deploy
```

Optional route:

```bash
wrangler route add "signalbrain.ai/agent-beacon*" signalbrain-agent-beacon
```
