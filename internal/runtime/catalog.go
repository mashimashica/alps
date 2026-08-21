package runtime

import (
	"context"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/mashimashica/alps/internal/domain"
	alpsmodel "github.com/mashimashica/alps/internal/model"
)

type Asset struct {
	ID                 string              `json:"id"`
	Kind               string              `json:"kind"`
	Name               string              `json:"name"`
	Description        string              `json:"description"`
	Scope              string              `json:"scope"`
	Provider           string              `json:"provider"`
	Realm              string              `json:"realm,omitempty"`
	Host               string              `json:"host,omitempty"`
	SourcePath         string              `json:"sourcePath"`
	SourceURI          string              `json:"sourceUri"`
	Digest             string              `json:"digest"`
	SourceState        string              `json:"sourceState"`
	Validation         string              `json:"validation"`
	ValidationIssues   []ValidationIssue   `json:"validationIssues,omitempty"`
	HostState          string              `json:"hostState"`
	ALPSState          string              `json:"alpsState"`
	CaptureMode        string              `json:"captureMode"`
	AdoptedRevisionID  string              `json:"adoptedRevisionId,omitempty"`
	ExecutableSurfaces []ExecutableSurface `json:"executableSurfaces,omitempty"`
	UpdatedAt          string              `json:"updatedAt"`
	LastSeenAt         string              `json:"lastSeenAt,omitempty"`
}

type ValidationIssue struct {
	Path     string `json:"path"`
	Code     string `json:"code"`
	Message  string `json:"message"`
	Severity string `json:"severity"`
}

type ExecutableSurface struct {
	Path string `json:"path"`
	Kind string `json:"kind"`
}

type ManifestFile struct {
	Path       string `json:"path"`
	Digest     string `json:"digest"`
	Size       int64  `json:"size"`
	Executable bool   `json:"executable"`
}

type ResourceManifest struct {
	Root  string         `json:"root"`
	Files []ManifestFile `json:"files"`
}

type AssetDetail struct {
	Asset
	Files       []string         `json:"files"`
	Content     string           `json:"content"`
	ContentPath string           `json:"contentPath"`
	Manifest    ResourceManifest `json:"manifest"`
}

type DiffEntry struct {
	Path   string `json:"path"`
	Status string `json:"status"`
	Before string `json:"before,omitempty"`
	After  string `json:"after,omitempty"`
}

type AssetDiff struct {
	AssetID            string              `json:"assetId"`
	AdoptedRevisionID  string              `json:"adoptedRevisionId,omitempty"`
	Entries            []DiffEntry         `json:"entries"`
	ExecutableSurfaces []ExecutableSurface `json:"executableSurfaces"`
}

type skillDescription struct {
	Name        string
	Description string
	Purpose     string
	Outcomes    []string
	ALPSVersion string
}

func (r *Runtime) Scan(ctx context.Context) ([]Asset, error) {
	roots := r.Roots()
	seen := map[string]struct{}{}
	for _, root := range roots {
		absoluteRoot, err := filepath.Abs(root.Path)
		if err != nil {
			continue
		}
		if _, err := os.Stat(absoluteRoot); err != nil {
			continue
		}
		sourceID := "source_" + shortID(root.Provider+"\x00"+root.Scope+"\x00"+root.Realm+"\x00"+absoluteRoot+"\x00"+root.Host)
		_, _ = r.db.ExecContext(ctx, `INSERT INTO asset_sources(id,provider,scope,realm,root_uri,host,last_seen_at) VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET last_seen_at=excluded.last_seen_at`, sourceID, root.Provider, root.Scope, defaultString(root.Realm, "local"), fileURI(absoluteRoot), nullIfEmpty(root.Host), now())
		err = filepath.WalkDir(absoluteRoot, func(path string, entry fs.DirEntry, walkErr error) error {
			if walkErr != nil {
				return nil
			}
			if entry.IsDir() {
				if skipDiscoveryDirectory(entry.Name()) && path != absoluteRoot {
					return filepath.SkipDir
				}
				return nil
			}
			kind := detectedKind(path, entry.Name())
			if kind == "" {
				return nil
			}
			asset, inspectErr := inspectAsset(path, kind, root, sourceID)
			if inspectErr != nil {
				return nil
			}
			seen[asset.ID] = struct{}{}
			if err := r.upsertAsset(ctx, asset); err != nil {
				return err
			}
			return nil
		})
		if err != nil {
			return nil, err
		}
	}
	if err := r.markMissing(ctx, roots, seen); err != nil {
		return nil, err
	}
	assets, err := r.Catalog(ctx)
	if err != nil {
		return nil, err
	}
	_, _ = r.appendEvent(WithActor(ctx, domain.Actor{Type: domain.ActorSystem, Channel: domain.ChannelInternal}), "catalog", "global", "catalog.scanned", map[string]any{"count": len(assets)})
	return assets, nil
}

