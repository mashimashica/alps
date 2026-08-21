from pathlib import Path


server = Path("internal/httpapi/server.go")
lines = server.read_text().splitlines()
rewritten = []
for number, line in enumerate(lines, 1):
    stripped = line.lstrip()
    if stripped.startswith("respond(writer, s.runtime.") and stripped.endswith(")"):
        indent = line[: len(line) - len(stripped)]
        expression = stripped[len("respond(writer, ") : -1]
        value_name = f"value{number}"
        error_name = f"err{number}"
        rewritten.append(f"{indent}{value_name}, {error_name} := {expression}")
        rewritten.append(f"{indent}respond(writer, {value_name}, {error_name})")
    else:
        rewritten.append(line)
server.write_text("\n".join(rewritten) + "\n")


test = Path("internal/runtime/runtime_test.go")
value = test.read_text()
value = value.replace(
    '"testing"\n)',
    '"testing"\n\n\t"github.com/mashimashica/alps/internal/domain"\n)',
)
helper = '''
func operatorContext() context.Context {
	return WithActor(context.Background(), domain.Actor{
		Type:      domain.ActorHuman,
		ID:        "tester",
		Authority: "operator",
		Channel:   domain.ChannelInternal,
	})
}
'''
value = value.replace("\nfunc TestRunDecisionFlow", helper + "\nfunc TestRunDecisionFlow")
value = value.replace("ctx := context.Background()", "ctx := operatorContext()")
value = value.replace(
    'content := []byte("---\\nname: sample\\ndescription: sample skill\\n---\\n# Sample\\n")',
    'content := []byte("---\\nname: sample\\ndescription: Produce a sample result. ALPS-conformant.\\n---\\n# Sample\\n\\n## Purpose\\n\\nEstablish a sample result.\\n\\n## Outcomes\\n\\n- A sample result is available.\\n")',
)
test.write_text(value)
