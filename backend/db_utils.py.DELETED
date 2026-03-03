"""Minimal DB utilities using psycopg2 subprocess pattern."""
import subprocess, json, os

DB_NAME = "quirrely_prod"

def db_run(sql, params=None):
    """Run SQL and return (rows, success)."""
    try:
        if params:
            for p in params:
                escaped = str(p).replace("'","''")
                sql = sql.replace("?", f"'{escaped}'", 1)
        r = subprocess.run(
            ["sudo","-u","postgres","psql","-d",DB_NAME,"-t","--csv","-c",sql],
            capture_output=True, text=True, timeout=10)
        rows = [l.strip() for l in r.stdout.strip().splitlines() if l.strip()]
        return rows, r.returncode == 0
    except Exception as e:
        return [], False

def db_one(sql, params=None):
    rows, ok = db_run(sql, params)
    return rows[0] if rows and ok else None
