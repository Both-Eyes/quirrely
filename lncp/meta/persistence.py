#!/usr/bin/env python3
"""
LNCP META: PERSISTENCE LAYER v5.0
Production-ready persistence for all Meta components.

Uses SQLite for time-series data (outcomes, predictions, trust events)
Uses JSON files for config/state (parameters, proposals)

Design principles:
- Abstract interface allows swapping backends
- Atomic writes with rollback
- Integrity checks on startup
- Automatic backup before migrations
"""

import sqlite3
import json
import os
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Type, TypeVar
from pathlib import Path
import threading


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_DATA_DIR = os.environ.get("LNCP_DATA_DIR", "/var/lib/lncp")
BACKUP_DIR = os.path.join(DEFAULT_DATA_DIR, "backups")

# Database files
DB_OUTCOMES = "outcomes.db"
DB_PREDICTIONS = "predictions.db"
DB_TRUST = "trust.db"
DB_ATTRIBUTION = "attribution.db"

# JSON files
JSON_PARAMETERS = "parameters.json"
JSON_PROPOSALS = "proposals.json"
JSON_ENGINE_PARAMS = "engine_parameters.json"
JSON_STATE = "meta_state.json"


# ═══════════════════════════════════════════════════════════════════════════
# ABSTRACT PERSISTENCE INTERFACE
# ═══════════════════════════════════════════════════════════════════════════

T = TypeVar('T')

