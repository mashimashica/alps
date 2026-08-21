package runtime

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"strings"

	"github.com/mashimashica/alps/internal/domain"
)

type ModelCatalogSnapshot struct {
	ID         string           `json:"id"`
	Host       string           `json:"host"`
	Scope      string           `json:"scope,omitempty"`
	Models     []map[string]any `json:"models"`
	ObservedAt string           `json:"observedAt"`
}

type ModelInvocationInput struct {
	RunID             string         `json:"runId"`
	Requested         map[string]any `json:"requested"`
	Effective         map[string]any `json:"effective"`
	Resolved          map[string]any `json:"resolved"`
	Parameters        map[string]any `json:"parameters,omitempty"`
	Role              string         `json:"role,omitempty"`
	CatalogSnapshotID string         `json:"catalogSnapshotId,omitempty"`
	StartedAt         string         `json:"startedAt,omitempty"`
	FinishedAt        string         `json:"finishedAt,omitempty"`
}

type UsageInput struct {
	InvocationID    string                `json:"invocationId,omitempty"`
	RunID           string                `json:"runId"`
	SourceType      string                `json:"sourceType"`
	SourceHost      string                `json:"sourceHost,omitempty"`
	AdapterVersion  string                `json:"adapterVersion,omitempty"`
	Scope           string                `json:"scope"`
	Status          string                `json:"status"`
	AccountingBasis string                `json:"accountingBasis,omitempty"`
	Tokens          domain.UsageTokens    `json:"tokens"`
	Inclusion       domain.UsageInclusion `json:"inclusion"`
	MappingRevision string                `json:"mappingRevision,omitempty"`
	ObservedAt      string                `json:"observedAt,omitempty"`
}

type CostInput struct {
	InvocationID    string `json:"invocationId,omitempty"`
	RunID           string `json:"runId"`
	Source          string `json:"source"`
	Kind            string `json:"kind"`
	Currency        string `json:"currency,omitempty"`
	CreditType      string `json:"creditType,omitempty"`
	Amount          string `json:"amount"`
	Status          string `json:"status"`
	MappingRevision string `json:"mappingRevision,omitempty"`
	ObservedAt      string `json:"observedAt,omitempty"`
}

func (r *Runtime) RecordModelCatalog(ctx context.Context, host, scope string, models []map[string]any) (ModelCatalogSnapshot, error) {
	if host == "" {
		return ModelCatalogSnapshot{}, fmt.Errorf("%w: host is required", ErrInvalid)
	}
	snapshot := ModelCatalogSnapshot{ID: newID("catalog"), Host: host, Scope: scope, Models: models, ObservedAt: now()}
	actor := ActorFromContext(ctx)
	var event domain.Event
	err := r.write(ctx, "model_catalog.record", func(tx *sql.Tx) error {
		if _, err := tx.ExecContext(ctx, `INSERT INTO model_catalog_snapshots(id,host,scope,models_json,observed_at) VALUES(?,?,?,?,?)`, snapshot.ID, snapshot.Host, nullIfEmpty(snapshot.Scope), marshal(snapshot.Models), snapshot.ObservedAt); err != nil {
			return err
		}
		var appendErr error
		event, appendErr = appendEventTx(ctx, tx, actor, "model-catalog", snapshot.ID, "model_catalog.recorded", snapshot.ID, "", "v1", snapshot)
		return appendErr
	})
	if err != nil {
		return ModelCatalogSnapshot{}, err
	}
	r.publish(event)
	return snapshot, nil
}

