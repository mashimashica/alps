package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/gofrs/flock"
)

var runtimeOwnerLock *flock.Flock

func init() {
	if len(os.Args) < 2 || os.Args[1] != "serve" {
		return
	}

	workspace := workspaceArgument(os.Args[2:])
	if err := os.MkdirAll(filepath.Join(workspace, "runtime"), 0o700); err != nil {
		fmt.Fprintln(os.Stderr, "alps: create runtime directory:", err)
		os.Exit(1)
	}

	lockPath := filepath.Join(workspace, "runtime", "owner.lock")
	ownerLock := flock.New(lockPath, flock.SetPermissions(0o600))
	locked, err := ownerLock.TryLock()
	if err != nil {
		fmt.Fprintln(os.Stderr, "alps: acquire runtime owner lock:", err)
		os.Exit(1)
	}
	if !locked {
		fmt.Fprintf(os.Stderr, "alps: workspace %q is already owned by another Runtime\n", workspace)
		os.Exit(1)
	}
	runtimeOwnerLock = ownerLock

	metadata, _ := json.MarshalIndent(map[string]any{
		"pid":        os.Getpid(),
		"startedAt":  time.Now().UTC().Format(time.RFC3339Nano),
		"workspace":  workspace,
		"executable": executablePath(),
	}, "", "  ")
	_ = os.WriteFile(filepath.Join(workspace, "runtime", "owner.json"), metadata, 0o600)
}

func workspaceArgument(arguments []string) string {
	workspace := defaultWorkspace()
	for index := 0; index < len(arguments); index++ {
		switch {
		case arguments[index] == "--workspace" && index+1 < len(arguments):
			return arguments[index+1]
		case strings.HasPrefix(arguments[index], "--workspace="):
			return strings.TrimPrefix(arguments[index], "--workspace=")
		}
	}
	return workspace
}

func executablePath() string {
	path, err := os.Executable()
	if err != nil {
		return ""
	}
	absolute, err := filepath.Abs(path)
	if err != nil {
		return path
	}
	return absolute
}
