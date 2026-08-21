package runtime

import (
	"context"
	"os"
	"path/filepath"
	"testing"

	"github.com/mashimashica/alps/internal/domain"
)

func operatorContext() context.Context {
	return WithActor(context.Background(), domain.Actor{
		Type:      domain.ActorHuman,
		ID:        "tester",
		Authority: "operator",
		Channel:   domain.ChannelInternal,
	})
}

func TestRunDecisionFlow(t *testing.T) {
	ctx := operatorContext()
	runtime, err := Open(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	defer runtime.Close()

	run, err := runtime.CreateRun(ctx, "Test Run", "Apply Skills", "")
	if err != nil {
		t.Fatal(err)
	}
	gate, err := runtime.OpenGate(ctx, run.ID, "Publish result", "Write an Artifact outside the Runtime", "operator", true, run.Version)
	if err != nil {
		t.Fatal(err)
	}
	waiting, err := runtime.Run(ctx, run.ID)
	if err != nil {
		t.Fatal(err)
	}
	if waiting.State != "waiting_for_decision" {
		t.Fatalf("state = %q", waiting.State)
	}
	if err := runtime.Decide(ctx, gate.ID, "continue", "tester", "", waiting.Version); err != nil {
		t.Fatal(err)
	}
	active, err := runtime.Run(ctx, run.ID)
	if err != nil {
		t.Fatal(err)
	}
	if active.State != "active" {
		t.Fatalf("state = %q", active.State)
	}
}

func TestDiscoveryAndAdoption(t *testing.T) {
	root := t.TempDir()
	skill := filepath.Join(root, "skills", "sample")
	if err := os.MkdirAll(skill, 0o755); err != nil {
		t.Fatal(err)
	}
	content := []byte("---\nname: sample\ndescription: Produce a sample result. ALPS-conformant.\n---\n# Sample\n\n## Purpose\n\nEstablish a sample result.\n\n## Outcomes\n\n- A sample result is available.\n")
	if err := os.WriteFile(filepath.Join(skill, "SKILL.md"), content, 0o644); err != nil {
		t.Fatal(err)
	}

	runtime, err := Open(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	defer runtime.Close()
	runtime.SetRoots([]Root{{Path: root, Scope: "project", Provider: "test"}})

	assets, err := runtime.Scan(context.Background())
	if err != nil {
		t.Fatal(err)
	}
	if len(assets) != 1 {
		t.Fatalf("assets = %d", len(assets))
	}
	revision, err := runtime.Adopt(context.Background(), assets[0].ID)
	if err != nil {
		t.Fatal(err)
	}
	if revision == "" {
		t.Fatal("empty revision")
	}
}

func TestStaleDecisionIsRejected(t *testing.T) {
	ctx := operatorContext()
	runtime, err := Open(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	defer runtime.Close()

	run, err := runtime.CreateRun(ctx, "Test Run", "Apply Skills", "")
	if err != nil {
		t.Fatal(err)
	}
	gate, err := runtime.OpenGate(ctx, run.ID, "Confirm", "Continue", "operator", true, run.Version)
	if err != nil {
		t.Fatal(err)
	}
	if err := runtime.Decide(ctx, gate.ID, "continue", "tester", "", run.Version); err != ErrStale {
		t.Fatalf("error = %v, want ErrStale", err)
	}
}
