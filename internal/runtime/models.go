package runtime

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"sort"
	"strings"

	alpsmodel "github.com/mashimashica/alps/internal/model"
)

type GraphNode struct {
	ID         string         `json:"id"`
	Name       string         `json:"name"`
	Kind       string         `json:"kind"`
	RevisionID string         `json:"revisionId,omitempty"`
	Metadata   map[string]any `json:"metadata,omitempty"`
}

type GraphEdge struct {
	ID        string `json:"id"`
	From      string `json:"from"`
	To        string `json:"to"`
	Kind      string `json:"kind"`
	BindingID string `json:"bindingId,omitempty"`
	HandoffID string `json:"handoffId,omitempty"`
	Optional  bool   `json:"optional,omitempty"`
}

type GraphLive struct {
	RunID     string `json:"runId"`
	ProcessID string `json:"processId"`
	State     string `json:"state"`
	Attention bool   `json:"attention"`
}

type GraphFlow struct {
	ID          string `json:"id"`
	HandoffID   string `json:"handoffId,omitempty"`
	ArtifactID  string `json:"artifactId,omitempty"`
	InterfaceID string `json:"interfaceId,omitempty"`
	From        string `json:"from,omitempty"`
	To          string `json:"to,omitempty"`
	Status      string `json:"status"`
}

type Graph struct {
	ModelID        string           `json:"modelId,omitempty"`
	ModelName      string           `json:"modelName,omitempty"`
	ModelRevision  string           `json:"modelRevisionId,omitempty"`
	DescriptorHash string           `json:"descriptorDigest,omitempty"`
	Mode           string           `json:"mode"`
	Processes      []GraphNode      `json:"processes"`
	Interfaces     []GraphNode      `json:"interfaces"`
	Edges          []GraphEdge      `json:"edges"`
	Live           []GraphLive      `json:"live,omitempty"`
	Flow           []GraphFlow      `json:"flow,omitempty"`
	Relationships  []map[string]any `json:"relationships,omitempty"`
	EntryPoints    []string         `json:"entryPoints,omitempty"`
}

type ProcessModelSummary struct {
	RevisionID string `json:"revisionId"`
	AssetID    string `json:"assetId"`
	ModelID    string `json:"modelId"`
	Name       string `json:"name"`
	Version    string `json:"version,omitempty"`
	Digest     string `json:"digest"`
	CreatedAt  string `json:"createdAt"`
}

func (r *Runtime) Graph(ctx context.Context) (Graph, error) {
	return r.ProcessModelGraph(ctx, "", "structure")
}

