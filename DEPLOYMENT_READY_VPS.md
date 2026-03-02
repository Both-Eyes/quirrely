# QUIRRELY v3.1.3 — VPS DEPLOYMENT GUIDE
## WHC cPanel/WHM Server · IP: 67.215.14.130 · SSH Port: 2243

---

## ENTRY POINT
```bash
cd /backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Production (PM2 — process manager)
```bash
# Install PM2 globally (one-time)
npm install -g pm2

# Start Quirrely with PM2 cluster mode (2 workers)
pm2 start "uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2" \
    --name quirrely \
    --interpreter none \
    --cwd /path/to/backend

# Persist across reboots
pm2 save
pm2 startup    # follow printed command to enable auto-start

# Useful PM2 commands
pm2 status                 # Show running processes
pm2 logs quirrely          # Stream logs
pm2 restart quirrely       # Rolling restart (zero-downtime)
pm2 stop quirrely          # Graceful stop
pm2 delete quirrely        # Remove from PM2
```

### ecosystem.config.js (alternative — place in /backend)
```js
module.exports = {
  apps: [{
    name:        'quirrely',
    script:      'uvicorn',
    args:        'app:app --host 0.0.0.0 --port 8000 --workers 2',
    cwd:         '/path/to/backend',
    interpreter: 'none',
    env: {
      NODE_ENV: 'production',
    },
    max_memory_restart: '500M',
    error_file:  '/var/log/quirrely/error.log',
    out_file:    '/var/log/quirrely/out.log',
  }]
};
```
Start with: `pm2 start ecosystem.config.js`

---

## DATABASE
PostgreSQL (NOT MySQL/MariaDB)
All schemas in /database/ and /backend/schema_*.sql

## SCHEMA FILES (run in order)
1. database/schema.sql
2. backend/schema_auth.sql
3. backend/schema_payments.sql
4. backend/schema_subscriptions_v2.sql
5. backend/schema_analytics.sql
6. backend/schema_email.sql
7. backend/schema_stretch.sql       ← NEW in v3.1.3
8. backend/schema_admin.sql
9. backend/schema_authority.sql
10. backend/schema_curator.sql
11. backend/schema_milestones.sql
12. backend/schema_profiles.sql
13. backend/schema_reader.sql
14. backend/schema_token_ledger.sql
15. backend/schema_halo.sql         ← NEW in v3.1.3 (also in database/)

### Seed stretch prompts
```bash
psql $DATABASE_URL -c "
  INSERT INTO stretch_prompts_base (target_profile, cycle_number, prompt_position, variant, story_starter, instruction, difficulty)
  SELECT p->>'target_profile', (p->>'cycle_number')::int, (p->>'prompt_position')::int, 
         (p->>'variant')::int, p->>'story_starter', p->>'instruction', (p->>'difficulty')::int
  FROM jsonb_array_elements((SELECT content::jsonb->'prompts' FROM (
    SELECT pg_read_file('/path/to/database/stretch_prompts_base.json') AS content
  ) t)) AS p
  ON CONFLICT DO NOTHING;
"
```

---

## CLOUDFLARE CONFIGURATION

### DNS records (Cloudflare dashboard → DNS)
```
Type  Name            Content             Proxy
A     quirrely.com    67.215.14.130       ✓ (orange cloud)
A     api             67.215.14.130       ✓
A     www             67.215.14.130       ✓
CNAME admin           quirrely.com        ✓
```

### Page Rules / Transform Rules
1. **Geo-blocking** — Block US visitors:
   - Expression: `(ip.geoip.country eq "US")`
   - Action: Block (or redirect to /unavailable.html)

2. **Cache static assets** — Cache-Control: max-age=86400
   - Expression: `(http.request.uri.path matches "^/assets/")`

3. **Force HTTPS** — Always Use HTTPS: ON (SSL/TLS → Edge Certificates)

### WAF Rules (Cloudflare → Security → WAF)
- Block bad bots: OWASP ruleset ON
- Rate limiting: 100 req/min per IP on `/api/` endpoints

### SSL/TLS
- Mode: **Full (strict)**
- Minimum TLS version: TLS 1.2
- Certificate: Cloudflare Universal (auto-renew)

### Quirrely Performance settings
- Auto Minify: JS ✓ CSS ✓ HTML ✓
- Brotli: ON
- HTTP/3 (QUIC): ON

---

## DOMAIN REDIRECTS

### quirrely.ca → quirrely.com (primary)
In Cloudflare (quirrely.ca zone) → Rules → Redirect Rules:
```
Source:      https://quirrely.ca/*
Destination: https://quirrely.com/$1
Type:        301 (Permanent)
```
Or via nginx (on VPS):
```nginx
server {
    listen 80;
    server_name quirrely.ca www.quirrely.ca;
    return 301 https://quirrely.com$request_uri;
}
```

### Other country domains → quirrely.com
Same pattern for: quirrely.co.uk, quirrely.com.au, quirrely.co.nz

---

## HEALTH CHECK URLS
- https://api.quirrely.com/health
- https://api.quirrely.com/api/admin/v2/health
- https://api.quirrely.com/api/extension/sync
- wss://api.quirrely.com/ws/metrics

---

## WHAT'S NEW IN v3.1.3
- backend/app.py — unified entry point (stretch_api now mounted)
- backend/extension_api.py — Chrome extension sync
- backend/stretch_api.py — STRETCH exercises
- backend/schema_stretch.sql — 11 new tables
- backend/schema_halo.sql — HALO safety layer tables
- database/stretch_prompts_base.json — prompt seed data
- assets/css/compat.css — cross-browser compatibility
- assets/js/compat.js — runtime browser fixes
- assets/js/stretch-components.js — portable STRETCH UI
- extension/ — Chrome Extension v2.0.0
- assets/css/responsive.css — mobile polish
- lncp/meta/stretch_observer.py — meta integration
- lncp/meta/funnel_observer.py — funnel tracking
- lncp/meta/viral_observer.py — viral/referral tracking
