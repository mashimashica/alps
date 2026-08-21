from pathlib import Path


def replace(path: str, old: str, new: str) -> None:
    file = Path(path)
    value = file.read_text()
    if old not in value:
        raise SystemExit(f"missing correction pattern in {path}: {old[:100]}")
    file.write_text(value.replace(old, new))


mcp_replacements = {
    'return nil, client.get(ctx, "/v1/catalog")': 'return client.get(ctx, "/v1/catalog")',
    'return nil, client.get(ctx, "/v1/assets/"+in.AssetID)': 'return client.get(ctx, "/v1/assets/"+in.AssetID)',
    'return nil, client.post(ctx, "/v1/runs", in)': 'return client.post(ctx, "/v1/runs", in)',
    'return nil, client.get(ctx, "/v1/runs/"+in.RunID)': 'return client.get(ctx, "/v1/runs/"+in.RunID)',
    'return nil, client.post(ctx, "/v1/runs/"+in.RunID+"/reports", withoutRunID(in))': 'return client.post(ctx, "/v1/runs/"+in.RunID+"/reports", withoutRunID(in))',
    'return nil, client.post(ctx, "/v1/runs/"+in.RunID+"/completion-requests", map[string]any{"expectedVersion": in.ExpectedVersion})': 'return client.post(ctx, "/v1/runs/"+in.RunID+"/completion-requests", map[string]any{"expectedVersion": in.ExpectedVersion})',
    'return nil, client.post(ctx, "/v1/runs/"+in.RunID+"/artifacts", payload)': 'return client.post(ctx, "/v1/runs/"+in.RunID+"/artifacts", payload)',
    'return nil, client.post(ctx, "/v1/runs/"+in.RunID+"/gates", withoutRunID(in))': 'return client.post(ctx, "/v1/runs/"+in.RunID+"/gates", withoutRunID(in))',
    'return nil, client.get(ctx, "/v1/gates/"+in.GateID)': 'return client.get(ctx, "/v1/gates/"+in.GateID)',
    'return nil, client.post(ctx, "/v1/assessments", in)': 'return client.post(ctx, "/v1/assessments", in)',
    'return nil, client.post(ctx, "/v1/handoffs", in)': 'return client.post(ctx, "/v1/handoffs", in)',
    'return nil, client.post(ctx, "/v1/model-invocations", in)': 'return client.post(ctx, "/v1/model-invocations", in)',
    'return nil, client.post(ctx, "/v1/usage-observations", in)': 'return client.post(ctx, "/v1/usage-observations", in)',
}
for old, new in mcp_replacements.items():
    replace("internal/mcp/mcp.go", old, new)
replace(
    "internal/mcp/mcp.go",
    "func (client *httpClient) get(ctx context.Context, path string) (any, error) {\n\treturn client.do(ctx, http.MethodGet, path, nil)\n}\n\nfunc (client *httpClient) post(ctx context.Context, path string, input any) (any, error) {\n\treturn client.do(ctx, http.MethodPost, path, input)\n}",
    "func (client *httpClient) get(ctx context.Context, path string) (*mcpsdk.CallToolResult, any, error) {\n\tresult, err := client.do(ctx, http.MethodGet, path, nil)\n\treturn nil, result, err\n}\n\nfunc (client *httpClient) post(ctx context.Context, path string, input any) (*mcpsdk.CallToolResult, any, error) {\n\tresult, err := client.do(ctx, http.MethodPost, path, input)\n\treturn nil, result, err\n}",
)