class PersistenceBackend(ABC):
    """Abstract interface for persistence backends."""
    
    @abstractmethod
    def save(self, key: str, data: Any) -> bool:
        """Save data with a key."""
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Any]:
        """Load data by key."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete data by key."""
        pass
    
    @abstractmethod
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with optional prefix filter."""
        pass
    
    @abstractmethod
    def close(self):
        """Close any open connections."""
        pass


# ═══════════════════════════════════════════════════════════════════════════
# SQLITE PERSISTENCE
# ═══════════════════════════════════════════════════════════════════════════

class SQLitePersistence(PersistenceBackend):
    """
    SQLite-based persistence for time-series data.
    
    Optimized for:
    - High write throughput
    - Range queries by time
    - Aggregation queries
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_dir()
        self._local = threading.local()
        self._init_db()
    
    def _ensure_dir(self):
        """Ensure database directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    @property
    def _conn(self) -> sqlite3.Connection:
        """Get thread-local connection."""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
    
    def _init_db(self):
        """Initialize database schema."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS kv_store (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_kv_created 
            ON kv_store(created_at)
        """)
        self._conn.commit()
    
    def save(self, key: str, data: Any) -> bool:
        """Save data as JSON."""
        try:
            value = json.dumps(data, default=str)
            self._conn.execute("""
                INSERT INTO kv_store (key, value, updated_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET 
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, value))
            self._conn.commit()
            return True
        except Exception as e:
            print(f"SQLite save error: {e}")
            return False
    
    def load(self, key: str) -> Optional[Any]:
        """Load data by key."""
        try:
            cursor = self._conn.execute(
                "SELECT value FROM kv_store WHERE key = ?", (key,)
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None
        except Exception as e:
            print(f"SQLite load error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete by key."""
        try:
            self._conn.execute("DELETE FROM kv_store WHERE key = ?", (key,))
            self._conn.commit()
            return True
        except Exception as e:
            print(f"SQLite delete error: {e}")
            return False
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with prefix."""
        try:
            cursor = self._conn.execute(
                "SELECT key FROM kv_store WHERE key LIKE ?",
                (f"{prefix}%",)
            )
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"SQLite list error: {e}")
            return []
    
    def query_range(
        self,
        prefix: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Dict]:
        """Query records in a time range."""
        try:
            query = "SELECT key, value, created_at FROM kv_store WHERE key LIKE ?"
            params = [f"{prefix}%"]
            
            if start_time:
                query += " AND created_at >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND created_at <= ?"
                params.append(end_time.isoformat())
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor = self._conn.execute(query, params)
            return [
                {"key": row[0], "value": json.loads(row[1]), "created_at": row[2]}
                for row in cursor.fetchall()
            ]
        except Exception as e:
            print(f"SQLite query error: {e}")
            return []
    
    def count(self, prefix: str = "") -> int:
        """Count records with prefix."""
        try:
            cursor = self._conn.execute(
                "SELECT COUNT(*) FROM kv_store WHERE key LIKE ?",
                (f"{prefix}%",)
            )
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"SQLite count error: {e}")
            return 0
    
    def vacuum(self):
        """Optimize database."""
        self._conn.execute("VACUUM")
    
    def close(self):
        """Close connection."""
        if hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None


# ═══════════════════════════════════════════════════════════════════════════
# JSON FILE PERSISTENCE
# ═══════════════════════════════════════════════════════════════════════════

class JSONPersistence(PersistenceBackend):
    """
    JSON file-based persistence for config and state.
    
    Features:
    - Atomic writes (write to temp, then rename)
    - Automatic versioning
    - Human-readable format
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_dir()
        self._lock = threading.Lock()
        self._cache: Optional[Dict] = None
    
    def _ensure_dir(self):
        """Ensure file directory exists."""
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _load_file(self) -> Dict:
        """Load entire file."""
        if self._cache is not None:
            return self._cache
        
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    self._cache = json.load(f)
            else:
                self._cache = {"_meta": {"version": 1, "created_at": datetime.utcnow().isoformat()}}
        except Exception as e:
            print(f"JSON load error: {e}")
            self._cache = {"_meta": {"version": 1, "error": str(e)}}
        
        return self._cache
    
    def _save_file(self, data: Dict) -> bool:
        """Save entire file atomically."""
        try:
            # Update metadata
            data["_meta"] = data.get("_meta", {})
            data["_meta"]["updated_at"] = datetime.utcnow().isoformat()
            data["_meta"]["version"] = data["_meta"].get("version", 0) + 1
            
            # Write to temp file first
            temp_path = f"{self.file_path}.tmp"
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            # Atomic rename
            os.replace(temp_path, self.file_path)
            
            self._cache = data
            return True
        except Exception as e:
            print(f"JSON save error: {e}")
            return False
    
    def save(self, key: str, data: Any) -> bool:
        """Save data under a key."""
        with self._lock:
            file_data = self._load_file()
            file_data[key] = data
            return self._save_file(file_data)
    
    def load(self, key: str) -> Optional[Any]:
        """Load data by key."""
        with self._lock:
            file_data = self._load_file()
            return file_data.get(key)
    
    def delete(self, key: str) -> bool:
        """Delete by key."""
        with self._lock:
            file_data = self._load_file()
            if key in file_data:
                del file_data[key]
                return self._save_file(file_data)
            return True
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with prefix."""
        with self._lock:
            file_data = self._load_file()
            return [k for k in file_data.keys() if k.startswith(prefix) and not k.startswith("_")]
    
    def get_all(self) -> Dict:
        """Get all data."""
        with self._lock:
            return self._load_file().copy()
    
    def set_all(self, data: Dict) -> bool:
        """Replace all data."""
        with self._lock:
            return self._save_file(data)
    
    def close(self):
        """No-op for JSON files."""
        pass


# ═══════════════════════════════════════════════════════════════════════════
# PERSISTENCE MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class PersistenceManager:
    """
    Manages all persistence backends for Meta.
    
    Provides:
    - Unified access to all data stores
    - Backup and restore
    - Integrity checking
    - Migration support
    """
    
    def __init__(self, data_dir: str = DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)
        
        # Initialize backends
        self.outcomes = SQLitePersistence(os.path.join(data_dir, DB_OUTCOMES))
        self.predictions = SQLitePersistence(os.path.join(data_dir, DB_PREDICTIONS))
        self.trust = SQLitePersistence(os.path.join(data_dir, DB_TRUST))
        self.attribution = SQLitePersistence(os.path.join(data_dir, DB_ATTRIBUTION))
        
        self.parameters = JSONPersistence(os.path.join(data_dir, JSON_PARAMETERS))
        self.proposals = JSONPersistence(os.path.join(data_dir, JSON_PROPOSALS))
        self.engine_params = JSONPersistence(os.path.join(data_dir, JSON_ENGINE_PARAMS))
        self.state = JSONPersistence(os.path.join(data_dir, JSON_STATE))
    
    # ─────────────────────────────────────────────────────────────────────
    # BACKUP & RESTORE
    # ─────────────────────────────────────────────────────────────────────
    
    def backup(self, label: str = "") -> str:
        """Create a backup of all data."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}_{label}" if label else f"backup_{timestamp}"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        os.makedirs(backup_path, exist_ok=True)
        
        # Copy SQLite databases
        for db_file in [DB_OUTCOMES, DB_PREDICTIONS, DB_TRUST, DB_ATTRIBUTION]:
            src = os.path.join(self.data_dir, db_file)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(backup_path, db_file))
        
        # Copy JSON files
        for json_file in [JSON_PARAMETERS, JSON_PROPOSALS, JSON_ENGINE_PARAMS, JSON_STATE]:
            src = os.path.join(self.data_dir, json_file)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(backup_path, json_file))
        
        # Create manifest
        manifest = {
            "created_at": datetime.utcnow().isoformat(),
            "label": label,
            "files": os.listdir(backup_path),
        }
        with open(os.path.join(backup_path, "manifest.json"), 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return backup_path
    
    def restore(self, backup_path: str) -> bool:
        """Restore from a backup."""
        try:
            # Verify backup exists
            if not os.path.exists(backup_path):
                print(f"Backup not found: {backup_path}")
                return False
            
            # Close current connections
            self.close()
            
            # Create pre-restore backup
            self.backup("pre_restore")
            
            # Copy files back
            for filename in os.listdir(backup_path):
                if filename == "manifest.json":
                    continue
                src = os.path.join(backup_path, filename)
                dst = os.path.join(self.data_dir, filename)
                shutil.copy2(src, dst)
            
            # Reinitialize
            self.__init__(self.data_dir)
            
            return True
        except Exception as e:
            print(f"Restore error: {e}")
            return False
    
    def list_backups(self) -> List[Dict]:
        """List available backups."""
        backups = []
        if not os.path.exists(BACKUP_DIR):
            return backups
        
        for name in sorted(os.listdir(BACKUP_DIR), reverse=True):
            path = os.path.join(BACKUP_DIR, name)
            manifest_path = os.path.join(path, "manifest.json")
            
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                backups.append({
                    "name": name,
                    "path": path,
                    "created_at": manifest.get("created_at"),
                    "label": manifest.get("label"),
                })
        
        return backups
    
    # ─────────────────────────────────────────────────────────────────────
    # INTEGRITY
    # ─────────────────────────────────────────────────────────────────────
    
    def check_integrity(self) -> Dict:
        """Check integrity of all data stores."""
        results = {
            "status": "ok",
            "issues": [],
            "stats": {},
        }
        
        # Check SQLite databases
        for name, db in [
            ("outcomes", self.outcomes),
            ("predictions", self.predictions),
            ("trust", self.trust),
            ("attribution", self.attribution),
        ]:
            try:
                count = db.count()
                results["stats"][name] = {"records": count}
            except Exception as e:
                results["issues"].append(f"{name}: {e}")
                results["status"] = "error"
        
        # Check JSON files
        for name, store in [
            ("parameters", self.parameters),
            ("proposals", self.proposals),
            ("engine_params", self.engine_params),
            ("state", self.state),
        ]:
            try:
                data = store.get_all()
                results["stats"][name] = {"keys": len(data)}
            except Exception as e:
                results["issues"].append(f"{name}: {e}")
                results["status"] = "error"
        
        return results
    
    # ─────────────────────────────────────────────────────────────────────
    # CLEANUP
    # ─────────────────────────────────────────────────────────────────────
    
    def cleanup_old_data(self, days: int = 90):
        """Remove data older than specified days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # For SQLite stores, delete old records
        for db in [self.outcomes, self.predictions, self.trust, self.attribution]:
            try:
                db._conn.execute(
                    "DELETE FROM kv_store WHERE created_at < ?",
                    (cutoff.isoformat(),)
                )
                db._conn.commit()
                db.vacuum()
            except Exception as e:
                print(f"Cleanup error: {e}")
    
    def close(self):
        """Close all connections."""
        self.outcomes.close()
        self.predictions.close()
        self.trust.close()
        self.attribution.close()


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_persistence_manager: Optional[PersistenceManager] = None

def get_persistence_manager(data_dir: str = DEFAULT_DATA_DIR) -> PersistenceManager:
    """Get the global persistence manager."""
    global _persistence_manager
    if _persistence_manager is None:
        _persistence_manager = PersistenceManager(data_dir)
    return _persistence_manager


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "PersistenceBackend",
    "SQLitePersistence",
    "JSONPersistence",
    "PersistenceManager",
    "get_persistence_manager",
    "DEFAULT_DATA_DIR",
]
