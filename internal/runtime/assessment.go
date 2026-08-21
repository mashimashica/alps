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

type AssessmentInput struct {
	RunID            string               `json:"runId,omitempty"`
	SubjectType      string               `json:"subjectType"`
	SubjectID        string               `json:"subjectId"`
	AssessmentType   string               `json:"assessmentType"`
	CriteriaRevision string               `json:"criteriaRevision,omitempty"`
	Result           string               `json:"result"`
	Rationale        string               `json:"rationale,omitempty"`
	Evidence         []domain.EvidenceRef `json:"evidence,omitempty"`
}

type HandoffInput struct {
	ProviderRunID      string               `json:"providerRunId"`
	ProviderArtifactID string               `json:"providerArtifactId"`
	RecipientRunID     string               `json:"recipientRunId,omitempty"`
	RecipientProcessID string               `json:"recipientProcessId,omitempty"`
	RecipientInput     string               `json:"recipientInput"`
	CriteriaRevision   string               `json:"criteriaRevision,omitempty"`
	Status             string               `json:"status,omitempty"`
	Evidence           []domain.EvidenceRef `json:"evidence,omitempty"`
}

func (r *Runtime) RecordAssessment(ctx context.Context, input AssessmentInput) (domain.Assessment, error) {
	if input.SubjectType == "" || input.SubjectID == "" || input.AssessmentType == "" || input.Result == "" {
		return domain.Assessment{}, fmt.Errorf("%w: subject, assessment type, and result are required", ErrInvalid)
	}
	actor := ActorFromContext(ctx)
	assessment := domain.Assessment{
		ID:               newID("assessment"),
		RunID:            input.RunID,
		SubjectType:      input.SubjectType,
		SubjectID:        input.SubjectID,
		AssessmentType:   input.AssessmentType,
		CriteriaRevision: input.CriteriaRevision,
		Result:           input.Result,
		Rationale:        input.Rationale,
		Evidence:         input.Evidence,
		Actor:            actor,
		CreatedAt:        now(),
	}
	streamID := input.SubjectID
	if input.RunID != "" {
		streamID = input.RunID
	}
	var event domain.Event
	err := r.write(ctx, "assessment.record", func(tx *sql.Tx) error {
		if input.RunID != "" {
			if _, _, err := currentRunVersionTx(ctx, tx, input.RunID); err != nil {
				return err
			}
		}
		_, err := tx.ExecContext(ctx, `INSERT INTO assessments(id,run_id,subject_type,subject_id,assessment_type,criteria_revision,result,rationale,evidence_json,actor_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)`, assessment.ID, nullIfEmpty(assessment.RunID), assessment.SubjectType, assessment.SubjectID, assessment.AssessmentType, nullIfEmpty(assessment.CriteriaRevision), assessment.Result, nullIfEmpty(assessment.Rationale), marshal(assessment.Evidence), marshal(assessment.Actor), assessment.CreatedAt)
		if err != nil {
			return err
		}
		if input.SubjectType == "outcome" && input.RunID != "" {
			status := "unassessed"
			switch strings.ToLower(input.Result) {
			case "achieved", "pass", "passed", "conformant":
				status = "assessed_achieved"
			case "not_achieved", "fail", "failed", "nonconformant":
				status = "not_achieved"
			case "unknown", "inconclusive":
				status = "unassessed"
			}
			result, err := tx.ExecContext(ctx, `UPDATE run_outcomes SET status=?,evidence_json=?,assessment_id=?,updated_at=? WHERE run_id=? AND (id=? OR name=?)`, status, marshal(input.Evidence), assessment.ID, assessment.CreatedAt, input.RunID, input.SubjectID, input.SubjectID)
			if err != nil {
				return err
			}
			if affected, _ := result.RowsAffected(); affected == 0 {
				return fmt.Errorf("%w: Outcome not found", ErrNotFound)
			}
		}
		event, err = appendEventTx(ctx, tx, actor, "run", streamID, "assessment.recorded", input.RunID, "", "v1", assessment)
		return err
	})
	if err != nil {
		return domain.Assessment{}, err
	}
	r.publish(event)
	return assessment, nil
}

func (r *Runtime) Assessments(ctx context.Context, runID string) ([]domain.Assessment, error) {
	query := `SELECT id,COALESCE(run_id,''),subject_type,subject_id,assessment_type,COALESCE(criteria_revision,''),result,COALESCE(rationale,''),evidence_json,actor_json,created_at FROM assessments`
	var args []any
	if runID != "" {
		query += ` WHERE run_id=?`
		args = append(args, runID)
	}
	query += ` ORDER BY created_at DESC`
	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var assessments []domain.Assessment
	for rows.Next() {
		var current domain.Assessment
		var evidenceJSON, actorJSON string
		if err := rows.Scan(&current.ID, &current.RunID, &current.SubjectType, &current.SubjectID, &current.AssessmentType, &current.CriteriaRevision, &current.Result, &current.Rationale, &evidenceJSON, &actorJSON, &current.CreatedAt); err != nil {
			return nil, err
		}
		_ = json.Unmarshal([]byte(evidenceJSON), &current.Evidence)
		_ = json.Unmarshal([]byte(actorJSON), &current.Actor)
		assessments = append(assessments, current)
	}
	return assessments, rows.Err()
}

