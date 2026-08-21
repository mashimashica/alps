package runtime

import (
	"context"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/mashimashica/alps/internal/domain"
)

const (
	RunCreated                  = "created"
	RunActive                   = "active"
	RunWaitingForDecision       = "waiting_for_decision"
	RunWaitingForInput          = "waiting_for_input"
	RunWaitingForExternalResult = "waiting_for_external_result"
	RunWaitingForResource       = "waiting_for_resource"
	RunCompletionRequested      = "completion_requested"
	RunCompleted                = "completed"
	RunFailed                   = "failed"
	RunCancelled                = "cancelled"
)

type Run struct {
	ID                     string            `json:"id"`
	Title                  string            `json:"title"`
	Process                string            `json:"process"`
	AssetID                string            `json:"assetId,omitempty"`
	State                  string            `json:"state"`
	Version                int64             `json:"version"`
	Progress               *int              `json:"progress,omitempty"`
	StatusText             string            `json:"statusText"`
	ProcessRevisionID      string            `json:"processRevisionId,omitempty"`
	SkillPackageRevisionID string            `json:"skillPackageRevisionId,omitempty"`
	PluginRevisionIDs      []string          `json:"pluginRevisionIds,omitempty"`
	ProcessModelRevisionID string            `json:"processModelRevisionId,omitempty"`
	Context                domain.RunContext `json:"context"`
	Actor                  domain.Actor      `json:"actor"`
	CreatedAt              string            `json:"createdAt"`
	UpdatedAt              string            `json:"updatedAt"`
	CompletionRequestedAt  string            `json:"completionRequestedAt,omitempty"`
	CompletedAt            string            `json:"completedAt,omitempty"`
	FailedAt               string            `json:"failedAt,omitempty"`
	CancelledAt            string            `json:"cancelledAt,omitempty"`
}

type RunReport struct {
	ID        string               `json:"id"`
	RunID     string               `json:"runId"`
	Actor     string               `json:"actor"`
	Message   string               `json:"message"`
	Progress  *int                 `json:"progress,omitempty"`
	Claims    map[string]any       `json:"claims,omitempty"`
	Evidence  []domain.EvidenceRef `json:"evidence,omitempty"`
	CreatedAt string               `json:"createdAt"`
}

type Gate struct {
	ID                 string               `json:"id"`
	RunID              string               `json:"runId"`
	Title              string               `json:"title"`
	Effect             string               `json:"effect"`
	ExternalEffect     string               `json:"externalEffect,omitempty"`
	Reversible         bool                 `json:"reversible"`
	Authority          string               `json:"authority"`
	Status             string               `json:"status"`
	TargetRevisionID   string               `json:"targetRevisionId,omitempty"`
	ExpectedRunVersion int64                `json:"expectedRunVersion"`
	Criteria           []string             `json:"criteria,omitempty"`
	Controls           []string             `json:"controls,omitempty"`
	Constraints        []string             `json:"constraints,omitempty"`
	Evidence           []domain.EvidenceRef `json:"evidence,omitempty"`
	Unknown            []string             `json:"unknown,omitempty"`
	CreatedAt          string               `json:"createdAt"`
	DecidedAt          string               `json:"decidedAt,omitempty"`
}

type Decision struct {
	ID         string               `json:"id"`
	GateID     string               `json:"gateId"`
	Type       string               `json:"type"`
	Actor      string               `json:"actor"`
	Authority  string               `json:"authority,omitempty"`
	Rationale  string               `json:"rationale,omitempty"`
	Conditions []string             `json:"conditions,omitempty"`
	Evidence   []domain.EvidenceRef `json:"evidence,omitempty"`
	Final      bool                 `json:"final"`
	CreatedAt  string               `json:"createdAt"`
}

type Artifact struct {
	ID             string         `json:"id"`
	RunID          string         `json:"runId"`
	Name           string         `json:"name"`
	Digest         string         `json:"digest"`
	MediaType      string         `json:"mediaType"`
	Size           int64          `json:"size"`
	Path           string         `json:"path"`
	Role           string         `json:"role"`
	ProcessElement string         `json:"processElement,omitempty"`
	Provenance     map[string]any `json:"provenance,omitempty"`
	CreatedAt      string         `json:"createdAt"`
}

type ModelInvocation struct {
	ID                string         `json:"id"`
	RunID             string         `json:"runId"`
	Requested         map[string]any `json:"requested"`
	Effective         map[string]any `json:"effective"`
	Resolved          map[string]any `json:"resolved"`
	Parameters        map[string]any `json:"parameters,omitempty"`
	Role              string         `json:"role,omitempty"`
	CatalogSnapshotID string         `json:"catalogSnapshotId,omitempty"`
	StartedAt         string         `json:"startedAt,omitempty"`
	FinishedAt        string         `json:"finishedAt,omitempty"`
	CreatedAt         string         `json:"createdAt"`
}

