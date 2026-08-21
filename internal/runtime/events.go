package runtime

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"time"

	"github.com/mashimashica/alps/internal/domain"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/metric"
)

func appendEventTx(ctx context.Context, transaction *sql.Tx, actor domain.Actor, streamType, streamID, eventType, correlationID, causationID, payloadVersion string, payload any) (domain.Event, error) {
	if payloadVersion == "" {
		payloadVersion = "v1"
	}
	encoded, err := json.Marshal(payload)
	if err != nil {
		return domain.Event{}, err
	}
	var streamSequence int64
	if err := transaction.QueryRowContext(ctx, `SELECT COALESCE(MAX(stream_sequence),0)+1 FROM domain_events WHERE stream_type=? AND stream_id=?`, streamType, streamID).Scan(&streamSequence); err != nil {
		return domain.Event{}, err
	}
	event := domain.Event{
		EventID:        newID("event"),
		StreamType:     streamType,
		StreamID:       streamID,
		StreamSequence: streamSequence,
		EventType:      eventType,
		OccurredAt:     now(),
		Actor:          actor,
		CorrelationID:  correlationID,
		CausationID:    causationID,
		PayloadVersion: payloadVersion,
		Payload:        encoded,
	}
	result, err := transaction.ExecContext(ctx, `
INSERT INTO domain_events(event_id,stream_type,stream_id,stream_sequence,event_type,occurred_at,actor_type,actor_id,actor_authority,channel,correlation_id,causation_id,payload_version,payload)
VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
		event.EventID, event.StreamType, event.StreamID, event.StreamSequence, event.EventType, event.OccurredAt,
		event.Actor.Type, nullIfEmpty(event.Actor.ID), nullIfEmpty(event.Actor.Authority), event.Actor.Channel,
		nullIfEmpty(event.CorrelationID), nullIfEmpty(event.CausationID), event.PayloadVersion, string(event.Payload),
	)
	if err != nil {
		return domain.Event{}, err
	}
	sequence, err := result.LastInsertId()
	if err != nil {
		return domain.Event{}, err
	}
	event.GlobalSequence = sequence
	outboxPayload, _ := json.Marshal(map[string]any{
		"eventId":        event.EventID,
		"globalSequence": event.GlobalSequence,
		"streamType":     event.StreamType,
		"streamId":       event.StreamID,
		"eventType":      event.EventType,
		"occurredAt":     event.OccurredAt,
		"actorType":      event.Actor.Type,
		"channel":        event.Actor.Channel,
	})
	_, err = transaction.ExecContext(ctx, `
INSERT INTO telemetry_outbox(id,source_event_sequence,mapping_revision,payload_json,export_status,created_at)
VALUES(?,?,?,?,?,?)`, newID("outbox"), event.GlobalSequence, "alps-domain-event/1", string(outboxPayload), "pending", now())
	return event, err
}

func (r *Runtime) appendEvent(ctx context.Context, streamType, streamID, eventType string, payload any) (domain.Event, error) {
	var event domain.Event
	err := r.write(ctx, eventType, func(transaction *sql.Tx) error {
		var err error
		event, err = appendEventTx(ctx, transaction, ActorFromContext(ctx), streamType, streamID, eventType, "", "", "v1", payload)
		return err
	})
	if err != nil {
		return domain.Event{}, err
	}
	r.publish(event)
	return event, nil
}

func (r *Runtime) latestEvent(ctx context.Context) (domain.Event, error) {
	row := r.db.QueryRowContext(ctx, eventSelect+` ORDER BY sequence DESC LIMIT 1`)
	return scanEvent(row)
}

func (r *Runtime) publish(event domain.Event) {
	r.subMu.RLock()
	defer r.subMu.RUnlock()
	for subscriber := range r.subscribers {
		select {
		case subscriber <- event:
		default:
		}
	}
}

func (r *Runtime) Subscribe() (<-chan domain.Event, func()) {
	channel := make(chan domain.Event, 64)
	r.subMu.Lock()
	r.subscribers[channel] = struct{}{}
	r.subMu.Unlock()
	return channel, func() {
		r.subMu.Lock()
		if _, exists := r.subscribers[channel]; exists {
			delete(r.subscribers, channel)
			close(channel)
		}
		r.subMu.Unlock()
	}
}

func (r *Runtime) EventsAfter(ctx context.Context, sequence int64) ([]domain.Event, error) {
	rows, err := r.db.QueryContext(ctx, eventSelect+` WHERE sequence>? ORDER BY sequence LIMIT 1000`, sequence)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	return scanEvents(rows)
}

func (r *Runtime) EventsForStream(ctx context.Context, streamType, streamID string, limit int) ([]domain.Event, error) {
	if limit <= 0 || limit > 10000 {
		limit = 1000
	}
	rows, err := r.db.QueryContext(ctx, eventSelect+` WHERE stream_type=? AND stream_id=? ORDER BY sequence DESC LIMIT ?`, streamType, streamID, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	return scanEvents(rows)
}

const eventSelect = `SELECT event_id,sequence,stream_type,stream_id,stream_sequence,event_type,occurred_at,actor_type,COALESCE(actor_id,''),COALESCE(actor_authority,''),channel,COALESCE(correlation_id,''),COALESCE(causation_id,''),payload_version,payload FROM domain_events`

type rowScanner interface {
	Scan(...any) error
}

func scanEvent(row rowScanner) (domain.Event, error) {
	var event domain.Event
	var payload string
	err := row.Scan(
		&event.EventID, &event.GlobalSequence, &event.StreamType, &event.StreamID, &event.StreamSequence,
		&event.EventType, &event.OccurredAt, &event.Actor.Type, &event.Actor.ID, &event.Actor.Authority,
		&event.Actor.Channel, &event.CorrelationID, &event.CausationID, &event.PayloadVersion, &payload,
	)
	if err != nil {
		return domain.Event{}, err
	}
	event.Payload = json.RawMessage(payload)
	return event, nil
}

func scanEvents(rows *sql.Rows) ([]domain.Event, error) {
	var events []domain.Event
	for rows.Next() {
		event, err := scanEvent(rows)
		if err != nil {
			return nil, err
		}
		events = append(events, event)
	}
	return events, rows.Err()
}

func (r *Runtime) exportOutbox(ctx context.Context) {
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			r.flushOutbox(ctx)
		}
	}
}

func (r *Runtime) flushOutbox(ctx context.Context) {
	rows, err := r.db.QueryContext(ctx, `SELECT id,source_event_sequence,payload_json,attempt_count FROM telemetry_outbox WHERE export_status='pending' ORDER BY source_event_sequence LIMIT 100`)
	if err != nil {
		return
	}
	type item struct {
		id       string
		sequence int64
		payload  string
		attempts int
	}
	var items []item
	for rows.Next() {
		var current item
		if scanErr := rows.Scan(&current.id, &current.sequence, &current.payload, &current.attempts); scanErr == nil {
			items = append(items, current)
		}
	}
	_ = rows.Close()
	for _, current := range items {
		if r.telemetry != nil {
			r.telemetry.OutboxExports.Add(ctx, 1, metric.WithAttributes(
				attribute.Int64("alps.event.sequence", current.sequence),
				attribute.String("alps.mapping.revision", "alps-domain-event/1"),
			))
		}
		r.writeMu.Lock()
		_, updateErr := r.db.ExecContext(ctx, `UPDATE telemetry_outbox SET export_status='exported',attempt_count=attempt_count+1,exported_at=?,last_error=NULL WHERE id=? AND export_status='pending'`, now(), current.id)
		r.writeMu.Unlock()
		if updateErr != nil && !errors.Is(updateErr, context.Canceled) {
			r.writeMu.Lock()
			_, _ = r.db.ExecContext(context.Background(), `UPDATE telemetry_outbox SET attempt_count=attempt_count+1,last_error=? WHERE id=?`, updateErr.Error(), current.id)
			r.writeMu.Unlock()
		}
	}
}
