package runtime

import (
	"context"
	"crypto/rand"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"errors"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"

	_ "modernc.org/sqlite"
)

type Root struct {
	Path     string
	Scope    string
	Provider string
}

type Runtime struct {
	db          *sql.DB
	workspace   string
	token       string
	roots       []Root
	mu          sync.RWMutex
	subscribers map[chan Event]struct{}
}

type Asset struct {
	ID                string `json:"id"`
	Kind              string `json:"kind"`
	Name              string `json:"name"`
	Description       string `json:"description"`
	Scope             string `json:"scope"`
	Provider          string `json:"provider"`
	SourcePath        string `json:"sourcePath"`
	Digest            string `json:"digest"`
	Validation        string `json:"validation"`
	ALPSState         string `json:"alpsState"`
	AdoptedRevisionID string `json:"adoptedRevisionId,omitempty"`
	UpdatedAt         string `json:"updatedAt"`
}

type AssetDetail struct {
	Asset
	Files       []string `json:"files"`
	Content     string   `json:"content"`
	ContentPath string   `json:"contentPath"`
}

type Run struct {
	ID         string `json:"id"`
	Title      string `json:"title"`
	Process    string `json:"process"`
	AssetID    string `json:"assetId,omitempty"`
	State      string `json:"state"`
	Version    int64  `json:"version"`
	Progress   *int   `json:"progress,omitempty"`
	StatusText string `json:"statusText"`
	CreatedAt  string `json:"createdAt"`
	UpdatedAt  string `json:"updatedAt"`
}

type Gate struct {
	ID                 string `json:"id"`
	RunID              string `json:"runId"`
	Title              string `json:"title"`
	Effect             string `json:"effect"`
	Reversible         bool   `json:"reversible"`
	Authority          string `json:"authority"`
	Status             string `json:"status"`
	ExpectedRunVersion int64  `json:"expectedRunVersion"`
	CreatedAt          string `json:"createdAt"`
}

type Event struct {
	Sequence   int64           `json:"sequence"`
	Type       string          `json:"type"`
	StreamType string          `json:"streamType"`
	StreamID   string          `json:"streamId"`
	Payload    json.RawMessage `json:"payload"`
	OccurredAt string          `json:"occurredAt"`
}

type GraphNode struct {
	ID   string `json:"id"`
	Name string `json:"name"`
	Kind string `json:"kind"`
}

type GraphEdge struct {
	From string `json:"from"`
	To   string `json:"to"`
	Kind string `json:"kind"`
}

type GraphLive struct {
	RunID     string `json:"runId"`
	ProcessID string `json:"processId"`
	State     string `json:"state"`
}

type Graph struct {
	Processes  []GraphNode `json:"processes"`
	Interfaces []GraphNode `json:"interfaces"`
	Edges      []GraphEdge `json:"edges"`
	Live       []GraphLive `json:"live"`
}

type Analysis struct {
	Active    int   `json:"active"`
	Waiting   int   `json:"waiting"`
	Completed int   `json:"completed"`
	Assets    int   `json:"assets"`
	Gates     int   `json:"gates"`
	Tokens    int64 `json:"tokens"`
}

type RunDetail struct {
	Run    Run     `json:"run"`
	Gate   *Gate   `json:"gate,omitempty"`
	Events []Event `json:"events"`
}

var ErrStale = errors.New("stale version")

func Open(workspace string) (*Runtime, error) {
	for _, directory := range []string{"db", "blobs/sha256", "snapshots", "backups", "exports/runs", "runtime"} {
		if err := os.MkdirAll(filepath.Join(workspace, directory), 0o700); err != nil {
			return nil, err
		}
	}
	token, err := ensureToken(filepath.Join(workspace, "runtime", "access.token"))
	if err != nil {
		return nil, err
	}
	database, err := sql.Open("sqlite", filepath.Join(workspace, "db", "alps.sqlite3"))
	if err != nil {
		return nil, err
	}
	database.SetMaxOpenConns(1)
	runtime := &Runtime{db: database, workspace: workspace, token: token, subscribers: map[chan Event]struct{}{}}
	if err := runtime.migrate(); err != nil {
		database.Close()
		return nil, err
	}
	return runtime, nil
}

func (r *Runtime) Close() error       { return r.db.Close() }
func (r *Runtime) Token() string      { return r.token }
func (r *Runtime) Workspace() string  { return r.workspace }
func (r *Runtime) SetRoots(roots []Root) { r.roots = roots }

func DefaultRoots(project string) []Root {
	roots := []Root{{Path: project, Scope: "project", Provider: "project"}}
	if home, err := os.UserHomeDir(); err == nil {
		for _, path := range []string{".agents/skills", ".claude/skills", ".cursor/skills", ".copilot/skills"} {
			roots = append(roots, Root{Path: filepath.Join(home, path), Scope: "user", Provider: strings.Split(path, "/")[0]})
		}
	}
	return roots
}