func detectedKind(path, name string) string {
	normalized := filepath.ToSlash(path)
	switch {
	case name == "SKILL.md":
		return "skill"
	case name == "plugin.json":
		return "plugin"
	case name == "process-model.yaml":
		return "process-model"
	case strings.HasSuffix(name, ".yaml") && strings.Contains(normalized, "/.alps/process-models/"):
		return "process-model"
	default:
		return ""
	}
}

func skipDiscoveryDirectory(name string) bool {
	switch name {
	case ".git", "node_modules", ".worktrees", "dist", "build", "vendor", "snapshots", "backups", "blobs", ".alps-workspace-local-check", ".alps-workspace-codex-check":
		return true
	default:
		return strings.HasPrefix(name, ".alps-workspace-")
	}
}

func inspectAsset(path, kind string, root Root, sourceID string) (Asset, error) {
	absolute, err := filepath.Abs(path)
	if err != nil {
		return Asset{}, err
	}
	manifest, err := manifestForAsset(absolute, kind)
	if err != nil {
		return Asset{}, err
	}
	digest := manifestDigest(manifest)
	name := strings.TrimSuffix(filepath.Base(path), filepath.Ext(path))
	description := ""
	captureMode := "materialized"
	var issues []ValidationIssue
	var surfaces []ExecutableSurface
	for _, file := range manifest.Files {
		if surfaceKind(file.Path) != "" {
			surfaces = append(surfaces, ExecutableSurface{Path: file.Path, Kind: surfaceKind(file.Path)})
		}
	}
	switch kind {
	case "skill":
		content, readErr := os.ReadFile(path)
		if readErr != nil {
			return Asset{}, readErr
		}
		descriptionValue := parseSkillDescription(string(content))
		name, description = descriptionValue.Name, descriptionValue.Description
		if name == "" {
			name = filepath.Base(filepath.Dir(path))
		}
		issues = validateSkill(descriptionValue)
	case "plugin":
		content, readErr := os.ReadFile(path)
		if readErr != nil {
			return Asset{}, readErr
		}
		var value map[string]any
		if unmarshalErr := json.Unmarshal(content, &value); unmarshalErr != nil {
			issues = append(issues, ValidationIssue{Path: "plugin.json", Code: "invalid_json", Message: unmarshalErr.Error(), Severity: "error"})
		} else {
			if text, ok := value["name"].(string); ok && text != "" {
				name = text
			} else {
				issues = append(issues, ValidationIssue{Path: "name", Code: "required", Message: "plugin name is required", Severity: "error"})
			}
			if text, ok := value["description"].(string); ok {
				description = text
			}
			if external, ok := value["external"].(bool); ok && external {
				captureMode = "referenced"
			}
		}
	case "process-model":
		descriptor, descriptorIssues, loadErr := alpsmodel.Load(path)
		if loadErr != nil {
			issues = append(issues, ValidationIssue{Path: path, Code: "read_failed", Message: loadErr.Error(), Severity: "error"})
		} else {
			if descriptor.Metadata.Name != "" {
				name = descriptor.Metadata.Name
			}
			description = descriptor.Metadata.Description
			for _, issue := range descriptorIssues {
				issues = append(issues, ValidationIssue(issue))
			}
		}
	}
	validation := "valid"
	for _, issue := range issues {
		if issue.Severity == "error" {
			validation = "invalid"
			break
		}
	}
	lastSeen := now()
	return Asset{
		ID:                 shortID(kind + "\x00" + absolute),
		Kind:               kind,
		Name:               name,
		Description:        description,
		Scope:              root.Scope,
		Provider:           root.Provider,
		Realm:              defaultString(root.Realm, "local"),
		Host:               root.Host,
		SourcePath:         absolute,
		SourceURI:          fileURI(absolute),
		Digest:             digest,
		SourceState:        "detected",
		Validation:         validation,
		ValidationIssues:   issues,
		HostState:          "unknown",
		ALPSState:          "external",
		CaptureMode:        captureMode,
		ExecutableSurfaces: surfaces,
		UpdatedAt:          lastSeen,
		LastSeenAt:         lastSeen,
	}, nil
}

