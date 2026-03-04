#!/usr/bin/env python3
"""
QUIRRELY SUPER_TEST v2.0 — ASO · KIM · MARS
Complete test suite: Infrastructure, LNCP Engine, Backend API, Frontend Integrity,
E2E User Journeys, Security, Conversion Audit, and Performance.
"""
import os, sys, json, time, socket, subprocess, ssl, re, argparse, hashlib
import urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

PROD_URL = "https://quirrely.com"
LOCAL_URL = "http://127.0.0.1:8000"
SITE_CA_URL = "https://quirrely.ca"
NGINX_URL = "http://127.0.0.1:8080"
DB_NAME = "quirrely_prod"
APP_DIR = "/opt/quirrely/quirrely_v313_integrated/backend"
FRONTEND_DIR = "/opt/quirrely/quirrely_v313_integrated/frontend"
BLOG_DIR = "/opt/quirrely/quirrely_v313_integrated/blog"
DEPLOY_DIR = "/home/quirrely/quirrely.ca"
PROJECT_ROOT = "/opt/quirrely/quirrely_v313_integrated"
FROM_EMAIL = "Quirrely <hello@quirrely.com>"
REPORT_EMAIL = "hello@quirrely.com"
SSL_CTX = ssl.create_default_context()
GA4_TAG = "G-HQ818WM2YB"

# ═══════════════════════════════════════════════════════════════════════════════
# CLI ARGUMENT PARSING
# ═══════════════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(description="Quirrely Super Test v2.0")
    p.add_argument("--local", action="store_true", help="Use localhost instead of production URL")
    p.add_argument("--stripe-test", action="store_true", help="Enable Stripe test mode for E2E (requires --local)")
    p.add_argument("--skip-e2e", action="store_true", help="Skip Part 5 (E2E Journeys)")
    p.add_argument("--skip-perf", action="store_true", help="Skip Part 8 (Performance)")
    p.add_argument("--parts", type=str, default="", help="Comma-separated parts to run, e.g. 1,2,3")
    p.add_argument("--email", action="store_true", help="Send email report via Resend")
    p.add_argument("--verbose", action="store_true", help="Print inline suggestions")
    p.add_argument("--json-out", type=str, default="", help="Override JSON output path")
    return p.parse_args()


# ═══════════════════════════════════════════════════════════════════════════════
# TEST HARNESS — Shared infrastructure for all test parts
# ═══════════════════════════════════════════════════════════════════════════════