func (r *Runtime) migrate() error {
	const schema = `
PRAGMA foreign_keys=ON;
PRAGMA journal_mode=WAL;
PRAGMA synchronous=FULL;
PRAGMA busy_timeout=5000;
CREATE TABLE IF NOT EXISTS assets(id TEXT PRIMARY KEY, kind TEXT NOT NULL, name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', scope TEXT NOT NULL, provider TEXT NOT NULL, source_path TEXT NOT NULL UNIQUE, digest TEXT NOT NULL, validation TEXT NOT NULL, alps_state TEXT NOT NULL, adopted_revision_id TEXT, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS revisions(id TEXT PRIMARY KEY, asset_id TEXT NOT NULL REFERENCES assets(id), kind TEXT NOT NULL, digest TEXT NOT NULL, snapshot_path TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE(asset_id,digest));
CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, title TEXT NOT NULL, process TEXT NOT NULL, asset_id TEXT, state TEXT NOT NULL, version INTEGER NOT NULL, progress INTEGER, status_text TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS run_reports(id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), actor TEXT NOT NULL, message TEXT NOT NULL, progress INTEGER, claims_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS decision_gates(id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), title TEXT NOT NULL, effect TEXT NOT NULL, reversible INTEGER NOT NULL, authority TEXT NOT NULL, status TEXT NOT NULL, expected_run_version INTEGER NOT NULL, created_at TEXT NOT NULL, decided_at TEXT);
CREATE TABLE IF NOT EXISTS decisions(id TEXT PRIMARY KEY, gate_id TEXT NOT NULL REFERENCES decision_gates(id), decision_type TEXT NOT NULL, actor TEXT NOT NULL, rationale TEXT NOT NULL DEFAULT '', final INTEGER NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), name TEXT NOT NULL, digest TEXT NOT NULL, media_type TEXT NOT NULL, size INTEGER NOT NULL, path TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS model_invocations(id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), requested_model TEXT, effective_model TEXT, resolved_model TEXT, effort TEXT, role TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS usage_observations(id TEXT PRIMARY KEY, invocation_id TEXT, run_id TEXT NOT NULL REFERENCES runs(id), source TEXT NOT NULL, status TEXT NOT NULL, input_tokens INTEGER, output_tokens INTEGER, cache_read_tokens INTEGER, cache_write_tokens INTEGER, reasoning_tokens INTEGER, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS host_observations(id TEXT PRIMARY KEY, host TEXT NOT NULL, event_name TEXT NOT NULL, raw_json TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS domain_events(sequence INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE, stream_type TEXT NOT NULL, stream_id TEXT NOT NULL, event_type TEXT NOT NULL, payload TEXT NOT NULL, occurred_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS idempotency_keys(key TEXT PRIMARY KEY, response_json TEXT NOT NULL, created_at TEXT NOT NULL);
`
	_, err := r.db.Exec(schema)
	return err
}

func ensureToken(path string) (string, error) {
	if content, err := os.ReadFile(path); err == nil && strings.TrimSpace(string(content)) != "" {
		return strings.TrimSpace(string(content)), nil
	}
	value := make([]byte, 32)
	if _, err := rand.Read(value); err != nil {
		return "", err
	}
	token := hex.EncodeToString(value)
	if err := os.WriteFile(path, []byte(token+"\n"), 0o600); err != nil {
		return "", err
	}
	return token, nil
}

func (r *Runtime) WriteEndpoint(url string) error {
	data, _ := json.MarshalIndent(map[string]any{"url": url, "pid": os.Getpid(), "startedAt": now()}, "", "  ")
	return os.WriteFile(filepath.Join(r.workspace, "runtime", "endpoint.json"), data, 0o600)
}

func ReadEndpoint(workspace string) (string, error) {
	data, err := os.ReadFile(filepath.Join(workspace, "runtime", "endpoint.json"))
	if err != nil {
		return "", err
	}
	var value struct {
		URL string `json:"url"`
	}
	if err := json.Unmarshal(data, &value); err != nil {
		return "", err
	}
	if value.URL == "" {
		return "", errors.New("empty endpoint")
	}
	return value.URL, nil
}

func (r *Runtime) Scan(ctx context.Context) ([]Asset, error) {
	seen := map[string]struct{}{}
	for _, root := range r.roots {
		if _, err := os.Stat(root.Path); err != nil {
			continue
		}
		err := filepath.WalkDir(root.Path, func(path string, entry fs.DirEntry, walkErr error) error {
			if walkErr != nil {
				return nil
			}
			if entry.IsDir() {
				switch entry.Name() {
				case ".git", "node_modules", ".worktrees", "snapshots", ".alps-runtime":
					return filepath.SkipDir
				default:
					return nil
				}
			}
			kind := ""
			switch {
			case entry.Name() == "SKILL.md":
				kind = "skill"
			case entry.Name() == "plugin.json":
				kind = "plugin"
			case entry.Name() == "process-model.yaml" || strings.HasSuffix(path, ".yaml") && strings.Contains(filepath.ToSlash(path), "/.alps/process-models/"):
				kind = "process-model"
			default:
				return nil
			}
			absolute, _ := filepath.Abs(path)
			if _, exists := seen[absolute]; exists {
				return nil
			}
			seen[absolute] = struct{}{}
			asset, err := inspectAsset(path, kind, root.Scope, root.Provider)
			if err != nil {
				return nil
			}
			return r.upsertAsset(ctx, asset)
		})
		if err != nil {
			return nil, err
		}
	}
	assets, err := r.Catalog(ctx)
	if err == nil {
		_, _ = r.appendEvent(ctx, "catalog", "global", "catalog.scanned", map[string]any{"count": len(assets)})
	}
	return assets, err
}