func validateSkill(description skillDescription) []ValidationIssue {
	var issues []ValidationIssue
	if description.Name == "" {
		issues = append(issues, ValidationIssue{Path: "frontmatter.name", Code: "required", Message: "Skill name is required", Severity: "error"})
	}
	if description.Description == "" {
		issues = append(issues, ValidationIssue{Path: "frontmatter.description", Code: "required", Message: "Skill discovery description is required", Severity: "error"})
	} else if !strings.HasSuffix(description.Description, "ALPS-conformant.") && !strings.HasSuffix(description.Description, "ALPS準拠。") {
		issues = append(issues, ValidationIssue{Path: "frontmatter.description", Code: "missing_conformance_marker", Message: "Skill discovery description does not end with the ALPS conformance marker", Severity: "warning"})
	}
	if description.Purpose == "" {
		issues = append(issues, ValidationIssue{Path: "Purpose", Code: "required", Message: "Purpose is required", Severity: "error"})
	}
	if len(description.Outcomes) == 0 {
		issues = append(issues, ValidationIssue{Path: "Outcomes", Code: "required", Message: "At least one Outcome is required", Severity: "error"})
	}
	return issues
}

func parseSkillDescription(content string) skillDescription {
	var result skillDescription
	lines := strings.Split(content, "\n")
	if len(lines) > 2 && strings.TrimSpace(lines[0]) == "---" {
		for _, line := range lines[1:] {
			if strings.TrimSpace(line) == "---" {
				break
			}
			key, value, ok := strings.Cut(line, ":")
			if !ok {
				continue
			}
			switch strings.TrimSpace(key) {
			case "name":
				result.Name = strings.Trim(strings.TrimSpace(value), "\"")
			case "description":
				result.Description = strings.Trim(strings.TrimSpace(value), "\"")
			case "alps-version", "alpsVersion":
				result.ALPSVersion = strings.Trim(strings.TrimSpace(value), "\"")
			}
		}
	}
	section := ""
	for _, line := range lines {
		trimmed := strings.TrimSpace(line)
		if strings.HasPrefix(trimmed, "## ") {
			section = strings.ToLower(strings.TrimSpace(strings.TrimPrefix(trimmed, "## ")))
			continue
		}
		if strings.HasPrefix(trimmed, "### ") {
			continue
		}
		switch section {
		case "purpose", "目的":
			if trimmed != "" && !strings.HasPrefix(trimmed, "#") && result.Purpose == "" {
				result.Purpose = strings.TrimSpace(strings.TrimPrefix(trimmed, ">"))
			}
		case "outcomes", "outcome", "成果", "達成結果":
			if strings.HasPrefix(trimmed, "- ") || strings.HasPrefix(trimmed, "* ") {
				result.Outcomes = append(result.Outcomes, strings.TrimSpace(trimmed[2:]))
			}
		}
	}
	return result
}

func (r *Runtime) upsertAsset(ctx context.Context, asset Asset) error {
	var previousDigest, state, revision string
	err := r.db.QueryRowContext(ctx, `SELECT digest,alps_state,COALESCE(adopted_revision_id,'') FROM assets WHERE id=?`, asset.ID).Scan(&previousDigest, &state, &revision)
	if err == nil {
		if previousDigest != asset.Digest && state == "adopted" {
			asset.ALPSState = "changed"
		} else if state != "" {
			asset.ALPSState = state
		}
		asset.AdoptedRevisionID = revision
	}
	manifest, _ := manifestForAsset(asset.SourcePath, asset.Kind)
	_, err = r.db.ExecContext(ctx, `
INSERT INTO assets(id,kind,name,description,scope,provider,source_path,digest,validation,alps_state,adopted_revision_id,updated_at,source_state,host_state,validation_json,capture_mode,manifest_json,source_id,last_seen_at)
VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
ON CONFLICT(id) DO UPDATE SET
 name=excluded.name,description=excluded.description,digest=excluded.digest,validation=excluded.validation,
 alps_state=excluded.alps_state,updated_at=excluded.updated_at,source_state=excluded.source_state,
 validation_json=excluded.validation_json,capture_mode=excluded.capture_mode,manifest_json=excluded.manifest_json,last_seen_at=excluded.last_seen_at`,
		asset.ID, asset.Kind, asset.Name, asset.Description, asset.Scope, asset.Provider, asset.SourcePath, asset.Digest,
		asset.Validation, asset.ALPSState, nullIfEmpty(asset.AdoptedRevisionID), asset.UpdatedAt, asset.SourceState,
		asset.HostState, marshal(asset.ValidationIssues), asset.CaptureMode, marshal(manifest), nil, asset.LastSeenAt,
	)
	return err
}