type RunDetail struct {
	Run         Run                       `json:"run"`
	Outcomes    []domain.OutcomeStatus    `json:"outcomes"`
	Reports     []RunReport               `json:"reports"`
	OpenGate    *Gate                     `json:"gate,omitempty"`
	Decisions   []Decision                `json:"decisions"`
	Artifacts   []Artifact                `json:"artifacts"`
	Assessments []domain.Assessment       `json:"assessments"`
	Handoffs    []domain.Handoff          `json:"handoffs"`
	Invocations []ModelInvocation         `json:"modelInvocations"`
	Usage       []domain.UsageObservation `json:"usageObservations"`
	Costs       []domain.CostObservation  `json:"costObservations"`
	Events      []domain.Event            `json:"events"`
}

type StartRunInput struct {
	Title                  string            `json:"title"`
	Process                string            `json:"process"`
	AssetID                string            `json:"assetId,omitempty"`
	ProcessRevisionID      string            `json:"processRevisionId,omitempty"`
	SkillPackageRevisionID string            `json:"skillPackageRevisionId,omitempty"`
	PluginRevisionIDs      []string          `json:"pluginRevisionIds,omitempty"`
	ProcessModelRevisionID string            `json:"processModelRevisionId,omitempty"`
	Context                domain.RunContext `json:"context,omitempty"`
	Outcomes               []string          `json:"outcomes,omitempty"`
}

type ReportRunInput struct {
	Actor           string               `json:"actor"`
	Message         string               `json:"message"`
	Progress        *int                 `json:"progress,omitempty"`
	Claims          map[string]any       `json:"claims,omitempty"`
	Evidence        []domain.EvidenceRef `json:"evidence,omitempty"`
	ExpectedVersion int64                `json:"expectedVersion"`
}

type OpenGateInput struct {
	Title            string               `json:"title"`
	Effect           string               `json:"effect"`
	ExternalEffect   string               `json:"externalEffect,omitempty"`
	Authority        string               `json:"authority"`
	Reversible       bool                 `json:"reversible"`
	TargetRevisionID string               `json:"targetRevisionId,omitempty"`
	Criteria         []string             `json:"criteria,omitempty"`
	Controls         []string             `json:"controls,omitempty"`
	Constraints      []string             `json:"constraints,omitempty"`
	Evidence         []domain.EvidenceRef `json:"evidence,omitempty"`
	Unknown          []string             `json:"unknown,omitempty"`
	ExpectedVersion  int64                `json:"expectedVersion"`
}

type DecisionInput struct {
	Decision        string               `json:"decision"`
	Actor           string               `json:"actor"`
	Authority       string               `json:"authority,omitempty"`
	Rationale       string               `json:"rationale,omitempty"`
	Conditions      []string             `json:"conditions,omitempty"`
	Evidence        []domain.EvidenceRef `json:"evidence,omitempty"`
	ExpectedVersion int64                `json:"expectedVersion"`
}

type ArtifactInput struct {
	Name           string         `json:"name"`
	MediaType      string         `json:"mediaType"`
	Role           string         `json:"role,omitempty"`
	ProcessElement string         `json:"processElement,omitempty"`
	Provenance     map[string]any `json:"provenance,omitempty"`
	Content        []byte         `json:"-"`
}

func (r *Runtime) CreateRun(ctx context.Context, title, process, assetID string) (Run, error) {
	return r.StartRun(ctx, StartRunInput{Title: title, Process: process, AssetID: assetID})
}