func (r *Runtime) RecordModelInvocation(ctx context.Context, input ModelInvocationInput) (ModelInvocation, error) {
	if input.RunID == "" {
		return ModelInvocation{}, fmt.Errorf("%w: Run is required", ErrInvalid)
	}
	if _, err := r.Run(ctx, input.RunID); err != nil {
		return ModelInvocation{}, err
	}
	if input.Role == "" {
		input.Role = "main"
	}
	created := now()
	if input.StartedAt == "" {
		input.StartedAt = created
	}
	invocation := ModelInvocation{ID: newID("invocation"), RunID: input.RunID, Requested: defaultMap(input.Requested), Effective: defaultMap(input.Effective), Resolved: defaultMap(input.Resolved), Parameters: defaultMap(input.Parameters), Role: input.Role, CatalogSnapshotID: input.CatalogSnapshotID, StartedAt: input.StartedAt, FinishedAt: input.FinishedAt, CreatedAt: created}
	actor := ActorFromContext(ctx)
	var event domain.Event
	err := r.write(ctx, "model_invocation.record", func(tx *sql.Tx) error {
		requestedRaw := textValue(invocation.Requested, "modelRaw")
		effectiveRaw := textValue(invocation.Effective, "modelRaw")
		resolvedRaw := textValue(invocation.Resolved, "modelRaw")
		effort := textValue(invocation.Effective, "effortRaw")
		if effort == "" {
			effort = textValue(invocation.Parameters, "effort")
		}
		_, err := tx.ExecContext(ctx, `INSERT INTO model_invocations(id,run_id,requested_model,effective_model,resolved_model,effort,role,requested_json,effective_json,resolved_json,parameters_json,catalog_snapshot_id,started_at,finished_at,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`, invocation.ID, invocation.RunID, nullIfEmpty(requestedRaw), nullIfEmpty(effectiveRaw), nullIfEmpty(resolvedRaw), nullIfEmpty(effort), invocation.Role, marshal(invocation.Requested), marshal(invocation.Effective), marshal(invocation.Resolved), marshal(invocation.Parameters), nullIfEmpty(invocation.CatalogSnapshotID), nullIfEmpty(invocation.StartedAt), nullIfEmpty(invocation.FinishedAt), invocation.CreatedAt)
		if err != nil {
			return err
		}
		event, err = appendEventTx(ctx, tx, actor, "run", invocation.RunID, "model_invocation.recorded", invocation.RunID, invocation.ID, "v1", invocation)
		return err
	})
	if err != nil {
		return ModelInvocation{}, err
	}
	r.publish(event)
	return invocation, nil
}

func (r *Runtime) RecordUsageObservation(ctx context.Context, input UsageInput) (domain.UsageObservation, error) {
	if input.RunID == "" || input.SourceType == "" {
		return domain.UsageObservation{}, fmt.Errorf("%w: Run and source type are required", ErrInvalid)
	}
	if input.Scope == "" {
		input.Scope = "invocation"
	}
	if input.Status == "" {
		input.Status = "reported"
	}
	if !validObservationStatus(input.Status) {
		return domain.UsageObservation{}, fmt.Errorf("%w: invalid observation status", ErrInvalid)
	}
	if input.ObservedAt == "" {
		input.ObservedAt = now()
	}
	observation := domain.UsageObservation{ID: newID("usage"), InvocationID: input.InvocationID, RunID: input.RunID, SourceType: input.SourceType, SourceHost: input.SourceHost, AdapterVersion: input.AdapterVersion, Scope: input.Scope, Status: input.Status, AccountingBasis: input.AccountingBasis, Tokens: input.Tokens, Inclusion: input.Inclusion, MappingRevision: input.MappingRevision, ObservedAt: input.ObservedAt}
	actor := ActorFromContext(ctx)
	var event domain.Event
	err := r.write(ctx, "usage.record", func(tx *sql.Tx) error {
		if _, _, err := currentRunVersionTx(ctx, tx, input.RunID); err != nil {
			return err
		}
		_, err := tx.ExecContext(ctx, `INSERT INTO usage_observations(id,invocation_id,run_id,source,status,input_tokens,output_tokens,cache_read_tokens,cache_write_tokens,reasoning_tokens,source_type,source_host,adapter_version,scope,accounting_basis,inclusion_json,mapping_revision,observed_at,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`, observation.ID, nullIfEmpty(observation.InvocationID), observation.RunID, observation.SourceType, observation.Status, observation.Tokens.InputTotal, observation.Tokens.OutputTotal, observation.Tokens.CacheReadInput, observation.Tokens.CacheCreationInput, observation.Tokens.ReasoningOutput, observation.SourceType, nullIfEmpty(observation.SourceHost), nullIfEmpty(observation.AdapterVersion), observation.Scope, nullIfEmpty(observation.AccountingBasis), marshal(observation.Inclusion), nullIfEmpty(observation.MappingRevision), observation.ObservedAt, observation.ObservedAt)
		if err != nil {
			return err
		}
		event, err = appendEventTx(ctx, tx, actor, "run", observation.RunID, "usage.observed", observation.RunID, observation.ID, "v1", observation)
		return err
	})
	if err != nil {
		return domain.UsageObservation{}, err
	}
	r.publish(event)
	return observation, nil
}

