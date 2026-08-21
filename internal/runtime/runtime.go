package runtime

import (
	"context"
	"crypto/rand"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/mashimashica/alps/internal/domain"
	alpstelemetry "github.com/mashimashica/alps/internal/telemetry"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/metric"

	_ "modernc.org/sqlite"
)

type Root struct {
	Path     string `json:"path"`
	Scope    string `json:"scope"`
	Provider string `json:"provider"`
	Realm    string `json:"realm,omitempty"`
	Host     string `json:"host,omitempty"`
}

type Runtime struct {
	db            *sql.DB
	workspace     string
	token         string
	rootsMu       sync.RWMutex
	roots         []Root
	writeMu       sync.Mutex
	idempotencyMu sync.Mutex
	subMu         sync.RWMutex
	subscribers   map[chan domain.Event]struct{}
	telemetry     *alpstelemetry.Runtime
	stopOutbox    context.CancelFunc
}

type contextActorKey struct{}

type CommandResult struct {
	Status int
	Body   []byte
}

var (
	ErrStale             = errors.New("stale version")
	ErrNotFound          = errors.New("not found")
	ErrConflict          = errors.New("conflict")
	ErrInvalid           = errors.New("invalid input")
	ErrForbidden         = errors.New("forbidden")
	ErrCompletionBlocked = errors.New("completion blocked")
)

func WithActor(ctx context.Context, actor domain.Actor) context.Context {
	return context.WithValue(ctx, contextActorKey{}, actor)
}

func ActorFromContext(ctx context.Context) domain.Actor {
	if actor, ok := ctx.Value(contextActorKey{}).(domain.Actor); ok {
		if actor.Type == "" {
			actor.Type = domain.ActorSystem
		}
		if actor.Channel == "" {
			actor.Channel = domain.ChannelInternal
		}
		return actor
	}
	return domain.Actor{Type: domain.ActorSystem, Channel: domain.ChannelInternal}
}

func Open(workspace string) (*Runtime, error) {
	for _, directory := range []string{
		"db", "blobs/sha256", "snapshots/skill", "snapshots/plugin", "snapshots/process-model",
		"backups", "exports/runs", "runtime",
	} {
		if err := os.MkdirAll(filepath.Join(workspace, directory), 0o700); err != nil {
			return nil, err
		}
	}
	token, err := ensureToken(filepath.Join(workspace, "runtime", "access.token"))
	if err != nil {
		return nil, err
	}
	databasePath := filepath.Join(workspace, "db", "alps.sqlite3")
	database, err := sql.Open("sqlite", databasePath)
	if err != nil {
		return nil, err
	}
	database.SetMaxOpenConns(8)
	database.SetMaxIdleConns(4)
	runtime := &Runtime{
		db:          database,
		workspace:   workspace,
		token:       token,
		subscribers: map[chan domain.Event]struct{}{},
	}
	if err := runtime.migrate(); err != nil {
		_ = database.Close()
		return nil, err
	}
	telemetryRuntime, err := alpstelemetry.Setup(context.Background(), "alps-local-runtime")
	if err != nil {
		_ = database.Close()
		return nil, err
	}
	runtime.telemetry = telemetryRuntime
	outboxContext, cancel := context.WithCancel(context.Background())
	runtime.stopOutbox = cancel
	go runtime.exportOutbox(outboxContext)
	return runtime, nil
}