func (r *Runtime) StartRun(ctx context.Context, input StartRunInput) (Run, error) {
	input.Title = strings.TrimSpace(input.Title)
	input.Process = strings.TrimSpace(input.Process)
	if input.Title == "" || input.Process == "" {
		return Run{}, fmt.Errorf("%w: title and process are required", ErrInvalid)
	}
	if input.AssetID != "" {
		detail, err := r.Asset(ctx, input.AssetID)
		if err != nil {
			return Run{}, err
		}
		asset := detail.Asset
		if input.SkillPackageRevisionID == "" && asset.Kind == "skill" {
			input.SkillPackageRevisionID = asset.AdoptedRevisionID
		}
		if input.ProcessRevisionID == "" && input.SkillPackageRevisionID != "" {
			_ = r.db.QueryRowContext(ctx, `SELECT process_revision_id FROM skill_package_revisions WHERE id=?`, input.SkillPackageRevisionID).Scan(&input.ProcessRevisionID)
		}
		if len(input.Outcomes) == 0 && input.ProcessRevisionID != "" {
			var raw string
			if err := r.db.QueryRowContext(ctx, `SELECT outcomes_json FROM process_revisions WHERE id=?`, input.ProcessRevisionID).Scan(&raw); err == nil {
				_ = json.Unmarshal([]byte(raw), &input.Outcomes)
			}
		}
	}
	input.Context.ProcessRevisionID = defaultString(input.Context.ProcessRevisionID, input.ProcessRevisionID)
	input.Context.SkillPackageRevisionID = defaultString(input.Context.SkillPackageRevisionID, input.SkillPackageRevisionID)
	input.Context.ProcessModelRevisionID = defaultString(input.Context.ProcessModelRevisionID, input.ProcessModelRevisionID)
	if len(input.Context.PluginRevisionIDs) == 0 {
		input.Context.PluginRevisionIDs = append([]string(nil), input.PluginRevisionIDs...)
	}

	actor := ActorFromContext(ctx)
	timestamp := now()
	run := Run{
		ID:                     newID("run"),
		Title:                  input.Title,
		Process:                input.Process,
		AssetID:                input.AssetID,
		State:                  RunActive,
		Version:                1,
		StatusText:             "Started",
		ProcessRevisionID:      input.ProcessRevisionID,
		SkillPackageRevisionID: input.SkillPackageRevisionID,
		PluginRevisionIDs:      append([]string(nil), input.PluginRevisionIDs...),
		ProcessModelRevisionID: input.ProcessModelRevisionID,
		Context:                input.Context,
		Actor:                  actor,
		CreatedAt:              timestamp,
		UpdatedAt:              timestamp,
	}
	var event domain.Event
	err := r.write(ctx, "run.start", func(tx *sql.Tx) error {
		_, err := tx.ExecContext(ctx, `INSERT INTO runs(id,title,process,asset_id,state,version,status_text,process_revision_id,skill_package_revision_id,plugin_revision_ids_json,process_model_revision_id,context_json,actor_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
			run.ID, run.Title, run.Process, nullIfEmpty(run.AssetID), run.State, run.Version, run.StatusText,
			nullIfEmpty(run.ProcessRevisionID), nullIfEmpty(run.SkillPackageRevisionID), marshal(run.PluginRevisionIDs), nullIfEmpty(run.ProcessModelRevisionID), marshal(run.Context), marshal(run.Actor), run.CreatedAt, run.UpdatedAt)
		if err != nil {
			return err
		}
		for _, outcome := range uniqueNonEmpty(input.Outcomes) {
			_, err = tx.ExecContext(ctx, `INSERT INTO run_outcomes(id,run_id,name,status,required,evidence_json,updated_at) VALUES(?,?,?,?,1,'[]',?)`, newID("outcome"), run.ID, outcome, "unassessed", timestamp)
			if err != nil {
				return err
			}
		}
		if _, err = tx.ExecContext(ctx, `INSERT INTO run_state_intervals(id,run_id,state,started_at) VALUES(?,?,?,?)`, newID("interval"), run.ID, run.State, timestamp); err != nil {
			return err
		}
		event, err = appendEventTx(ctx, tx, actor, "run", run.ID, "run.created", run.ID, "", "v1", run)
		return err
	})
	if err != nil {
		return Run{}, err
	}
	r.publish(event)
	return run, nil
}

func (r *Runtime) Runs(ctx context.Context) ([]Run, error) {
	rows, err := r.db.QueryContext(ctx, runSelect+` ORDER BY updated_at DESC`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var runs []Run
	for rows.Next() {
		run, err := scanRun(rows)
		if err != nil {
			return nil, err
		}
		runs = append(runs, run)
	}
	return runs, rows.Err()
}

func (r *Runtime) Run(ctx context.Context, id string) (Run, error) {
	run, err := scanRun(r.db.QueryRowContext(ctx, runSelect+` WHERE id=?`, id))
	if errors.Is(err, sql.ErrNoRows) {
		return Run{}, ErrNotFound
	}
	return run, err
}

const runSelect = `SELECT id,title,process,COALESCE(asset_id,''),state,version,progress,status_text,COALESCE(process_revision_id,''),COALESCE(skill_package_revision_id,''),COALESCE(plugin_revision_ids_json,'[]'),COALESCE(process_model_revision_id,''),COALESCE(context_json,'{}'),COALESCE(actor_json,'{}'),created_at,updated_at,COALESCE(completion_requested_at,''),COALESCE(completed_at,''),COALESCE(failed_at,''),COALESCE(cancelled_at,'') FROM runs`

func scanRun(row rowScanner) (Run, error) {
	var run Run
	var progress sql.NullInt64
	var pluginJSON, contextJSON, actorJSON string
	err := row.Scan(&run.ID, &run.Title, &run.Process, &run.AssetID, &run.State, &run.Version, &progress, &run.StatusText,
		&run.ProcessRevisionID, &run.SkillPackageRevisionID, &pluginJSON, &run.ProcessModelRevisionID, &contextJSON, &actorJSON,
		&run.CreatedAt, &run.UpdatedAt, &run.CompletionRequestedAt, &run.CompletedAt, &run.FailedAt, &run.CancelledAt)
	if err != nil {
		return Run{}, err
	}
	if progress.Valid {
		value := int(progress.Int64)
		run.Progress = &value
	}
	_ = json.Unmarshal([]byte(pluginJSON), &run.PluginRevisionIDs)
	_ = json.Unmarshal([]byte(contextJSON), &run.Context)
	_ = json.Unmarshal([]byte(actorJSON), &run.Actor)
	return run, nil
}

func (r *Runtime) RunDetail(ctx context.Context, id string) (RunDetail, error) {
	run, err := r.Run(ctx, id)
	if err != nil {
		return RunDetail{}, err
	}
	detail := RunDetail{Run: run}
	detail.Outcomes, _ = r.Outcomes(ctx, id)
	detail.Reports, _ = r.RunReports(ctx, id)
	detail.Artifacts, _ = r.Artifacts(ctx, id)
	detail.Assessments, _ = r.Assessments(ctx, id)
	detail.Handoffs, _ = r.HandoffsForRun(ctx, id)
	detail.Invocations, _ = r.ModelInvocations(ctx, id)
	detail.Usage, _ = r.UsageObservations(ctx, id)
	detail.Costs, _ = r.CostObservations(ctx, id)
	detail.Decisions, _ = r.DecisionsForRun(ctx, id)
	detail.Events, _ = r.EventsForStream(ctx, "run", id, 1000)
	gates, _ := r.GatesForRun(ctx, id, "open")
	if len(gates) > 0 {
		detail.OpenGate = &gates[0]
	}
	return detail, nil
}

func (r *Runtime) ReportRun(ctx context.Context, id, actor, message string, progress *int, expected int64) (Run, error) {
	return r.Report(ctx, id, ReportRunInput{Actor: actor, Message: message, Progress: progress, ExpectedVersion: expected})
}

func (r *Runtime) Report(ctx context.Context, id string, input ReportRunInput) (Run, error) {
	if strings.TrimSpace(input.Message) == "" {
		return Run{}, fmt.Errorf("%w: report message is required", ErrInvalid)
	}
	if input.Progress != nil && (*input.Progress < 0 || *input.Progress > 100) {
		return Run{}, fmt.Errorf("%w: progress must be between 0 and 100", ErrInvalid)
	}
	actor := ActorFromContext(ctx)
	if input.Actor == "" {
		input.Actor = actor.ID
	}
	var event domain.Event
	err := r.write(ctx, "run.report", func(tx *sql.Tx) error {
		version, state, err := currentRunVersionTx(ctx, tx, id)
		if err != nil {
			return err
		}
		if terminalState(state) {
			return fmt.Errorf("%w: terminal Run cannot be reported", ErrConflict)
		}
		if input.ExpectedVersion > 0 && version != input.ExpectedVersion {
			return ErrStale
		}
		newVersion := version + 1
		timestamp := now()
		if _, err := tx.ExecContext(ctx, `UPDATE runs SET version=?,progress=?,status_text=?,updated_at=? WHERE id=?`, newVersion, input.Progress, input.Message, timestamp, id); err != nil {
			return err
		}
		report := RunReport{ID: newID("report"), RunID: id, Actor: input.Actor, Message: input.Message, Progress: input.Progress, Claims: input.Claims, Evidence: input.Evidence, CreatedAt: timestamp}
		if _, err := tx.ExecContext(ctx, `INSERT INTO run_reports(id,run_id,actor,message,progress,claims_json,evidence_json,created_at) VALUES(?,?,?,?,?,?,?,?)`, report.ID, id, report.Actor, report.Message, report.Progress, marshal(report.Claims), marshal(report.Evidence), report.CreatedAt); err != nil {
			return err
		}
		event, err = appendEventTx(ctx, tx, actor, "run", id, "run.reported", id, "", "v1", map[string]any{"report": report, "version": newVersion})
		return err
	})
	if err != nil {
		return Run{}, err
	}
	r.publish(event)
	return r.Run(ctx, id)
}

func (r *Runtime) RequestCompletion(ctx context.Context, id string, expected int64) (Run, error) {
	actor := ActorFromContext(ctx)
	var event domain.Event
	err := r.transition(ctx, id, expected, RunCompletionRequested, "Completion requested", actor, "run.completion_requested", func(tx *sql.Tx, timestamp string) error {
		_, err := tx.ExecContext(ctx, `UPDATE runs SET completion_requested_at=? WHERE id=?`, timestamp, id)
		return err
	}, &event)
	if err != nil {
		return Run{}, err
	}
	r.publish(event)
	return r.Run(ctx, id)
}

func (r *Runtime) CompleteRun(ctx context.Context, id string, expected int64) (Run, error) {
	blockers, err := r.CompletionBlockers(ctx, id)
	if err != nil {
		return Run{}, err
	}
	if len(blockers) > 0 {
		return Run{}, fmt.Errorf("%w: %s", ErrCompletionBlocked, strings.Join(blockers, "; "))
	}
	actor := ActorFromContext(ctx)
	var event domain.Event
	err = r.transition(ctx, id, expected, RunCompleted, "Completed", actor, "run.completed", func(tx *sql.Tx, timestamp string) error {
		_, err := tx.ExecContext(ctx, `UPDATE runs SET completed_at=?,progress=100 WHERE id=?`, timestamp, id)
		return err
	}, &event)
	if err != nil {
		return Run{}, err
	}
	r.publish(event)
	return r.Run(ctx, id)
}

func (r *Runtime) CompletionBlockers(ctx context.Context, id string) ([]string, error) {
	run, err := r.Run(ctx, id)
	if err != nil {
		return nil, err
	}
	if terminalState(run.State) {
		return []string{"Run is already terminal"}, nil
	}
	var blockers []string
	var count int
	if err := r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM decision_gates WHERE run_id=? AND status='open'`, id).Scan(&count); err != nil {
		return nil, err
	}
	if count > 0 {
		blockers = append(blockers, "an unresolved Decision Gate remains")
	}
	if err := r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM run_outcomes WHERE run_id=? AND required=1 AND status!='assessed_achieved'`, id).Scan(&count); err != nil {
		return nil, err
	}
	if count > 0 {
		blockers = append(blockers, fmt.Sprintf("%d required Outcome(s) are not assessed as achieved", count))
	}
	if err := r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM handoffs WHERE provider_run_id=? AND status NOT IN ('accepted','cancelled')`, id).Scan(&count); err != nil {
		return nil, err
	}
	if count > 0 {
		blockers = append(blockers, fmt.Sprintf("%d Handoff(s) are unresolved", count))
	}
	for _, criterion := range run.Context.ExitCriteria {
		if strings.TrimSpace(criterion) == "" {
			blockers = append(blockers, "an Exit Criterion is empty")
		}
	}
	return blockers, nil
}

func (r *Runtime) transition(ctx context.Context, id string, expected int64, newState, status string, actor domain.Actor, eventType string, extra func(*sql.Tx, string) error, event *domain.Event) error {
	return r.write(ctx, eventType, func(tx *sql.Tx) error {
		version, oldState, err := currentRunVersionTx(ctx, tx, id)
		if err != nil {
			return err
		}
		if expected > 0 && version != expected {
			return ErrStale
		}
		if terminalState(oldState) {
			return fmt.Errorf("%w: terminal Run cannot transition", ErrConflict)
		}
		timestamp := now()
		if _, err := tx.ExecContext(ctx, `UPDATE run_state_intervals SET ended_at=? WHERE run_id=? AND ended_at IS NULL`, timestamp, id); err != nil {
			return err
		}
		if _, err := tx.ExecContext(ctx, `INSERT INTO run_state_intervals(id,run_id,state,started_at) VALUES(?,?,?,?)`, newID("interval"), id, newState, timestamp); err != nil {
			return err
		}
		if _, err := tx.ExecContext(ctx, `UPDATE runs SET state=?,version=version+1,status_text=?,updated_at=? WHERE id=?`, newState, status, timestamp, id); err != nil {
			return err
		}
		if extra != nil {
			if err := extra(tx, timestamp); err != nil {
				return err
			}
		}
		*event, err = appendEventTx(ctx, tx, actor, "run", id, eventType, id, "", "v1", map[string]any{"from": oldState, "to": newState, "version": version + 1})
		return err
	})
}

func currentRunVersionTx(ctx context.Context, tx *sql.Tx, id string) (int64, string, error) {
	var version int64
	var state string
	if err := tx.QueryRowContext(ctx, `SELECT version,state FROM runs WHERE id=?`, id).Scan(&version, &state); err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return 0, "", ErrNotFound
		}
		return 0, "", err
	}
	return version, state, nil
}