func inspectAsset(path, kind, scope, provider string) (Asset, error) {
	packagePath := path
	if kind == "skill" {
		packagePath = filepath.Dir(path)
	}
	digest, err := digestPath(packagePath)
	if err != nil {
		return Asset{}, err
	}
	name := strings.TrimSuffix(filepath.Base(path), filepath.Ext(path))
	description := ""
	if kind == "skill" {
		content, _ := os.ReadFile(path)
		name, description = parseFrontmatter(string(content))
		if name == "" {
			name = filepath.Base(filepath.Dir(path))
		}
	} else if kind == "plugin" {
		content, _ := os.ReadFile(path)
		var manifest map[string]any
		_ = json.Unmarshal(content, &manifest)
		if value, ok := manifest["name"].(string); ok {
			name = value
		}
		if value, ok := manifest["description"].(string); ok {
			description = value
		}
	}
	return Asset{
		ID:         shortID(kind + "\x00" + path),
		Kind:       kind,
		Name:       name,
		Description: description,
		Scope:      scope,
		Provider:   provider,
		SourcePath: path,
		Digest:     digest,
		Validation: "valid",
		ALPSState:  "external",
		UpdatedAt:  now(),
	}, nil
}

func parseFrontmatter(value string) (string, string) {
	lines := strings.Split(value, "\n")
	if len(lines) < 3 || strings.TrimSpace(lines[0]) != "---" {
		return "", ""
	}
	name, description := "", ""
	for _, line := range lines[1:] {
		if strings.TrimSpace(line) == "---" {
			break
		}
		key, raw, ok := strings.Cut(line, ":")
		if !ok {
			continue
		}
		switch strings.TrimSpace(key) {
		case "name":
			name = strings.Trim(strings.TrimSpace(raw), "\"")
		case "description":
			description = strings.Trim(strings.TrimSpace(raw), "\"")
		}
	}
	return name, description
}

func digestPath(path string) (string, error) {
	hash := sha256.New()
	info, err := os.Stat(path)
	if err != nil {
		return "", err
	}
	if !info.IsDir() {
		content, err := os.ReadFile(path)
		if err != nil {
			return "", err
		}
		hash.Write(content)
		return "sha256:" + hex.EncodeToString(hash.Sum(nil)), nil
	}
	var files []string
	_ = filepath.WalkDir(path, func(current string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return nil
		}
		if entry.IsDir() {
			if entry.Name() == ".git" {
				return filepath.SkipDir
			}
			return nil
		}
		files = append(files, current)
		return nil
	})
	sort.Strings(files)
	for _, file := range files {
		relative, _ := filepath.Rel(path, file)
		hash.Write([]byte(filepath.ToSlash(relative)))
		content, err := os.ReadFile(file)
		if err == nil {
			hash.Write(content)
		}
	}
	return "sha256:" + hex.EncodeToString(hash.Sum(nil)), nil
}

func shortID(value string) string {
	digest := sha256.Sum256([]byte(value))
	return hex.EncodeToString(digest[:8])
}

func newID(prefix string) string {
	value := make([]byte, 8)
	_, _ = rand.Read(value)
	return prefix + "_" + hex.EncodeToString(value)
}

func now() string { return time.Now().UTC().Format(time.RFC3339Nano) }

func nullIfEmpty(value string) any {
	if value == "" {
		return nil
	}
	return value
}

func (r *Runtime) upsertAsset(ctx context.Context, asset Asset) error {
	var previousDigest, state, revision string
	err := r.db.QueryRowContext(ctx, "SELECT digest,alps_state,COALESCE(adopted_revision_id,'') FROM assets WHERE id=?", asset.ID).Scan(&previousDigest, &state, &revision)
	if err == nil {
		if previousDigest != asset.Digest && state == "adopted" {
			asset.ALPSState = "changed"
		} else {
			asset.ALPSState = state
		}
		asset.AdoptedRevisionID = revision
	}
	_, err = r.db.ExecContext(ctx, `INSERT INTO assets(id,kind,name,description,scope,provider,source_path,digest,validation,alps_state,adopted_revision_id,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,description=excluded.description,digest=excluded.digest,validation=excluded.validation,alps_state=excluded.alps_state,updated_at=excluded.updated_at`, asset.ID, asset.Kind, asset.Name, asset.Description, asset.Scope, asset.Provider, asset.SourcePath, asset.Digest, asset.Validation, asset.ALPSState, nullIfEmpty(asset.AdoptedRevisionID), asset.UpdatedAt)
	return err
}

