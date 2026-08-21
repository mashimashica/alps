package mcp

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	mcpsdk "github.com/modelcontextprotocol/go-sdk/mcp"
)

const serverVersion = "0.0.0-v0-conformance"

type emptyInput struct{}

type assetInput struct {
	AssetID string `json:"assetId" jsonschema:"opaque ALPS asset identifier"`
}

type runInput struct {
	Title                  string         `json:"title" jsonschema:"human-readable Run title"`
	Process                string         `json:"process" jsonschema:"Process or Skill name"`
	AssetID                string         `json:"assetId,omitempty" jsonschema:"optional discovered asset identifier"`
	ProcessRevisionID      string         `json:"processRevisionId,omitempty"`
	SkillPackageRevisionID string         `json:"skillPackageRevisionId,omitempty"`
	PluginRevisionIDs      []string       `json:"pluginRevisionIds,omitempty"`
	ProcessModelRevisionID string         `json:"processModelRevisionId,omitempty"`
	Context                map[string]any `json:"context,omitempty"`
	Outcomes               []string       `json:"outcomes,omitempty"`
}

type runIDInput struct {
	RunID string `json:"runId" jsonschema:"opaque ALPS Run identifier"`
}

type runReportInput struct {
	RunID           string         `json:"runId" jsonschema:"opaque ALPS Run identifier"`
	Actor           string         `json:"actor,omitempty"`
	Message         string         `json:"message" jsonschema:"Agent-observed progress statement; not an assessed Outcome"`
	Progress        *int           `json:"progress,omitempty" jsonschema:"optional percentage from 0 through 100"`
	Claims          map[string]any `json:"claims,omitempty"`
	Evidence        []evidence     `json:"evidence,omitempty"`
	ExpectedVersion int64          `json:"expectedVersion" jsonschema:"optimistic Run version"`
}

type completionInput struct {
	RunID           string `json:"runId"`
	ExpectedVersion int64  `json:"expectedVersion"`
}

type artifactInput struct {
	RunID          string         `json:"runId"`
	Name           string         `json:"name"`
	MediaType      string         `json:"mediaType"`
	Role           string         `json:"role,omitempty"`
	ProcessElement string         `json:"processElement,omitempty"`
	Provenance     map[string]any `json:"provenance,omitempty"`
	Content        string         `json:"content" jsonschema:"UTF-8 text or base64-encoded bytes"`
	Encoding       string         `json:"encoding,omitempty" jsonschema:"empty for UTF-8 text or base64"`
}

type gateInput struct {
	RunID            string     `json:"runId"`
	Title            string     `json:"title"`
	Effect           string     `json:"effect"`
	ExternalEffect   string     `json:"externalEffect,omitempty"`
	Authority        string     `json:"authority"`
	Reversible       bool       `json:"reversible"`
	TargetRevisionID string     `json:"targetRevisionId,omitempty"`
	Criteria         []string   `json:"criteria,omitempty"`
	Controls         []string   `json:"controls,omitempty"`
	Constraints      []string   `json:"constraints,omitempty"`
	Evidence         []evidence `json:"evidence,omitempty"`
	Unknown          []string   `json:"unknown,omitempty"`
	ExpectedVersion  int64      `json:"expectedVersion"`
}

type gateIDInput struct {
	GateID string `json:"gateId"`
}

type assessmentInput struct {
	RunID            string     `json:"runId"`
	SubjectType      string     `json:"subjectType"`
	SubjectID        string     `json:"subjectId"`
	AssessmentType   string     `json:"assessmentType"`
	CriteriaRevision string     `json:"criteriaRevision,omitempty"`
	Result           string     `json:"result"`
	OutcomeStatus    string     `json:"outcomeStatus,omitempty"`
	Evidence         []evidence `json:"evidence,omitempty"`
}

type handoffInput struct {
	ProviderRunID    string     `json:"providerRunId"`
	ProviderArtifact string     `json:"providerArtifact"`
	RecipientRunID   string     `json:"recipientRunId,omitempty"`
	RecipientInput   string     `json:"recipientInput"`
	InterfaceID      string     `json:"interfaceId,omitempty"`
	CriteriaRevision string     `json:"criteriaRevision,omitempty"`
	Status           string     `json:"status,omitempty"`
	Evidence         []evidence `json:"evidence,omitempty"`
}

type invocationInput struct {
	RunID             string         `json:"runId"`
	Requested         map[string]any `json:"requested,omitempty"`
	Effective         map[string]any `json:"effective,omitempty"`
	Resolved          map[string]any `json:"resolved,omitempty"`
	Parameters        map[string]any `json:"parameters,omitempty"`
	Role              string         `json:"role,omitempty"`
	CatalogSnapshotID string         `json:"catalogSnapshotId,omitempty"`
	StartedAt         string         `json:"startedAt,omitempty"`
	FinishedAt        string         `json:"finishedAt,omitempty"`
}