func (r *Runtime) RecordCostObservation(ctx context.Context, input CostInput) (domain.CostObservation, error) {
	if input.RunID == "" || input.Source == "" || input.Kind == "" || input.Amount == "" {
		return domain.CostObservation{}, fmt.Errorf("%w: Run, source, kind, and amount are required", ErrInvalid)
	}
	if input.Status == "" {
		input.Status = "reported"
	}
	if !validObservationStatus(input.Status) {
		return domain.CostObservation{}, fmt.Errorf("%w: invalid observation status", ErrInvalid)
	}
	if input.ObservedAt == "" {
		input.ObservedAt = now()
	}
	observation := domain.CostObservation{ID: newID("cost"), InvocationID: input.InvocationID, RunID: input.RunID, Source: input.Source, Kind: input.Kind, Currency: input.Currency, CreditType: input.CreditType, Amount: input.Amount, Status: input.Status, MappingRevision: input.MappingRevision, ObservedAt: input.ObservedAt}
	actor := ActorFromContext(ctx)
	var event domain.Event
	err := r.write(ctx, "cost.record", func(tx *sql.Tx) error {
		if _, _, err := currentRunVersionTx(ctx, tx, input.RunID); err != nil {
			return err
		}
		_, err := tx.ExecContext(ctx, `INSERT INTO cost_observations(id,invocation_id,run_id,source,kind,currency,credit_type,amount,status,mapping_revision,observed_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)`, observation.ID, nullIfEmpty(observation.InvocationID), observation.RunID, observation.Source, observation.Kind, nullIfEmpty(observation.Currency), nullIfEmpty(observation.CreditType), observation.Amount, observation.Status, nullIfEmpty(observation.MappingRevision), observation.ObservedAt)
		if err != nil {
			return err
		}
		event, err = appendEventTx(ctx, tx, actor, "run", observation.RunID, "cost.observed", observation.RunID, observation.ID, "v1", observation)
		return err
	})
	if err != nil {
		return domain.CostObservation{}, err
	}
	r.publish(event)
	return observation, nil
}

func (r *Runtime) RecordUsage(ctx context.Context, runID, requested, effective, resolved, effort, source string, input, output, cacheRead, cacheWrite, reasoning *int64) error {
	invocation, err := r.RecordModelInvocation(ctx, ModelInvocationInput{RunID: runID, Requested: map[string]any{"modelRaw": requested}, Effective: map[string]any{"modelRaw": effective, "effortRaw": effort}, Resolved: map[string]any{"modelRaw": resolved, "status": "reported"}})
	if err != nil {
		return err
	}
	_, err = r.RecordUsageObservation(ctx, UsageInput{InvocationID: invocation.ID, RunID: runID, SourceType: source, Scope: "invocation", Status: "reported", Tokens: domain.UsageTokens{InputTotal: input, OutputTotal: output, CacheReadInput: cacheRead, CacheCreationInput: cacheWrite, ReasoningOutput: reasoning}})
	return err
}