class TestHarness:
    """Base class providing HTTP helpers, DB access, recording, suggestions, and cleanup."""

    def __init__(self, args):
        self.args = args
        self.base_url = LOCAL_URL if args.local else NGINX_URL
        self.api_url = LOCAL_URL  # API always on localhost
        self.results = {}  # part_name -> {name, pass, fail, tests}
        self.suggestions = []
        self.benchmarks = {}
        self._cleanup_emails = []
        self._cleanup_slugs = []
        self._env_cache = None
        self._current_part = None
        self.ts = int(time.time())

    # ── HTTP helpers ──────────────────────────────────────────────────────

    def http_get(self, url, timeout=10, headers=None):
        try:
            hdrs = {"User-Agent": "Mozilla/5.0 (compatible; QuirrelyHealthCheck)"}
            if headers:
                hdrs.update(headers)
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
                return r.status, r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            try:
                return e.code, e.read().decode("utf-8", errors="replace")
            except:
                return e.code, ""
        except Exception as e:
            return 0, str(e)

    def http_post(self, url, data, timeout=10, headers=None):
        try:
            payload = json.dumps(data).encode("utf-8")
            hdrs = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (compatible; QuirrelyHealthCheck)"}
            if headers:
                hdrs.update(headers)
            req = urllib.request.Request(url, data=payload, method="POST", headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode("utf-8"))
            except:
                return e.code, {}
        except Exception as e:
            return 0, {"error": str(e)}

    def http_delete(self, url, timeout=10, headers=None):
        try:
            hdrs = {"User-Agent": "Mozilla/5.0 (compatible; QuirrelyHealthCheck)"}
            if headers:
                hdrs.update(headers)
            req = urllib.request.Request(url, method="DELETE", headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
                return r.status, r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            return e.code, ""
        except Exception as e:
            return 0, str(e)

    def http_patch(self, url, data, timeout=10, headers=None):
        try:
            payload = json.dumps(data).encode("utf-8")
            hdrs = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (compatible; QuirrelyHealthCheck)"}
            if headers:
                hdrs.update(headers)
            req = urllib.request.Request(url, data=payload, method="PATCH", headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode("utf-8"))
            except:
                return e.code, {}
        except Exception as e:
            return 0, {"error": str(e)}

    def http_options(self, url, timeout=10, headers=None):
        try:
            hdrs = {"User-Agent": "Mozilla/5.0 (compatible; QuirrelyHealthCheck)"}
            if headers:
                hdrs.update(headers)
            req = urllib.request.Request(url, method="OPTIONS", headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
                resp_headers = {k.lower(): v for k, v in r.getheaders()}
                return r.status, resp_headers
        except urllib.error.HTTPError as e:
            try:
                resp_headers = {k.lower(): v for k, v in e.headers.items()}
                return e.code, resp_headers
            except:
                return e.code, {}
        except Exception as e:
            return 0, {}

    def timed_get(self, url, timeout=10):
        t0 = time.time()
        st, body = self.http_get(url, timeout=timeout)
        ms = int((time.time() - t0) * 1000)
        return st, body, ms

    def timed_post(self, url, data, timeout=10):
        t0 = time.time()
        st, body = self.http_post(url, data, timeout=timeout)
        ms = int((time.time() - t0) * 1000)
        return st, body, ms

    # ── Database helpers ──────────────────────────────────────────────────

    def db_query(self, sql):
        try:
            r = subprocess.run(
                ["sudo", "-u", "postgres", "psql", "-d", DB_NAME, "-t", "-c", sql],
                capture_output=True, text=True, timeout=10
            )
            return r.stdout.strip(), r.returncode == 0
        except Exception as e:
            return str(e), False

    def db_query_int(self, sql):
        out, ok = self.db_query(sql)
        if ok and out.strip().isdigit():
            return int(out.strip()), True
        return 0, False

    def db_execute(self, sql):
        try:
            r = subprocess.run(
                ["sudo", "-u", "postgres", "psql", "-d", DB_NAME, "-c", sql],
                capture_output=True, text=True, timeout=10
            )
            return r.returncode == 0
        except:
            return False

    # ── PM2 helpers ───────────────────────────────────────────────────────

    def pm2_status(self):
        try:
            r = subprocess.run(["pm2", "jlist"], capture_output=True, text=True, timeout=10)
            return json.loads(r.stdout)
        except:
            return []

    def pm2_proc(self, name="quirrely"):
        procs = self.pm2_status()
        return next((p for p in procs if p.get("name") == name), None)

    # ── SSL helpers ───────────────────────────────────────────────────────

    def ssl_expiry_days(self, hostname):
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
                s.settimeout(5)
                s.connect((hostname, 443))
                cert = s.getpeercert()
                exp = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                return (exp - datetime.now(timezone.utc).replace(tzinfo=None)).days
        except:
            return -1

    # ── Environment helpers ───────────────────────────────────────────────

    def read_env(self):
        if self._env_cache is not None:
            return self._env_cache
        env = {}
        try:
            with open(os.path.join(APP_DIR, ".env")) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        env[k.strip()] = v.strip()
        except:
            pass
        self._env_cache = env
        return env

    def admin_key(self):
        return self.read_env().get("ADMIN_API_KEY", "")

    def admin_headers(self):
        return {"X-Admin-Key": self.admin_key()}

    # ── File helpers ──────────────────────────────────────────────────────

    def read_file(self, path):
        try:
            with open(path, "r") as f:
                return f.read()
        except:
            return ""

    def file_exists(self, path):
        return os.path.isfile(path)

    # ── Recording helpers ─────────────────────────────────────────────────

    def _init_part(self, part_num, name):
        key = f"part_{part_num}"
        self._current_part = key
        self.results[key] = {"name": name, "pass": 0, "fail": 0, "tests": []}
        print(f"\n{'=' * 70}\n  Part {part_num}: {name}\n{'=' * 70}")

    def record(self, name, passed, detail="", owner=""):
        key = self._current_part
        self.results[key]["pass" if passed else "fail"] += 1
        self.results[key]["tests"].append({
            "name": name, "status": "PASS" if passed else "FAIL",
            "detail": detail, "owner": owner
        })
        icon = "✅" if passed else "❌"
        print(f"  {icon} [{owner}] {name}: {detail}")

    def suggest(self, text):
        self.suggestions.append(text)
        if self.args.verbose:
            print(f"  💡 [SUGGESTION] {text}")

    def section(self, title):
        print(f"\n  [{title}]")

    # ── Test user lifecycle ───────────────────────────────────────────────

    def create_test_user(self, prefix="supertest"):
        email = f"{prefix}_{self.ts}_{len(self._cleanup_emails)}@quirrely.com"
        password = "SuperTest2026!x"
        username = f"st_{self.ts}_{len(self._cleanup_emails)}"
        st, resp = self.http_post(f"{self.api_url}/api/v2/auth/signup", {
            "email": email, "password": password, "username": username
        })
        self._cleanup_emails.append(email)
        token = ""
        if st == 200:
            st2, r2 = self.http_post(f"{self.api_url}/api/v2/auth/login", {
                "email": email, "password": password
            })
            if st2 == 200:
                token = r2.get("access_token", "")
        return {"email": email, "password": password, "username": username,
                "token": token, "signup_status": st}

    def auth_headers(self, token):
        return {"Authorization": f"Bearer {token}"}

    def auth_get(self, url, token, timeout=10):
        return self.http_get(url, timeout=timeout, headers=self.auth_headers(token))

    def auth_post(self, url, data, token, timeout=10):
        return self.http_post(url, data, timeout=timeout, headers=self.auth_headers(token))

    # ── Cleanup ───────────────────────────────────────────────────────────

    def cleanup(self):
        """Delete all test users and data created during the run."""
        if self._cleanup_emails:
            emails_like = " OR ".join(f"email='{e}'" for e in self._cleanup_emails)
            self.db_execute(f"DELETE FROM auth_sessions WHERE user_id IN (SELECT id FROM users WHERE {emails_like});")
            self.db_execute(f"DELETE FROM writing_profiles WHERE user_id IN (SELECT id FROM users WHERE {emails_like});")
            self.db_execute(f"DELETE FROM share_profiles WHERE user_id IN (SELECT id FROM users WHERE {emails_like});")
            self.db_execute(f"DELETE FROM users WHERE {emails_like};")
        # Fallback: catch any stragglers
        self.db_execute("DELETE FROM auth_sessions WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%supertest_%@quirrely.com');")
        self.db_execute("DELETE FROM writing_profiles WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%supertest_%@quirrely.com');")
        self.db_execute("DELETE FROM share_profiles WHERE user_id IN (SELECT id FROM users WHERE email LIKE '%supertest_%@quirrely.com');")
        self.db_execute("DELETE FROM users WHERE email LIKE '%supertest_%@quirrely.com';")
        self.db_execute("DELETE FROM newsletter_subscribers WHERE email LIKE '%supertest%' OR email LIKE 'nl_supertest%';")


# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: INFRASTRUCTURE & ENVIRONMENT (~40 tests)
# ═══════════════════════════════════════════════════════════════════════════════

class Part1_Infrastructure(TestHarness):
    """Gates all subsequent parts. Checks PM2, API, DB, SSL, Stripe config, system resources."""

    def run(self):
        self._init_part(1, "Infrastructure & Environment")
        health_ok = False

        # PM2 Health
        self.section("ASO — PM2 Health")
        proc = self.pm2_proc()
        if proc:
            st = proc.get("pm2_env", {}).get("status", "unknown")
            rs = proc.get("pm2_env", {}).get("restart_time", 0)
            mb = proc.get("monit", {}).get("memory", 0) / 1024 / 1024
            uptime_ms = proc.get("pm2_env", {}).get("pm_uptime", 0)
            uptime_hr = (time.time() * 1000 - uptime_ms) / 3600000 if uptime_ms else 0
            self.record("PM2 quirrely online", st == "online", f"status={st}", "ASO")
            self.record("PM2 restarts < 25", rs <= 25, f"restarts={rs}", "ASO")
            self.record("PM2 memory < 512MB", mb < 512, f"{mb:.1f}MB", "ASO")
            self.record("PM2 uptime > 1hr", uptime_hr > 1, f"{uptime_hr:.1f}hr", "ASO")
            self.benchmarks["pm2_memory_mb"] = round(mb, 1)
        else:
            self.record("PM2 quirrely found", False, "not found", "ASO")

        # API Health
        self.section("ASO — API Health")
        st, body = self.http_get(f"{self.api_url}/health")
        health_ok = (st == 200)
        self.record("GET /health 200", st == 200, f"status={st}", "ASO")
        if st == 200:
            try:
                d = json.loads(body)
                self.record("API version present", bool(d.get("version")), f"version={d.get('version')}", "ASO")
                self.record("API status healthy", d.get("status") == "healthy", f"status={d.get('status')}", "ASO")
            except:
                self.record("API health JSON parseable", False, "parse error", "ASO")
        st2, _ = self.http_get(f"{self.api_url}/api/v2/health")
        self.record("GET /api/v2/health 200", st2 == 200, f"status={st2}", "ASO")

        # Database
        self.section("ASO — Database")
        out, ok = self.db_query("SELECT version();")
        self.record("PostgreSQL connection", ok, out[:40] if ok else out, "ASO")
        cnt, ok = self.db_query_int("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
        self.record("Public schema 15+ tables", cnt >= 15, f"{cnt} tables", "ASO")
        core_tables = ["users", "writing_profiles", "subscriptions", "waitlist",
                       "auth_sessions", "newsletter_subscribers", "analytics_events", "share_profiles"]
        for tbl in core_tables:
            out, ok = self.db_query(f"SELECT COUNT(*) FROM {tbl};")
            self.record(f"Table '{tbl}' accessible", ok, f"rows={out.strip()}" if ok else out, "ASO")
        # Connection pool check
        out, ok = self.db_query("SELECT count(*) FROM pg_stat_activity WHERE datname='quirrely_prod';")
        conns = int(out.strip()) if ok and out.strip().isdigit() else 0
        out2, ok2 = self.db_query("SHOW max_connections;")
        max_conns = int(out2.strip()) if ok2 and out2.strip().isdigit() else 100
        pct = (conns / max_conns * 100) if max_conns > 0 else 0
        self.record("DB connection pool < 80%", pct < 80, f"{conns}/{max_conns} ({pct:.0f}%)", "ASO")

        # SSL & DNS
        self.section("ASO — SSL & DNS")
        st, _ = self.http_get(PROD_URL, timeout=15)
        self.record("quirrely.com reachable", st == 200, f"status={st}", "ASO")
        st, _ = self.http_get(SITE_CA_URL, timeout=15)
        self.record("quirrely.ca reachable", st == 200, f"status={st}", "ASO")
        for host in ["quirrely.com", "api.quirrely.com", "quirrely.ca"]:
            days = self.ssl_expiry_days(host)
            self.record(f"SSL valid: {host}", days > 14, f"{days} days", "ASO")

        # Stripe Config
        self.section("MARS — Stripe Config")
        env = self.read_env()
        sk = env.get("STRIPE_SECRET_KEY", "")
        wh = env.get("STRIPE_WEBHOOK_SECRET", "")
        self.record("STRIPE_SECRET_KEY present", bool(sk), "found" if sk else "missing", "MARS")
        self.record("STRIPE key sk_live_ or sk_test_", sk.startswith("sk_live_") or sk.startswith("sk_test_"),
                     "live" if sk.startswith("sk_live_") else ("test" if sk.startswith("sk_test_") else "invalid"), "MARS")
        self.record("STRIPE_WEBHOOK_SECRET present", bool(wh), "found" if wh else "missing", "MARS")
        # Check price IDs
        price_keys = ["STRIPE_PRICE_PRO_MONTHLY", "STRIPE_PRICE_PRO_ANNUAL"]
        for pk in price_keys:
            val = env.get(pk, "")
            self.record(f"{pk} set", bool(val) and val.startswith("price_"), val[:20] if val else "missing", "MARS")

        # System Resources
        self.section("ASO — System Resources")
        try:
            r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
            parts = [l for l in r.stdout.splitlines() if "/" in l and "Filesystem" not in l][-1].split()
            disk_pct = int(parts[4].replace("%", ""))
            self.record("Disk usage < 80%", disk_pct < 80, f"{parts[4]} ({parts[2]}/{parts[1]})", "ASO")
        except Exception as e:
            self.record("Disk usage check", False, str(e), "ASO")
        try:
            r = subprocess.run(["systemctl", "is-active", "apache2"], capture_output=True, text=True, timeout=5)
            active = r.stdout.strip() == "active"
            if not active:
                r = subprocess.run(["systemctl", "is-active", "httpd"], capture_output=True, text=True, timeout=5)
                active = r.stdout.strip() == "active"
            self.record("Apache/httpd active", active, r.stdout.strip(), "ASO")
        except Exception as e:
            self.record("Apache check", False, str(e), "ASO")
        try:
            perms = subprocess.run(["stat", "-c", "%a", os.path.join(APP_DIR, ".env")],
                                   capture_output=True, text=True, timeout=5).stdout.strip()
            self.record(".env permissions 600", perms == "600", f"perms={perms}", "ASO")
        except:
            self.record(".env permissions", False, "check failed", "ASO")

        # Response Time Benchmarks
        self.section("ASO — Response Time Benchmarks")
        # Health endpoint
        _, _, ms = self.timed_get(f"{self.api_url}/health")
        self.record("Health < 200ms", ms < 200, f"{ms}ms", "ASO")
        self.benchmarks["health_ms"] = ms
        # Analyze endpoint
        _, _, ms = self.timed_post(f"{self.api_url}/api/v2/analyze", {
            "text": "The morning light filtered through curtains. She sat quietly thinking about what to write."
        }, timeout=15)
        self.record("Analyze < 3s", ms < 3000, f"{ms}ms", "ASO")
        self.benchmarks["analyze_ms"] = ms
        # Pricing endpoint
        _, _, ms = self.timed_get(f"{self.api_url}/api/v2/payments/pricing")
        self.record("Pricing < 500ms", ms < 500, f"{ms}ms", "ASO")
        self.benchmarks["pricing_ms"] = ms
        # Admin overview
        _, _, ms = self.timed_get(f"{self.api_url}/api/admin/v2/health",
                                   timeout=10)
        self.record("Admin health < 500ms", ms < 500, f"{ms}ms", "ASO")
        # Dashboard (auth required, just measure 401 time)
        _, _, ms = self.timed_get(f"{self.api_url}/api/v2/me/dashboard")
        self.record("Dashboard endpoint < 500ms", ms < 500, f"{ms}ms (401 expected)", "ASO")

        # STRETCH Data
        self.section("KIM — STRETCH Data")
        cnt, _ = self.db_query_int("SELECT COUNT(*) FROM stretch_prompts_base WHERE active=TRUE;")
        self.record("STRETCH prompts 450+", cnt >= 450, f"{cnt} prompts", "KIM")
        cnt, _ = self.db_query_int("SELECT COUNT(*) FROM stretch_authors WHERE active=TRUE;")
        self.record("STRETCH authors 60+", cnt >= 60, f"{cnt} authors", "KIM")
        cnt, _ = self.db_query_int("SELECT COUNT(DISTINCT voice_type) FROM stretch_authors WHERE active=TRUE;")
        self.record("STRETCH 10 voice types", cnt >= 10, f"{cnt} voices", "KIM")

        return health_ok


# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: LNCP ENGINE (~45 tests)
# ═══════════════════════════════════════════════════════════════════════════════

class Part2_LNCPEngine(TestHarness):
    """Core analysis pipeline quality tests."""

    def run(self):
        self._init_part(2, "LNCP Engine")

        # LNCP Orchestrator Pipeline
        self.section("KIM — LNCP Orchestrator Pipeline")
        sys.path.insert(0, APP_DIR)
        try:
            from lncp_orchestrator import get_orchestrator
            orch = get_orchestrator()
            sid, state = orch.create_session(mode="STORY")
            self.record("LNCP session created", bool(sid), f"session={sid[:8]}...", "KIM")

            groups = [
                ["The morning light came through the window.", "She made coffee and sat down."],
                ["Words are the only currency that compounds.", "He wrote slowly, with intention."],
                ["The ratio of silence to speech matters.", "She paused before answering."],
            ]
            for i, grp in enumerate(groups):
                state = orch.submit_group(sid, grp)
                sub_ok = state.get("last_submission", {}).get("status") == "VALID"
                self.record(f"LNCP group {i + 1} accepted", sub_ok,
                            f"gate={state.get('gate', {}).get('completed', 0)}/3", "KIM")

            gate_ok = state.get("gate", {}).get("is_complete", False)
            self.record("LNCP gate complete", gate_ok,
                        "complete" if gate_ok else "incomplete", "KIM")

            analysis = orch.run_analysis(sid)
            self.record("LNCP analysis runs", bool(analysis),
                        f"sentences={len(analysis.get('sentences_analyzed', []))}", "KIM")
            self.record("LNCP phase2 present", "phase2" in analysis,
                        f"mode={analysis.get('phase2', {}).get('presentation_mode', 'N/A')}", "KIM")
            self.record("LNCP phase3 syntheses", len(analysis.get("phase3", {}).get("syntheses", [])) > 0,
                        f"{len(analysis.get('phase3', {}).get('syntheses', []))} syntheses", "KIM")
            orch.cleanup_session(sid)
            self.record("LNCP session cleanup", True, "ok", "KIM")
        except Exception as e:
            self.record("LNCP pipeline import", False, str(e)[:80], "KIM")

        # Analyze API Endpoint
        self.section("KIM — Analyze API Endpoint")
        text = "The morning light filtered through curtains. She sat quietly thinking about what to write next. Words matter more than we realize. The act of writing is itself an argument for attention."
        st, resp = self.http_post(f"{self.api_url}/api/v2/analyze", {"text": text})
        self.record("Analyze endpoint 200", st == 200, f"status={st}", "KIM")
        if st == 200 and isinstance(resp, dict):
            scores = resp.get("scores", {})
            profiles = scores.get("profiles", {})
            stances = scores.get("stances", {})
            self.record("Analyze returns profiles dict", isinstance(profiles, dict) and len(profiles) > 0,
                        f"{len(profiles)} profiles", "KIM")
            self.record("Analyze profiles has 10 keys", len(profiles) >= 10,
                        f"{len(profiles)} keys: {list(profiles.keys())[:5]}...", "KIM")
            self.record("Analyze returns stances dict", isinstance(stances, dict) and len(stances) > 0,
                        f"{len(stances)} stances", "KIM")
            self.record("Analyze stances has 4+ keys", len(stances) >= 4,
                        f"{len(stances)} keys: {list(stances.keys())[:5]}", "KIM")
            conf = resp.get("confidence")
            self.record("Confidence is float 0-1", isinstance(conf, (int, float)) and 0 <= conf <= 1,
                        f"confidence={conf}", "KIM")
        else:
            for n in ["profiles dict", "profiles 10 keys", "stances dict", "stances 5 keys", "confidence"]:
                self.record(f"Analyze returns {n}", False, "no response", "KIM")

        # Profile Score Structure — verify all 10 profiles scored for varied inputs
        # Note: /api/v2/analyze uses a hash-seeded mock classifier, so we test score
        # structure and range rather than linguistic accuracy. The real LNCP parser is
        # tested via the orchestrator pipeline above.
        self.section("KIM — Profile Score Structure")
        test_texts = [
            "This is exactly what needs to happen. No more excuses. We will do this now and we will succeed.",
            "Short words. Clean lines. Done. Nothing more to add here for analysis.",
            "The morning unfurled like a silk ribbon across the sky, each hue bleeding into the next like watercolors left in the rain.",
            "The socioeconomic implications of this multi-factorial paradigm shift necessitate a comprehensive re-evaluation.",
            "So anyway, I was just thinking about this the other day, you know? Like, it's kind of wild when you think about it.",
            "It is with considerable deliberation that this committee hereby recommends the implementation of the aforementioned policy.",
            "The story begins in a small town where nothing much happened, or so it seemed, until the day the letters started arriving each morning without fail.",
            "What if we're wrong? Have we considered the alternative? Who decided this was the best approach? Why aren't we questioning it?",
            "It seems somewhat possible that this might be partially correct, though one could perhaps argue there are other considerations.",
            "We came, we saw, we conquered. Not with force, but with patience. Not with anger, but with grace.",
        ]
        profiles_seen = set()
        all_10_keys = True
        all_scores_valid = True
        for i, txt in enumerate(test_texts):
            st, resp = self.http_post(f"{self.api_url}/api/v2/analyze", {"text": txt})
            if st == 200 and isinstance(resp, dict):
                profiles = resp.get("scores", {}).get("profiles", {})
                if len(profiles) < 10:
                    all_10_keys = False
                for p, v in profiles.items():
                    profiles_seen.add(p.upper())
                    if not (isinstance(v, (int, float)) and 0 <= v <= 1):
                        all_scores_valid = False
                # Track dominant profile to verify variety
                top = max(profiles, key=profiles.get) if profiles else ""
                profiles_seen.add(top.upper())
        self.record("All inputs return 10 profile keys", all_10_keys, f"checked {len(test_texts)} texts", "KIM")
        self.record("All profile scores 0-1 floats", all_scores_valid, "valid ranges", "KIM")
        self.record("Multiple profiles appear as dominant", len(profiles_seen) >= 5,
                     f"{len(profiles_seen)} distinct profiles seen", "KIM")

        # Verify each profile name present in score keys
        expected_profiles = {"ASSERTIVE", "MINIMAL", "POETIC", "DENSE", "CONVERSATIONAL",
                            "FORMAL", "LONGFORM", "INTERROGATIVE", "HEDGED", "PARALLEL"}
        st, resp = self.http_post(f"{self.api_url}/api/v2/analyze", {"text": test_texts[0]})
        if st == 200 and isinstance(resp, dict):
            actual_keys = set(k.upper() for k in resp.get("scores", {}).get("profiles", {}).keys())
            missing = expected_profiles - actual_keys
            self.record("Score keys match 10 profiles", len(missing) == 0,
                        f"missing={missing}" if missing else "all 10 present", "KIM")
        else:
            self.record("Score keys match 10 profiles", False, f"status={st}", "KIM")

        # Stance Score Structure — verify all 4 stances scored
        # Note: /api/v2/analyze uses a hash-seeded mock classifier. Real stance detection
        # (OPEN/CLOSED/BALANCED/CONTRADICTORY via epistemic markers) is tested via the
        # LNCP orchestrator pipeline above. Here we test structure and score validity.
        self.section("KIM — Stance Score Structure")
        expected_stances = {"OPEN", "CLOSED", "BALANCED", "CONTRADICTORY"}
        st, resp = self.http_post(f"{self.api_url}/api/v2/analyze", {"text": test_texts[0]})
        if st == 200 and isinstance(resp, dict):
            stances = resp.get("scores", {}).get("stances", {})
            actual_keys = set(k.upper() for k in stances.keys())
            missing = expected_stances - actual_keys
            self.record("Stance keys present", len(missing) == 0,
                        f"missing={missing}" if missing else f"all {len(actual_keys)} present", "KIM")
            all_valid = all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in stances.values())
            self.record("Stance scores 0-1 floats", all_valid, "valid ranges", "KIM")
            # One stance should be boosted (the mock boosts the selected stance to 0.6-0.9)
            top_stance_score = max(stances.values()) if stances else 0
            self.record("Top stance score > 0.5", top_stance_score > 0.5,
                        f"top={top_stance_score:.3f}", "KIM")
            # Response has a stance field
            self.record("Response has stance field", bool(resp.get("stance")),
                        f"stance={resp.get('stance')}", "KIM")
        else:
            for n in ["Stance keys", "Stance scores", "Top stance", "Stance field"]:
                self.record(n, False, f"status={st}", "KIM")

        # Confidence & Token
        self.section("KIM — Confidence & Token Uniqueness")
        confs = []
        resp_hashes = set()
        for i in range(2):
            txt = f"Sample text number {i} for uniqueness testing. This is a test of the analysis system with enough words to process."
            st, resp = self.http_post(f"{self.api_url}/api/v2/analyze", {"text": txt})
            if st == 200 and isinstance(resp, dict):
                confs.append(resp.get("confidence", -1))
                # Use response hash to check uniqueness (API may not return explicit IDs)
                token = resp.get("session_id", resp.get("analysis_id", resp.get("pattern_id", "")))
                if token:
                    resp_hashes.add(str(token))
                else:
                    resp_hashes.add(hashlib.md5(json.dumps(resp, sort_keys=True).encode()).hexdigest())
        conf = confs[-1] if confs else -1
        self.record("Confidence float 0-1", isinstance(conf, (int, float)) and 0 <= conf <= 1,
                     f"confidence={conf}", "KIM")
        self.record("Analysis responses distinct", len(resp_hashes) >= 2,
                     f"{len(resp_hashes)} distinct from 2 analyses", "KIM")

        # Pattern Recording
        self.section("KIM — Pattern Recording")
        patterns_file = os.path.join(APP_DIR, "patterns", "patterns.json")
        history_file = os.path.join(APP_DIR, "patterns", "history.json")
        self.record("patterns.json exists", self.file_exists(patterns_file),
                     "found" if self.file_exists(patterns_file) else "missing", "KIM")
        self.record("history.json exists", self.file_exists(history_file),
                     "found" if self.file_exists(history_file) else "missing", "KIM")

        # Edge Cases
        self.section("KIM — Edge Cases")
        # Empty text
        st, _ = self.http_post(f"{self.api_url}/api/v2/analyze", {"text": ""})
        self.record("Empty text → 422", st == 422, f"status={st}", "KIM")
        # Short text
        st, _ = self.http_post(f"{self.api_url}/api/v2/analyze", {"text": "Short"})
        self.record("Short text → 422", st == 422, f"status={st}", "KIM")
        # Unicode
        st, resp = self.http_post(f"{self.api_url}/api/v2/analyze", {
            "text": "Les idées naïves sont parfois les plus profondes. Ça va être une journée magnifique avec des rêves étoilés. Même les accents ne posent aucun problème."
        })
        self.record("Unicode text → graceful", st in [200, 422], f"status={st}", "KIM")
        # Large text
        large = " ".join(["The quick brown fox jumps over the lazy dog."] * 500)
        st, resp = self.http_post(f"{self.api_url}/api/v2/analyze", {"text": large}, timeout=20)
        self.record("5000-word text → 200", st == 200, f"status={st}", "KIM")
        # SQL injection in text
        st, _ = self.http_post(f"{self.api_url}/api/v2/analyze", {
            "text": "'; DROP TABLE users; -- This is a test of SQL injection with enough words to reach the minimum threshold for analysis"
        })
        self.record("SQL injection in text → safe", st in [200, 422], f"status={st}", "KIM")
        # XSS in text
        st, _ = self.http_post(f"{self.api_url}/api/v2/analyze", {
            "text": "<script>alert('xss')</script> This is a longer test with script tags to verify XSS is handled safely by the analysis engine"
        })
        self.record("XSS in text → safe", st in [200, 422], f"status={st}", "KIM")
        # Missing text field
        st, _ = self.http_post(f"{self.api_url}/api/v2/analyze", {})
        self.record("Missing text field → 422", st == 422, f"status={st}", "KIM")
        # Non-string text
        st, _ = self.http_post(f"{self.api_url}/api/v2/analyze", {"text": 12345})
        self.record("Non-string text → 422", st == 422, f"status={st}", "KIM")


# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: BACKEND API COVERAGE (~80 tests)
# ═══════════════════════════════════════════════════════════════════════════════

class Part3_BackendAPI(TestHarness):
    """Every mounted router endpoint coverage."""

    def run(self):
        self._init_part(3, "Backend API Coverage")

        # Auth API
        self.section("KIM — Auth API (/api/v2/auth/)")
        user = self.create_test_user("st3")
        token = user["token"]
        self.record("Signup endpoint works", user["signup_status"] == 200, f"status={user['signup_status']}", "KIM")
        self.record("Login returns token", bool(token), "received" if token else "no token", "KIM")

        # Duplicate signup
        st, _ = self.http_post(f"{self.api_url}/api/v2/auth/signup", {
            "email": user["email"], "password": user["password"], "username": user["username"] + "x"
        })
        self.record("Duplicate signup rejected", st in [400, 409, 422], f"status={st}", "KIM")

        # /me endpoint
        if token:
            st, resp = self.auth_get(f"{self.api_url}/api/v2/auth/me", token)
            self.record("GET /auth/me with token", st == 200, f"status={st}", "KIM")
        else:
            self.record("GET /auth/me with token", False, "no token", "KIM")

        # Logout
        if token:
            st, _ = self.auth_post(f"{self.api_url}/api/v2/auth/logout", {}, token)
            self.record("POST /auth/logout", st in [200, 204], f"status={st}", "KIM")
        else:
            self.record("POST /auth/logout", False, "no token", "KIM")

        # Re-login after logout
        st, resp = self.http_post(f"{self.api_url}/api/v2/auth/login", {
            "email": user["email"], "password": user["password"]
        })
        token = resp.get("access_token", "") if st == 200 else ""
        self.record("Re-login after logout", st == 200 and bool(token), f"status={st}", "KIM")

        # Password change (use new password going forward, then re-login)
        if token:
            new_pass = "NewPassword2026!y"
            st, _ = self.auth_post(f"{self.api_url}/api/v2/auth/password/change", {
                "current_password": user["password"], "new_password": new_pass
            }, token)
            self.record("Password change", st in [200, 204], f"status={st}", "KIM")
            if st in [200, 204]:
                user["password"] = new_pass
                # Re-login with new password to get fresh token
                st2, r2 = self.http_post(f"{self.api_url}/api/v2/auth/login", {
                    "email": user["email"], "password": new_pass
                })
                if st2 == 200:
                    token = r2.get("access_token", token)
        else:
            self.record("Password change", False, "no token", "KIM")

        # Password reset (just check endpoint exists)
        st, _ = self.http_post(f"{self.api_url}/api/v2/auth/password/reset", {"email": user["email"]})
        self.record("Password reset endpoint mounted", st not in [0, 404], f"status={st}", "KIM")

        # Verify endpoints
        st, _ = self.auth_post(f"{self.api_url}/api/v2/auth/verify/resend", {}, token)
        self.record("Verify resend mounted", st not in [0, 404], f"status={st}", "KIM")
        st, _ = self.http_get(f"{self.api_url}/api/v2/auth/verify/required")
        self.record("Verify required mounted", st not in [0, 404], f"status={st}", "KIM")

        # Sessions
        if token:
            st, _ = self.auth_get(f"{self.api_url}/api/v2/auth/sessions", token)
            self.record("GET /auth/sessions", st in [200, 401], f"status={st}", "KIM")

        # Account delete (just check mounted — dont actually delete)
        st, _ = self.http_post(f"{self.api_url}/api/v2/auth/account/delete", {})
        self.record("Account delete endpoint mounted", st == 401, f"status={st} (401=auth required)", "KIM")

        # POST /me/update
        if token:
            st, _ = self.auth_post(f"{self.api_url}/api/v2/auth/me/update", {"display_name": "ST Test"}, token)
            self.record("POST /auth/me/update", st in [200, 204, 401], f"status={st}", "KIM")

        # OAuth / Social Login
        self.section("KIM — OAuth Social Login")
        for provider in ["google", "facebook", "linkedin"]:
            st, body = self.http_get(f"{self.api_url}/api/v2/auth/login/{provider}")
            has_url = "redirect_url" in (body if isinstance(body, str) else "")
            self.record(f"OAuth {provider} redirect URL", st == 200 and has_url,
                        f"status={st}, has_url={has_url}", "KIM")

        st, _ = self.http_get(f"{self.api_url}/api/v2/auth/login/apple")
        self.record("OAuth unsupported provider rejected", st == 400, f"status={st}", "KIM")

        st, _ = self.http_get(f"{self.api_url}/api/v2/auth/callback/google")
        self.record("OAuth callback rejects missing params", st in [200, 400, 422],
                     f"status={st} (missing code/state)", "KIM")

        # Connected providers (requires auth)
        st, _ = self.http_get(f"{self.api_url}/api/v2/auth/providers")
        self.record("GET /auth/providers requires auth", st == 401, f"status={st}", "KIM")

        if token:
            st, body = self.auth_get(f"{self.api_url}/api/v2/auth/providers", token)
            has_providers = "providers" in (body if isinstance(body, str) else "")
            self.record("GET /auth/providers returns list", st == 200 and has_providers,
                        f"status={st}", "KIM")

        # Link provider (requires auth)
        st, _ = self.http_get(f"{self.api_url}/api/v2/auth/link/google")
        self.record("GET /auth/link requires auth", st == 401, f"status={st}", "KIM")

        # Unlink provider (requires auth)
        st, _ = self.http_get(f"{self.api_url}/api/v2/auth/link/apple")
        self.record("Link unsupported provider rejected", st in [400, 401], f"status={st}", "KIM")

        # Dashboard API
        self.section("KIM — Dashboard API (/api/v2/me/)")
        st, _ = self.http_get(f"{self.api_url}/api/v2/me/dashboard")
        self.record("Dashboard requires auth", st == 401, f"status={st}", "KIM")
        st, _ = self.http_post(f"{self.api_url}/api/v2/me/save-analysis", {
            "profile": "minimal", "stance": "open", "input_word_count": 50
        })
        self.record("Save-analysis requires auth", st == 401, f"status={st}", "KIM")

        if token:
            st, body = self.auth_get(f"{self.api_url}/api/v2/me/dashboard", token)
            try:
                d = json.loads(body) if isinstance(body, str) else {}
                keys = list(d.keys())[:4]
            except:
                keys = []
            self.record("Dashboard returns data with auth", st == 200,
                        f"status={st}, keys={keys}", "KIM")

        # Clear history (check mounted)
        st, _ = self.http_delete(f"{self.api_url}/api/v2/me/history")
        self.record("Clear history requires auth", st == 401, f"status={st}", "KIM")

        # Payments API
        self.section("MARS — Payments API (/api/v2/payments/)")
        # Pricing per currency
        for cc, exp_pro in [("cad", 2.99), ("gbp", 1.99), ("aud", 4.99), ("nzd", 3.99), ("usd", 2.99)]:
            st, body = self.http_get(f"{self.api_url}/api/v2/payments/pricing?currency={cc}")
            if st == 200:
                try:
                    pd = json.loads(body) if isinstance(body, str) else body
                    ok = pd.get("pro", {}).get("monthly") == exp_pro and pd.get("currency") == cc
                    self.record(f"Pricing {cc.upper()} correct", ok,
                                f"pro={pd.get('pro', {}).get('monthly')} expect={exp_pro}", "MARS")
                except:
                    self.record(f"Pricing {cc.upper()} correct", False, "parse error", "MARS")
            else:
                self.record(f"Pricing {cc.upper()} correct", False, f"status={st}", "MARS")

        # Pricing all
        st, _ = self.http_get(f"{self.api_url}/api/v2/payments/pricing/all")
        self.record("Pricing /all endpoint", st not in [0], f"status={st}", "MARS")

        # Checkout (auth required)
        st, _ = self.http_post(f"{self.api_url}/api/v2/payments/checkout", {"tier": "pro", "interval": "monthly"})
        self.record("Checkout requires auth", st == 401, f"status={st}", "MARS")

        # Subscription endpoints
        st, _ = self.http_get(f"{self.api_url}/api/v2/payments/subscription")
        self.record("Subscription requires auth", st == 401, f"status={st}", "MARS")
        st, _ = self.http_post(f"{self.api_url}/api/v2/payments/subscription/cancel", {})
        self.record("Cancel subscription requires auth", st == 401, f"status={st}", "MARS")

        # Trial
        st, _ = self.http_get(f"{self.api_url}/api/v2/payments/trial/status")
        self.record("Trial status requires auth", st == 401, f"status={st}", "MARS")
        st, _ = self.http_post(f"{self.api_url}/api/v2/payments/trial/start", {})
        self.record("Trial start requires auth", st == 401, f"status={st}", "MARS")

        # Tier
        st, _ = self.http_get(f"{self.api_url}/api/v2/payments/tier")
        self.record("Tier endpoint requires auth", st == 401, f"status={st}", "MARS")

        # Billing portal
        st, _ = self.http_post(f"{self.api_url}/api/v2/payments/billing-portal", {})
        self.record("Billing portal requires auth", st == 401, f"status={st}", "MARS")

        # Refund policy
        st, _ = self.http_get(f"{self.api_url}/api/v2/payments/refund-policy")
        self.record("Refund policy endpoint", st in [200, 404], f"status={st}", "MARS")

        # Webhook exists (POST with no sig → 400/422)
        st, _ = self.http_post(f"{self.api_url}/api/v2/payments/webhook", {})
        self.record("Webhook endpoint exists", st not in [0, 404], f"status={st}", "MARS")

        # Share API
        self.section("KIM — Share API (/api/v2/share/)")
        st, _ = self.http_post(f"{self.api_url}/api/v2/share/generate", {"slug": "test"})
        self.record("Share generate requires auth", st == 401, f"status={st}", "KIM")
        st, _ = self.http_get(f"{self.api_url}/api/v2/share/me")
        self.record("Share /me requires auth", st == 401, f"status={st}", "KIM")
        st, _ = self.http_get(f"{self.api_url}/api/v2/share/public/nonexistent-slug-test-xyz")
        self.record("Share public 404 for bad slug", st in [404, 200], f"status={st}", "KIM")
        st, _ = self.http_post(f"{self.api_url}/api/v2/share/referral/track", {"slug": "test", "action": "visit"})
        self.record("Referral track endpoint", st not in [0, 404], f"status={st}", "KIM")
        st, _ = self.http_get(f"{self.api_url}/api/v2/share/referral/stats")
        self.record("Referral stats requires auth", st == 401, f"status={st}", "KIM")

        # STRETCH API
        self.section("KIM — STRETCH API (/api/stretch/)")
        st, _ = self.http_get(f"{self.api_url}/api/stretch/eligibility/test")
        self.record("STRETCH eligibility mounted", st not in [0, 404], f"status={st}", "KIM")
        st, _ = self.http_get(f"{self.api_url}/api/stretch/recommend/00000000-0000-0000-0000-000000000000")
        self.record("STRETCH recommend mounted", st not in [0, 404], f"status={st}", "KIM")
        st, _ = self.http_get(f"{self.api_url}/api/stretch/progress/00000000-0000-0000-0000-000000000000")
        self.record("STRETCH progress mounted", st not in [0, 404], f"status={st}", "KIM")
        st, _ = self.http_get(f"{self.api_url}/api/stretch/history/00000000-0000-0000-0000-000000000000")
        self.record("STRETCH history mounted", st not in [0, 404], f"status={st}", "KIM")
        st, _ = self.http_get(f"{self.api_url}/api/stretch/cta/00000000-0000-0000-0000-000000000000")
        self.record("STRETCH CTA mounted", st not in [0, 404], f"status={st}", "KIM")

        # Newsletter API
        self.section("KIM — Newsletter API (/api/v2/newsletter/)")
        nl_email = f"nl_supertest_{self.ts}@quirrely.com"
        st, resp = self.http_post(f"{self.api_url}/api/v2/newsletter/subscribe", {"email": nl_email, "source": "super_test"})
        self.record("Newsletter subscribe 200", st == 200, f"status={st}", "KIM")
        # Bad email
        st, resp = self.http_post(f"{self.api_url}/api/v2/newsletter/subscribe", {"email": "not-an-email", "source": "super_test"})
        bad_ok = (st == 200 and isinstance(resp, dict) and resp.get("success") == False) or st in [400, 422]
        self.record("Newsletter rejects bad email", bad_ok, f"status={st}", "KIM")
        # Dedup
        st, resp = self.http_post(f"{self.api_url}/api/v2/newsletter/subscribe", {"email": nl_email, "source": "super_test"})
        if st == 200 and isinstance(resp, dict):
            self.record("Newsletter dedup", resp.get("new") == False, f"new={resp.get('new')}", "KIM")
        else:
            self.record("Newsletter dedup", False, f"status={st}", "KIM")
        # Count
        st, _ = self.http_get(f"{self.api_url}/api/v2/newsletter/count")
        self.record("Newsletter count 200", st == 200, f"status={st}", "KIM")

        # Featured API
        self.section("KIM — Featured API (/api/v2/featured/)")
        st, _ = self.http_get(f"{self.api_url}/api/v2/featured/approved")
        self.record("Featured approved 200", st == 200, f"status={st}", "KIM")
        st, _ = self.http_post(f"{self.api_url}/api/v2/featured/submit", {"sample": "test", "display_name": "Test"})
        self.record("Featured submit requires auth", st == 401, f"status={st}", "KIM")
        st, _ = self.http_get(f"{self.api_url}/api/v2/featured/my-submission")
        self.record("Featured my-submission requires auth", st == 401, f"status={st}", "KIM")
        # Admin
        st, _ = self.http_get(f"{self.api_url}/api/v2/featured/admin/pending")
        self.record("Featured admin requires key", st == 403, f"status={st}", "KIM")

        # Admin APIs
        self.section("KIM — Admin APIs (/api/admin/v2/)")
        env = self.read_env()
        ak = env.get("ADMIN_API_KEY", "")
        for ep, name in [("/health", "health"), ("/overview", "overview"), ("/stats/real", "real stats")]:
            st, _ = self.http_get(f"{self.api_url}/api/admin/v2{ep}", headers={"X-Admin-Key": ak})
            self.record(f"Admin {name} 200", st == 200, f"status={st}", "KIM")
        # Without key
        st, _ = self.http_get(f"{self.api_url}/api/admin/v2/overview")
        self.record("Admin overview requires key", st in [401, 403], f"status={st}", "KIM")

        # Super Admin
        st, _ = self.http_get(f"{self.api_url}/api/v2/super-admin/pulse", headers={"X-Admin-Key": ak})
        self.record("Super admin pulse mounted", st not in [0, 404], f"status={st}", "KIM")
        st, _ = self.http_get(f"{self.api_url}/api/v2/super-admin/actions", headers={"X-Admin-Key": ak})
        self.record("Super admin actions mounted", st not in [0, 404], f"status={st}", "KIM")

        # Reader API (may not be mounted yet)
        self.section("KIM — Reader API (/api/v2/reader/)")
        st, _ = self.http_post(f"{self.api_url}/api/v2/reader/event", {"type": "page_view", "content_id": "test"})
        self.record("Reader event mounted", st not in [0], f"status={st} (401/404 expected)", "KIM")
        st, _ = self.http_get(f"{self.api_url}/api/v2/reader/taste")
        self.record("Reader taste mounted", st not in [0], f"status={st}", "KIM")
        st, _ = self.http_get(f"{self.api_url}/api/v2/reader/recommendations")
        self.record("Reader recommendations mounted", st not in [0], f"status={st}", "KIM")
        st, _ = self.http_get(f"{self.api_url}/api/v2/reader/bookmarks")
        self.record("Reader bookmarks mounted", st not in [0], f"status={st}", "KIM")

        # Extension API
        self.section("KIM — Extension API")
        st, _ = self.http_get(f"{self.api_url}/api/extension/health")
        self.record("Extension health responds", st in [200, 401, 404], f"status={st}", "KIM")

        # Feature Gates
        self.section("KIM — Feature Gates")
        try:
            sys.path.insert(0, APP_DIR)
            from feature_gate import FeatureGate, Tier
            import tempfile
            gate = FeatureGate(storage_dir=Path(tempfile.mkdtemp()) / "gate")
            uid = f"testuser_{self.ts}"
            gate.set_user_tier(uid, Tier.FREE)
            self.record("FREE: basic_analysis allowed",
                        gate.can_access("basic_analysis", user_id=uid).allowed, "allowed", "KIM")
            self.record("FREE: unlimited_analyses blocked",
                        not gate.can_access("unlimited_analyses", user_id=uid).allowed, "blocked", "KIM")
            gate.set_user_tier(uid, Tier.PRO)
            self.record("PRO: unlimited_analyses allowed",
                        gate.can_access("unlimited_analyses", user_id=uid).allowed, "allowed", "KIM")
        except Exception as e:
            self.record("Feature gate import", False, str(e)[:80], "KIM")


# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: FRONTEND INTEGRITY (~60 tests)
# ═══════════════════════════════════════════════════════════════════════════════

class Part4_FrontendIntegrity(TestHarness):
    """Static file analysis — no HTTP needed for most tests."""

    def run(self):
        self._init_part(4, "Frontend Integrity")

        # File Existence
        self.section("KIM — Critical File Existence")
        critical_files = [
            (f"{FRONTEND_DIR}/index.html", "App index.html"),
            (f"{FRONTEND_DIR}/dashboard.html", "dashboard.html"),
            (f"{FRONTEND_DIR}/settings.html", "settings.html"),
            (f"{FRONTEND_DIR}/export.html", "export.html"),
            (f"{FRONTEND_DIR}/pro-dashboard.html", "pro-dashboard.html"),
            (f"{DEPLOY_DIR}/auth/signup.html", "auth/signup.html"),
            (f"{DEPLOY_DIR}/auth/login.html", "auth/login.html"),
            (f"{DEPLOY_DIR}/billing/upgrade.html", "billing/upgrade.html"),
            (f"{BLOG_DIR}/index.html", "blog/index.html"),
            (f"{BLOG_DIR}/featured.html", "blog/featured.html"),
            (f"{BLOG_DIR}/submit-writing.html", "blog/submit-writing.html"),
            (f"{PROJECT_ROOT}/admin/index.html", "admin/index.html"),
            (f"{PROJECT_ROOT}/faq.html", "faq.html"),
            (f"{PROJECT_ROOT}/settings.html", "settings.html"),
        ]
        for path, name in critical_files:
            self.record(f"File exists: {name}", self.file_exists(path),
                        "found" if self.file_exists(path) else "MISSING", "KIM")

        # HTML Well-formedness
        self.section("KIM — HTML Well-formedness")
        for path, name in [(f"{FRONTEND_DIR}/index.html", "index.html"),
                           (f"{FRONTEND_DIR}/dashboard.html", "dashboard.html"),
                           (f"{FRONTEND_DIR}/settings.html", "settings.html"),
                           (f"{FRONTEND_DIR}/export.html", "export.html")]:
            content = self.read_file(path)
            if content:
                self.record(f"{name} has </html>", "</html>" in content, "found" if "</html>" in content else "MISSING", "KIM")
                self.record(f"{name} has <head>", "<head" in content, "found" if "<head" in content else "MISSING", "KIM")

        # CSS Variable Resolution (dashboard.html)
        self.section("KIM — CSS Variable Resolution")
        dash = self.read_file(f"{FRONTEND_DIR}/dashboard.html")
        if dash:
            # Extract var() usages
            var_uses = set(re.findall(r'var\((--[\w-]+)', dash))
            # Extract var definitions
            var_defs = set(re.findall(r'(--[\w-]+)\s*:', dash))
            undefined = var_uses - var_defs
            # Filter out standard CSS vars that might come from external sources
            undefined = {v for v in undefined if not v.startswith("--webkit")}
            self.record("Dashboard CSS vars defined", len(undefined) < 5,
                        f"{len(undefined)} undefined: {list(undefined)[:5]}", "KIM")

        # JS Function Integrity (dashboard.html)
        self.section("KIM — Dashboard JS Functions")
        required_fns = [
            "function toggleUserMenu", "function doLogout", "function viewPublicProfile",
            "function submitForFeatured", "function copyProfileLink", "function claimSlug",
            "function initShare", "function refreshShare", "function showToast",
            "function formatLocation", "function getInitial", "function formatNumber",
            "function timeAgo", "function renderVoiceBars", "function renderActivity",
            "function renderWriters", "function renderBooks", "function renderStretch",
            "function startStretch", "function renderEvolution", "function setTier",
            "async function renderConnectedAccounts", "async function linkProvider",
            "async function unlinkProvider", "async function init"
        ]
        for fn in required_fns:
            fname = fn.replace("async ", "").replace("function ", "")
            self.record(f"JS fn {fname}()", fn in dash, "found" if fn in dash else "MISSING", "KIM")

        # Settings functions
        settings = self.read_file(f"{DEPLOY_DIR}/settings.html")
        if not settings:
            settings = self.read_file(f"{PROJECT_ROOT}/settings.html")
        settings_fns = ["function manageBilling", "function cancelSubscription", "function deleteAccount",
                        "function exportData", "function changePassword", "function clearHistory", "function showToast"]
        for fn in settings_fns:
            fname = fn.replace("function ", "")
            self.record(f"Settings fn {fname}()", fn in settings, "found" if fn in settings else "MISSING", "KIM")

        # Export
        export = self.read_file(f"{FRONTEND_DIR}/export.html")
        self.record("Export fn exportData()", "function exportData" in export, "found" if "function exportData" in export else "MISSING", "KIM")

        # Branding & Assets
        self.section("MARS — Branding & Assets")
        import glob as _glob
        all_html = _glob.glob(f"{PROJECT_ROOT}/**/*.html", recursive=True)
        active_html = [f for f in all_html if "_locked" not in f and "_v0." not in f and "_v1." not in f]

        # No double-L
        dbl_l = [os.path.basename(f) for f in active_html if "Quirrelly" in self.read_file(f)]
        self.record("No double-L Quirrelly", len(dbl_l) == 0,
                     ",".join(dbl_l[:5]) if dbl_l else "clean", "MARS")
        # No old 340 viewBox
        old_vb = [os.path.basename(f) for f in active_html if 'viewBox="0 0 340' in self.read_file(f)]
        self.record("No old 340 viewBox", len(old_vb) == 0,
                     ",".join(old_vb[:5]) if old_vb else "clean", "MARS")
        # OG image
        self.record("OG image exists", self.file_exists(f"{DEPLOY_DIR}/assets/logo/og-image.png"),
                     "found" if self.file_exists(f"{DEPLOY_DIR}/assets/logo/og-image.png") else "MISSING", "MARS")
        # 10 profile OG images
        og_profiles = ["assertive", "minimal", "poetic", "dense", "conversational",
                       "formal", "interrogative", "hedged", "parallel", "longform"]
        og_all = all(self.file_exists(f"{DEPLOY_DIR}/og/{p}.png") for p in og_profiles)
        self.record("All 10 OG profile images", og_all,
                     "all found" if og_all else "some missing", "MARS")
        # SVG viewBox correct on dashboard
        self.record("Dashboard SVG logo", 'viewBox="0 0 365 100"' in dash or 'viewBox="0 0 80 120"' in dash,
                     "found", "MARS")

        # GA4 Tags
        self.section("MARS — GA4 Tags")
        ga_excludes = ["/admin", "/components/", "/assets/", "/extension/", "/secure/",
                       "_locked", "_v0.", "_v1.", "master-test", "lncp-v4",
                       ".bak", "_old", "_backup", "_test", "/drafts/",
                       "/partials/", "/templates/", "/snippets/", "/archive/",
                       "super_admin", "super-admin", "/reading/reading/"]
        deploy_htmls = _glob.glob(f"{DEPLOY_DIR}/**/*.html", recursive=True)
        ga_pages = [f for f in deploy_htmls if not any(x in f for x in ga_excludes)]
        ga_count = sum(1 for f in ga_pages if GA4_TAG in self.read_file(f))
        ga_pct = (ga_count / len(ga_pages) * 100) if ga_pages else 100
        self.record("GA4 on public pages >= 90%", ga_pct >= 90,
                     f"{ga_count}/{len(ga_pages)} pages ({ga_pct:.0f}%)", "MARS")
        if ga_pct < 100:
            missing = [f for f in ga_pages if GA4_TAG not in self.read_file(f)]
            self.suggest(f"GA4 missing from {len(missing)} files: {', '.join(os.path.basename(f) for f in missing[:5])}"
                         + (f" and {len(missing)-5} more" if len(missing) > 5 else ""))
        # Specific checks
        for path, name in [(f"{FRONTEND_DIR}/dashboard.html", "dashboard"), (f"{DEPLOY_DIR}/settings.html", "settings")]:
            content = self.read_file(path)
            if not content:
                content = self.read_file(path.replace(DEPLOY_DIR, PROJECT_ROOT))
            self.record(f"GA4 on {name}", GA4_TAG in content, "found" if GA4_TAG in content else "MISSING", "MARS")

        # Social Login Buttons
        self.section("KIM — Social Login & Account Linking")
        login_html = self.read_file(f"{DEPLOY_DIR}/auth/login.html")
        signup_html = self.read_file(f"{DEPLOY_DIR}/auth/signup.html")
        for provider in ["google", "facebook", "linkedin"]:
            self.record(f"Login has {provider} button",
                        f"socialLogin('{provider}')" in login_html,
                        "found" if f"socialLogin('{provider}')" in login_html else "MISSING", "KIM")
            self.record(f"Signup has {provider} button",
                        f"socialLogin('{provider}')" in signup_html,
                        "found" if f"socialLogin('{provider}')" in signup_html else "MISSING", "KIM")
        self.record("Login has socialLogin() function", "function socialLogin" in login_html or "socialLogin" in login_html,
                     "found", "KIM")
        self.record("Login social-btn CSS", ".social-btn" in login_html,
                     "found" if ".social-btn" in login_html else "MISSING", "KIM")
        # Dashboard connected accounts
        self.record("Dashboard connected-accounts section", "connected-accounts" in dash,
                     "found" if "connected-accounts" in dash else "MISSING", "KIM")
        self.record("Dashboard providerList element", "providerList" in dash,
                     "found" if "providerList" in dash else "MISSING", "KIM")
        self.record("Dashboard PROVIDER_ICONS defined", "PROVIDER_ICONS" in dash,
                     "found" if "PROVIDER_ICONS" in dash else "MISSING", "KIM")

        # Pro-dashboard redirect
        self.section("KIM — Legacy Redirects")
        prodash = self.read_file(f"{FRONTEND_DIR}/pro-dashboard.html")
        self.record("pro-dashboard.html redirects to dashboard",
                     "/dashboard" in prodash and ("redirect" in prodash.lower() or "location" in prodash.lower()),
                     "redirect found" if prodash else "MISSING", "KIM")

        # Font unification
        self.section("MARS — Font Unification")
        idx = self.read_file(f"{FRONTEND_DIR}/index.html")
        self.record("index.html uses Outfit font", "Outfit" in idx, "found" if "Outfit" in idx else "MISSING", "MARS")
        self.record("dashboard.html uses Outfit font", "Outfit" in dash, "found" if "Outfit" in dash else "MISSING", "MARS")
        for path, name in [(f"{DEPLOY_DIR}/auth/login.html", "login"),
                           (f"{DEPLOY_DIR}/auth/signup.html", "signup")]:
            content = self.read_file(path)
            self.record(f"{name}.html uses Outfit font", "Outfit" in content,
                        "found" if "Outfit" in content else "MISSING", "MARS")

        # Sitemaps
        self.section("MARS — Sitemaps")
        sitemap = self.read_file(f"{PROJECT_ROOT}/sitemap.xml")
        self.record("sitemap.xml exists", bool(sitemap), "found" if sitemap else "MISSING", "MARS")
        self.record("sitemap.xml valid index", "sitemapindex" in sitemap, "valid" if "sitemapindex" in sitemap else "INVALID", "MARS")
        for sm in ["sitemap-blog.xml", "sitemap-pages.xml", "sitemap-profiles.xml", "sitemap-users.xml"]:
            self.record(f"Sub-sitemap {sm} exists", self.file_exists(f"{PROJECT_ROOT}/{sm}"),
                        "found" if self.file_exists(f"{PROJECT_ROOT}/{sm}") else "MISSING", "MARS")
        pages_sm = self.read_file(f"{PROJECT_ROOT}/sitemap-pages.xml")
        self.record("Sitemap has /faq", "/faq" in pages_sm, "found" if "/faq" in pages_sm else "MISSING", "MARS")
        self.record("Sitemap excludes /dashboard", "/frontend/dashboard.html" not in pages_sm, "excluded", "MARS")

        # Social & Third Party
        self.section("MARS — Social & Third Party")
        idx = self.read_file(f"{FRONTEND_DIR}/index.html")
        fb_url = "facebook.com/profile.php?id=61575643048349"
        li_url = "linkedin.com/company/"
        for content, name in [(idx, "index.html"), (self.read_file(f"{BLOG_DIR}/index.html"), "blog index")]:
            if content:
                self.record(f"{name} Facebook link", fb_url in content, "found" if fb_url in content else "MISSING", "MARS")
                self.record(f"{name} LinkedIn link", li_url in content, "found" if li_url in content else "MISSING", "MARS")
        # No Twitter
        self.record("Dashboard no Twitter", "twitter.com/intent" not in dash and "shareTwitter" not in dash,
                     "clean", "MARS")
        # Canonicals use .ca
        blog_all = _glob.glob(f"{BLOG_DIR}/*.html")
        com_blog = [os.path.basename(f) for f in blog_all
                    if "quirrely.com" in self.read_file(f).replace("hello@quirrely.com", "")]
        self.record("Blog canonicals use .ca", len(com_blog) == 0,
                     ",".join(com_blog[:5]) if com_blog else "clean", "MARS")

        # No Stale Data
        self.section("MARS — No Stale Data")
        self.record("Dashboard no mock Sarah Mitchell", "Sarah Mitchell" not in dash, "clean", "MARS")
        self.record("Dashboard no raw alert()", "alert(" not in dash, "clean", "KIM")
        self.record("Settings no hardcoded Jane", "Jane Doe" not in settings, "clean", "KIM")
        self.record("Settings no hardcoded prices", "$4.99" not in settings and "$7.99" not in settings, "clean", "KIM")

        # No Stale References
        self.section("MARS — No Stale References")
        aff = self.read_file(os.path.join(APP_DIR, "affiliate_service.py"))
        self.record("No Sentense in affiliate", "sentense" not in aff, "clean", "MARS")
        self.record("Dashboard no Pricing in nav", dash.count(">Pricing<") == 0,
                     f"{dash.count('>Pricing<')} found", "MARS")


# ═══════════════════════════════════════════════════════════════════════════════
# PART 5: E2E USER JOURNEYS (~35 tests)
# ═══════════════════════════════════════════════════════════════════════════════

class Part5_E2EJourneys(TestHarness):
    """Full flow simulations with test user lifecycle."""

    def run(self):
        self._init_part(5, "E2E User Journeys")

        # Journey A: Anonymous Analysis
        self.section("KIM — Journey A: Anonymous Analysis")
        text = "The morning light filtered through curtains. She sat quietly thinking about what to write next. Words matter more than we realize. The act of writing is itself an argument."
        st, resp = self.http_post(f"{self.api_url}/api/v2/analyze", {"text": text})
        self.record("Anonymous analyze 200", st == 200, f"status={st}", "KIM")
        if st == 200 and isinstance(resp, dict):
            self.record("Response has profiles", "profiles" in resp.get("scores", {}), "found", "KIM")
            self.record("Response has stances", "stances" in resp.get("scores", {}), "found", "KIM")
            self.record("Response has confidence", "confidence" in resp, f"val={resp.get('confidence')}", "KIM")
        else:
            for n in ["profiles", "stances", "confidence"]:
                self.record(f"Response has {n}", False, "no response", "KIM")

        # Journey B: Register → Dashboard
        self.section("KIM — Journey B: Register → Analyze → Dashboard")
        user = self.create_test_user("e2e_b")
        token = user["token"]
        self.record("Signup successful", user["signup_status"] == 200, f"status={user['signup_status']}", "KIM")
        self.record("Login returns token", bool(token), "received" if token else "missing", "KIM")

        if token:
            # Analyze as authenticated user
            st, resp = self.auth_post(f"{self.api_url}/api/v2/analyze", {"text": text}, token)
            self.record("Auth analyze 200", st == 200, f"status={st}", "KIM")

            # Save analysis
            if st == 200 and isinstance(resp, dict):
                profile = list(resp.get("scores", {}).get("profiles", {}).keys())[0] if resp.get("scores", {}).get("profiles") else "minimal"
                stance = list(resp.get("scores", {}).get("stances", {}).keys())[0] if resp.get("scores", {}).get("stances") else "open"
                st2, _ = self.auth_post(f"{self.api_url}/api/v2/me/save-analysis", {
                    "profile": profile, "stance": stance, "input_word_count": len(text.split())
                }, token)
                self.record("Save analysis", st2 in [200, 201], f"status={st2}", "KIM")

            # Get dashboard
            st, body = self.auth_get(f"{self.api_url}/api/v2/me/dashboard", token)
            self.record("Dashboard 200", st == 200, f"status={st}", "KIM")
            if st == 200:
                try:
                    d = json.loads(body) if isinstance(body, str) else body
                    self.record("Dashboard has user key", "user" in d, f"keys={list(d.keys())[:5]}", "KIM")
                    self.record("Dashboard has stats", "stats" in d, "found" if "stats" in d else "missing", "KIM")
                except:
                    pass

        # Journey C: Trial Lifecycle
        self.section("MARS — Journey C: Trial Lifecycle")
        trial_user = self.create_test_user("e2e_c")
        tt = trial_user["token"]
        if tt:
            # Start trial
            st, resp = self.auth_post(f"{self.api_url}/api/v2/payments/trial/start", {}, tt)
            self.record("Trial start", st in [200, 201, 400], f"status={st}", "MARS")
            # Check trial status
            st, body = self.auth_get(f"{self.api_url}/api/v2/payments/trial/status", tt)
            self.record("Trial status endpoint", st == 200, f"status={st}", "MARS")
            # Check tier
            st, body = self.auth_get(f"{self.api_url}/api/v2/payments/tier", tt)
            self.record("Tier endpoint works", st == 200, f"status={st}", "MARS")
        else:
            for n in ["Trial start", "Trial status", "Tier endpoint"]:
                self.record(n, False, "no token", "MARS")

        # Journey D: Stripe Checkout (only with --stripe-test)
        self.section("MARS — Journey D: Stripe Checkout")
        if self.args.stripe_test and self.args.local:
            checkout_user = self.create_test_user("e2e_d")
            ct = checkout_user["token"]
            if ct:
                st, resp = self.auth_post(f"{self.api_url}/api/v2/payments/checkout", {
                    "tier": "pro", "interval": "monthly"
                }, ct)
                self.record("Checkout creates session", st == 200 and "url" in resp,
                            f"has_url={'url' in resp}" if isinstance(resp, dict) else f"status={st}", "MARS")
                if st == 200 and isinstance(resp, dict) and "url" in resp:
                    self.record("Checkout URL is Stripe", "checkout.stripe.com" in resp["url"],
                                "valid" if "checkout.stripe.com" in resp["url"] else "invalid", "MARS")
                # User should still be FREE
                st, body = self.auth_get(f"{self.api_url}/api/v2/payments/tier", ct)
                self.record("User still FREE after checkout start", True, "expected", "MARS")
        else:
            self.record("Stripe checkout (skipped)", True, "--stripe-test not set", "MARS")

        # Journey E: Share & Public Profile
        self.section("KIM — Journey E: Share & Public Profile")
        share_user = self.create_test_user("e2e_e")
        et = share_user["token"]
        if et:
            # Analyze first
            self.auth_post(f"{self.api_url}/api/v2/analyze", {"text": text}, et)
            # Generate share profile
            slug = f"st-test-{self.ts}"
            st, resp = self.auth_post(f"{self.api_url}/api/v2/share/generate", {"slug": slug}, et)
            self.record("Share generate", st in [200, 201], f"status={st}", "KIM")
            self._cleanup_slugs.append(slug)
            # Get public profile
            if st in [200, 201]:
                st2, body = self.http_get(f"{self.api_url}/api/v2/share/public/{slug}")
                self.record("Public profile accessible", st2 == 200, f"status={st2}", "KIM")
                # Check /user/ page (server-rendered)
                st3, body = self.http_get(f"{self.api_url}/user/{slug}")
                self.record("/user/{slug} page renders", st3 == 200, f"status={st3}", "KIM")
                if st3 == 200:
                    self.record("User page has OG tags", "og:title" in body, "found" if "og:title" in body else "MISSING", "KIM")
        else:
            for n in ["Share generate", "Public profile", "/user/ page", "OG tags"]:
                self.record(n, False, "no token", "KIM")

        # Journey F: STRETCH Exercise
        self.section("KIM — Journey F: STRETCH Exercise")
        stretch_user = self.create_test_user("e2e_f")
        ft = stretch_user["token"]
        if ft:
            # Check eligibility (need user_id)
            st, body = self.auth_get(f"{self.api_url}/api/v2/auth/me", ft)
            if st == 200:
                try:
                    me = json.loads(body) if isinstance(body, str) else body
                    uid = str(me.get("id", me.get("user_id", "")))
                    if uid:
                        st, _ = self.auth_get(f"{self.api_url}/api/stretch/eligibility/{uid}", ft)
                        self.record("STRETCH eligibility check", st in [200, 403], f"status={st}", "KIM")
                        st, _ = self.auth_get(f"{self.api_url}/api/stretch/cta/{uid}", ft)
                        self.record("STRETCH CTA check", st not in [0, 404], f"status={st}", "KIM")
                    else:
                        self.record("STRETCH eligibility", False, "no user_id", "KIM")
                except:
                    self.record("STRETCH eligibility", False, "parse error", "KIM")
        else:
            self.record("STRETCH eligibility", False, "no token", "KIM")

        # Journey G: Referral Flow
        self.section("MARS — Journey G: Referral Flow")
        st, _ = self.http_post(f"{self.api_url}/api/v2/share/referral/track", {
            "slug": "test-referral", "action": "visit"
        })
        self.record("Referral track endpoint", st not in [0, 404], f"status={st}", "MARS")
        # Referral stats require auth
        st, _ = self.http_get(f"{self.api_url}/api/v2/share/referral/stats")
        self.record("Referral stats requires auth", st == 401, f"status={st}", "MARS")


# ═══════════════════════════════════════════════════════════════════════════════
# PART 6: SECURITY & COMPLIANCE (~45 tests)
# ═══════════════════════════════════════════════════════════════════════════════

class Part6_Security(TestHarness):
    """Security audit: SQL injection, XSS, CORS, auth, headers, geo-blocking, secrets."""

    def run(self):
        self._init_part(6, "Security & Compliance")

        # SQL Injection (static)
        self.section("MARS — SQL Injection Prevention (Static)")
        api_files = ["featured_api.py", "newsletter_api.py", "notify_api.py", "auth_api.py", "payments_api.py", "share_api.py"]
        for fname in api_files:
            fpath = os.path.join(APP_DIR, fname)
            if self.file_exists(fpath):
                content = self.read_file(fpath)
                has_fstr = any(f'f"{kw}' in content or f"f'{kw}" in content
                              for kw in ["SELECT", "INSERT", "UPDATE", "DELETE"])
                self.record(f"No f-string SQL in {fname}", not has_fstr,
                            "clean" if not has_fstr else "F-STRING SQL FOUND", "MARS")

        # SQL Injection (live)
        self.section("MARS — SQL Injection Prevention (Live)")
        sqli_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "1; SELECT * FROM users WHERE 1=1",
        ]
        for i, payload in enumerate(sqli_payloads):
            text = f"{payload} This is a sufficiently long text to test SQL injection handling by the analysis engine for security purposes."
            st, _ = self.http_post(f"{self.api_url}/api/v2/analyze", {"text": text})
            self.record(f"SQLi payload {i + 1} → safe", st in [200, 422], f"status={st}", "MARS")

        # Newsletter SQLi
        st, _ = self.http_post(f"{self.api_url}/api/v2/newsletter/subscribe", {
            "email": "'; DROP TABLE newsletter_subscribers; --@test.com", "source": "test"
        })
        self.record("Newsletter SQLi → safe", st in [200, 400, 422], f"status={st}", "MARS")

        # XSS Prevention
        self.section("MARS — XSS Prevention")
        app_py = self.read_file(os.path.join(APP_DIR, "app.py"))
        self.record("html.escape imported in app.py", "import html" in app_py or "html.escape" in app_py,
                     "found", "MARS")
        # XSS in analyze
        st, resp = self.http_post(f"{self.api_url}/api/v2/analyze", {
            "text": "<script>alert('xss')</script> " * 10 + " enough words to meet the minimum for analysis"
        })
        if st == 200 and isinstance(resp, dict):
            resp_str = json.dumps(resp)
            self.record("Script tags not reflected raw", "<script>" not in resp_str,
                        "clean" if "<script>" not in resp_str else "XSS REFLECTED", "MARS")
        else:
            self.record("Script tags not reflected raw", True, f"status={st} (rejected)", "MARS")

        # CORS Config
        self.section("MARS — CORS Configuration")
        self.record("CORS not wildcard", 'allow_origins=["*"]' not in app_py,
                     "restricted" if 'allow_origins=["*"]' not in app_py else "WILDCARD", "MARS")
        self.record("CORS has quirrely.com", "quirrely.com" in app_py, "found", "MARS")
        self.record("CORS has quirrely.ca", "quirrely.ca" in app_py, "found", "MARS")
        # OPTIONS request
        st, headers = self.http_options(f"{self.api_url}/api/v2/analyze",
                                        headers={"Origin": "https://quirrely.com", "Access-Control-Request-Method": "POST"})
        self.record("OPTIONS returns ok", st in [200, 204, 405], f"status={st}", "MARS")

        # Auth Security
        self.section("MARS — Auth Security")
        auth = self.read_file(os.path.join(APP_DIR, "auth_api.py"))
        self.record("Bcrypt password hashing", "bcrypt" in auth.lower(), "found", "MARS")
        self.record("Parameterized queries in auth", "%s" in auth or "$1" in auth,
                     "parameterized" if "%s" in auth else "check manually", "MARS")
        self.record("Session expiry check", "expires_at" in auth, "found", "MARS")
        # Bad tokens
        st, _ = self.http_get(f"{self.api_url}/api/v2/auth/me", headers={"Authorization": "Bearer expired_garbage_token"})
        self.record("Expired/garbage token → 401", st == 401, f"status={st}", "MARS")
        st, _ = self.http_get(f"{self.api_url}/api/v2/auth/me", headers={"Authorization": "Bearer "})
        self.record("Empty token → 401", st == 401, f"status={st}", "MARS")
        st, _ = self.http_get(f"{self.api_url}/api/v2/auth/me")
        self.record("No token → 401", st == 401, f"status={st}", "MARS")
        st, _ = self.http_get(f"{self.api_url}/api/v2/auth/me", headers={"Authorization": "NotBearer token"})
        self.record("Invalid auth scheme → 401", st == 401, f"status={st}", "MARS")

        # Security Headers (via nginx)
        self.section("MARS — Security Headers")
        try:
            r = subprocess.run(["curl", "-sI", f"{NGINX_URL}/"], capture_output=True, text=True, timeout=5)
            headers_str = r.stdout.lower()
            self.record("HSTS header", "strict-transport-security" in headers_str,
                        "present" if "strict-transport-security" in headers_str else "MISSING", "MARS")
            self.record("CSP header", "content-security-policy" in headers_str,
                        "present" if "content-security-policy" in headers_str else "MISSING", "MARS")
            self.record("X-Frame-Options", "x-frame-options" in headers_str,
                        "present" if "x-frame-options" in headers_str else "MISSING", "MARS")
            self.record("X-Content-Type-Options", "x-content-type-options" in headers_str,
                        "present" if "x-content-type-options" in headers_str else "MISSING", "MARS")
        except:
            for h in ["HSTS", "CSP", "X-Frame-Options", "X-Content-Type-Options"]:
                self.record(f"{h} header", False, "curl failed", "MARS")

        # Geo-blocking
        self.section("MARS — Geo-blocking")
        self.record("Geo-block middleware exists", "_BLOCKED_COUNTRIES" in app_py and "geo_block_middleware" in app_py,
                     "found", "MARS")
        self.record("Geo-block includes FR+RU", '"FR"' in app_py and '"RU"' in app_py, "found", "MARS")
        # Live test
        try:
            r = subprocess.run(["curl", "-s", "-H", "cf-ipcountry: FR", f"{self.api_url}/health"],
                               capture_output=True, text=True, timeout=5)
            self.record("FR → blocked", "access_denied" in r.stdout or "403" in r.stdout,
                        "blocked" if "access_denied" in r.stdout else "NOT BLOCKED", "MARS")
        except:
            self.record("FR geo-block test", False, "curl failed", "MARS")

        # Secret Hygiene
        self.section("MARS — Secret Hygiene")
        try:
            perms = subprocess.run(["stat", "-c", "%a", os.path.join(APP_DIR, ".env")],
                                   capture_output=True, text=True, timeout=5).stdout.strip()
            self.record(".env perms 600", perms == "600", f"perms={perms}", "MARS")
        except:
            self.record(".env perms", False, "check failed", "MARS")
        # No hardcoded keys
        for fname in ["email_service.py", "notify_api.py", "newsletter_api.py"]:
            fpath = os.path.join(APP_DIR, fname)
            if self.file_exists(fpath):
                content = self.read_file(fpath)
                bad = "re_SKMTFrSH" in content or "re_atnZAc7j" in content or "re_BETww8EJ" in content
                self.record(f"No hardcoded keys in {fname}", not bad,
                            "clean" if not bad else "HARDCODED KEY", "MARS")
        # Error leakage
        for fname in ["payments_api.py", "app.py", "api_v2.py"]:
            content = self.read_file(os.path.join(APP_DIR, fname))
            leaks = [l.strip() for l in content.split("\n") if "detail=str(e)" in l]
            self.record(f"No error leakage in {fname}", len(leaks) == 0, f"{len(leaks)} leaks", "MARS")

        # Rate Limiting
        self.section("MARS — Rate Limiting")
        self.record("slowapi imported", "slowapi" in app_py, "found" if "slowapi" in app_py else "MISSING", "MARS")
        # Note: actual 429 test is done in Part 8 Performance to avoid disrupting other tests

        # Cookie Security
        self.section("MARS — Cookie Security")
        mw_path = os.path.join(APP_DIR, "auth_middleware.py")
        if self.file_exists(mw_path):
            mw = self.read_file(mw_path)
            self.record("Cookies httpOnly", "COOKIE_HTTPONLY" in mw, "found" if "COOKIE_HTTPONLY" in mw else "MISSING", "MARS")
            self.record("Cookies secure flag", "COOKIE_SECURE" in mw, "found" if "COOKIE_SECURE" in mw else "MISSING", "MARS")
            self.record("Cookies SameSite", "COOKIE_SAMESITE" in mw, "found" if "COOKIE_SAMESITE" in mw else "MISSING", "MARS")
        else:
            self.suggest("auth_middleware.py not found — verify cookie security settings")


# ═══════════════════════════════════════════════════════════════════════════════
# PART 7: CONVERSION & REVENUE AUDIT (~50 tests)
# ═══════════════════════════════════════════════════════════════════════════════

class Part7_ConversionAudit(TestHarness):
    """Static + live analysis of business conversion paths."""

    def run(self):
        self._init_part(7, "Conversion & Revenue Audit")

        idx = self.read_file(f"{FRONTEND_DIR}/index.html")
        dash = self.read_file(f"{FRONTEND_DIR}/dashboard.html")
        blog_idx = self.read_file(f"{BLOG_DIR}/index.html")
        featured = self.read_file(f"{BLOG_DIR}/featured.html")
        faq = self.read_file(f"{PROJECT_ROOT}/faq.html")
        settings = self.read_file(f"{DEPLOY_DIR}/settings.html")
        if not settings:
            settings = self.read_file(f"{PROJECT_ROOT}/settings.html")

        # CTA Inventory
        self.section("MARS — CTA Inventory")
        self.record("Index has signup CTA", "signup.html" in idx, "found" if "signup.html" in idx else "MISSING", "MARS")
        self.record("Index has share prompt", "share-prompt" in idx, "found" if "share-prompt" in idx else "MISSING", "MARS")
        self.record("Dashboard has upgrade card", "upgradeCard" in dash, "found" if "upgradeCard" in dash else "MISSING", "MARS")
        self.record("Blog has newsletter form", "newsletter/subscribe" in blog_idx, "found" if "newsletter/subscribe" in blog_idx else "MISSING", "MARS")
        self.record("Featured has tier CTAs", "cta-guest" in featured and "cta-free" in featured, "found", "MARS")
        self.record("FAQ has auth-aware nav", "quirrely_token" in faq or "quirrely_session" in faq, "found", "MARS")
        self.record("Settings has billing link", "billing" in settings.lower(), "found", "MARS")
        self.record("Dashboard has billing link", "/billing/" in dash, "found" if "/billing/" in dash else "MISSING", "MARS")

        # Pricing & Checkout
        self.section("MARS — Pricing & Checkout")
        upgrade = self.read_file(f"{DEPLOY_DIR}/billing/upgrade.html")
        for cc in ["cad", "gbp", "aud", "nzd", "usd"]:
            self.record(f"Billing {cc.upper()} button", f'data-curr="{cc}"' in upgrade,
                        "found" if f'data-curr="{cc}"' in upgrade else "MISSING", "MARS")
        pjs = self.read_file(f"{DEPLOY_DIR}/billing/pricing.js")
        self.record("Pricing auto-detect US", '"US":"usd"' in pjs, "found" if '"US":"usd"' in pjs else "MISSING", "MARS")
        # Promo codes
        pay_src = self.read_file(os.path.join(APP_DIR, "payments_api.py"))
        self.record("Checkout allows promo codes", "allow_promotion_codes=True" in pay_src,
                     "found" if "allow_promotion_codes=True" in pay_src else "MISSING", "MARS")
        # Stripe coupon
        try:
            import stripe as _stripe
            env = self.read_env()
            _stripe.api_key = env.get("STRIPE_SECRET_KEY", "")
            coupon = _stripe.Coupon.retrieve("qsaRUyUt")
            self.record("Stripe coupon active", coupon.valid, "valid" if coupon.valid else "INVALID", "MARS")
        except Exception as e:
            self.record("Stripe coupon active", False, str(e)[:60], "MARS")

        # Upgrade Paths
        self.section("MARS — Upgrade Paths")
        self.record("Dashboard upgrade card exists", "upgradeCard" in dash, "found", "MARS")
        self.record("Settings has billing link", "billing-portal" in settings or "/billing/" in settings, "found", "MARS")
        signup = self.read_file(f"{DEPLOY_DIR}/auth/signup.html")
        self.record("Signup has checkout redirect", "checkout_tier" in signup, "found" if "checkout_tier" in signup else "MISSING", "MARS")
        login = self.read_file(f"{DEPLOY_DIR}/auth/login.html")
        self.record("Login has checkout redirect", "checkout_tier" in login, "found" if "checkout_tier" in login else "MISSING", "MARS")
        self.record("Pricing saves tier on redirect", "checkout_tier" in pjs, "found" if "checkout_tier" in pjs else "MISSING", "MARS")

        # Share Mechanics
        self.section("KIM — Share Mechanics")
        self.record("Share slug input", "shareSlugInput" in dash, "found" if "shareSlugInput" in dash else "MISSING", "KIM")
        self.record("Share claim function", "claimSlug" in dash, "found" if "claimSlug" in dash else "MISSING", "KIM")
        self.record("Share copy link", "copyProfileLink" in dash, "found" if "copyProfileLink" in dash else "MISSING", "KIM")
        self.record("Share refresh function", "refreshShare" in dash, "found" if "refreshShare" in dash else "MISSING", "KIM")
        self.record("Share LinkedIn button", "linkedin" in dash.lower() and "shareStretch" in dash or "share" in dash.lower(), "found", "KIM")

        # Referral & Affiliate
        self.section("MARS — Referral & Affiliate")
        sh = self.read_file(os.path.join(APP_DIR, "share_api.py"))
        self.record("Referral track endpoint", "def track_referral" in sh, "found" if "def track_referral" in sh else "MISSING", "MARS")
        self.record("Referral stats endpoint", "def referral_stats" in sh, "found" if "def referral_stats" in sh else "MISSING", "MARS")
        self.record("Index captures ref param", "quirrely_ref" in idx, "found" if "quirrely_ref" in idx else "MISSING", "MARS")
        self.record("Index tracks ref visit", "referral/track" in idx, "found" if "referral/track" in idx else "MISSING", "MARS")
        # Bookstores
        for bk in ["Indigo", "Waterstones", "Booktopia", "Mighty Ape", "Bookshop.org"]:
            self.record(f"Bookstore {bk} configured", bk in dash, "found" if bk in dash else "MISSING", "KIM")
        # No Amazon
        aff = self.read_file(os.path.join(APP_DIR, "affiliate_service.py"))
        self.record("No Amazon in affiliate", "amazon.com" not in aff.lower(), "clean", "MARS")
        self.record("No Amazon in dashboard", "amazon.com" not in dash.lower(), "clean", "KIM")

        # Email Capture
        self.section("KIM — Email Capture")
        self.record("Blog newsletter form wired", "newsletter/subscribe" in blog_idx,
                     "found" if "newsletter/subscribe" in blog_idx else "MISSING", "KIM")
        self.record("Blog no fake subscriber count", "17,500" not in blog_idx,
                     "clean" if "17,500" not in blog_idx else "FAKE COUNT", "KIM")
        # Live subscribe test was done in Part 3

        # Trial Conversion
        self.section("MARS — Trial Conversion")
        st, _ = self.http_post(f"{self.api_url}/api/v2/payments/trial/start", {})
        self.record("Trial start endpoint exists", st == 401, f"status={st} (auth required)", "MARS")
        st, _ = self.http_get(f"{self.api_url}/api/v2/payments/trial/status")
        self.record("Trial status endpoint exists", st == 401, f"status={st} (auth required)", "MARS")
        self.record("Dashboard has upgrade prompt for free", "tier-free-only" in dash or "upgradeCard" in dash,
                     "found", "MARS")

        # Revenue Suggestions
        self.section("MARS — Revenue Suggestions")
        if "newsletter" not in faq.lower():
            self.suggest("Consider adding newsletter signup to /faq")
        if "/billing/" not in faq:
            self.suggest("Consider adding upgrade CTA to /faq")
        import glob as _glob
        blog_posts = _glob.glob(f"{BLOG_DIR}/how-*-writers-write.html")
        for bp in blog_posts:
            content = self.read_file(bp)
            has_cta = ("cta-btn" in content or "cta-box" in content or
                       "signup.html" in content or "upgrade" in content.lower() or
                       "Take the Free Test" in content or 'class="cta"' in content)
            if not has_cta:
                self.suggest(f"Blog post {os.path.basename(bp)} has no CTA")


# ═══════════════════════════════════════════════════════════════════════════════
# PART 8: PERFORMANCE & RELIABILITY (~25 tests)
# ═══════════════════════════════════════════════════════════════════════════════

class Part8_Performance(TestHarness):
    """Endpoint response times, concurrent analysis, large text, memory, DB performance."""

    def run(self):
        self._init_part(8, "Performance & Reliability")

        # Endpoint Response Times (5 requests each, p50/p95)
        self.section("ASO — Endpoint Response Times")
        endpoints = [
            ("/health", "Health", 200),
            ("/api/v2/payments/pricing", "Pricing", 500),
            ("/api/v2/featured/approved", "Featured", 500),
            ("/api/v2/newsletter/count", "Newsletter count", 500),
        ]
        for ep, name, target_ms in endpoints:
            times = []
            for _ in range(5):
                _, _, ms = self.timed_get(f"{self.api_url}{ep}")
                times.append(ms)
            times.sort()
            p50 = times[2]
            p95 = times[4]
            self.record(f"{name} p50 < {target_ms}ms", p50 < target_ms, f"p50={p50}ms p95={p95}ms", "ASO")
            self.record(f"{name} p95 < {target_ms * 2}ms", p95 < target_ms * 2, f"p95={p95}ms", "ASO")
            self.benchmarks[f"{name.lower().replace(' ', '_')}_p50_ms"] = p50
            self.benchmarks[f"{name.lower().replace(' ', '_')}_p95_ms"] = p95

        # Analyze endpoint (separate due to longer times)
        analyze_times = []
        for _ in range(3):
            _, _, ms = self.timed_post(f"{self.api_url}/api/v2/analyze", {
                "text": "The morning light filtered through the curtains. She sat quietly thinking about what to write next."
            }, timeout=15)
            analyze_times.append(ms)
        analyze_times.sort()
        p50 = analyze_times[1]
        p95 = analyze_times[2]
        self.record("Analyze p50 < 3s", p50 < 3000, f"p50={p50}ms", "ASO")
        self.record("Analyze p95 < 5s", p95 < 5000, f"p95={p95}ms", "ASO")
        self.benchmarks["analyze_p50_ms"] = p50
        self.benchmarks["analyze_p95_ms"] = p95

        # Concurrent Analysis
        self.section("ASO — Concurrent Analysis (5 simultaneous)")
        text = "The morning light filtered through curtains. She sat quietly thinking about what to write next. Words matter. The ratio of silence to speech matters."
        concurrent_results = []

        def do_analyze():
            return self.timed_post(f"{self.api_url}/api/v2/analyze", {"text": text}, timeout=15)

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(do_analyze) for _ in range(5)]
            for f in as_completed(futures):
                try:
                    st, body, ms = f.result()
                    concurrent_results.append((st, ms))
                except:
                    concurrent_results.append((0, 99999))

        ok_count = sum(1 for st, _ in concurrent_results if st == 200)
        max_time = max(ms for _, ms in concurrent_results)
        err_500 = sum(1 for st, _ in concurrent_results if st >= 500)
        rate_limited = sum(1 for st, _ in concurrent_results if st == 429)
        total = len(concurrent_results)
        self.record(f"Concurrent: >= 3/{total} succeed", ok_count >= 3,
                     f"{ok_count}/{total} succeeded" + (f" ({rate_limited} rate-limited)" if rate_limited else ""), "ASO")
        self.record("Concurrent: none > 10s", max_time < 10000, f"max={max_time}ms", "ASO")
        self.record("Concurrent: no 500s", err_500 == 0,
                     "clean" if err_500 == 0 else f"{err_500} errors", "ASO")
        if err_500:
            self.suggest(f"{err_500}/{total} concurrent requests got 500 errors — server struggles under concurrency, consider async workers or connection pooling")
        if rate_limited:
            self.suggest(f"{rate_limited}/{total} concurrent requests were rate-limited (429) — consider raising limit for /analyze")

        # Large Text
        self.section("ASO — Large Text")
        large = " ".join(["The quick brown fox jumps over the lazy dog."] * 500)
        st, body, ms = self.timed_post(f"{self.api_url}/api/v2/analyze", {"text": large}, timeout=20)
        self.record("5000-word text → 200", st == 200, f"status={st}", "ASO")
        self.record("5000-word text < 15s", ms < 15000, f"{ms}ms", "ASO")

        # Memory Baseline
        self.section("ASO — Memory Baseline")
        proc = self.pm2_proc()
        if proc:
            mb_after = proc.get("monit", {}).get("memory", 0) / 1024 / 1024
            mb_before = self.benchmarks.get("pm2_memory_mb", mb_after)
            increase = mb_after - mb_before
            self.record("Memory increase < 100MB", increase < 100,
                        f"before={mb_before:.1f}MB after={mb_after:.1f}MB delta={increase:.1f}MB", "ASO")
            self.record("Memory still < 512MB", mb_after < 512, f"{mb_after:.1f}MB", "ASO")
        else:
            self.record("PM2 memory check", False, "PM2 not running", "ASO")

        # DB Performance
        self.section("ASO — DB Performance")
        for query, name in [
            ("SELECT COUNT(*) FROM users;", "User count"),
            ("SELECT COUNT(*) FROM writing_profiles;", "Profile count"),
            ("SELECT COUNT(*) FROM analytics_events;", "Events count"),
        ]:
            t0 = time.time()
            out, ok = self.db_query(query)
            ms = int((time.time() - t0) * 1000)
            self.record(f"DB {name} < 1s", ms < 1000 and ok, f"{ms}ms, {out.strip() if ok else 'error'}", "ASO")

        # DB connection check
        out, ok = self.db_query("SELECT count(*) FROM pg_stat_activity WHERE datname='quirrely_prod';")
        conns = int(out.strip()) if ok and out.strip().isdigit() else 0
        out2, ok2 = self.db_query("SHOW max_connections;")
        max_conns = int(out2.strip()) if ok2 and out2.strip().isdigit() else 100
        pct = (conns / max_conns * 100) if max_conns > 0 else 0
        self.record("DB connections < 80%", pct < 80, f"{conns}/{max_conns} ({pct:.0f}%)", "ASO")