type usageInput struct {
	InvocationID    string         `json:"invocationId,omitempty"`
	RunID           string         `json:"runId"`
	SourceType      string         `json:"sourceType"`
	SourceHost      string         `json:"sourceHost,omitempty"`
	AdapterVersion  string         `json:"adapterVersion,omitempty"`
	Scope           string         `json:"scope,omitempty"`
	Status          string         `json:"status,omitempty"`
	AccountingBasis string         `json:"accountingBasis,omitempty"`
	Tokens          map[string]any `json:"tokens,omitempty"`
	Inclusion       map[string]any `json:"inclusion,omitempty"`
	MappingRevision string         `json:"mappingRevision,omitempty"`
	ObservedAt      string         `json:"observedAt,omitempty"`
}

type evidence struct {
	Kind        string `json:"kind"`
	ID          string `json:"id"`
	Digest      string `json:"digest,omitempty"`
	URI         string `json:"uri,omitempty"`
	Description string `json:"description,omitempty"`
}

type httpClient struct {
	endpoint string
	token    string
	client   *http.Client
}

// Serve exposes the Runtime over the official MCP Go SDK and an IO transport.
// The explicit Reader and Writer make the adapter testable without binding
// domain state to an MCP transport session.
func Serve(ctx context.Context, input io.Reader, output io.Writer, endpoint, token string) error {
	client := &httpClient{endpoint: strings.TrimRight(endpoint, "/"), token: token, client: &http.Client{Timeout: 30 * time.Second}}
	server := mcpsdk.NewServer(&mcpsdk.Implementation{Name: "alps-local-runtime", Version: serverVersion}, nil)

	addTool(server, "alps_catalog_list", "List discovered ALPS Skills, Plugins, and Process Models.", func(ctx context.Context, _ *mcpsdk.CallToolRequest, _ emptyInput) (*mcpsdk.CallToolResult, any, error) {
		return client.get(ctx, "/v1/catalog")
	})
	addTool(server, "alps_asset_get", "Read one discovered ALPS asset and its safe package preview metadata.", func(ctx context.Context, _ *mcpsdk.CallToolRequest, in assetInput) (*mcpsdk.CallToolResult, any, error) {
		return client.get(ctx, "/v1/assets/"+in.AssetID)
	})
	addTool(server, "alps_run_start", "Start an ALPS Run using immutable revision references when available.", func(ctx context.Context, _ *mcpsdk.CallToolRequest, in runInput) (*mcpsdk.CallToolResult, any, error) {
		return client.post(ctx, "/v1/runs", in)
	})
	addTool(server, "alps_run_get", "Read a Run with reports, Outcomes, Artifacts, Decisions, Assessments, Handoffs, usage, and audit events.", func(ctx context.Context, _ *mcpsdk.CallToolRequest, in runIDInput) (*mcpsdk.CallToolResult, any, error) {
		return client.get(ctx, "/v1/runs/"+in.RunID)
	})
	addTool(server, "alps_run_report", "Record Agent-observed progress without asserting assessed Outcome achievement.", func(ctx context.Context, _ *mcpsdk.CallToolRequest, in runReportInput) (*mcpsdk.CallToolResult, any, error) {
		return client.post(ctx, "/v1/runs/"+in.RunID+"/reports", withoutRunID(in))
	})
	addTool(server, "alps_run_request_completion", "Request completion; the Runtime verifies Exit Criteria, required Assessments, Artifacts, Gates, and Handoffs.", func(ctx context.Context, _ *mcpsdk.CallToolRequest, in completionInput) (*mcpsdk.CallToolResult, any, error) {
		return client.post(ctx, "/v1/runs/"+in.RunID+"/completion-requests", map[string]any{"expectedVersion": in.ExpectedVersion})
	})
	addTool(server, "alps_artifact_commit", "Commit an immutable content-addressed Artifact to a Run.", func(ctx context.Context, _ *mcpsdk.CallToolRequest, in artifactInput) (*mcpsdk.CallToolResult, any, error) {
		payload := map[string]any{"name": in.Name, "mediaType": in.MediaType, "role": in.Role, "processElement": in.ProcessElement, "provenance": in.Provenance, "content": in.Content, "encoding": in.Encoding}
		if in.Encoding == "base64" {
			if _, err := base64.StdEncoding.DecodeString(in.Content); err != nil {
				return nil, nil, fmt.Errorf("invalid base64 Artifact content: %w", err)
			}
		}
		return client.post(ctx, "/v1/runs/"+in.RunID+"/artifacts", payload)
	})
	addTool(server, "alps_gate_open", "Open a Human Decision Gate. Agents cannot finalize Human Decisions through MCP.", func(ctx context.Context, _ *mcpsdk.CallToolRequest, in gateInput) (*mcpsdk.CallToolResult, any, error) {
		return client.post(ctx, "/v1/runs/"+in.RunID+"/gates", withoutRunID(in))
	})
	addTool(server, "alps_gate_get", "Read one Human Decision Gate and its decision context.", func(ctx context.Context, _ *mcpsdk.CallToolRequest, in gateIDInput) (*mcpsdk.CallToolResult, any, error) {
		return client.get(ctx, "/v1/gates/"+in.GateID)
	})
	addTool(server, "alps_assessment_record", "Record an evidence-based Assessment separately from Agent self-report.", func(ctx context.Context, _ *mcpsdk.CallToolRequest, in assessmentInput) (*mcpsdk.CallToolResult, any, error) {
		return client.post(ctx, "/v1/assessments", in)
	})
	addTool(server, "alps_handoff_create", "Create a provider Artifact to recipient Input Handoff.", func(ctx context.Context, _ *mcpsdk.CallToolRequest, in handoffInput) (*mcpsdk.CallToolResult, any, error) {
		return client.post(ctx, "/v1/handoffs", in)
	})
	addTool(server, "alps_model_invocation_report", "Record requested, effective, and resolved model configuration for one invocation.", func(ctx context.Context, _ *mcpsdk.CallToolRequest, in invocationInput) (*mcpsdk.CallToolResult, any, error) {
		return client.post(ctx, "/v1/model-invocations", in)
	})
	addTool(server, "alps_usage_report", "Record versioned token usage semantics without converting unavailable values to zero.", func(ctx context.Context, _ *mcpsdk.CallToolRequest, in usageInput) (*mcpsdk.CallToolResult, any, error) {
		return client.post(ctx, "/v1/usage-observations", in)
	})

	transport := &mcpsdk.IOTransport{Reader: io.NopCloser(input), Writer: nopWriteCloser{Writer: output}}
	return server.Run(ctx, transport)
}

