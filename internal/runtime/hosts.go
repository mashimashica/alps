package runtime

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"path/filepath"
	"strings"

	"github.com/mashimashica/alps/internal/domain"
	"github.com/mashimashica/alps/internal/hooks"
	"github.com/mashimashica/alps/internal/hosts"
)

type HostContext struct {
	ID             string   `json:"id"`
	Host           string   `json:"host"`
	Version        string   `json:"version,omitempty"`
	WorkspaceRoots []string `json:"workspaceRoots,omitempty"`
	RepositoryRoot string   `json:"repositoryRoot,omitempty"`
	Realm          string   `json:"realm,omitempty"`
	ReportedAt     string   `json:"reportedAt"`
}

type HostObservation struct {
	ID           string         `json:"id"`
	Host         string         `json:"host"`
	Event        string         `json:"event"`
	Envelope     hooks.Envelope `json:"envelope"`
	RawReference string         `json:"rawReference,omitempty"`
	CreatedAt    string         `json:"createdAt"`
}

func (r *Runtime) RegisterHostInventory(ctx context.Context, inventory hosts.Inventory) (HostContext, error) {
	if inventory.Host == "" {
		return HostContext{}, fmt.Errorf("%w: host is required", ErrInvalid)
	}
	contextValue := HostContext{ID: newID("hostctx"), Host: inventory.Host, Version: inventory.Version, WorkspaceRoots: inventory.WorkspaceRoots, RepositoryRoot: inventory.RepositoryRoot, Realm: defaultString(inventory.Realm, "local"), ReportedAt: defaultString(inventory.ReportedAt, now())}
	actor := ActorFromContext(ctx)
	var event domain.Event
	err := r.write(ctx, "host_inventory.register", func(tx *sql.Tx) error {
		if _, err := tx.ExecContext(ctx, `INSERT INTO host_contexts(id,host,version,workspace_roots_json,repository_root,realm,reported_at) VALUES(?,?,?,?,?,?,?)`, contextValue.ID, contextValue.Host, nullIfEmpty(contextValue.Version), marshal(contextValue.WorkspaceRoots), nullIfEmpty(contextValue.RepositoryRoot), contextValue.Realm, contextValue.ReportedAt); err != nil {
			return err
		}
		profile := builtinProfile(inventory.Host)
		if profile.Host != "" {
			profile.ID = "hostprofile_" + shortID(inventory.Host+inventory.Version+profile.AdapterVersion)
			profile.Version = inventory.Version
			profile.ObservedAt = contextValue.ReportedAt
			if _, err := tx.ExecContext(ctx, `INSERT OR REPLACE INTO host_capability_profiles(id,host,version,adapter_version,capabilities_json,observed_at) VALUES(?,?,?,?,?,?)`, profile.ID, profile.Host, nullIfEmpty(profile.Version), profile.AdapterVersion, marshal(profile.Capabilities), profile.ObservedAt); err != nil {
				return err
			}
		}
		var appendErr error
		event, appendErr = appendEventTx(ctx, tx, actor, "host", inventory.Host, "host.inventory_registered", contextValue.ID, "", "v1", map[string]any{"context": contextValue, "skillRoots": inventory.SkillRoots, "pluginRoots": inventory.PluginRoots})
		return appendErr
	})
	if err != nil {
		return HostContext{}, err
	}
	for _, root := range append(append([]string{}, inventory.SkillRoots...), inventory.PluginRoots...) {
		if root == "" {
			continue
		}
		absolute, _ := filepath.Abs(root)
		r.addRoot(Root{Path: absolute, Scope: "host", Provider: inventory.Host, Realm: contextValue.Realm, Host: inventory.Host})
	}
	r.publish(event)
	return contextValue, nil
}

func (r *Runtime) addRoot(root Root) {
	r.rootsMu.Lock()
	defer r.rootsMu.Unlock()
	for _, existing := range r.roots {
		if existing.Path == root.Path && existing.Provider == root.Provider && existing.Host == root.Host {
			return
		}
	}
	r.roots = append(r.roots, root)
}