func (r *Runtime) Catalog(ctx context.Context) ([]Asset, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT id,kind,name,description,scope,provider,source_path,digest,validation,alps_state,COALESCE(adopted_revision_id,''),updated_at FROM assets ORDER BY kind,name`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var assets []Asset
	for rows.Next() {
		var asset Asset
		if err := rows.Scan(&asset.ID, &asset.Kind, &asset.Name, &asset.Description, &asset.Scope, &asset.Provider, &asset.SourcePath, &asset.Digest, &asset.Validation, &asset.ALPSState, &asset.AdoptedRevisionID, &asset.UpdatedAt); err != nil {
			return nil, err
		}
		assets = append(assets, asset)
	}
	return assets, rows.Err()
}

func (r *Runtime) Asset(ctx context.Context, id string) (AssetDetail, error) {
	var asset Asset
	err := r.db.QueryRowContext(ctx, `SELECT id,kind,name,description,scope,provider,source_path,digest,validation,alps_state,COALESCE(adopted_revision_id,''),updated_at FROM assets WHERE id=?`, id).Scan(&asset.ID, &asset.Kind, &asset.Name, &asset.Description, &asset.Scope, &asset.Provider, &asset.SourcePath, &asset.Digest, &asset.Validation, &asset.ALPSState, &asset.AdoptedRevisionID, &asset.UpdatedAt)
	if err != nil {
		return AssetDetail{}, err
	}
	detail := AssetDetail{Asset: asset}
	root := filepath.Dir(asset.SourcePath)
	_ = filepath.WalkDir(root, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return nil
		}
		if entry.IsDir() {
			if entry.Name() == ".git" {
				return filepath.SkipDir
			}
			return nil
		}
		relative, _ := filepath.Rel(root, path)
		detail.Files = append(detail.Files, filepath.ToSlash(relative))
		return nil
	})
	sort.Strings(detail.Files)
	target := asset.SourcePath
	if asset.Kind == "skill" {
		target = filepath.Join(root, "SKILL.md")
	}
	if content, readErr := os.ReadFile(target); readErr == nil && len(content) < 1<<20 {
		detail.Content = string(content)
		detail.ContentPath = filepath.Base(target)
	}
	return detail, nil
}

func (r *Runtime) AssetFile(ctx context.Context, id, relative string) (string, string, error) {
	detail, err := r.Asset(ctx, id)
	if err != nil {
		return "", "", err
	}
	root := filepath.Dir(detail.SourcePath)
	clean := filepath.Clean(filepath.FromSlash(relative))
	if clean == "." || filepath.IsAbs(clean) || strings.HasPrefix(clean, ".."+string(filepath.Separator)) {
		return "", "", errors.New("invalid asset path")
	}
	target := filepath.Join(root, clean)
	absoluteRoot, _ := filepath.Abs(root)
	absoluteTarget, _ := filepath.Abs(target)
	if absoluteTarget != absoluteRoot && !strings.HasPrefix(absoluteTarget, absoluteRoot+string(filepath.Separator)) {
		return "", "", errors.New("asset path leaves package root")
	}
	content, err := os.ReadFile(absoluteTarget)
	if err != nil {
		return "", "", err
	}
	if len(content) > 1<<20 {
		return "", "", errors.New("asset preview exceeds 1 MiB")
	}
	return filepath.ToSlash(clean), string(content), nil
}

func (r *Runtime) Adopt(ctx context.Context, id string) (string, error) {
	detail, err := r.Asset(ctx, id)
	if err != nil {
		return "", err
	}
	revisionID := "rev_" + shortID(id+detail.Digest)
	destination := filepath.Join(r.workspace, "snapshots", detail.Kind, revisionID)
	if err := copyAsset(detail.SourcePath, destination, detail.Kind); err != nil {
		return "", err
	}
	transaction, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return "", err
	}
	defer transaction.Rollback()
	if _, err := transaction.ExecContext(ctx, `INSERT OR IGNORE INTO revisions(id,asset_id,kind,digest,snapshot_path,created_at) VALUES(?,?,?,?,?,?)`, revisionID, id, detail.Kind, detail.Digest, destination, now()); err != nil {
		return "", err
	}
	if _, err := transaction.ExecContext(ctx, `UPDATE assets SET alps_state='adopted',adopted_revision_id=? WHERE id=?`, revisionID, id); err != nil {
		return "", err
	}
	if err := appendEventTx(ctx, transaction, "asset", id, "asset.adopted", map[string]any{"revisionId": revisionID}); err != nil {
		return "", err
	}
	if err := transaction.Commit(); err != nil {
		return "", err
	}
	r.publishLatest(ctx)
	return revisionID, nil
}

func copyAsset(source, destination, kind string) error {
	root := source
	if kind == "skill" {
		root = filepath.Dir(source)
	}
	info, err := os.Stat(root)
	if err != nil {
		return err
	}
	if !info.IsDir() {
		if err := os.MkdirAll(filepath.Dir(destination), 0o700); err != nil {
			return err
		}
		return copyFile(root, destination)
	}
	return filepath.WalkDir(root, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		relative, _ := filepath.Rel(root, path)
		target := filepath.Join(destination, relative)
		if entry.IsDir() {
			return os.MkdirAll(target, 0o700)
		}
		return copyFile(path, target)
	})
}

func copyFile(source, destination string) error {
	if err := os.MkdirAll(filepath.Dir(destination), 0o700); err != nil {
		return err
	}
	input, err := os.Open(source)
	if err != nil {
		return err
	}
	defer input.Close()
	output, err := os.Create(destination)
	if err != nil {
		return err
	}
	_, copyErr := io.Copy(output, input)
	closeErr := output.Close()
	if copyErr != nil {
		return copyErr
	}
	return closeErr
}

func (r *Runtime) CreateRun(ctx context.Context, title, process, assetID string) (Run, error) {
	if strings.TrimSpace(title) == "" || strings.TrimSpace(process) == "" {
		return Run{}, errors.New("title and process are required")
	}
	id, timestamp := newID("run"), now()
	run := Run{ID: id, Title: title, Process: process, AssetID: assetID, State: "active", Version: 1, StatusText: "Started", CreatedAt: timestamp, UpdatedAt: timestamp}
	transaction, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return Run{}, err
	}
	defer transaction.Rollback()
	if _, err := transaction.ExecContext(ctx, `INSERT INTO runs(id,title,process,asset_id,state,version,status_text,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)`, id, title, process, nullIfEmpty(assetID), run.State, run.Version, run.StatusText, timestamp, timestamp); err != nil {
		return Run{}, err
	}
	if err := appendEventTx(ctx, transaction, "run", id, "run.created", run); err != nil {
		return Run{}, err
	}
	if err := transaction.Commit(); err != nil {
		return Run{}, err
	}
	r.publishLatest(ctx)
	return run, nil
}

func (r *Runtime) Runs(ctx context.Context) ([]Run, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT id,title,process,COALESCE(asset_id,''),state,version,progress,status_text,created_at,updated_at FROM runs ORDER BY updated_at DESC`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var runs []Run
	for rows.Next() {
		var run Run
		var progress sql.NullInt64
		if err := rows.Scan(&run.ID, &run.Title, &run.Process, &run.AssetID, &run.State, &run.Version, &progress, &run.StatusText, &run.CreatedAt, &run.UpdatedAt); err != nil {
			return nil, err
		}
		if progress.Valid {
			value := int(progress.Int64)
			run.Progress = &value
		}
		runs = append(runs, run)
	}
	return runs, rows.Err()
}