replace(
    "internal/runtime/assessment.go",
    '\t\tevent, err = appendEventTx(ctx, tx, actor, "run", handoff.ProviderRunID, "handoff.updated", handoff.ProviderRunID, id, "v1", handoff)\n\t\treturn err',
    '\t\tvar appendErr error\n\t\tevent, appendErr = appendEventTx(ctx, tx, actor, "run", handoff.ProviderRunID, "handoff.updated", handoff.ProviderRunID, id, "v1", handoff)\n\t\treturn appendErr',
)
replace(
    "internal/runtime/hosts.go",
    '\t\tevent, err = appendEventTx(ctx, tx, actor, "host", inventory.Host, "host.inventory_registered", contextValue.ID, "", "v1", map[string]any{"context": contextValue, "skillRoots": inventory.SkillRoots, "pluginRoots": inventory.PluginRoots})\n\t\treturn err',
    '\t\tvar appendErr error\n\t\tevent, appendErr = appendEventTx(ctx, tx, actor, "host", inventory.Host, "host.inventory_registered", contextValue.ID, "", "v1", map[string]any{"context": contextValue, "skillRoots": inventory.SkillRoots, "pluginRoots": inventory.PluginRoots})\n\t\treturn appendErr',
)
replace(
    "internal/runtime/hosts.go",
    '\t\tevent, err := appendEventTx(ctx, tx, actor, "hook", id, "hook_binding.recorded", id, "", "v1", map[string]any{"id": id, "binding": binding, "digest": digest})\n\t\treturn err',
    '\t\tvar appendErr error\n\t\tevent, appendErr = appendEventTx(ctx, tx, actor, "hook", id, "hook_binding.recorded", id, "", "v1", map[string]any{"id": id, "binding": binding, "digest": digest})\n\t\treturn appendErr',
)
replace(
    "internal/runtime/hosts.go",
    '\t\tevent, err = appendEventTx(ctx, tx, actor, "host-observation", streamID, "host.observed", envelope.RunID, observation.ID, "v1", observation)\n\t\treturn err',
    '\t\tvar appendErr error\n\t\tevent, appendErr = appendEventTx(ctx, tx, actor, "host-observation", streamID, "host.observed", envelope.RunID, observation.ID, "v1", observation)\n\t\treturn appendErr',
)
replace(
    "internal/runtime/inference.go",
    '\t\tevent, err := appendEventTx(ctx, tx, actor, "model-catalog", snapshot.ID, "model_catalog.recorded", snapshot.ID, "", "v1", snapshot)\n\t\treturn err',
    '\t\tvar appendErr error\n\t\tevent, appendErr = appendEventTx(ctx, tx, actor, "model-catalog", snapshot.ID, "model_catalog.recorded", snapshot.ID, "", "v1", snapshot)\n\t\treturn appendErr',
)

replace(
    "internal/runtime/events.go",
    '"go.opentelemetry.io/otel/attribute"',
    '"go.opentelemetry.io/otel/attribute"\n\t"go.opentelemetry.io/otel/metric"',
)
replace(
    "internal/runtime/events.go",
    '\t\t\tr.telemetry.OutboxExports.Add(ctx, 1,\n\t\t\t\tattribute.Int64("alps.event.sequence", current.sequence),\n\t\t\t\tattribute.String("alps.mapping.revision", "alps-domain-event/1"),\n\t\t\t)',
    '\t\t\tr.telemetry.OutboxExports.Add(ctx, 1, metric.WithAttributes(\n\t\t\t\tattribute.Int64("alps.event.sequence", current.sequence),\n\t\t\t\tattribute.String("alps.mapping.revision", "alps-domain-event/1"),\n\t\t\t))',
)

replace(
    "internal/runtime/runs.go",
    '\tif input.AssetID != "" {\n\t\tvar asset Asset\n\t\tasset, err := r.Asset(ctx, input.AssetID)\n\t\tif err != nil {\n\t\t\treturn Run{}, err\n\t\t}\n',
    '\tif input.AssetID != "" {\n\t\tdetail, err := r.Asset(ctx, input.AssetID)\n\t\tif err != nil {\n\t\t\treturn Run{}, err\n\t\t}\n\t\tasset := detail.Asset\n',
)
replace(
    "internal/runtime/runs.go",
    '\t\tevent, err = appendEventTx(ctx, tx, actor, "run", runID, "artifact.committed", runID, "", "v1", artifact)\n\t\tif err == nil {\n\t\t\t_, err = tx.ExecContext(ctx, `UPDATE artifact_relations SET created_event_id=? WHERE id=?`, event.EventID, relationID)\n\t\t}\n\t\treturn err',
    '\t\tvar appendErr error\n\t\tevent, appendErr = appendEventTx(ctx, tx, actor, "run", runID, "artifact.committed", runID, "", "v1", artifact)\n\t\tif appendErr != nil {\n\t\t\treturn appendErr\n\t\t}\n\t\t_, appendErr = tx.ExecContext(ctx, `UPDATE artifact_relations SET created_event_id=? WHERE id=?`, event.EventID, relationID)\n\t\treturn appendErr',
)
replace(
    "internal/runtime/runtime.go",
    '"go.opentelemetry.io/otel/attribute"',
    '"go.opentelemetry.io/otel/attribute"\n\t"go.opentelemetry.io/otel/metric"',
)
replace(
    "internal/runtime/runtime.go",
    '\t\tr.telemetry.Commands.Add(ctx, 1, attribute.String("alps.command", command))\n\t\tr.telemetry.CommandDuration.Record(ctx, float64(time.Since(started).Microseconds())/1000, attribute.String("alps.command", command))',
    '\t\tattributes := metric.WithAttributes(attribute.String("alps.command", command))\n\t\tr.telemetry.Commands.Add(ctx, 1, attributes)\n\t\tr.telemetry.CommandDuration.Record(ctx, float64(time.Since(started).Microseconds())/1000, attributes)',
)