func (r *Runtime) markMissing(ctx context.Context, roots []Root, seen map[string]struct{}) error {
	rows, err := r.db.QueryContext(ctx, `SELECT id,source_path FROM assets`)
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
		var id, sourcePath string
		if err := rows.Scan(&id, &sourcePath); err != nil {
			return err
		}
		if _, exists := seen[id]; exists {
			continue
		}
		for _, root := range roots {
			absoluteRoot, _ := filepath.Abs(root.Path)
			if withinRoot(absoluteRoot, sourcePath) {
				_, _ = r.db.ExecContext(ctx, `UPDATE assets SET source_state='missing',updated_at=? WHERE id=?`, now(), id)
				break
			}
		}
	}
	return rows.Err()
}

func (r *Runtime) Catalog(ctx context.Context) ([]Asset, error) {
	rows, err := r.db.QueryContext(ctx, `
SELECT id,kind,name,description,scope,provider,source_path,digest,validation,alps_state,COALESCE(adopted_revision_id,''),updated_at,
 source_state,host_state,validation_json,capture_mode,last_seen_at
FROM assets ORDER BY kind,name`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var assets []Asset
	for rows.Next() {
		asset, scanErr := scanAsset(rows)
		if scanErr != nil {
			return nil, scanErr
		}
		assets = append(assets, asset)
	}
	return assets, rows.Err()
}

func (r *Runtime) Asset(ctx context.Context, id string) (AssetDetail, error) {
	row := r.db.QueryRowContext(ctx, `
SELECT id,kind,name,description,scope,provider,source_path,digest,validation,alps_state,COALESCE(adopted_revision_id,''),updated_at,
 source_state,host_state,validation_json,capture_mode,last_seen_at
FROM assets WHERE id=?`, id)
	asset, err := scanAsset(row)
	if errors.Is(err, sql.ErrNoRows) {
		return AssetDetail{}, ErrNotFound
	}
	if err != nil {
		return AssetDetail{}, err
	}
	manifest, err := manifestForAsset(asset.SourcePath, asset.Kind)
	if err != nil && asset.SourceState != "missing" {
		return AssetDetail{}, err
	}
	detail := AssetDetail{Asset: asset, Manifest: manifest}
	for _, file := range manifest.Files {
		detail.Files = append(detail.Files, file.Path)
	}
	target := asset.SourcePath
	if content, readErr := os.ReadFile(target); readErr == nil && len(content) <= 1<<20 {
		detail.Content = string(content)
		detail.ContentPath = filepath.Base(target)
		if asset.Kind == "skill" {
			detail.ContentPath = "SKILL.md"
		}
	}
	return detail, nil
}

func scanAsset(scanner interface{ Scan(...any) error }) (Asset, error) {
	var asset Asset
	var issuesJSON string
	if err := scanner.Scan(&asset.ID, &asset.Kind, &asset.Name, &asset.Description, &asset.Scope, &asset.Provider, &asset.SourcePath, &asset.Digest, &asset.Validation, &asset.ALPSState, &asset.AdoptedRevisionID, &asset.UpdatedAt, &asset.SourceState, &asset.HostState, &issuesJSON, &asset.CaptureMode, &asset.LastSeenAt); err != nil {
		return Asset{}, err
	}
	asset.SourceURI = fileURI(asset.SourcePath)
	_ = json.Unmarshal([]byte(issuesJSON), &asset.ValidationIssues)
	manifest, _ := manifestForAsset(asset.SourcePath, asset.Kind)
	for _, file := range manifest.Files {
		if kind := surfaceKind(file.Path); kind != "" {
			asset.ExecutableSurfaces = append(asset.ExecutableSurfaces, ExecutableSurface{Path: file.Path, Kind: kind})
		}
	}
	return asset, nil
}

func (r *Runtime) AssetFile(ctx context.Context, id, relative string) (string, string, error) {
	detail, err := r.Asset(ctx, id)
	if err != nil {
		return "", "", err
	}
	root := assetRoot(detail.SourcePath, detail.Kind)
	clean := filepath.Clean(filepath.FromSlash(relative))
	if clean == "." || filepath.IsAbs(clean) || clean == ".." || strings.HasPrefix(clean, ".."+string(filepath.Separator)) {
		return "", "", fmt.Errorf("%w: invalid asset path", ErrInvalid)
	}
	target := filepath.Join(root, clean)
	rootReal, err := filepath.EvalSymlinks(root)
	if err != nil {
		return "", "", err
	}
	targetReal, err := filepath.EvalSymlinks(target)
	if err != nil {
		return "", "", err
	}
	if !withinRoot(rootReal, targetReal) {
		return "", "", fmt.Errorf("%w: asset path leaves package root", ErrForbidden)
	}
	content, err := os.ReadFile(targetReal)
	if err != nil {
		return "", "", err
	}
	if len(content) > 1<<20 {
		return "", "", fmt.Errorf("%w: asset preview exceeds 1 MiB", ErrInvalid)
	}
	return filepath.ToSlash(clean), string(content), nil
}

func (r *Runtime) ValidateAsset(ctx context.Context, id string) (Asset, error) {
	detail, err := r.Asset(ctx, id)
	if err != nil {
		return Asset{}, err
	}
	root := Root{Path: filepath.Dir(detail.SourcePath), Scope: detail.Scope, Provider: detail.Provider, Realm: detail.Realm, Host: detail.Host}
	inspected, err := inspectAsset(detail.SourcePath, detail.Kind, root, "")
	if err != nil {
		return Asset{}, err
	}
	inspected.ID = detail.ID
	inspected.ALPSState = detail.ALPSState
	inspected.AdoptedRevisionID = detail.AdoptedRevisionID
	if err := r.upsertAsset(ctx, inspected); err != nil {
		return Asset{}, err
	}
	validated, err := r.Asset(ctx, id)
	return validated.Asset, err
}

func (r *Runtime) DiffAsset(ctx context.Context, id string) (AssetDiff, error) {
	detail, err := r.Asset(ctx, id)
	if err != nil {
		return AssetDiff{}, err
	}
	diff := AssetDiff{AssetID: id, AdoptedRevisionID: detail.AdoptedRevisionID, ExecutableSurfaces: detail.ExecutableSurfaces}
	if detail.AdoptedRevisionID == "" {
		for _, file := range detail.Manifest.Files {
			diff.Entries = append(diff.Entries, DiffEntry{Path: file.Path, Status: "added", After: file.Digest})
		}
		return diff, nil
	}
	var manifestJSON string
	if err := r.db.QueryRowContext(ctx, `SELECT manifest_json FROM revisions WHERE id=?`, detail.AdoptedRevisionID).Scan(&manifestJSON); err != nil {
		return AssetDiff{}, err
	}
	var previous ResourceManifest
	_ = json.Unmarshal([]byte(manifestJSON), &previous)
	before := map[string]string{}
	after := map[string]string{}
	for _, file := range previous.Files {
		before[file.Path] = file.Digest
	}
	for _, file := range detail.Manifest.Files {
		after[file.Path] = file.Digest
	}
	paths := map[string]struct{}{}
	for path := range before {
		paths[path] = struct{}{}
	}
	for path := range after {
		paths[path] = struct{}{}
	}
	var names []string
	for path := range paths {
		names = append(names, path)
	}
	sort.Strings(names)
	for _, path := range names {
		switch {
		case before[path] == "":
			diff.Entries = append(diff.Entries, DiffEntry{Path: path, Status: "added", After: after[path]})
		case after[path] == "":
			diff.Entries = append(diff.Entries, DiffEntry{Path: path, Status: "removed", Before: before[path]})
		case before[path] != after[path]:
			diff.Entries = append(diff.Entries, DiffEntry{Path: path, Status: "modified", Before: before[path], After: after[path]})
		}
	}
	return diff, nil
}

func (r *Runtime) Adopt(ctx context.Context, id string) (string, error) {
	detail, err := r.Asset(ctx, id)
	if err != nil {
		return "", err
	}
	if detail.Validation != "valid" {
		return "", fmt.Errorf("%w: asset validation is %s", ErrInvalid, detail.Validation)
	}
	manifest := detail.Manifest
	root := assetRoot(detail.SourcePath, detail.Kind)
	revisionPrefix := map[string]string{"skill": "skillrev", "plugin": "pluginrev", "process-model": "modelrev"}[detail.Kind]
	revisionID := revisionPrefix + "_" + shortID(detail.ID+detail.Digest)
	destination := filepath.Join(r.workspace, "snapshots", detail.Kind, revisionID)
	if detail.CaptureMode == "materialized" {
		if err := snapshotDirectory(root, destination); err != nil {
			return "", err
		}
	}
	actor := ActorFromContext(ctx)
	var event domain.Event
	err = r.write(ctx, "asset.adopt", func(transaction *sql.Tx) error {
		if _, err := transaction.ExecContext(ctx, `INSERT OR IGNORE INTO revisions(id,asset_id,kind,digest,snapshot_path,created_at,logical_id,manifest_json,metadata_json) VALUES(?,?,?,?,?,?,?,?,?)`, revisionID, id, detail.Kind, detail.Digest, destination, now(), detail.Name, marshal(manifest), marshal(map[string]any{"captureMode": detail.CaptureMode})); err != nil {
			return err
		}
		switch detail.Kind {
		case "skill":
			if err := r.adoptSkillTx(ctx, transaction, detail, revisionID, destination, manifest); err != nil {
				return err
			}
		case "plugin":
			if err := r.adoptPluginTx(ctx, transaction, detail, revisionID, destination, manifest); err != nil {
				return err
			}
		case "process-model":
			if err := r.adoptModelTx(ctx, transaction, detail, revisionID, destination); err != nil {
				return err
			}
		}
		if _, err := transaction.ExecContext(ctx, `UPDATE assets SET alps_state='adopted',adopted_revision_id=?,source_state='detected' WHERE id=?`, revisionID, id); err != nil {
			return err
		}
		var appendErr error
		event, appendErr = appendEventTx(ctx, transaction, actor, "asset", id, "asset.adopted", "", "", "v1", map[string]any{"revisionId": revisionID, "kind": detail.Kind, "digest": detail.Digest})
		return appendErr
	})
	if err != nil {
		if detail.CaptureMode == "materialized" {
			_ = os.RemoveAll(destination)
		}
		return "", err
	}
	r.publish(event)
	return revisionID, nil
}

func (r *Runtime) adoptSkillTx(ctx context.Context, transaction *sql.Tx, detail AssetDetail, packageRevisionID, destination string, manifest ResourceManifest) error {
	content, err := os.ReadFile(detail.SourcePath)
	if err != nil {
		return err
	}
	description := parseSkillDescription(string(content))
	processRevisionID := "processrev_" + shortID(detail.ID+detail.Digest)
	logicalID := description.Name
	if logicalID == "" {
		logicalID = detail.Name
	}
	if _, err := transaction.ExecContext(ctx, `INSERT OR IGNORE INTO process_revisions(id,logical_process_id,asset_id,digest,source_uri,alps_version,name,purpose,outcomes_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)`, processRevisionID, logicalID, detail.ID, detail.Digest, detail.SourceURI, description.ALPSVersion, detail.Name, description.Purpose, marshal(description.Outcomes), now()); err != nil {
		return err
	}
	_, err = transaction.ExecContext(ctx, `INSERT OR IGNORE INTO skill_package_revisions(id,asset_id,process_revision_id,digest,manifest_json,snapshot_path,created_at) VALUES(?,?,?,?,?,?,?)`, packageRevisionID, detail.ID, processRevisionID, detail.Digest, marshal(manifest), destination, now())
	return err
}

func (r *Runtime) adoptPluginTx(ctx context.Context, transaction *sql.Tx, detail AssetDetail, revisionID, destination string, manifest ResourceManifest) error {
	manifestContent, err := os.ReadFile(detail.SourcePath)
	if err != nil {
		return err
	}
	if _, err := transaction.ExecContext(ctx, `INSERT OR IGNORE INTO plugin_revisions(id,asset_id,plugin_identity,digest,manifest_json,capture_mode,snapshot_path,created_at) VALUES(?,?,?,?,?,?,?,?)`, revisionID, detail.ID, detail.Name, detail.Digest, string(manifestContent), detail.CaptureMode, nullIfEmpty(destination), now()); err != nil {
		return err
	}
	for _, file := range manifest.Files {
		componentType := surfaceKind(file.Path)
		if strings.HasSuffix(file.Path, "/SKILL.md") || file.Path == "SKILL.md" {
			componentType = "skill"
		}
		if componentType == "" {
			continue
		}
		if _, err := transaction.ExecContext(ctx, `INSERT OR IGNORE INTO plugin_components(id,plugin_revision_id,component_type,source_uri,digest,permissions_json) VALUES(?,?,?,?,?,?)`, "component_"+shortID(revisionID+file.Path), revisionID, componentType, fileURI(filepath.Join(assetRoot(detail.SourcePath, detail.Kind), filepath.FromSlash(file.Path))), file.Digest, `{}`); err != nil {
			return err
		}
	}
	return nil
}

func (r *Runtime) adoptModelTx(ctx context.Context, transaction *sql.Tx, detail AssetDetail, revisionID, destination string) error {
	resolved, issues, err := alpsmodel.Resolve(detail.SourcePath, func(path string) string { return r.revisionForSource(ctx, path) })
	if err != nil {
		return err
	}
	for _, issue := range issues {
		if issue.Severity == "error" {
			return fmt.Errorf("%w: process model %s: %s", ErrInvalid, issue.Path, issue.Message)
		}
	}
	descriptorJSON, _ := json.Marshal(resolved.Descriptor)
	if _, err := transaction.ExecContext(ctx, `INSERT OR IGNORE INTO process_model_revisions(id,asset_id,model_id,name,version,digest,descriptor_json,snapshot_path,created_at) VALUES(?,?,?,?,?,?,?,?,?)`, revisionID, detail.ID, resolved.Descriptor.Metadata.ID, resolved.Descriptor.Metadata.Name, resolved.Descriptor.Metadata.Version, resolved.Digest, string(descriptorJSON), destination, now()); err != nil {
		return err
	}
	for _, process := range resolved.Processes {
		if _, err := transaction.ExecContext(ctx, `INSERT OR REPLACE INTO model_processes(model_revision_id,process_id,process_revision_id,ref,name,digest) VALUES(?,?,?,?,?,?)`, revisionID, process.ID, nullIfEmpty(process.Revision), process.Ref, process.Name, process.Digest); err != nil {
			return err
		}
	}
	for _, item := range resolved.Descriptor.Spec.Interfaces {
		if _, err := transaction.ExecContext(ctx, `INSERT OR REPLACE INTO interface_types(model_revision_id,interface_id,name,kind,media_types_json,schema_ref,schema_digest,required) VALUES(?,?,?,?,?,?,?,?)`, revisionID, item.ID, item.Name, item.Kind, marshal(item.MediaTypes), nullIfEmpty(item.SchemaRef), nullIfEmpty(resolved.SchemaFiles[item.ID]), item.Required); err != nil {
			return err
		}
	}
	for _, binding := range resolved.Descriptor.Spec.Bindings {
		if _, err := transaction.ExecContext(ctx, `INSERT OR REPLACE INTO process_bindings(model_revision_id,binding_id,process_id,role,item_name,interface_id,optional) VALUES(?,?,?,?,?,?,?)`, revisionID, binding.ID, binding.Process, binding.Role, binding.Item, binding.Interface, binding.Optional); err != nil {
			return err
		}
	}
	for _, handoff := range resolved.Descriptor.Spec.Handoffs {
		if _, err := transaction.ExecContext(ctx, `INSERT OR REPLACE INTO handoff_definitions(model_revision_id,handoff_id,from_binding,to_binding,acceptance_ref,acceptance_digest) VALUES(?,?,?,?,?,?)`, revisionID, handoff.ID, handoff.From, handoff.To, nullIfEmpty(handoff.AcceptanceRef), nullIfEmpty(resolved.Criteria[handoff.ID])); err != nil {
			return err
		}
	}
	for index, relationship := range resolved.Descriptor.Spec.Relationships {
		if _, err := transaction.ExecContext(ctx, `INSERT OR REPLACE INTO model_relationships(model_revision_id,relationship_type,processes_json,ordinal) VALUES(?,?,?,?)`, revisionID, relationship.Type, marshal(relationship.Processes), index); err != nil {
			return err
		}
	}
	for index, entry := range resolved.Descriptor.Spec.EntryPoints {
		if _, err := transaction.ExecContext(ctx, `INSERT OR REPLACE INTO model_entry_points(model_revision_id,process_id,ordinal) VALUES(?,?,?)`, revisionID, entry.Process, index); err != nil {
			return err
		}
	}
	return nil
}

func (r *Runtime) revisionForSource(ctx context.Context, path string) string {
	absolute, _ := filepath.Abs(path)
	var revision string
	_ = r.db.QueryRowContext(ctx, `SELECT COALESCE(adopted_revision_id,'') FROM assets WHERE source_path=?`, absolute).Scan(&revision)
	return revision
}

func manifestForAsset(sourcePath, kind string) (ResourceManifest, error) {
	root := assetRoot(sourcePath, kind)
	return buildManifest(root)
}

func assetRoot(sourcePath, kind string) string {
	switch kind {
	case "skill", "plugin", "process-model":
		return filepath.Dir(sourcePath)
	default:
		return filepath.Dir(sourcePath)
	}
}

func buildManifest(root string) (ResourceManifest, error) {
	root, err := filepath.Abs(root)
	if err != nil {
		return ResourceManifest{}, err
	}
	manifest := ResourceManifest{Root: fileURI(root)}
	fileCount := 0
	var totalSize int64
	err = filepath.WalkDir(root, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() {
			if path != root && skipDiscoveryDirectory(entry.Name()) {
				return filepath.SkipDir
			}
			return nil
		}
		info, err := entry.Info()
		if err != nil {
			return err
		}
		if info.Mode()&os.ModeSymlink != 0 {
			return nil
		}
		fileCount++
		totalSize += info.Size()
		if fileCount > 10000 || totalSize > 256<<20 {
			return fmt.Errorf("package exceeds discovery limits")
		}
		content, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		digest := sha256.Sum256(content)
		relative, _ := filepath.Rel(root, path)
		manifest.Files = append(manifest.Files, ManifestFile{Path: filepath.ToSlash(relative), Digest: "sha256:" + hex.EncodeToString(digest[:]), Size: info.Size(), Executable: info.Mode()&0o111 != 0})
		return nil
	})
	sort.Slice(manifest.Files, func(i, j int) bool { return manifest.Files[i].Path < manifest.Files[j].Path })
	return manifest, err
}