func (r *Runtime) Run(ctx context.Context, id string) (Run, error) {
	var run Run
	var progress sql.NullInt64
	err := r.db.QueryRowContext(ctx, `SELECT id,title,process,COALESCE(asset_id,''),state,version,progress,status_text,created_at,updated_at FROM runs WHERE id=?`, id).Scan(&run.ID, &run.Title, &run.Process, &run.AssetID, &run.State, &run.Version, &progress, &run.StatusText, &run.CreatedAt, &run.UpdatedAt)
	if progress.Valid {
		value := int(progress.Int64)
		run.Progress = &value
	}
	return run, err
}

func (r *Runtime) RunDetail(ctx context.Context, id string) (RunDetail, error) {
	run, err := r.Run(ctx, id)
	if err != nil {
		return RunDetail{}, err
	}
	detail := RunDetail{Run: run}
	var gate Gate
	err = r.db.QueryRowContext(ctx, `SELECT id,run_id,title,effect,reversible,authority,status,expected_run_version,created_at FROM decision_gates WHERE run_id=? AND status='open' ORDER BY created_at DESC LIMIT 1`, id).Scan(&gate.ID, &gate.RunID, &gate.Title, &gate.Effect, &gate.Reversible, &gate.Authority, &gate.Status, &gate.ExpectedRunVersion, &gate.CreatedAt)
	if err == nil {
		detail.Gate = &gate
	} else if !errors.Is(err, sql.ErrNoRows) {
		return RunDetail{}, err
	}
	detail.Events, err = r.EventsForStream(ctx, "run", id, 100)
	return detail, err
}

func (r *Runtime) ReportRun(ctx context.Context, id, actor, message string, progress *int, expected int64) (Run, error) {
	transaction, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return Run{}, err
	}
	defer transaction.Rollback()
	var version int64
	if err := transaction.QueryRowContext(ctx, "SELECT version FROM runs WHERE id=?", id).Scan(&version); err != nil {
		return Run{}, err
	}
	if expected > 0 && version != expected {
		return Run{}, ErrStale
	}
	newVersion := version + 1
	if _, err := transaction.ExecContext(ctx, `UPDATE runs SET version=?,progress=?,status_text=?,updated_at=? WHERE id=?`, newVersion, progress, message, now(), id); err != nil {
		return Run{}, err
	}
	if _, err := transaction.ExecContext(ctx, `INSERT INTO run_reports(id,run_id,actor,message,progress,created_at) VALUES(?,?,?,?,?,?)`, newID("report"), id, actor, message, progress, now()); err != nil {
		return Run{}, err
	}
	if err := appendEventTx(ctx, transaction, "run", id, "run.reported", map[string]any{"actor": actor, "message": message, "progress": progress, "version": newVersion}); err != nil {
		return Run{}, err
	}
	if err := transaction.Commit(); err != nil {
		return Run{}, err
	}
	r.publishLatest(ctx)
	return r.Run(ctx, id)
}