func terminalState(state string) bool {
	return state == RunCompleted || state == RunFailed || state == RunCancelled
}

func (r *Runtime) OpenGate(ctx context.Context, runID, title, effect, authority string, reversible bool, expected int64) (Gate, error) {
	return r.CreateGate(ctx, runID, OpenGateInput{Title: title, Effect: effect, Authority: authority, Reversible: reversible, ExpectedVersion: expected})
}

func (r *Runtime) CreateGate(ctx context.Context, runID string, input OpenGateInput) (Gate, error) {
	if strings.TrimSpace(input.Title) == "" || strings.TrimSpace(input.Effect) == "" {
		return Gate{}, fmt.Errorf("%w: gate title and effect are required", ErrInvalid)
	}
	if input.Authority == "" {
		input.Authority = "operator"
	}
	actor := ActorFromContext(ctx)
	var gate Gate
	var event domain.Event
	err := r.write(ctx, "gate.open", func(tx *sql.Tx) error {
		version, state, err := currentRunVersionTx(ctx, tx, runID)
		if err != nil {
			return err
		}
		if terminalState(state) {
			return fmt.Errorf("%w: terminal Run cannot open a gate", ErrConflict)
		}
		if input.ExpectedVersion > 0 && version != input.ExpectedVersion {
			return ErrStale
		}
		var openCount int
		if err := tx.QueryRowContext(ctx, `SELECT COUNT(*) FROM decision_gates WHERE run_id=? AND status='open'`, runID).Scan(&openCount); err != nil {
			return err
		}
		if openCount > 0 {
			return fmt.Errorf("%w: Run already has an open Decision Gate", ErrConflict)
		}
		timestamp := now()
		gate = Gate{ID: newID("gate"), RunID: runID, Title: input.Title, Effect: input.Effect, ExternalEffect: input.ExternalEffect, Reversible: input.Reversible, Authority: input.Authority, Status: "open", TargetRevisionID: input.TargetRevisionID, ExpectedRunVersion: version + 1, Criteria: input.Criteria, Controls: input.Controls, Constraints: input.Constraints, Evidence: input.Evidence, Unknown: input.Unknown, CreatedAt: timestamp}
		_, err = tx.ExecContext(ctx, `INSERT INTO decision_gates(id,run_id,title,effect,external_effect,reversible,authority,status,target_revision_id,expected_run_version,criteria_json,controls_json,constraints_json,evidence_json,unknown_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`, gate.ID, runID, gate.Title, gate.Effect, nullIfEmpty(gate.ExternalEffect), gate.Reversible, gate.Authority, gate.Status, nullIfEmpty(gate.TargetRevisionID), gate.ExpectedRunVersion, marshal(gate.Criteria), marshal(gate.Controls), marshal(gate.Constraints), marshal(gate.Evidence), marshal(gate.Unknown), timestamp)
		if err != nil {
			return err
		}
		if _, err := tx.ExecContext(ctx, `UPDATE run_state_intervals SET ended_at=? WHERE run_id=? AND ended_at IS NULL`, timestamp, runID); err != nil {
			return err
		}
		if _, err := tx.ExecContext(ctx, `INSERT INTO run_state_intervals(id,run_id,state,started_at) VALUES(?,?,?,?)`, newID("interval"), runID, RunWaitingForDecision, timestamp); err != nil {
			return err
		}
		if _, err := tx.ExecContext(ctx, `UPDATE runs SET state=?,version=version+1,status_text=?,updated_at=? WHERE id=?`, RunWaitingForDecision, gate.Title, timestamp, runID); err != nil {
			return err
		}
		event, err = appendEventTx(ctx, tx, actor, "run", runID, "gate.opened", runID, "", "v1", gate)
		return err
	})
	if err != nil {
		return Gate{}, err
	}
	r.publish(event)
	return gate, nil
}