func (r *Runtime) HostCapabilityProfiles(ctx context.Context) ([]hosts.Profile, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT id,host,COALESCE(version,''),adapter_version,capabilities_json,observed_at FROM host_capability_profiles ORDER BY host,observed_at DESC`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var profiles []hosts.Profile
	for rows.Next() {
		var profile hosts.Profile
		var capabilities string
		if err := rows.Scan(&profile.ID, &profile.Host, &profile.Version, &profile.AdapterVersion, &capabilities, &profile.ObservedAt); err != nil {
			return nil, err
		}
		_ = json.Unmarshal([]byte(capabilities), &profile.Capabilities)
		profiles = append(profiles, profile)
	}
	if len(profiles) == 0 {
		return hosts.BuiltinProfiles(), nil
	}
	return profiles, rows.Err()
}

func (r *Runtime) RecordHookBinding(ctx context.Context, binding hooks.Binding, generated map[string]any, capabilities map[string]any) (string, error) {
	if message := hooks.ValidateBinding(binding); message != "" {
		return "", fmt.Errorf("%w: %s", ErrInvalid, message)
	}
	digest := "sha256:" + shortID(marshal(binding)+marshal(generated)+marshal(capabilities))
	id := "hookrev_" + shortID(binding.ID+digest)
	actor := ActorFromContext(ctx)
	var event domain.Event
	err := r.write(ctx, "hook_binding.record", func(tx *sql.Tx) error {
		if _, err := tx.ExecContext(ctx, `INSERT OR IGNORE INTO hook_revisions(id,binding_json,generated_definition_json,digest,capabilities_json,created_at) VALUES(?,?,?,?,?,?)`, id, marshal(binding), marshal(generated), digest, marshal(capabilities), now()); err != nil {
			return err
		}
		var appendErr error
		event, appendErr = appendEventTx(ctx, tx, actor, "hook", id, "hook_binding.recorded", id, "", "v1", map[string]any{"id": id, "binding": binding, "digest": digest})
		return appendErr
	})
	if err != nil {
		return "", err
	}
	r.publish(event)
	return id, nil
}

func (r *Runtime) RecordHostObservation(ctx context.Context, envelope hooks.Envelope, rawReference string) (HostObservation, error) {
	if envelope.Host == "" || envelope.Event == "" {
		return HostObservation{}, fmt.Errorf("%w: host and event are required", ErrInvalid)
	}
	if envelope.SchemaVersion == "" {
		envelope.SchemaVersion = "alps.dev/host-observation/v1"
	}
	if envelope.ObservationID == "" {
		envelope.ObservationID = newID("observation")
	}
	if envelope.OccurredAt == "" {
		envelope.OccurredAt = now()
	}
	envelope.Metadata = hooks.RedactMetadata(envelope.Metadata)
	observation := HostObservation{ID: envelope.ObservationID, Host: envelope.Host, Event: envelope.Event, Envelope: envelope, RawReference: rawReference, CreatedAt: now()}
	actor := ActorFromContext(ctx)
	var event domain.Event
	err := r.write(ctx, "host_observation.record", func(tx *sql.Tx) error {
		if _, err := tx.ExecContext(ctx, `INSERT INTO host_observations(id,host,event_name,raw_json,envelope_json,raw_reference,created_at) VALUES(?,?,?,?,?,?,?)`, observation.ID, observation.Host, observation.Event, string(envelope.Metadata), marshal(envelope), nullIfEmpty(rawReference), observation.CreatedAt); err != nil {
			return err
		}
		streamID := observation.Host
		if envelope.RunID != "" {
			streamID = envelope.RunID
		}
		var appendErr error
		event, appendErr = appendEventTx(ctx, tx, actor, "host-observation", streamID, "host.observed", envelope.RunID, observation.ID, "v1", observation)
		return appendErr
	})
	if err != nil {
		return HostObservation{}, err
	}
	r.publish(event)
	return observation, nil
}

func (r *Runtime) HostObservation(ctx context.Context, host, eventName string, raw json.RawMessage) error {
	_, err := r.RecordHostObservation(ctx, hooks.Envelope{Host: host, Event: eventName, Metadata: raw}, "")
	return err
}

func builtinProfile(host string) hosts.Profile {
	for _, profile := range hosts.BuiltinProfiles() {
		if strings.EqualFold(profile.Host, host) {
			return profile
		}
	}
	return hosts.Profile{}
}
