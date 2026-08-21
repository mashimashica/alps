-- Canonical schema snapshot. Runtime migrations remain executable Go for the embedded single binary.
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
PRAGMA busy_timeout = 5000;

-- Operational projections
CREATE TABLE IF NOT EXISTS assets(id TEXT PRIMARY KEY, kind TEXT NOT NULL, name TEXT NOT NULL, source_uri TEXT NOT NULL UNIQUE, digest TEXT NOT NULL, validation TEXT NOT NULL, source_state TEXT NOT NULL, host_state TEXT NOT NULL, alps_state TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS revisions(id TEXT PRIMARY KEY, asset_id TEXT NOT NULL REFERENCES assets(id), kind TEXT NOT NULL, digest TEXT NOT NULL, snapshot_path TEXT NOT NULL, manifest_json TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE(asset_id,digest));
CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, title TEXT NOT NULL, process TEXT NOT NULL, state TEXT NOT NULL, version INTEGER NOT NULL, context_json TEXT NOT NULL, actor_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS domain_events(global_sequence INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE, stream_type TEXT NOT NULL, stream_id TEXT NOT NULL, stream_sequence INTEGER NOT NULL, event_type TEXT NOT NULL, actor_json TEXT NOT NULL, authority TEXT, correlation_id TEXT, causation_id TEXT, payload_version TEXT NOT NULL, payload_json TEXT NOT NULL, occurred_at TEXT NOT NULL, UNIQUE(stream_type,stream_id,stream_sequence));
CREATE TABLE IF NOT EXISTS telemetry_outbox(id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL REFERENCES domain_events(event_id), mapping_revision TEXT NOT NULL, export_state TEXT NOT NULL, attempt_count INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, exported_at TEXT);
CREATE TABLE IF NOT EXISTS idempotency_keys(key TEXT PRIMARY KEY, command TEXT NOT NULL, request_digest TEXT NOT NULL, status INTEGER NOT NULL, response_json TEXT NOT NULL, created_at TEXT NOT NULL);