func addTool[In any](server *mcpsdk.Server, name, description string, handler mcpsdk.ToolHandlerFor[In, any]) {
	mcpsdk.AddTool(server, &mcpsdk.Tool{Name: name, Description: description}, handler)
}

type nopWriteCloser struct{ io.Writer }

func (nopWriteCloser) Close() error { return nil }

func (client *httpClient) get(ctx context.Context, path string) (*mcpsdk.CallToolResult, any, error) {
	result, err := client.do(ctx, http.MethodGet, path, nil)
	return nil, result, err
}

func (client *httpClient) post(ctx context.Context, path string, input any) (*mcpsdk.CallToolResult, any, error) {
	result, err := client.do(ctx, http.MethodPost, path, input)
	return nil, result, err
}

func (client *httpClient) do(ctx context.Context, method, path string, input any) (any, error) {
	var body io.Reader
	if input != nil {
		encoded, err := json.Marshal(input)
		if err != nil {
			return nil, err
		}
		body = bytes.NewReader(encoded)
	}
	request, err := http.NewRequestWithContext(ctx, method, client.endpoint+path, body)
	if err != nil {
		return nil, err
	}
	request.Header.Set("Authorization", "Bearer "+client.token)
	request.Header.Set("X-ALPS-Actor-Type", "agent")
	request.Header.Set("X-ALPS-Actor-ID", "mcp-agent")
	request.Header.Set("X-ALPS-Channel", "mcp")
	if input != nil {
		request.Header.Set("Content-Type", "application/json")
		request.Header.Set("Idempotency-Key", idempotencyKey(path, input))
	}
	response, err := client.client.Do(request)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()
	raw, err := io.ReadAll(io.LimitReader(response.Body, 16<<20))
	if err != nil {
		return nil, err
	}
	if response.StatusCode >= 300 {
		return nil, fmt.Errorf("ALPS Runtime %s: %s", response.Status, strings.TrimSpace(string(raw)))
	}
	if len(raw) == 0 {
		return map[string]any{"ok": true}, nil
	}
	var value any
	if err := json.Unmarshal(raw, &value); err != nil {
		return string(raw), nil
	}
	return value, nil
}

func idempotencyKey(path string, input any) string {
	encoded, _ := json.Marshal(input)
	return fmt.Sprintf("mcp:%d:%x", time.Now().UnixNano(), simpleHash(path, encoded))
}

func simpleHash(path string, body []byte) uint64 {
	var value uint64 = 1469598103934665603
	for _, current := range append([]byte(path), body...) {
		value ^= uint64(current)
		value *= 1099511628211
	}
	return value
}

func withoutRunID(value any) map[string]any {
	encoded, _ := json.Marshal(value)
	var result map[string]any
	_ = json.Unmarshal(encoded, &result)
	delete(result, "runId")
	return result
}