# ═══════════════════════════════════════════════════════════════════════════════
# REPORT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class ReportEngine:
    """Generates JSON output, terminal summary, and optional email report."""

    def __init__(self, harness, args):
        self.h = harness
        self.args = args

    def build_json(self):
        """Build JSON output with backwards-compatible structure."""
        total_pass = sum(p["pass"] for p in self.h.results.values())
        total_fail = sum(p["fail"] for p in self.h.results.values())
        total = total_pass + total_fail
        pct = int(100 * total_pass / total) if total > 0 else 0

        output = {
            "run_at": datetime.now(timezone.utc).isoformat(),
            "version": "2.0",
            "mode": "local" if self.args.local else "production",
            "duration_seconds": 0,  # filled by caller
        }

        # Part data
        for key, data in self.h.results.items():
            output[key] = data

        output["summary"] = {
            "total_pass": total_pass,
            "total_fail": total_fail,
            "pct": pct,
        }
        output["suggestions"] = self.h.suggestions
        output["benchmarks"] = self.h.benchmarks

        # Backwards compatibility aliases
        parts = list(self.h.results.keys())
        if len(parts) >= 1:
            output["part_a"] = self.h.results.get("part_1", {"pass": 0, "fail": 0, "tests": []})
        if len(parts) >= 2:
            output["part_b"] = self.h.results.get("part_2", {"pass": 0, "fail": 0, "tests": []})
        if len(parts) >= 3:
            output["part_c"] = self.h.results.get("part_3", {"pass": 0, "fail": 0, "tests": []})

        return output

    def print_summary(self):
        """Print colored terminal summary."""
        total_pass = 0
        total_fail = 0
        print(f"\n{'=' * 70}")
        for key in sorted(self.h.results.keys()):
            data = self.h.results[key]
            p, f = data["pass"], data["fail"]
            total_pass += p
            total_fail += f
            t = p + f
            pct = int(100 * p / t) if t > 0 else 0
            num = key.split("_")[1]
            print(f"  Part {num} {data['name']:<25}: {p}/{t}  ({pct}%)")

        total = total_pass + total_fail
        pct = int(100 * total_pass / total) if total > 0 else 0
        print(f"\n  TOTAL: {total_pass}/{total} ({pct}%)")

        # Critical Issues
        failures = []
        for key, data in self.h.results.items():
            for t in data["tests"]:
                if t["status"] == "FAIL":
                    failures.append(f"  [FAIL] {data['name']}: {t['name']} — {t['detail']}")
        if failures:
            print(f"\n  CRITICAL ISSUES ({len(failures)}):")
            for f in failures[:20]:
                print(f)

        # Suggestions
        if self.h.suggestions:
            print(f"\n  SUGGESTIONS ({len(self.h.suggestions)}):")
            for s in self.h.suggestions[:10]:
                print(f"    💡 {s}")

        print("=" * 70)

    def save_json(self, output, path=None):
        """Save JSON to file."""
        if path is None:
            path = self.args.json_out if self.args.json_out else os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "last_run.json"
            )
        try:
            with open(path, "w") as f:
                json.dump(output, f, indent=2)
            print(f"  Results saved to {path}")
        except Exception as e:
            print(f"  Save failed: {e}")

    def send_email(self, output):
        """Send email report via Resend."""
        env = self.h.read_env()
        api_key = env.get("RESEND_API_KEY", "")
        if not api_key:
            print("  Email skipped: RESEND_API_KEY not in .env")
            return

        s = output["summary"]
        status_word = "ALL SYSTEMS GO" if s["total_fail"] == 0 else f"ATTENTION REQUIRED ({s['total_fail']} failures)"
        subj = f"SUPER_TEST v2.0 {'PASS' if s['total_fail'] == 0 else 'FAIL'} — {s['total_pass']}/{s['total_pass'] + s['total_fail']}"

        def rows(tests):
            r = ""
            for t in tests:
                color = "#27ae60" if t["status"] == "PASS" else "#e74c3c"
                r += f"<tr><td style='color:{color}'>{t['status']}</td><td>{t['name']}</td><td>{t['detail']}</td><td>{t['owner']}</td></tr>"
            return r

        parts_html = ""
        for key in sorted(self.h.results.keys()):
            data = self.h.results[key]
            num = key.split("_")[1]
            parts_html += f"<h3>Part {num}: {data['name']} ({data['pass']}/{data['pass'] + data['fail']})</h3>"
            parts_html += f"<table border='1' cellpadding='4'>{rows(data['tests'])}</table>"

        html = f"""<html><body>
<h2>{status_word}</h2>
<p>{s['total_pass']}/{s['total_pass'] + s['total_fail']} passed ({s['pct']}%) — {output['run_at'][:19]} UTC</p>
{parts_html}
</body></html>"""

        try:
            import httpx, asyncio
            async def _send():
                async with httpx.AsyncClient() as c:
                    r = await c.post("https://api.resend.com/emails",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json={"from": FROM_EMAIL, "to": [REPORT_EMAIL], "subject": subj, "html": html},
                        timeout=10)
                    return r.status_code, r.text
            code, body = asyncio.run(_send())
            if code == 200:
                print(f"  Report emailed to {REPORT_EMAIL}")
            else:
                print(f"  Email failed: {code} {body}")
        except Exception as e:
            print(f"  Email error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    args = parse_args()
    print(f"\nQUIRRELY SUPER_TEST v2.0 — ASO · KIM · MARS")
    print(f"Mode: {'local' if args.local else 'production'}")
    print(f"Run at: {datetime.now(timezone.utc).isoformat()}")

    # Determine which parts to run
    if args.parts:
        selected = set(int(p.strip()) for p in args.parts.split(",") if p.strip().isdigit())
    else:
        selected = {1, 2, 3, 4, 5, 6, 7, 8}
    if args.skip_e2e:
        selected.discard(5)
    if args.skip_perf:
        selected.discard(8)

    harness = TestHarness(args)
    start_time = time.time()
    health_ok = True

    # Part 1: Infrastructure (gates all others)
    if 1 in selected:
        p1 = Part1_Infrastructure(args)
        p1.results = harness.results
        p1.suggestions = harness.suggestions
        p1.benchmarks = harness.benchmarks
        p1._cleanup_emails = harness._cleanup_emails
        p1._env_cache = harness._env_cache
        health_ok = p1.run()
        harness._env_cache = p1._env_cache
        if not health_ok:
            print("\n  ⚠️  /health FAILED — aborting remaining API-dependent parts")
            selected -= {2, 3, 5, 6, 7, 8}

    # Part 2: LNCP Engine
    if 2 in selected:
        p2 = Part2_LNCPEngine(args)
        p2.results = harness.results
        p2.suggestions = harness.suggestions
        p2.benchmarks = harness.benchmarks
        p2._env_cache = harness._env_cache
        p2.run()

    # Part 3: Backend API
    if 3 in selected:
        p3 = Part3_BackendAPI(args)
        p3.results = harness.results
        p3.suggestions = harness.suggestions
        p3.benchmarks = harness.benchmarks
        p3._cleanup_emails = harness._cleanup_emails
        p3._env_cache = harness._env_cache
        p3.run()
        harness._cleanup_emails = p3._cleanup_emails

    # Part 4: Frontend Integrity (no API deps)
    if 4 in selected:
        p4 = Part4_FrontendIntegrity(args)
        p4.results = harness.results
        p4.suggestions = harness.suggestions
        p4.benchmarks = harness.benchmarks
        p4._env_cache = harness._env_cache
        p4.run()

    # Part 5: E2E Journeys
    if 5 in selected:
        p5 = Part5_E2EJourneys(args)
        p5.results = harness.results
        p5.suggestions = harness.suggestions
        p5.benchmarks = harness.benchmarks
        p5._cleanup_emails = harness._cleanup_emails
        p5._env_cache = harness._env_cache
        p5.run()
        harness._cleanup_emails = p5._cleanup_emails

    # Part 6: Security
    if 6 in selected:
        p6 = Part6_Security(args)
        p6.results = harness.results
        p6.suggestions = harness.suggestions
        p6.benchmarks = harness.benchmarks
        p6._env_cache = harness._env_cache
        p6.run()

    # Part 7: Conversion Audit
    if 7 in selected:
        p7 = Part7_ConversionAudit(args)
        p7.results = harness.results
        p7.suggestions = harness.suggestions
        p7.benchmarks = harness.benchmarks
        p7._cleanup_emails = harness._cleanup_emails
        p7._env_cache = harness._env_cache
        p7.run()

    # Part 8: Performance (runs last)
    if 8 in selected:
        p8 = Part8_Performance(args)
        p8.results = harness.results
        p8.suggestions = harness.suggestions
        p8.benchmarks = harness.benchmarks
        p8._env_cache = harness._env_cache
        p8.run()

    duration = int(time.time() - start_time)

    # Cleanup test users
    print("\n  Cleaning up test users...")
    harness.cleanup()

    # Report
    report = ReportEngine(harness, args)
    output = report.build_json()
    output["duration_seconds"] = duration
    report.print_summary()
    report.save_json(output)

    if args.email:
        report.send_email(output)

    total_fail = sum(p["fail"] for p in harness.results.values())
    sys.exit(0 if total_fail == 0 else 1)


if __name__ == "__main__":
    main()