func (r *Runtime) CreateHandoff(ctx context.Context, input HandoffInput) (domain.Handoff, error) {
	if input.ProviderRunID == "" || input.ProviderArtifactID == "" || input.RecipientInput == "" {
		return domain.Handoff{}, fmt.Errorf("%w: provider Run, Artifact, and recipient input are required", ErrInvalid)
	}
	if input.Status == "" {
		input.Status = "offered"
	}
	if !validHandoffStatus(input.Status) {
		return domain.Handoff{}, fmt.Errorf("%w: invalid Handoff status", ErrInvalid)
	}
	actor := ActorFromContext(ctx)
	timestamp := now()
	handoff := domain.Handoff{ID: newID("handoff"), ProviderRunID: input.ProviderRunID, ProviderArtifactID: input.ProviderArtifactID, RecipientRunID: input.RecipientRunID, RecipientProcessID: input.RecipientProcessID, RecipientInput: input.RecipientInput, CriteriaRevision: input.CriteriaRevision, Status: input.Status, Evidence: input.Evidence, CreatedAt: timestamp, UpdatedAt: timestamp}
	var event domain.Event
	err := r.write(ctx, "handoff.create", func(tx *sql.Tx) error {
		var count int
		if err := tx.QueryRowContext(ctx, `SELECT COUNT(*) FROM artifacts WHERE id=? AND run_id=?`, input.ProviderArtifactID, input.ProviderRunID).Scan(&count); err != nil {
			return err
		}
		if count == 0 {
			return fmt.Errorf("%w: provider Artifact does not belong to provider Run", ErrInvalid)
		}
		if input.RecipientRunID != "" {
			if _, _, err := currentRunVersionTx(ctx, tx, input.RecipientRunID); err != nil {
				return err
			}
		}
		_, err := tx.ExecContext(ctx, `INSERT INTO handoffs(id,provider_run_id,provider_artifact_id,recipient_run_id,recipient_process_id,recipient_input,criteria_revision,status,evidence_json,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)`, handoff.ID, handoff.ProviderRunID, handoff.ProviderArtifactID, nullIfEmpty(handoff.RecipientRunID), nullIfEmpty(handoff.RecipientProcessID), handoff.RecipientInput, nullIfEmpty(handoff.CriteriaRevision), handoff.Status, marshal(handoff.Evidence), handoff.CreatedAt, handoff.UpdatedAt)
		if err != nil {
			return err
		}
		event, err = appendEventTx(ctx, tx, actor, "run", handoff.ProviderRunID, "handoff.created", handoff.ProviderRunID, "", "v1", handoff)
		return err
	})
	if err != nil {
		return domain.Handoff{}, err
	}
	r.publish(event)
	return handoff, nil
}

func (r *Runtime) UpdateHandoff(ctx context.Context, id, status string, evidence []domain.EvidenceRef) (domain.Handoff, error) {
	if !validHandoffStatus(status) {
		return domain.Handoff{}, fmt.Errorf("%w: invalid Handoff status", ErrInvalid)
	}
	actor := ActorFromContext(ctx)
	var handoff domain.Handoff
	var event domain.Event
	err := r.write(ctx, "handoff.update", func(tx *sql.Tx) error {
		var evidenceJSON string
		if err := tx.QueryRowContext(ctx, `SELECT id,provider_run_id,provider_artifact_id,COALESCE(recipient_run_id,''),COALESCE(recipient_process_id,''),recipient_input,COALESCE(criteria_revision,''),status,evidence_json,created_at,updated_at FROM handoffs WHERE id=?`, id).Scan(&handoff.ID, &handoff.ProviderRunID, &handoff.ProviderArtifactID, &handoff.RecipientRunID, &handoff.RecipientProcessID, &handoff.RecipientInput, &handoff.CriteriaRevision, &handoff.Status, &evidenceJSON, &handoff.CreatedAt, &handoff.UpdatedAt); err != nil {
			if errors.Is(err, sql.ErrNoRows) {
				return ErrNotFound
			}
			return err
		}
		_ = json.Unmarshal([]byte(evidenceJSON), &handoff.Evidence)
		if evidence != nil {
			handoff.Evidence = evidence
		}
		handoff.Status = status
		handoff.UpdatedAt = now()
		if _, err := tx.ExecContext(ctx, `UPDATE handoffs SET status=?,evidence_json=?,updated_at=? WHERE id=?`, handoff.Status, marshal(handoff.Evidence), handoff.UpdatedAt, id); err != nil {
			return err
		}
		var appendErr error
		event, appendErr = appendEventTx(ctx, tx, actor, "run", handoff.ProviderRunID, "handoff.updated", handoff.ProviderRunID, id, "v1", handoff)
		return appendErr
	})
	if err != nil {
		return domain.Handoff{}, err
	}
	r.publish(event)
	return handoff, nil
}

func (r *Runtime) HandoffsForRun(ctx context.Context, runID string) ([]domain.Handoff, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT id,provider_run_id,provider_artifact_id,COALESCE(recipient_run_id,''),COALESCE(recipient_process_id,''),recipient_input,COALESCE(criteria_revision,''),status,evidence_json,created_at,updated_at FROM handoffs WHERE provider_run_id=? OR recipient_run_id=? ORDER BY updated_at DESC`, runID, runID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var handoffs []domain.Handoff
	for rows.Next() {
		var current domain.Handoff
		var evidenceJSON string
		if err := rows.Scan(&current.ID, &current.ProviderRunID, &current.ProviderArtifactID, &current.RecipientRunID, &current.RecipientProcessID, &current.RecipientInput, &current.CriteriaRevision, &current.Status, &evidenceJSON, &current.CreatedAt, &current.UpdatedAt); err != nil {
			return nil, err
		}
		_ = json.Unmarshal([]byte(evidenceJSON), &current.Evidence)
		handoffs = append(handoffs, current)
	}
	return handoffs, rows.Err()
}

func validHandoffStatus(status string) bool {
	switch status {
	case "offered", "accepted", "rejected", "waiting", "cancelled":
		return true
	default:
		return false
	}
}
