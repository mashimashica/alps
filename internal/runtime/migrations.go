package runtime

import (
	"database/sql"
	"fmt"
	"strings"
)

func (r *Runtime) migrate() error {
	if _, err := r.db.Exec(`
PRAGMA foreign_keys=ON;
PRAGMA journal_mode=WAL;
PRAGMA synchronous=FULL;
PRAGMA busy_timeout=5000;

CREATE TABLE IF NOT EXISTS schema_migrations(
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS asset_sources(
  id TEXT PRIMARY KEY,
  provider TEXT NOT NULL,
  scope TEXT NOT NULL,
  realm TEXT NOT NULL DEFAULT 'local',
  root_uri TEXT NOT NULL,
  host TEXT NOT NULL DEFAULT '',
  last_seen_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assets(
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  scope TEXT NOT NULL,
  provider TEXT NOT NULL,
  source_path TEXT NOT NULL UNIQUE,
  digest TEXT NOT NULL,
  validation TEXT NOT NULL,
  alps_state TEXT NOT NULL,
  adopted_revision_id TEXT,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS revisions(
  id TEXT PRIMARY KEY,
  asset_id TEXT NOT NULL REFERENCES assets(id),
  kind TEXT NOT NULL,
  digest TEXT NOT NULL,
  snapshot_path TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(asset_id,digest)
);
CREATE TABLE IF NOT EXISTS process_revisions(
  id TEXT PRIMARY KEY,
  logical_process_id TEXT NOT NULL,
  asset_id TEXT NOT NULL REFERENCES assets(id),
  digest TEXT NOT NULL,
  source_uri TEXT NOT NULL,
  alps_version TEXT,
  name TEXT NOT NULL,
  purpose TEXT,
  outcomes_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL,
  UNIQUE(asset_id,digest)
);
CREATE TABLE IF NOT EXISTS skill_package_revisions(
  id TEXT PRIMARY KEY,
  asset_id TEXT NOT NULL REFERENCES assets(id),
  process_revision_id TEXT NOT NULL REFERENCES process_revisions(id),
  digest TEXT NOT NULL,
  manifest_json TEXT NOT NULL,
  snapshot_path TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(asset_id,digest)
);
CREATE TABLE IF NOT EXISTS plugin_revisions(
  id TEXT PRIMARY KEY,
  asset_id TEXT NOT NULL REFERENCES assets(id),
  plugin_identity TEXT NOT NULL,
  digest TEXT NOT NULL,
  manifest_json TEXT NOT NULL,
  capture_mode TEXT NOT NULL,
  snapshot_path TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(asset_id,digest)
);
CREATE TABLE IF NOT EXISTS plugin_components(
  id TEXT PRIMARY KEY,
  plugin_revision_id TEXT NOT NULL REFERENCES plugin_revisions(id),
  component_type TEXT NOT NULL,
  source_uri TEXT NOT NULL,
  digest TEXT,
  permissions_json TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS process_model_revisions(
  id TEXT PRIMARY KEY,
  asset_id TEXT NOT NULL REFERENCES assets(id),
  model_id TEXT NOT NULL,
  name TEXT NOT NULL,
  version TEXT,
  digest TEXT NOT NULL,
  descriptor_json TEXT NOT NULL,
  snapshot_path TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(asset_id,digest)
);
CREATE TABLE IF NOT EXISTS model_processes(
  model_revision_id TEXT NOT NULL REFERENCES process_model_revisions(id),
  process_id TEXT NOT NULL,
  process_revision_id TEXT,
  ref TEXT NOT NULL,
  name TEXT NOT NULL,
  digest TEXT NOT NULL,
  PRIMARY KEY(model_revision_id,process_id)
);
CREATE TABLE IF NOT EXISTS interface_types(
  model_revision_id TEXT NOT NULL REFERENCES process_model_revisions(id),
  interface_id TEXT NOT NULL,
  name TEXT NOT NULL,
  kind TEXT NOT NULL,
  media_types_json TEXT NOT NULL DEFAULT '[]',
  schema_ref TEXT,
  schema_digest TEXT,
  required INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY(model_revision_id,interface_id)
);
CREATE TABLE IF NOT EXISTS process_bindings(
  model_revision_id TEXT NOT NULL REFERENCES process_model_revisions(id),
  binding_id TEXT NOT NULL,
  process_id TEXT NOT NULL,
  role TEXT NOT NULL,
  item_name TEXT NOT NULL,
  interface_id TEXT NOT NULL,
  optional INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY(model_revision_id,binding_id)
);
CREATE TABLE IF NOT EXISTS handoff_definitions(
  model_revision_id TEXT NOT NULL REFERENCES process_model_revisions(id),
  handoff_id TEXT NOT NULL,
  from_binding TEXT NOT NULL,
  to_binding TEXT NOT NULL,
  acceptance_ref TEXT,
  acceptance_digest TEXT,
  PRIMARY KEY(model_revision_id,handoff_id)
);
CREATE TABLE IF NOT EXISTS model_relationships(
  model_revision_id TEXT NOT NULL REFERENCES process_model_revisions(id),
  relationship_type TEXT NOT NULL,
  processes_json TEXT NOT NULL,
  ordinal INTEGER NOT NULL,
  PRIMARY KEY(model_revision_id,ordinal)
);
CREATE TABLE IF NOT EXISTS model_entry_points(
  model_revision_id TEXT NOT NULL REFERENCES process_model_revisions(id),
  process_id TEXT NOT NULL,
  ordinal INTEGER NOT NULL,
  PRIMARY KEY(model_revision_id,ordinal)
);
CREATE TABLE IF NOT EXISTS host_contexts(
  id TEXT PRIMARY KEY,
  host TEXT NOT NULL,
  version TEXT,
  workspace_roots_json TEXT NOT NULL DEFAULT '[]',
  repository_root TEXT,
  realm TEXT,
  reported_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS host_capability_profiles(
  id TEXT PRIMARY KEY,
  host TEXT NOT NULL,
  version TEXT,
  adapter_version TEXT NOT NULL,
  capabilities_json TEXT NOT NULL,
  observed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs(
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  process TEXT NOT NULL,
  asset_id TEXT,
  state TEXT NOT NULL,
  version INTEGER NOT NULL,
  progress INTEGER,
  status_text TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS run_outcomes(
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id),
  name TEXT NOT NULL,
  status TEXT NOT NULL,
  required INTEGER NOT NULL DEFAULT 1,
  evidence_json TEXT NOT NULL DEFAULT '[]',
  assessment_id TEXT,
  updated_at TEXT NOT NULL,
  UNIQUE(run_id,name)
);
CREATE TABLE IF NOT EXISTS run_reports(
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id),
  actor TEXT NOT NULL,
  message TEXT NOT NULL,
  progress INTEGER,
  claims_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decision_gates(
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id),
  title TEXT NOT NULL,
  effect TEXT NOT NULL,
  reversible INTEGER NOT NULL,
  authority TEXT NOT NULL,
  status TEXT NOT NULL,
  expected_run_version INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  decided_at TEXT
);
CREATE TABLE IF NOT EXISTS decisions(
  id TEXT PRIMARY KEY,
  gate_id TEXT NOT NULL REFERENCES decision_gates(id),
  decision_type TEXT NOT NULL,
  actor TEXT NOT NULL,
  rationale TEXT NOT NULL DEFAULT '',
  final INTEGER NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assessments(
  id TEXT PRIMARY KEY,
  run_id TEXT,
  subject_type TEXT NOT NULL,
  subject_id TEXT NOT NULL,
  assessment_type TEXT NOT NULL,
  criteria_revision TEXT,
  result TEXT NOT NULL,
  rationale TEXT,
  evidence_json TEXT NOT NULL DEFAULT '[]',
  actor_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS artifacts(
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id),
  name TEXT NOT NULL,
  digest TEXT NOT NULL,
  media_type TEXT NOT NULL,
  size INTEGER NOT NULL,
  path TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS artifact_relations(
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id),
  artifact_id TEXT NOT NULL REFERENCES artifacts(id),
  role TEXT NOT NULL,
  process_element TEXT,
  provenance_json TEXT NOT NULL DEFAULT '{}',
  created_event_id TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS handoffs(
  id TEXT PRIMARY KEY,
  provider_run_id TEXT NOT NULL REFERENCES runs(id),
  provider_artifact_id TEXT NOT NULL REFERENCES artifacts(id),
  recipient_run_id TEXT,
  recipient_process_id TEXT,
  recipient_input TEXT NOT NULL,
  criteria_revision TEXT,
  status TEXT NOT NULL,
  evidence_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS model_catalog_snapshots(
  id TEXT PRIMARY KEY,
  host TEXT NOT NULL,
  scope TEXT,
  models_json TEXT NOT NULL,
  observed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS model_invocations(
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id),
  requested_model TEXT,
  effective_model TEXT,
  resolved_model TEXT,
  effort TEXT,
  role TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS usage_observations(
  id TEXT PRIMARY KEY,
  invocation_id TEXT,
  run_id TEXT NOT NULL REFERENCES runs(id),
  source TEXT NOT NULL,
  status TEXT NOT NULL,
  input_tokens INTEGER,
  output_tokens INTEGER,
  cache_read_tokens INTEGER,
  cache_write_tokens INTEGER,
  reasoning_tokens INTEGER,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cost_observations(
  id TEXT PRIMARY KEY,
  invocation_id TEXT,
  run_id TEXT NOT NULL REFERENCES runs(id),
  source TEXT NOT NULL,
  kind TEXT NOT NULL,
  currency TEXT,
  credit_type TEXT,
  amount TEXT NOT NULL,
  status TEXT NOT NULL,
  mapping_revision TEXT,
  observed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS host_observations(
  id TEXT PRIMARY KEY,
  host TEXT NOT NULL,
  event_name TEXT NOT NULL,
  raw_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS hook_revisions(
  id TEXT PRIMARY KEY,
  binding_json TEXT NOT NULL,
  generated_definition_json TEXT,
  digest TEXT NOT NULL,
  capabilities_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS domain_events(
  sequence INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL UNIQUE,
  stream_type TEXT NOT NULL,
  stream_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  payload TEXT NOT NULL,
  occurred_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS telemetry_outbox(
  id TEXT PRIMARY KEY,
  source_event_sequence INTEGER NOT NULL UNIQUE,
  mapping_revision TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  export_status TEXT NOT NULL,
  attempt_count INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  created_at TEXT NOT NULL,
  exported_at TEXT
);
CREATE TABLE IF NOT EXISTS idempotency_keys(
  key TEXT PRIMARY KEY,
  response_json BLOB NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS run_state_intervals(
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id),
  state TEXT NOT NULL,
  started_at TEXT NOT NULL,
  ended_at TEXT
);
`); err != nil {
		return err
	}

	columns := map[string][]string{
		"assets": {
			"source_state TEXT NOT NULL DEFAULT 'detected'",
			"host_state TEXT NOT NULL DEFAULT 'unknown'",
			"validation_json TEXT NOT NULL DEFAULT '[]'",
			"capture_mode TEXT NOT NULL DEFAULT 'materialized'",
			"manifest_json TEXT NOT NULL DEFAULT '{}'",
			"source_id TEXT",
			"last_seen_at TEXT",
		},
		"revisions": {
			"logical_id TEXT",
			"manifest_json TEXT NOT NULL DEFAULT '{}'",
			"metadata_json TEXT NOT NULL DEFAULT '{}'",
		},
		"runs": {
			"process_revision_id TEXT",
			"skill_package_revision_id TEXT",
			"plugin_revision_ids_json TEXT NOT NULL DEFAULT '[]'",
			"process_model_revision_id TEXT",
			"context_json TEXT NOT NULL DEFAULT '{}'",
			"actor_json TEXT NOT NULL DEFAULT '{}'",
			"completion_requested_at TEXT",
			"completed_at TEXT",
			"failed_at TEXT",
			"cancelled_at TEXT",
		},
		"run_reports": {
			"evidence_json TEXT NOT NULL DEFAULT '[]'",
		},
		"decision_gates": {
			"target_revision_id TEXT",
			"criteria_json TEXT NOT NULL DEFAULT '[]'",
			"controls_json TEXT NOT NULL DEFAULT '[]'",
			"constraints_json TEXT NOT NULL DEFAULT '[]'",
			"evidence_json TEXT NOT NULL DEFAULT '[]'",
			"unknown_json TEXT NOT NULL DEFAULT '[]'",
			"external_effect TEXT",
		},
		"decisions": {
			"authority TEXT",
			"conditions_json TEXT NOT NULL DEFAULT '[]'",
			"evidence_json TEXT NOT NULL DEFAULT '[]'",
		},
		"artifacts": {
			"role TEXT NOT NULL DEFAULT 'output'",
			"process_element TEXT",
			"provenance_json TEXT NOT NULL DEFAULT '{}'",
		},
		"model_invocations": {
			"requested_json TEXT NOT NULL DEFAULT '{}'",
			"effective_json TEXT NOT NULL DEFAULT '{}'",
			"resolved_json TEXT NOT NULL DEFAULT '{}'",
			"parameters_json TEXT NOT NULL DEFAULT '{}'",
			"catalog_snapshot_id TEXT",
			"started_at TEXT",
			"finished_at TEXT",
		},
		"usage_observations": {
			"source_type TEXT",
			"source_host TEXT",
			"adapter_version TEXT",
			"scope TEXT NOT NULL DEFAULT 'invocation'",
			"accounting_basis TEXT",
			"inclusion_json TEXT NOT NULL DEFAULT '{}'",
			"mapping_revision TEXT",
			"observed_at TEXT",
		},
		"host_observations": {
			"envelope_json TEXT NOT NULL DEFAULT '{}'",
			"raw_reference TEXT",
		},
		"domain_events": {
			"stream_sequence INTEGER NOT NULL DEFAULT 0",
			"actor_type TEXT NOT NULL DEFAULT 'system'",
			"actor_id TEXT",
			"actor_authority TEXT",
			"channel TEXT NOT NULL DEFAULT 'internal'",
			"correlation_id TEXT",
			"causation_id TEXT",
			"payload_version TEXT NOT NULL DEFAULT 'v1'",
		},
		"idempotency_keys": {
			"command TEXT NOT NULL DEFAULT ''",
			"request_digest TEXT NOT NULL DEFAULT ''",
			"status_code INTEGER NOT NULL DEFAULT 200",
		},
	}
	for table, definitions := range columns {
		for _, definition := range definitions {
			if err := r.ensureColumn(table, definition); err != nil {
				return err
			}
		}
	}
	if _, err := r.db.Exec(`
UPDATE domain_events SET stream_sequence=sequence WHERE stream_sequence=0;
CREATE UNIQUE INDEX IF NOT EXISTS idx_asset_sources_identity ON asset_sources(provider,scope,realm,root_uri,host);
CREATE UNIQUE INDEX IF NOT EXISTS idx_domain_events_stream_sequence ON domain_events(stream_type,stream_id,stream_sequence);
CREATE INDEX IF NOT EXISTS idx_domain_events_type_sequence ON domain_events(event_type,sequence);
CREATE INDEX IF NOT EXISTS idx_runs_state_updated ON runs(state,updated_at);
CREATE INDEX IF NOT EXISTS idx_assets_kind_state ON assets(kind,alps_state);
CREATE INDEX IF NOT EXISTS idx_outbox_status ON telemetry_outbox(export_status,source_event_sequence);
CREATE INDEX IF NOT EXISTS idx_assessments_subject ON assessments(subject_type,subject_id,created_at);
CREATE INDEX IF NOT EXISTS idx_handoffs_status ON handoffs(status,updated_at);
INSERT OR IGNORE INTO schema_migrations(version,applied_at) VALUES(1,strftime('%Y-%m-%dT%H:%M:%fZ','now'));
INSERT OR IGNORE INTO schema_migrations(version,applied_at) VALUES(2,strftime('%Y-%m-%dT%H:%M:%fZ','now'));
`); err != nil {
		return err
	}
	return nil
}

func (r *Runtime) ensureColumn(table, definition string) error {
	column := strings.Fields(definition)[0]
	rows, err := r.db.Query(fmt.Sprintf("PRAGMA table_info(%s)", table))
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
		var cid int
		var name, columnType string
		var notNull, primaryKey int
		var defaultValue sql.NullString
		if err := rows.Scan(&cid, &name, &columnType, &notNull, &defaultValue, &primaryKey); err != nil {
			return err
		}
		if name == column {
			return nil
		}
	}
	_, err = r.db.Exec(fmt.Sprintf("ALTER TABLE %s ADD COLUMN %s", table, definition))
	return err
}