func (r *Runtime) OpenGate(ctx context.Context, runID, title, effect, authority string, reversible bool, expected int64) (Gate, error) {
	transaction, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return Gate{}, err
	}
	defer transaction.Rollback()
	var version int64
	if err := transaction.QueryRowContext(ctx, "SELECT version FROM runs WHERE id=?", runID).Scan(&version); err != nil {
		return Gate{}, err
	}
	if expected > 0 && version != expected {
		return Gate{}, ErrStale
	}
	gate := Gate{ID: newID("gate"), RunID: runID, Title: title, Effect: effect, Reversible: reversible, Authority: authority, Status: "open", ExpectedRunVersion: version + 1, CreatedAt: now()}
	if _, err := transaction.ExecContext(ctx, `INSERT INTO decision_gates(id,run_id,title,effect,reversible,authority,status,expected_run_version,created_at) VALUES(?,?,?,?,?,?,?,?,?)`, gate.ID, runID, title, effect, reversible, authority, gate.Status, gate.ExpectedRunVersion, gate.CreatedAt); err != nil {
		return Gate{}, err
	}
	if _, err := transaction.ExecContext(ctx, `UPDATE runs SET state='waiting_for_decision',version=version+1,status_text=?,updated_at=? WHERE id=?`, title, now(), runID); err != nil {
		return Gate{}, err
	}
	if err := appendEventTx(ctx, transaction, "run", runID, "gate.opened", gate); err != nil {
		return Gate{}, err
	}
	if err := transaction.Commit(); err != nil {
		return Gate{}, err
	}
	r.publishLatest(ctx)
	return gate, nil
}

