from pathlib import Path
import re

path = Path("internal/runtime/models.go")
value = path.read_text()

revision_pattern = re.compile(
    r'\n\trows, err = r\.db\.QueryContext\(ctx, `SELECT handoff_id,from_binding,to_binding FROM handoff_definitions WHERE model_revision_id=\? ORDER BY handoff_id`, revisionID\)\n'
    r'\tif err == nil \{\n'
    r'\t\tfor rows\.Next\(\) \{.*?'
    r'\t\t_ = rows\.Close\(\)\n'
    r'\t\}\n',
    re.DOTALL,
)
value, count = revision_pattern.subn("\n", value, count=1)
if count != 1:
    raise SystemExit(f"expected one revision handoff-edge block, found {count}")

resolved_pattern = re.compile(
    r'\n\tfor _, handoff := range resolved\.Descriptor\.Spec\.Handoffs \{\n'
    r'\t\tfrom := bindings\[handoff\.From\]\n'
    r'\t\tto := bindings\[handoff\.To\]\n'
    r'\t\tgraph\.Edges = append\(graph\.Edges, GraphEdge\{ID: "handoff:" \+ handoff\.ID, From: from\.Process, To: to\.Process, Kind: "handoff", HandoffID: handoff\.ID\}\)\n'
    r'\t\}\n'
)
value, count = resolved_pattern.subn("\n", value, count=1)
if count != 1:
    raise SystemExit(f"expected one resolved handoff-edge block, found {count}")

# Structure mode remains a true Process/Interface bipartite graph. Static
# handoff definitions are resolved into the immutable model revision and
# become visible through the Flow projection when instantiated.
path.write_text(value)