func manifestDigest(manifest ResourceManifest) string {
	copyManifest := manifest
	copyManifest.Root = ""
	encoded, _ := json.Marshal(copyManifest)
	digest := sha256.Sum256(encoded)
	return "sha256:" + hex.EncodeToString(digest[:])
}

func snapshotDirectory(source, destination string) error {
	if _, err := os.Stat(destination); err == nil {
		return nil
	}
	temporary := destination + ".tmp-" + shortID(now())
	if err := os.RemoveAll(temporary); err != nil {
		return err
	}
	if err := copyDirectory(source, temporary); err != nil {
		_ = os.RemoveAll(temporary)
		return err
	}
	if err := os.MkdirAll(filepath.Dir(destination), 0o700); err != nil {
		return err
	}
	return os.Rename(temporary, destination)
}

func copyDirectory(source, destination string) error {
	return filepath.WalkDir(source, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() && path != source && skipDiscoveryDirectory(entry.Name()) {
			return filepath.SkipDir
		}
		relative, _ := filepath.Rel(source, path)
		target := filepath.Join(destination, relative)
		if entry.IsDir() {
			return os.MkdirAll(target, 0o700)
		}
		info, err := entry.Info()
		if err != nil {
			return err
		}
		if info.Mode()&os.ModeSymlink != 0 {
			return nil
		}
		return copyFile(path, target, info.Mode().Perm())
	})
}

