package hooks

import (
	"encoding/json"
	"strings"
)

type Binding struct {
	ID         string         `json:"id" yaml:"id"`
	Event      string         `json:"event" yaml:"event"`
	Mode       string         `json:"mode" yaml:"mode"`
	Target     string         `json:"target,omitempty" yaml:"target,omitempty"`
	Policy     string         `json:"policy,omitempty" yaml:"policy,omitempty"`
	Parameters map[string]any `json:"parameters,omitempty" yaml:"parameters,omitempty"`
}

type Envelope struct {
	SchemaVersion string          `json:"schemaVersion"`
	ObservationID string          `json:"observationId"`
	Host          string          `json:"host"`
	HostVersion   string          `json:"hostVersion,omitempty"`
	Event         string          `json:"event"`
	OccurredAt    string          `json:"occurredAt"`
	ActorType     string          `json:"actorType,omitempty"`
	RunID         string          `json:"runId,omitempty"`
	ToolName      string          `json:"toolName,omitempty"`
	Outcome       string          `json:"outcome,omitempty"`
	Metadata      json.RawMessage `json:"metadata,omitempty"`
}

func ValidateBinding(binding Binding) string {
	switch binding.Mode {
	case "observe", "enrich", "validate", "gate", "transform", "notify":
	default:
		return "unsupported hook mode"
	}
	if strings.TrimSpace(binding.ID) == "" || strings.TrimSpace(binding.Event) == "" {
		return "hook id and event are required"
	}
	return ""
}

func RedactMetadata(raw json.RawMessage) json.RawMessage {
	if len(raw) == 0 {
		return nil
	}
	var value any
	if err := json.Unmarshal(raw, &value); err != nil {
		return json.RawMessage(`{"status":"unparseable"}`)
	}
	redacted := redact(value)
	encoded, _ := json.Marshal(redacted)
	return encoded
}

func redact(value any) any {
	switch current := value.(type) {
	case map[string]any:
		result := map[string]any{}
		for key, item := range current {
			lower := strings.ToLower(key)
			if sensitive(lower) {
				result[key] = "[redacted]"
				continue
			}
			result[key] = redact(item)
		}
		return result
	case []any:
		result := make([]any, len(current))
		for index, item := range current {
			result[index] = redact(item)
		}
		return result
	case string:
		if len(current) > 512 {
			return current[:512] + "…"
		}
		return current
	default:
		return current
	}
}

func sensitive(key string) bool {
	for _, fragment := range []string{"prompt", "response", "content", "source", "code", "argument", "secret", "token", "credential", "authorization", "password"} {
		if strings.Contains(key, fragment) {
			return true
		}
	}
	return false
}