func (r *Runtime) Close() error {
	if r.stopOutbox != nil {
		r.stopOutbox()
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	telemetryErr := r.telemetry.Shutdown(ctx)
	databaseErr := r.db.Close()
	return errors.Join(telemetryErr, databaseErr)
}

func (r *Runtime) Token() string     { return r.token }
func (r *Runtime) Workspace() string { return r.workspace }
func (r *Runtime) DB() *sql.DB       { return r.db }

func (r *Runtime) SetRoots(roots []Root) {
	r.rootsMu.Lock()
	defer r.rootsMu.Unlock()
	copyRoots := make([]Root, len(roots))
	copy(copyRoots, roots)
	r.roots = copyRoots
}

func (r *Runtime) Roots() []Root {
	r.rootsMu.RLock()
	defer r.rootsMu.RUnlock()
	copyRoots := make([]Root, len(r.roots))
	copy(copyRoots, r.roots)
	return copyRoots
}

func DefaultRoots(project string) []Root {
	project, _ = filepath.Abs(project)
	roots := []Root{{Path: project, Scope: "project", Provider: "configured-directory", Realm: "local"}}
	home, err := os.UserHomeDir()
	if err != nil {
		return roots
	}
	candidates := []struct {
		path     string
		provider string
		host     string
	}{
		{filepath.Join(home, ".agents", "skills"), "common-agent-skills", ""},
		{filepath.Join(home, ".claude", "skills"), "claude-code", "claude-code"},
		{filepath.Join(home, ".claude", "plugins"), "claude-code", "claude-code"},
		{filepath.Join(home, ".codex", "skills"), "codex", "codex"},
		{filepath.Join(home, ".codex", "plugins"), "codex", "codex"},
		{filepath.Join(home, ".cursor", "skills"), "cursor", "cursor"},
		{filepath.Join(home, ".cursor", "plugins"), "cursor", "cursor"},
		{filepath.Join(home, ".copilot", "skills"), "github-copilot-cli", "github-copilot-cli"},
		{filepath.Join(home, ".vscode", "skills"), "vscode", "vscode"},
	}
	for _, candidate := range candidates {
		if info, statErr := os.Stat(candidate.path); statErr == nil && info.IsDir() {
			roots = append(roots, Root{Path: candidate.path, Scope: "user", Provider: candidate.provider, Host: candidate.host, Realm: "local"})
		}
	}
	return roots
}

func (r *Runtime) WriteEndpoint(url string) error {
	data, _ := json.MarshalIndent(map[string]any{
		"url":       url,
		"pid":       os.Getpid(),
		"startedAt": now(),
		"workspace": r.workspace,
	}, "", "  ")
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

func (r *Runtime) write(ctx context.Context, command string, operation func(*sql.Tx) error) error {
	started := time.Now()
	r.writeMu.Lock()
	defer r.writeMu.Unlock()
	transaction, err := r.db.BeginTx(ctx, &sql.TxOptions{})
	if err != nil {
		return err
	}
	defer transaction.Rollback()
	if err := operation(transaction); err != nil {
		return err
	}
	if err := transaction.Commit(); err != nil {
		return err
	}
	if r.telemetry != nil {
		attributes := metric.WithAttributes(attribute.String("alps.command", command))
		r.telemetry.Commands.Add(ctx, 1, attributes)
		r.telemetry.CommandDuration.Record(ctx, float64(time.Since(started).Microseconds())/1000, attributes)
	}
	return nil
}

func (r *Runtime) Idempotent(ctx context.Context, key, command, requestDigest string, operation func() (CommandResult, error)) (CommandResult, error) {
	if strings.TrimSpace(key) == "" {
		return CommandResult{}, fmt.Errorf("%w: Idempotency-Key is required", ErrInvalid)
	}
	r.idempotencyMu.Lock()
	defer r.idempotencyMu.Unlock()
	var status int
	var body []byte
	var storedDigest string
	err := r.db.QueryRowContext(ctx, `SELECT status_code,response_json,request_digest FROM idempotency_keys WHERE key=?`, key).Scan(&status, &body, &storedDigest)
	if err == nil {
		if storedDigest != requestDigest {
			return CommandResult{}, fmt.Errorf("%w: idempotency key was used with a different request", ErrConflict)
		}
		return CommandResult{Status: status, Body: body}, nil
	}
	if !errors.Is(err, sql.ErrNoRows) {
		return CommandResult{}, err
	}
	result, err := operation()
	if err != nil {
		return CommandResult{}, err
	}
	_, err = r.db.ExecContext(ctx, `INSERT INTO idempotency_keys(key,command,request_digest,status_code,response_json,created_at) VALUES(?,?,?,?,?,?)`, key, command, requestDigest, result.Status, result.Body, now())
	return result, err
}

func RequestDigest(method, path string, body []byte) string {
	digest := sha256.Sum256(append([]byte(method+"\x00"+path+"\x00"), body...))
	return "sha256:" + hex.EncodeToString(digest[:])
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

func newID(prefix string) string {
	value := make([]byte, 12)
	_, _ = rand.Read(value)
	return prefix + "_" + hex.EncodeToString(value)
}

func shortID(value string) string {
	digest := sha256.Sum256([]byte(value))
	return hex.EncodeToString(digest[:12])
}

func now() string { return time.Now().UTC().Format(time.RFC3339Nano) }

func nullIfEmpty(value string) any {
	if value == "" {
		return nil
	}
	return value
}

func marshal(value any) string {
	encoded, _ := json.Marshal(value)
	return string(encoded)
}
