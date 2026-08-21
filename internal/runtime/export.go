package runtime

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

type BackupResult struct {
	Path      string `json:"path"`
	CreatedAt string `json:"createdAt"`
	Size      int64  `json:"size"`
}

type AuditBundle struct {
	SchemaVersion string         `json:"schemaVersion"`
	Run           RunDetail      `json:"run"`
	ArtifactFiles []ArtifactFile `json:"artifactFiles"`
	ExportedAt    string         `json:"exportedAt"`
}

type ArtifactFile struct {
	ID        string `json:"id"`
	Name      string `json:"name"`
	Digest    string `json:"digest"`
	MediaType string `json:"mediaType"`
	Size      int64  `json:"size"`
	BlobURI   string `json:"blobUri"`
}

func (r *Runtime) Backup(ctx context.Context) (string, error) {
	result, err := r.CreateBackup(ctx)
	return result.Path, err
}

func (r *Runtime) CreateBackup(ctx context.Context) (BackupResult, error) {
	path := filepath.Join(r.workspace, "backups", "alps-"+time.Now().UTC().Format("20060102T150405.000000000Z")+".sqlite3")
	escaped := strings.ReplaceAll(path, "'", "''")
	r.writeMu.Lock()
	_, err := r.db.ExecContext(ctx, "VACUUM INTO '"+escaped+"'")
	r.writeMu.Unlock()
	if err != nil {
		return BackupResult{}, err
	}
	info, err := os.Stat(path)
	if err != nil {
		return BackupResult{}, err
	}
	return BackupResult{Path: path, CreatedAt: now(), Size: info.Size()}, nil
}

func (r *Runtime) ExportRun(ctx context.Context, id string) (map[string]any, error) {
	bundle, err := r.RunAuditBundle(ctx, id)
	if err != nil {
		return nil, err
	}
	encoded, _ := json.Marshal(bundle)
	var value map[string]any
	_ = json.Unmarshal(encoded, &value)
	return value, nil
}

func (r *Runtime) RunAuditBundle(ctx context.Context, id string) (AuditBundle, error) {
	detail, err := r.RunDetail(ctx, id)
	if err != nil {
		return AuditBundle{}, err
	}
	bundle := AuditBundle{SchemaVersion: "alps.dev/run-audit/v1", Run: detail, ExportedAt: now()}
	for _, artifact := range detail.Artifacts {
		bundle.ArtifactFiles = append(bundle.ArtifactFiles, ArtifactFile{ID: artifact.ID, Name: artifact.Name, Digest: artifact.Digest, MediaType: artifact.MediaType, Size: artifact.Size, BlobURI: "file://" + filepath.ToSlash(artifact.Path)})
	}
	return bundle, nil
}

func (r *Runtime) WriteRunAuditBundle(ctx context.Context, id, destination string) (string, error) {
	bundle, err := r.RunAuditBundle(ctx, id)
	if err != nil {
		return "", err
	}
	if destination == "" {
		destination = filepath.Join(r.workspace, "exports", "runs", "alps-run-"+id+".json")
	}
	absolute, err := filepath.Abs(destination)
	if err != nil {
		return "", err
	}
	if err := os.MkdirAll(filepath.Dir(absolute), 0o700); err != nil {
		return "", err
	}
	encoded, err := json.MarshalIndent(bundle, "", "  ")
	if err != nil {
		return "", err
	}
	temporary := absolute + ".tmp"
	file, err := os.OpenFile(temporary, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0o600)
	if err != nil {
		return "", err
	}
	_, writeErr := file.Write(encoded)
	syncErr := file.Sync()
	closeErr := file.Close()
	if err := errors.Join(writeErr, syncErr, closeErr); err != nil {
		_ = os.Remove(temporary)
		return "", err
	}
	if err := os.Rename(temporary, absolute); err != nil {
		_ = os.Remove(temporary)
		return "", err
	}
	return absolute, nil
}

func (r *Runtime) DatabaseIntegrity(ctx context.Context) error {
	var result string
	if err := r.db.QueryRowContext(ctx, `PRAGMA integrity_check`).Scan(&result); err != nil {
		return err
	}
	if result != "ok" {
		return fmt.Errorf("database integrity check: %s", result)
	}
	var violations int
	rows, err := r.db.QueryContext(ctx, `PRAGMA foreign_key_check`)
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
		violations++
	}
	if violations > 0 {
		return fmt.Errorf("database has %d foreign-key violation(s)", violations)
	}
	return rows.Err()
}

func scanNullString(row *sql.Row) (string, error) {
	var value sql.NullString
	if err := row.Scan(&value); err != nil {
		return "", err
	}
	if !value.Valid {
		return "", nil
	}
	return value.String, nil
}
