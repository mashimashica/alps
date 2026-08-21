package domain

import "encoding/json"

const (
	ActorAgent  = "agent"
	ActorHuman  = "human"
	ActorSystem = "system"

	ChannelMCP      = "mcp"
	ChannelWeb      = "web"
	ChannelInternal = "internal"
	ChannelHook     = "hook"
)

type Actor struct {
	Type      string `json:"type"`
	ID        string `json:"id,omitempty"`
	Authority string `json:"authority,omitempty"`
	Channel   string `json:"channel"`
}

type Event struct {
	EventID        string          `json:"eventId"`
	GlobalSequence int64           `json:"globalSequence"`
	StreamType     string          `json:"streamType"`
	StreamID       string          `json:"streamId"`
	StreamSequence int64           `json:"streamSequence"`
	EventType      string          `json:"eventType"`
	OccurredAt     string          `json:"occurredAt"`
	Actor          Actor           `json:"actor"`
	CorrelationID  string          `json:"correlationId,omitempty"`
	CausationID    string          `json:"causationId,omitempty"`
	PayloadVersion string          `json:"payloadVersion"`
	Payload        json.RawMessage `json:"payload"`
}

type EvidenceRef struct {
	Kind        string `json:"kind"`
	ID          string `json:"id"`
	Digest      string `json:"digest,omitempty"`
	URI         string `json:"uri,omitempty"`
	Description string `json:"description,omitempty"`
}

type OutcomeStatus struct {
	ID           string        `json:"id"`
	RunID        string        `json:"runId"`
	Name         string        `json:"name"`
	Status       string        `json:"status"`
	Required     bool          `json:"required"`
	Evidence     []EvidenceRef `json:"evidence,omitempty"`
	AssessmentID string        `json:"assessmentId,omitempty"`
	UpdatedAt    string        `json:"updatedAt"`
}

type RunContext struct {
	ProcessRevisionID      string         `json:"processRevisionId,omitempty"`
	SkillPackageRevisionID string         `json:"skillPackageRevisionId,omitempty"`
	PluginRevisionIDs      []string       `json:"pluginRevisionIds,omitempty"`
	ProcessModelRevisionID string         `json:"processModelRevisionId,omitempty"`
	Controls               []string       `json:"controls,omitempty"`
	Constraints            []string       `json:"constraints,omitempty"`
	Tailoring              map[string]any `json:"tailoring,omitempty"`
	EntryCriteria          []string       `json:"entryCriteria,omitempty"`
	ExitCriteria           []string       `json:"exitCriteria,omitempty"`
	HostContextID          string         `json:"hostContextId,omitempty"`
	ModelCatalogSnapshotID string         `json:"modelCatalogSnapshotId,omitempty"`
	PolicyRevisionID       string         `json:"policyRevisionId,omitempty"`
	HookRevisionIDs        []string       `json:"hookRevisionIds,omitempty"`
}

type Assessment struct {
	ID               string        `json:"id"`
	RunID            string        `json:"runId,omitempty"`
	SubjectType      string        `json:"subjectType"`
	SubjectID        string        `json:"subjectId"`
	AssessmentType   string        `json:"assessmentType"`
	CriteriaRevision string        `json:"criteriaRevision,omitempty"`
	Result           string        `json:"result"`
	Rationale        string        `json:"rationale,omitempty"`
	Evidence         []EvidenceRef `json:"evidence,omitempty"`
	Actor            Actor         `json:"actor"`
	CreatedAt        string        `json:"createdAt"`
}

type Handoff struct {
	ID                 string        `json:"id"`
	ProviderRunID      string        `json:"providerRunId"`
	ProviderArtifactID string        `json:"providerArtifactId"`
	RecipientRunID     string        `json:"recipientRunId,omitempty"`
	RecipientProcessID string        `json:"recipientProcessId,omitempty"`
	RecipientInput     string        `json:"recipientInput"`
	CriteriaRevision   string        `json:"criteriaRevision,omitempty"`
	Status             string        `json:"status"`
	Evidence           []EvidenceRef `json:"evidence,omitempty"`
	CreatedAt          string        `json:"createdAt"`
	UpdatedAt          string        `json:"updatedAt"`
}

type UsageTokens struct {
	InputTotal         *int64 `json:"inputTotal,omitempty"`
	OutputTotal        *int64 `json:"outputTotal,omitempty"`
	CacheReadInput     *int64 `json:"cacheReadInput,omitempty"`
	CacheCreationInput *int64 `json:"cacheCreationInput,omitempty"`
	ReasoningOutput    *int64 `json:"reasoningOutput,omitempty"`
}

type UsageInclusion struct {
	CacheReadInInputTotal     *bool `json:"cacheReadInInputTotal,omitempty"`
	CacheCreationInInputTotal *bool `json:"cacheCreationInInputTotal,omitempty"`
	ReasoningInOutputTotal    *bool `json:"reasoningInOutputTotal,omitempty"`
}

type UsageObservation struct {
	ID              string         `json:"id"`
	InvocationID    string         `json:"invocationId,omitempty"`
	RunID           string         `json:"runId"`
	SourceType      string         `json:"sourceType"`
	SourceHost      string         `json:"sourceHost,omitempty"`
	AdapterVersion  string         `json:"adapterVersion,omitempty"`
	Scope           string         `json:"scope"`
	Status          string         `json:"status"`
	AccountingBasis string         `json:"accountingBasis,omitempty"`
	Tokens          UsageTokens    `json:"tokens"`
	Inclusion       UsageInclusion `json:"inclusion"`
	MappingRevision string         `json:"mappingRevision,omitempty"`
	ObservedAt      string         `json:"observedAt"`
}

type CostObservation struct {
	ID              string `json:"id"`
	InvocationID    string `json:"invocationId,omitempty"`
	RunID           string `json:"runId"`
	Source          string `json:"source"`
	Kind            string `json:"kind"`
	Currency        string `json:"currency,omitempty"`
	CreditType      string `json:"creditType,omitempty"`
	Amount          string `json:"amount"`
	Status          string `json:"status"`
	MappingRevision string `json:"mappingRevision,omitempty"`
	ObservedAt      string `json:"observedAt"`
}