func (r *Runtime) Gates(ctx context.Context) ([]Gate, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT id,run_id,title,effect,reversible,authority,status,expected_run_version,created_at FROM decision_gates WHERE status='open' ORDER BY created_at`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var gates []Gate
	for rows.Next() {
		var gate Gate
		if err := rows.Scan(&gate.ID, &gate.RunID, &gate.Title, &gate.Effect, &gate.Reversible, &gate.Authority, &gate.Status, &gate.ExpectedRunVersion, &gate.CreatedAt); err != nil {
			return nil, err
		}
		gates = append(gates, gate)
	}
	return gates, rows.Err()
}

func (r *Runtime) Decide(ctx context.Context, gateID, decision, actor, rationale string, expected int64) error {
	transaction, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return err
	}
	defer transaction.Rollback()
	var runID, status string
	var gateVersion int64
	if err := transaction.QueryRowContext(ctx, `SELECT run_id,status,expected_run_version FROM decision_gates WHERE id=?`, gateID).Scan(&runID, &status, &gateVersion); err != nil {
		return err
	}
	if status != "open" {
		return ErrStale
	}
	var runVersion int64
	if err := transaction.QueryRowContext(ctx, "SELECT version FROM runs WHERE id=?", runID).Scan(&runVersion); err != nil {
		return err
	}
	if expected > 0 && runVersion != expected || gateVersion != runVersion {
		return ErrStale
	}
	final := decision != "hold"
	newState := "waiting_for_decision"
	if final {
		newState = "active"
	}
	if decision == "terminate" {
		newState = "cancelled"
	}
	if _, err := transaction.ExecContext(ctx, `INSERT INTO decisions(id,gate_id,decision_type,actor,rationale,final,created_at) VALUES(?,?,?,?,?,?,?)`, newID("decision"), gateID, decision, actor, rationale, final, now()); err != nil {
		return err
	}
	if final {
		if _, err := transaction.ExecContext(ctx, `UPDATE decision_gates SET status='decided',decided_at=? WHERE id=?`, now(), gateID); err != nil {
			return err
		}
	}
	if _, err := transaction.ExecContext(ctx, `UPDATE runs SET state=?,version=version+1,status_text=?,updated_at=? WHERE id=?`, newState, decision, now(), runID); err != nil {
		return err
	}
	if err := appendEventTx(ctx, transaction, "run", runID, "decision.recorded", map[string]any{"gateId": gateID, "decision": decision, "actor": actor, "final": final}); err != nil {
		return err
	}
	if err := transaction.Commit(); err != nil {
		return err
	}
	r.publishLatest(ctx)
	return nil
}

func (r *Runtime) AddArtifact(ctx context.Context, runID, name, mediaType string, data []byte) (string, error) {
	digestBytes := sha256.Sum256(data)
	digestHex := hex.EncodeToString(digestBytes[:])
	digest := "sha256:" + digestHex
	path := filepath.Join(r.workspace, "blobs", "sha256", digestHex)
	if _, err := os.Stat(path); errors.Is(err, os.ErrNotExist) {
		temporary := path + ".tmp"
		if err := os.WriteFile(temporary, data, 0o600); err != nil {
			return "", err
		}
		if err := os.Rename(temporary, path); err != nil {
			return "", err
		}
	}
	artifactID := newID("artifact")
	transaction, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return "", err
	}
	defer transaction.Rollback()
	if _, err := transaction.ExecContext(ctx, `INSERT INTO artifacts(id,run_id,name,digest,media_type,size,path,created_at) VALUES(?,?,?,?,?,?,?,?)`, artifactID, runID, name, digest, mediaType, len(data), path, now()); err != nil {
		return "", err
	}
	if err := appendEventTx(ctx, transaction, "run", runID, "artifact.committed", map[string]any{"artifactId": artifactID, "name": name, "digest": digest}); err != nil {
		return "", err
	}
	if err := transaction.Commit(); err != nil {
		return "", err
	}
	r.publishLatest(ctx)
	return artifactID, nil
}

func (r *Runtime) RecordUsage(ctx context.Context, runID, requested, effective, resolved, effort, source string, input, output, cacheRead, cacheWrite, reasoning *int64) error {
	invocationID := newID("inv")
	transaction, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return err
	}
	defer transaction.Rollback()
	if _, err := transaction.ExecContext(ctx, `INSERT INTO model_invocations(id,run_id,requested_model,effective_model,resolved_model,effort,role,created_at) VALUES(?,?,?,?,?,?,?,?)`, invocationID, runID, requested, effective, resolved, effort, "main", now()); err != nil {
		return err
	}
	if _, err := transaction.ExecContext(ctx, `INSERT INTO usage_observations(id,invocation_id,run_id,source,status,input_tokens,output_tokens,cache_read_tokens,cache_write_tokens,reasoning_tokens,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)`, newID("usage"), invocationID, runID, source, "reported", input, output, cacheRead, cacheWrite, reasoning, now()); err != nil {
		return err
	}
	if err := appendEventTx(ctx, transaction, "run", runID, "usage.observed", map[string]any{"invocationId": invocationID, "source": source}); err != nil {
		return err
	}
	return transaction.Commit()
}

func (r *Runtime) Analysis(ctx context.Context) (Analysis, error) {
	var analysis Analysis
	_ = r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM assets").Scan(&analysis.Assets)
	_ = r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM runs WHERE state IN ('created','active')").Scan(&analysis.Active)
	_ = r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM runs WHERE state LIKE 'waiting_%' OR state='completion_requested'").Scan(&analysis.Waiting)
	_ = r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM runs WHERE state='completed'").Scan(&analysis.Completed)
	_ = r.db.QueryRowContext(ctx, "SELECT COUNT(*) FROM decision_gates WHERE status='open'").Scan(&analysis.Gates)
	_ = r.db.QueryRowContext(ctx, "SELECT COALESCE(SUM(COALESCE(input_tokens,0)+COALESCE(output_tokens,0)),0) FROM usage_observations").Scan(&analysis.Tokens)
	return analysis, nil
}

func (r *Runtime) Graph(ctx context.Context) (Graph, error) {
	assets, err := r.Catalog(ctx)
	if err != nil {
		return Graph{}, err
	}
	graph := Graph{}
	for _, asset := range assets {
		if asset.Kind == "skill" {
			graph.Processes = append(graph.Processes, GraphNode{ID: "process_" + asset.ID, Name: asset.Name, Kind: "process"})
		}
	}
	if len(graph.Processes) == 0 {
		graph.Processes = []GraphNode{{ID: "process_define", Name: "Define Skills", Kind: "process"}, {ID: "process_manage", Name: "Manage Skills", Kind: "process"}, {ID: "process_apply", Name: "Apply Skills", Kind: "process"}}
	}
	find := func(needle, fallback string) string {
		for _, node := range graph.Processes {
			if strings.Contains(strings.ToLower(node.Name), needle) {
				return node.ID
			}
		}
		return fallback
	}
	defineID := find("define", graph.Processes[0].ID)
	manageID := find("manage", graph.Processes[min(1, len(graph.Processes)-1)].ID)
	applyID := find("apply", graph.Processes[min(2, len(graph.Processes)-1)].ID)
	graph.Interfaces = []GraphNode{{ID: "interface_verified", Name: "Verified Skill", Kind: "interface"}, {ID: "interface_managed", Name: "Managed Skill", Kind: "interface"}, {ID: "interface_records", Name: "Execution Records", Kind: "interface"}, {ID: "interface_change", Name: "Change Request", Kind: "interface"}}
	graph.Edges = []GraphEdge{{From: defineID, To: "interface_verified", Kind: "produces"}, {From: "interface_verified", To: manageID, Kind: "consumes"}, {From: manageID, To: "interface_managed", Kind: "produces"}, {From: "interface_managed", To: applyID, Kind: "consumes"}, {From: applyID, To: "interface_records", Kind: "produces"}, {From: "interface_records", To: manageID, Kind: "consumes"}, {From: manageID, To: "interface_change", Kind: "produces"}, {From: "interface_change", To: defineID, Kind: "consumes"}}
	runs, _ := r.Runs(ctx)
	for _, run := range runs {
		if run.State != "active" && !strings.HasPrefix(run.State, "waiting_") {
			continue
		}
		needle := strings.ToLower(run.Process)
		if fields := strings.Fields(needle); len(fields) > 0 {
			needle = fields[0]
		}
		graph.Live = append(graph.Live, GraphLive{RunID: run.ID, ProcessID: find(needle, applyID), State: run.State})
	}
	return graph, nil
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func appendEventTx(ctx context.Context, transaction *sql.Tx, streamType, streamID, eventType string, payload any) error {
	encoded, _ := json.Marshal(payload)
	_, err := transaction.ExecContext(ctx, `INSERT INTO domain_events(event_id,stream_type,stream_id,event_type,payload,occurred_at) VALUES(?,?,?,?,?,?)`, newID("event"), streamType, streamID, eventType, string(encoded), now())
	return err
}

func (r *Runtime) appendEvent(ctx context.Context, streamType, streamID, eventType string, payload any) (Event, error) {
	transaction, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return Event{}, err
	}
	defer transaction.Rollback()
	if err := appendEventTx(ctx, transaction, streamType, streamID, eventType, payload); err != nil {
		return Event{}, err
	}
	if err := transaction.Commit(); err != nil {
		return Event{}, err
	}
	r.publishLatest(ctx)
	return r.latestEvent(ctx)
}

func (r *Runtime) latestEvent(ctx context.Context) (Event, error) {
	var event Event
	var payload string
	err := r.db.QueryRowContext(ctx, `SELECT sequence,event_type,stream_type,stream_id,payload,occurred_at FROM domain_events ORDER BY sequence DESC LIMIT 1`).Scan(&event.Sequence, &event.Type, &event.StreamType, &event.StreamID, &payload, &event.OccurredAt)
	event.Payload = json.RawMessage(payload)
	return event, err
}

func (r *Runtime) publishLatest(ctx context.Context) {
	event, err := r.latestEvent(ctx)
	if err != nil {
		return
	}
	r.mu.RLock()
	defer r.mu.RUnlock()
	for subscriber := range r.subscribers {
		select {
		case subscriber <- event:
		default:
		}
	}
}

func (r *Runtime) Subscribe() (chan Event, func()) {
	channel := make(chan Event, 32)
	r.mu.Lock()
	r.subscribers[channel] = struct{}{}
	r.mu.Unlock()
	return channel, func() {
		r.mu.Lock()
		delete(r.subscribers, channel)
		close(channel)
		r.mu.Unlock()
	}
}

func (r *Runtime) EventsAfter(ctx context.Context, sequence int64) ([]Event, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT sequence,event_type,stream_type,stream_id,payload,occurred_at FROM domain_events WHERE sequence>? ORDER BY sequence LIMIT 500`, sequence)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var events []Event
	for rows.Next() {
		var event Event
		var payload string
		if err := rows.Scan(&event.Sequence, &event.Type, &event.StreamType, &event.StreamID, &payload, &event.OccurredAt); err != nil {
			return nil, err
		}
		event.Payload = json.RawMessage(payload)
		events = append(events, event)
	}
	return events, rows.Err()
}