func (r *Runtime) ModelInvocations(ctx context.Context, runID string) ([]ModelInvocation, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT id,run_id,requested_json,effective_json,resolved_json,parameters_json,COALESCE(role,''),COALESCE(catalog_snapshot_id,''),COALESCE(started_at,''),COALESCE(finished_at,''),created_at FROM model_invocations WHERE run_id=? ORDER BY created_at DESC`, runID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var invocations []ModelInvocation
	for rows.Next() {
		var current ModelInvocation
		var requested, effective, resolved, parameters string
		if err := rows.Scan(&current.ID, &current.RunID, &requested, &effective, &resolved, &parameters, &current.Role, &current.CatalogSnapshotID, &current.StartedAt, &current.FinishedAt, &current.CreatedAt); err != nil {
			return nil, err
		}
		_ = json.Unmarshal([]byte(requested), &current.Requested)
		_ = json.Unmarshal([]byte(effective), &current.Effective)
		_ = json.Unmarshal([]byte(resolved), &current.Resolved)
		_ = json.Unmarshal([]byte(parameters), &current.Parameters)
		invocations = append(invocations, current)
	}
	return invocations, rows.Err()
}

func (r *Runtime) UsageObservations(ctx context.Context, runID string) ([]domain.UsageObservation, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT id,COALESCE(invocation_id,''),run_id,COALESCE(source_type,source),COALESCE(source_host,''),COALESCE(adapter_version,''),scope,status,COALESCE(accounting_basis,''),input_tokens,output_tokens,cache_read_tokens,cache_write_tokens,reasoning_tokens,inclusion_json,COALESCE(mapping_revision,''),COALESCE(observed_at,created_at) FROM usage_observations WHERE run_id=? ORDER BY COALESCE(observed_at,created_at) DESC`, runID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var observations []domain.UsageObservation
	for rows.Next() {
		var current domain.UsageObservation
		var inclusion string
		var input, output, cacheRead, cacheCreation, reasoning sql.NullInt64
		if err := rows.Scan(&current.ID, &current.InvocationID, &current.RunID, &current.SourceType, &current.SourceHost, &current.AdapterVersion, &current.Scope, &current.Status, &current.AccountingBasis, &input, &output, &cacheRead, &cacheCreation, &reasoning, &inclusion, &current.MappingRevision, &current.ObservedAt); err != nil {
			return nil, err
		}
		current.Tokens = domain.UsageTokens{InputTotal: nullableInt64(input), OutputTotal: nullableInt64(output), CacheReadInput: nullableInt64(cacheRead), CacheCreationInput: nullableInt64(cacheCreation), ReasoningOutput: nullableInt64(reasoning)}
		_ = json.Unmarshal([]byte(inclusion), &current.Inclusion)
		observations = append(observations, current)
	}
	return observations, rows.Err()
}

func (r *Runtime) CostObservations(ctx context.Context, runID string) ([]domain.CostObservation, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT id,COALESCE(invocation_id,''),run_id,source,kind,COALESCE(currency,''),COALESCE(credit_type,''),amount,status,COALESCE(mapping_revision,''),observed_at FROM cost_observations WHERE run_id=? ORDER BY observed_at DESC`, runID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var observations []domain.CostObservation
	for rows.Next() {
		var current domain.CostObservation
		if err := rows.Scan(&current.ID, &current.InvocationID, &current.RunID, &current.Source, &current.Kind, &current.Currency, &current.CreditType, &current.Amount, &current.Status, &current.MappingRevision, &current.ObservedAt); err != nil {
			return nil, err
		}
		observations = append(observations, current)
	}
	return observations, rows.Err()
}

func validObservationStatus(status string) bool {
	switch status {
	case "reported", "derived", "estimated", "unavailable":
		return true
	default:
		return false
	}
}

func nullableInt64(value sql.NullInt64) *int64 {
	if !value.Valid {
		return nil
	}
	result := value.Int64
	return &result
}

func defaultMap(value map[string]any) map[string]any {
	if value == nil {
		return map[string]any{}
	}
	return value
}

func textValue(value map[string]any, key string) string {
	if text, ok := value[key].(string); ok {
		return strings.TrimSpace(text)
	}
	return ""
}

func (r *Runtime) ModelCatalog(ctx context.Context, id string) (ModelCatalogSnapshot, error) {
	var snapshot ModelCatalogSnapshot
	var models string
	err := r.db.QueryRowContext(ctx, `SELECT id,host,COALESCE(scope,''),models_json,observed_at FROM model_catalog_snapshots WHERE id=?`, id).Scan(&snapshot.ID, &snapshot.Host, &snapshot.Scope, &models, &snapshot.ObservedAt)
	if errors.Is(err, sql.ErrNoRows) {
		return ModelCatalogSnapshot{}, ErrNotFound
	}
	_ = json.Unmarshal([]byte(models), &snapshot.Models)
	return snapshot, err
}