func copyFile(source, destination string, mode fs.FileMode) error {
	if err := os.MkdirAll(filepath.Dir(destination), 0o700); err != nil {
		return err
	}
	input, err := os.Open(source)
	if err != nil {
		return err
	}
	defer input.Close()
	output, err := os.OpenFile(destination, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, mode&0o700)
	if err != nil {
		return err
	}
	_, copyErr := io.Copy(output, input)
	syncErr := output.Sync()
	closeErr := output.Close()
	return errors.Join(copyErr, syncErr, closeErr)
}

func surfaceKind(path string) string {
	lower := strings.ToLower(filepath.ToSlash(path))
	switch {
	case strings.HasSuffix(lower, ".sh"), strings.HasSuffix(lower, ".ps1"), strings.HasSuffix(lower, ".bat"), strings.HasSuffix(lower, ".cmd"), strings.HasSuffix(lower, ".py"), strings.Contains(lower, "/scripts/"):
		return "script"
	case strings.Contains(lower, "hook"):
		return "hook"
	case strings.HasSuffix(lower, "mcp.json"), strings.Contains(lower, "mcp-server"):
		return "mcp-server"
	case strings.Contains(lower, "lsp"):
		return "lsp-server"
	case strings.Contains(lower, "app") && (strings.HasSuffix(lower, ".json") || strings.HasSuffix(lower, ".yaml")):
		return "app"
	default:
		return ""
	}
}

func fileURI(path string) string {
	absolute, _ := filepath.Abs(path)
	return "file://" + filepath.ToSlash(absolute)
}

func withinRoot(root, target string) bool {
	root, _ = filepath.Abs(root)
	target, _ = filepath.Abs(target)
	return target == root || strings.HasPrefix(target, root+string(filepath.Separator))
}

func defaultString(value, fallback string) string {
	if value == "" {
		return fallback
	}
	return value
}