func (r *Runtime) ProcessModels(ctx context.Context) ([]ProcessModelSummary, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT id,asset_id,model_id,name,COALESCE(version,''),digest,created_at FROM process_model_revisions ORDER BY created_at DESC`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var models []ProcessModelSummary
	for rows.Next() {
		var model ProcessModelSummary
		if err := rows.Scan(&model.RevisionID, &model.AssetID, &model.ModelID, &model.Name, &model.Version, &model.Digest, &model.CreatedAt); err != nil {
			return nil, err
		}
		models = append(models, model)
	}
	return models, rows.Err()
}

func (r *Runtime) ProcessModelGraph(ctx context.Context, revisionID, mode string) (Graph, error) {
	if mode == "" {
		mode = "structure"
	}
	if mode != "structure" && mode != "live" && mode != "flow" {
		return Graph{}, fmt.Errorf("%w: graph mode must be structure, live, or flow", ErrInvalid)
	}
	if revisionID == "" {
		_ = r.db.QueryRowContext(ctx, `SELECT id FROM process_model_revisions ORDER BY created_at DESC LIMIT 1`).Scan(&revisionID)
	}
	var graph Graph
	var err error
	if revisionID != "" {
		graph, err = r.graphFromRevision(ctx, revisionID)
		if err != nil && !errors.Is(err, ErrNotFound) {
			return Graph{}, err
		}
	}
	if graph.ModelID == "" {
		graph, err = r.graphFromObservedDescriptor(ctx)
		if err != nil {
			return Graph{}, err
		}
	}
	graph.Mode = mode
	if mode == "live" || mode == "flow" {
		graph.Live, _ = r.graphLive(ctx, graph)
	}
	if mode == "flow" {
		graph.Flow, _ = r.graphFlow(ctx, graph)
	}
	return graph, nil
}

func (r *Runtime) graphFromRevision(ctx context.Context, revisionID string) (Graph, error) {
	var graph Graph
	var descriptorJSON string
	err := r.db.QueryRowContext(ctx, `SELECT model_id,name,digest,descriptor_json FROM process_model_revisions WHERE id=?`, revisionID).Scan(&graph.ModelID, &graph.ModelName, &graph.DescriptorHash, &descriptorJSON)
	if errors.Is(err, sql.ErrNoRows) {
		return Graph{}, ErrNotFound
	}
	if err != nil {
		return Graph{}, err
	}
	graph.ModelRevision = revisionID

	rows, err := r.db.QueryContext(ctx, `SELECT process_id,COALESCE(process_revision_id,''),name,ref,digest FROM model_processes WHERE model_revision_id=? ORDER BY process_id`, revisionID)
	if err != nil {
		return Graph{}, err
	}
	for rows.Next() {
		var id, processRevision, name, ref, digest string
		if err := rows.Scan(&id, &processRevision, &name, &ref, &digest); err != nil {
			rows.Close()
			return Graph{}, err
		}
		graph.Processes = append(graph.Processes, GraphNode{ID: id, Name: name, Kind: "process", RevisionID: processRevision, Metadata: map[string]any{"ref": ref, "digest": digest}})
	}
	_ = rows.Close()

	rows, err = r.db.QueryContext(ctx, `SELECT interface_id,name,kind,media_types_json,COALESCE(schema_ref,''),COALESCE(schema_digest,''),required FROM interface_types WHERE model_revision_id=? ORDER BY interface_id`, revisionID)
	if err != nil {
		return Graph{}, err
	}
	for rows.Next() {
		var id, name, kind, mediaJSON, schemaRef, schemaDigest string
		var required bool
		if err := rows.Scan(&id, &name, &kind, &mediaJSON, &schemaRef, &schemaDigest, &required); err != nil {
			rows.Close()
			return Graph{}, err
		}
		var mediaTypes []string
		_ = json.Unmarshal([]byte(mediaJSON), &mediaTypes)
		graph.Interfaces = append(graph.Interfaces, GraphNode{ID: id, Name: name, Kind: kind, Metadata: map[string]any{"mediaTypes": mediaTypes, "schemaRef": schemaRef, "schemaDigest": schemaDigest, "required": required}})
	}
	_ = rows.Close()

	bindings := map[string]struct {
		Process   string
		Role      string
		Interface string
		Optional  bool
	}{}
	rows, err = r.db.QueryContext(ctx, `SELECT binding_id,process_id,role,interface_id,optional FROM process_bindings WHERE model_revision_id=? ORDER BY binding_id`, revisionID)
	if err != nil {
		return Graph{}, err
	}
	for rows.Next() {
		var id string
		var value struct {
			Process   string
			Role      string
			Interface string
			Optional  bool
		}
		if err := rows.Scan(&id, &value.Process, &value.Role, &value.Interface, &value.Optional); err != nil {
			rows.Close()
			return Graph{}, err
		}
		bindings[id] = value
		from, to, kind := value.Process, value.Interface, "produces"
		if value.Role == "input" {
			from, to, kind = value.Interface, value.Process, "consumes"
		}
		graph.Edges = append(graph.Edges, GraphEdge{ID: "binding:" + id, From: from, To: to, Kind: kind, BindingID: id, Optional: value.Optional})
	}
	_ = rows.Close()

	rows, err = r.db.QueryContext(ctx, `SELECT handoff_id,from_binding,to_binding FROM handoff_definitions WHERE model_revision_id=? ORDER BY handoff_id`, revisionID)
	if err == nil {
		for rows.Next() {
			var handoffID, fromBinding, toBinding string
			if rows.Scan(&handoffID, &fromBinding, &toBinding) == nil {
				from := bindings[fromBinding]
				to := bindings[toBinding]
				graph.Edges = append(graph.Edges, GraphEdge{ID: "handoff:" + handoffID, From: from.Process, To: to.Process, Kind: "handoff", HandoffID: handoffID})
			}
		}
		_ = rows.Close()
	}
	rows, err = r.db.QueryContext(ctx, `SELECT relationship_type,processes_json FROM model_relationships WHERE model_revision_id=? ORDER BY ordinal`, revisionID)
	if err == nil {
		for rows.Next() {
			var relationshipType, processesJSON string
			if rows.Scan(&relationshipType, &processesJSON) == nil {
				var processes []string
				_ = json.Unmarshal([]byte(processesJSON), &processes)
				graph.Relationships = append(graph.Relationships, map[string]any{"type": relationshipType, "processes": processes})
			}
		}
		_ = rows.Close()
	}
	rows, err = r.db.QueryContext(ctx, `SELECT process_id FROM model_entry_points WHERE model_revision_id=? ORDER BY ordinal`, revisionID)
	if err == nil {
		for rows.Next() {
			var processID string
			if rows.Scan(&processID) == nil {
				graph.EntryPoints = append(graph.EntryPoints, processID)
			}
		}
		_ = rows.Close()
	}
	return graph, nil
}

func (r *Runtime) graphFromObservedDescriptor(ctx context.Context) (Graph, error) {
	var path string
	err := r.db.QueryRowContext(ctx, `SELECT source_path FROM assets WHERE kind='process-model' AND validation='valid' AND source_state!='missing' ORDER BY scope='project' DESC,name LIMIT 1`).Scan(&path)
	if errors.Is(err, sql.ErrNoRows) {
		return r.referenceGraph(ctx), nil
	}
	if err != nil {
		return Graph{}, err
	}
	resolved, issues, err := alpsmodel.Resolve(path, func(source string) string { return r.revisionForSource(ctx, source) })
	if err != nil {
		return Graph{}, err
	}
	for _, issue := range issues {
		if issue.Severity == "error" {
			return Graph{}, fmt.Errorf("%w: model %s: %s", ErrInvalid, issue.Path, issue.Message)
		}
	}
	return graphFromResolved(resolved), nil
}

func graphFromResolved(resolved alpsmodel.Resolved) Graph {
	graph := Graph{ModelID: resolved.Descriptor.Metadata.ID, ModelName: resolved.Descriptor.Metadata.Name, DescriptorHash: resolved.Digest, ModelRevision: "external:" + resolved.Descriptor.Metadata.ID}
	for _, process := range resolved.Processes {
		graph.Processes = append(graph.Processes, GraphNode{ID: process.ID, Name: process.Name, Kind: "process", RevisionID: process.Revision, Metadata: map[string]any{"ref": process.Ref, "digest": process.Digest}})
	}
	for _, item := range resolved.Descriptor.Spec.Interfaces {
		graph.Interfaces = append(graph.Interfaces, GraphNode{ID: item.ID, Name: item.Name, Kind: item.Kind, Metadata: map[string]any{"mediaTypes": item.MediaTypes, "schemaRef": item.SchemaRef, "schemaDigest": resolved.SchemaFiles[item.ID], "required": item.Required}})
	}
	bindings := map[string]alpsmodel.Binding{}
	for _, binding := range resolved.Descriptor.Spec.Bindings {
		bindings[binding.ID] = binding
		from, to, kind := binding.Process, binding.Interface, "produces"
		if binding.Role == "input" {
			from, to, kind = binding.Interface, binding.Process, "consumes"
		}
		graph.Edges = append(graph.Edges, GraphEdge{ID: "binding:" + binding.ID, From: from, To: to, Kind: kind, BindingID: binding.ID, Optional: binding.Optional})
	}
	for _, handoff := range resolved.Descriptor.Spec.Handoffs {
		from := bindings[handoff.From]
		to := bindings[handoff.To]
		graph.Edges = append(graph.Edges, GraphEdge{ID: "handoff:" + handoff.ID, From: from.Process, To: to.Process, Kind: "handoff", HandoffID: handoff.ID})
	}
	for _, relationship := range resolved.Descriptor.Spec.Relationships {
		graph.Relationships = append(graph.Relationships, map[string]any{"type": relationship.Type, "processes": relationship.Processes})
	}
	for _, entry := range resolved.Descriptor.Spec.EntryPoints {
		graph.EntryPoints = append(graph.EntryPoints, entry.Process)
	}
	return graph
}

func (r *Runtime) referenceGraph(ctx context.Context) Graph {
	graph := Graph{ModelID: "alps-reference", ModelName: "ALPS Reference Model", ModelRevision: "generated"}
	assets, _ := r.Catalog(ctx)
	for _, asset := range assets {
		if asset.Kind == "skill" {
			graph.Processes = append(graph.Processes, GraphNode{ID: "process_" + asset.ID, Name: asset.Name, Kind: "process", RevisionID: asset.AdoptedRevisionID})
		}
	}
	if len(graph.Processes) == 0 {
		graph.Processes = []GraphNode{{ID: "define", Name: "Define ALPS", Kind: "process"}, {ID: "apply", Name: "Apply ALPS", Kind: "process"}, {ID: "manage", Name: "Manage ALPS", Kind: "process"}}
	}
	graph.Interfaces = []GraphNode{{ID: "verified-skill", Name: "Verified Skill", Kind: "artifact"}, {ID: "managed-skill", Name: "Managed Skill", Kind: "artifact"}, {ID: "execution-record", Name: "Execution Record", Kind: "information"}}
	return graph
}

func (r *Runtime) graphLive(ctx context.Context, graph Graph) ([]GraphLive, error) {
	runs, err := r.Runs(ctx)
	if err != nil {
		return nil, err
	}
	processByRevision := map[string]string{}
	processByName := map[string]string{}
	for _, process := range graph.Processes {
		processByRevision[process.RevisionID] = process.ID
		processByName[strings.ToLower(process.Name)] = process.ID
	}
	var live []GraphLive
	for _, run := range runs {
		if terminalState(run.State) {
			continue
		}
		processID := processByRevision[run.ProcessRevisionID]
		if processID == "" {
			for name, id := range processByName {
				if strings.Contains(strings.ToLower(run.Process), name) || strings.Contains(name, strings.ToLower(run.Process)) {
					processID = id
					break
				}
			}
		}
		if processID == "" && len(graph.Processes) > 0 {
			processID = graph.Processes[0].ID
		}
		live = append(live, GraphLive{RunID: run.ID, ProcessID: processID, State: run.State, Attention: run.State == RunWaitingForDecision})
	}
	return live, nil
}

func (r *Runtime) graphFlow(ctx context.Context, graph Graph) ([]GraphFlow, error) {
	rows, err := r.db.QueryContext(ctx, `SELECT h.id,h.provider_artifact_id,h.status,COALESCE(h.recipient_process_id,''),a.process_element FROM handoffs h JOIN artifacts a ON a.id=h.provider_artifact_id ORDER BY h.updated_at DESC LIMIT 500`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	var flow []GraphFlow
	for rows.Next() {
		var current GraphFlow
		var processElement sql.NullString
		if err := rows.Scan(&current.HandoffID, &current.ArtifactID, &current.Status, &current.To, &processElement); err != nil {
			return nil, err
		}
		current.ID = "flow:" + current.HandoffID
		if processElement.Valid {
			current.InterfaceID = processElement.String
		}
		flow = append(flow, current)
	}
	return flow, rows.Err()
}

func normalizeGraph(graph *Graph) {
	sort.Slice(graph.Processes, func(i, j int) bool { return graph.Processes[i].ID < graph.Processes[j].ID })
	sort.Slice(graph.Interfaces, func(i, j int) bool { return graph.Interfaces[i].ID < graph.Interfaces[j].ID })
	sort.Slice(graph.Edges, func(i, j int) bool { return graph.Edges[i].ID < graph.Edges[j].ID })
}