func (r *Runtime) EventsForStream(ctx context.Context, streamType, streamID string, limit int) ([]Event, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT sequence,event_type,stream_type,stream_id,payload,occurred_at FROM domain_events WHERE stream_type=? AND stream_id=? ORDER BY sequence DESC LIMIT ?`, streamType, streamID, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var events []Event
	for rows.Next() {
		var event Event
		var payload string
		if err := rows.Scan(&event.Sequence, &event.Type, &event.StreamType, &event.StreamID, &payload, &event.OccurredAt); err != nil {
			return nil, err
		}
		event.Payload = json.RawMessage(payload)
		events = append(events, event)
	}
	return events, rows.Err()
}

func (r *Runtime) HostObservation(ctx context.Context, host, eventName string, raw json.RawMessage) error {
	observationID := newID("hostobs")
	if _, err := r.db.ExecContext(ctx, `INSERT INTO host_observations(id,host,event_name,raw_json,created_at) VALUES(?,?,?,?,?)`, observationID, host, eventName, string(raw), now()); err != nil {
		return err
	}
	_, err := r.appendEvent(ctx, "host", host, "host.observed", map[string]any{"id": observationID, "event": eventName})
	return err
}

func (r *Runtime) Backup(ctx context.Context) (string, error) {
	path := filepath.Join(r.workspace, "backups", "alps-"+time.Now().UTC().Format("20060102T150405Z")+".sqlite3")
	escaped := strings.ReplaceAll(path, "'", "''")
	_, err := r.db.ExecContext(ctx, "VACUUM INTO '"+escaped+"'")
	return path, err
}

func (r *Runtime) ExportRun(ctx context.Context, id string) (map[string]any, error) {
	run, err := r.Run(ctx, id)
	if err != nil {
		return nil, err
	}
	events, err := r.EventsForStream(ctx, "run", id, 10000)
	if err != nil {
		return nil, err
	}
	return map[string]any{"run": run, "events": events, "exportedAt": now()}, nil
}