func (r *Runtime) Gates(ctx context.Context) ([]Gate, error) { return r.GatesForRun(ctx, "", "open") }

func (r *Runtime) GatesForRun(ctx context.Context, runID, status string) ([]Gate, error) {
	query := gateSelect + ` WHERE 1=1`
	var arguments []any
	if runID != "" {
		query += ` AND run_id=?`
		arguments = append(arguments, runID)
	}
	if status != "" {
		query += ` AND status=?`
		arguments = append(arguments, status)
	}
	query += ` ORDER BY created_at DESC`
	rows, err := r.db.QueryContext(ctx, query, arguments...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var gates []Gate
	for rows.Next() {
		gate, err := scanGate(rows)
		if err != nil {
			return nil, err
		}
		gates = append(gates, gate)
	}
	return gates, rows.Err()
}

func (r *Runtime) Gate(ctx context.Context, id string) (Gate, error) {
	gate, err := scanGate(r.db.QueryRowContext(ctx, gateSelect+` WHERE id=?`, id))
	if errors.Is(err, sql.ErrNoRows) {
		return Gate{}, ErrNotFound
	}
	return gate, err
}

const gateSelect = `SELECT id,run_id,title,effect,COALESCE(external_effect,''),reversible,authority,status,COALESCE(target_revision_id,''),expected_run_version,criteria_json,controls_json,constraints_json,evidence_json,unknown_json,created_at,COALESCE(decided_at,'') FROM decision_gates`

func scanGate(row rowScanner) (Gate, error) {
	var gate Gate
	var criteria, controls, constraints, evidence, unknown string
	err := row.Scan(&gate.ID, &gate.RunID, &gate.Title, &gate.Effect, &gate.ExternalEffect, &gate.Reversible, &gate.Authority, &gate.Status, &gate.TargetRevisionID, &gate.ExpectedRunVersion, &criteria, &controls, &constraints, &evidence, &unknown, &gate.CreatedAt, &gate.DecidedAt)
	if err != nil {
		return Gate{}, err
	}
	_ = json.Unmarshal([]byte(criteria), &gate.Criteria)
	_ = json.Unmarshal([]byte(controls), &gate.Controls)
	_ = json.Unmarshal([]byte(constraints), &gate.Constraints)
	_ = json.Unmarshal([]byte(evidence), &gate.Evidence)
	_ = json.Unmarshal([]byte(unknown), &gate.Unknown)
	return gate, nil
}

func (r *Runtime) Decide(ctx context.Context, gateID, decision, actor, rationale string, expected int64) error {
	_, err := r.RecordDecision(ctx, gateID, DecisionInput{Decision: decision, Actor: actor, Rationale: rationale, ExpectedVersion: expected})
	return err
}

func (r *Runtime) RecordDecision(ctx context.Context, gateID string, input DecisionInput) (Decision, error) {
	valid := map[string]bool{"continue": true, "hold": true, "change": true, "re-execute": true, "terminate": true}
	if !valid[input.Decision] {
		return Decision{}, fmt.Errorf("%w: unsupported Decision", ErrInvalid)
	}
	contextActor := ActorFromContext(ctx)
	if input.Actor == "" {
		input.Actor = contextActor.ID
	}
	if input.Authority == "" {
		input.Authority = contextActor.Authority
	}
	var recorded Decision
	var event domain.Event
	err := r.write(ctx, "decision.record", func(tx *sql.Tx) error {
		gate, err := scanGate(tx.QueryRowContext(ctx, gateSelect+` WHERE id=?`, gateID))
		if err != nil {
			if errors.Is(err, sql.ErrNoRows) {
				return ErrNotFound
			}
			return err
		}
		if gate.Status != "open" {
			return ErrStale
		}
		version, _, err := currentRunVersionTx(ctx, tx, gate.RunID)
		if err != nil {
			return err
		}
		if input.ExpectedVersion > 0 && version != input.ExpectedVersion || version != gate.ExpectedRunVersion {
			return ErrStale
		}
		if gate.Authority != "" && input.Authority != gate.Authority && input.Authority != "admin" {
			return fmt.Errorf("%w: authority %q is required", ErrForbidden, gate.Authority)
		}
		final := input.Decision != "hold"
		newState := RunWaitingForDecision
		statusText := "Held for decision"
		switch input.Decision {
		case "continue":
			newState, statusText = RunActive, "Continued"
		case "change":
			newState, statusText = RunActive, "Change requested"
		case "re-execute":
			newState, statusText = RunActive, "Re-execution requested"
		case "terminate":
			newState, statusText = RunCancelled, "Terminated"
		}
		timestamp := now()
		recorded = Decision{ID: newID("decision"), GateID: gateID, Type: input.Decision, Actor: input.Actor, Authority: input.Authority, Rationale: input.Rationale, Conditions: input.Conditions, Evidence: input.Evidence, Final: final, CreatedAt: timestamp}
		if _, err := tx.ExecContext(ctx, `INSERT INTO decisions(id,gate_id,decision_type,actor,authority,rationale,conditions_json,evidence_json,final,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)`, recorded.ID, gateID, recorded.Type, recorded.Actor, nullIfEmpty(recorded.Authority), recorded.Rationale, marshal(recorded.Conditions), marshal(recorded.Evidence), recorded.Final, timestamp); err != nil {
			return err
		}
		if final {
			if _, err := tx.ExecContext(ctx, `UPDATE decision_gates SET status='decided',decided_at=? WHERE id=?`, timestamp, gateID); err != nil {
				return err
			}
		}
		if _, err := tx.ExecContext(ctx, `UPDATE run_state_intervals SET ended_at=? WHERE run_id=? AND ended_at IS NULL`, timestamp, gate.RunID); err != nil {
			return err
		}
		if _, err := tx.ExecContext(ctx, `INSERT INTO run_state_intervals(id,run_id,state,started_at) VALUES(?,?,?,?)`, newID("interval"), gate.RunID, newState, timestamp); err != nil {
			return err
		}
		if _, err := tx.ExecContext(ctx, `UPDATE runs SET state=?,version=version+1,status_text=?,updated_at=?,cancelled_at=CASE WHEN ?='cancelled' THEN ? ELSE cancelled_at END WHERE id=?`, newState, statusText, timestamp, newState, timestamp, gate.RunID); err != nil {
			return err
		}
		event, err = appendEventTx(ctx, tx, contextActor, "run", gate.RunID, "decision.recorded", gate.RunID, gateID, "v1", recorded)
		return err
	})
	if err != nil {
		return Decision{}, err
	}
	r.publish(event)
	return recorded, nil
}

func (r *Runtime) AddArtifact(ctx context.Context, runID, name, mediaType string, data []byte) (string, error) {
	artifact, err := r.CommitArtifact(ctx, runID, ArtifactInput{Name: name, MediaType: mediaType, Role: "output", Content: data})
	return artifact.ID, err
}

func (r *Runtime) CommitArtifact(ctx context.Context, runID string, input ArtifactInput) (Artifact, error) {
	if strings.TrimSpace(input.Name) == "" || len(input.Content) == 0 {
		return Artifact{}, fmt.Errorf("%w: Artifact name and content are required", ErrInvalid)
	}
	if input.MediaType == "" {
		input.MediaType = "application/octet-stream"
	}
	if input.Role == "" {
		input.Role = "output"
	}
	if len(input.Content) > 64<<20 {
		return Artifact{}, fmt.Errorf("%w: Artifact exceeds 64 MiB", ErrInvalid)
	}
	if _, err := r.Run(ctx, runID); err != nil {
		return Artifact{}, err
	}
	digestBytes := sha256.Sum256(input.Content)
	digestHex := hex.EncodeToString(digestBytes[:])
	digest := "sha256:" + digestHex
	path := filepath.Join(r.workspace, "blobs", "sha256", digestHex)
	if _, err := os.Stat(path); errors.Is(err, os.ErrNotExist) {
		temporary := path + ".tmp-" + shortID(now())
		file, err := os.OpenFile(temporary, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o600)
		if err != nil {
			return Artifact{}, err
		}
		_, writeErr := file.Write(input.Content)
		syncErr := file.Sync()
		closeErr := file.Close()
		if err := errors.Join(writeErr, syncErr, closeErr); err != nil {
			_ = os.Remove(temporary)
			return Artifact{}, err
		}
		if err := os.Rename(temporary, path); err != nil {
			_ = os.Remove(temporary)
			return Artifact{}, err
		}
	}
	artifact := Artifact{ID: newID("artifact"), RunID: runID, Name: input.Name, Digest: digest, MediaType: input.MediaType, Size: int64(len(input.Content)), Path: path, Role: input.Role, ProcessElement: input.ProcessElement, Provenance: input.Provenance, CreatedAt: now()}
	actor := ActorFromContext(ctx)
	var event domain.Event
	err := r.write(ctx, "artifact.commit", func(tx *sql.Tx) error {
		if _, err := tx.ExecContext(ctx, `INSERT INTO artifacts(id,run_id,name,digest,media_type,size,path,role,process_element,provenance_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)`, artifact.ID, artifact.RunID, artifact.Name, artifact.Digest, artifact.MediaType, artifact.Size, artifact.Path, artifact.Role, nullIfEmpty(artifact.ProcessElement), marshal(artifact.Provenance), artifact.CreatedAt); err != nil {
			return err
		}
		relationID := newID("artifactrel")
		if _, err := tx.ExecContext(ctx, `INSERT INTO artifact_relations(id,run_id,artifact_id,role,process_element,provenance_json,created_at) VALUES(?,?,?,?,?,?,?)`, relationID, runID, artifact.ID, artifact.Role, nullIfEmpty(artifact.ProcessElement), marshal(artifact.Provenance), artifact.CreatedAt); err != nil {
			return err
		}
		var appendErr error
		event, appendErr = appendEventTx(ctx, tx, actor, "run", runID, "artifact.committed", runID, "", "v1", artifact)
		if appendErr != nil {
			return appendErr
		}
		_, appendErr = tx.ExecContext(ctx, `UPDATE artifact_relations SET created_event_id=? WHERE id=?`, event.EventID, relationID)
		return appendErr
	})
	if err != nil {
		return Artifact{}, err
	}
	r.publish(event)
	return artifact, nil
}

func (r *Runtime) Outcomes(ctx context.Context, runID string) ([]domain.OutcomeStatus, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT id,run_id,name,status,required,evidence_json,COALESCE(assessment_id,''),updated_at FROM run_outcomes WHERE run_id=? ORDER BY name`, runID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var outcomes []domain.OutcomeStatus
	for rows.Next() {
		var outcome domain.OutcomeStatus
		var evidence string
		if err := rows.Scan(&outcome.ID, &outcome.RunID, &outcome.Name, &outcome.Status, &outcome.Required, &evidence, &outcome.AssessmentID, &outcome.UpdatedAt); err != nil {
			return nil, err
		}
		_ = json.Unmarshal([]byte(evidence), &outcome.Evidence)
		outcomes = append(outcomes, outcome)
	}
	return outcomes, rows.Err()
}

func (r *Runtime) RunReports(ctx context.Context, runID string) ([]RunReport, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT id,run_id,actor,message,progress,claims_json,evidence_json,created_at FROM run_reports WHERE run_id=? ORDER BY created_at DESC`, runID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var reports []RunReport
	for rows.Next() {
		var report RunReport
		var progress sql.NullInt64
		var claims, evidence string
		if err := rows.Scan(&report.ID, &report.RunID, &report.Actor, &report.Message, &progress, &claims, &evidence, &report.CreatedAt); err != nil {
			return nil, err
		}
		if progress.Valid {
			value := int(progress.Int64)
			report.Progress = &value
		}
		_ = json.Unmarshal([]byte(claims), &report.Claims)
		_ = json.Unmarshal([]byte(evidence), &report.Evidence)
		reports = append(reports, report)
	}
	return reports, rows.Err()
}

func (r *Runtime) Artifacts(ctx context.Context, runID string) ([]Artifact, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT id,run_id,name,digest,media_type,size,path,role,COALESCE(process_element,''),provenance_json,created_at FROM artifacts WHERE run_id=? ORDER BY created_at DESC`, runID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var artifacts []Artifact
	for rows.Next() {
		var artifact Artifact
		var provenance string
		if err := rows.Scan(&artifact.ID, &artifact.RunID, &artifact.Name, &artifact.Digest, &artifact.MediaType, &artifact.Size, &artifact.Path, &artifact.Role, &artifact.ProcessElement, &provenance, &artifact.CreatedAt); err != nil {
			return nil, err
		}
		_ = json.Unmarshal([]byte(provenance), &artifact.Provenance)
		artifacts = append(artifacts, artifact)
	}
	return artifacts, rows.Err()
}

func (r *Runtime) DecisionsForRun(ctx context.Context, runID string) ([]Decision, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT d.id,d.gate_id,d.decision_type,d.actor,COALESCE(d.authority,''),d.rationale,d.conditions_json,d.evidence_json,d.final,d.created_at FROM decisions d JOIN decision_gates g ON g.id=d.gate_id WHERE g.run_id=? ORDER BY d.created_at DESC`, runID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var decisions []Decision
	for rows.Next() {
		var decision Decision
		var conditions, evidence string
		if err := rows.Scan(&decision.ID, &decision.GateID, &decision.Type, &decision.Actor, &decision.Authority, &decision.Rationale, &conditions, &evidence, &decision.Final, &decision.CreatedAt); err != nil {
			return nil, err
		}
		_ = json.Unmarshal([]byte(conditions), &decision.Conditions)
		_ = json.Unmarshal([]byte(evidence), &decision.Evidence)
		decisions = append(decisions, decision)
	}
	return decisions, rows.Err()
}

func uniqueNonEmpty(values []string) []string {
	seen := map[string]struct{}{}
	var result []string
	for _, value := range values {
		value = strings.TrimSpace(value)
		if value == "" {
			continue
		}
		if _, exists := seen[value]; exists {
			continue
		}
		seen[value] = struct{}{}
		result = append(result, value)
	}
	sort.Strings(result)
	return result
}
