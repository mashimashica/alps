package hosts

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

type Capability struct {
	Name    string `json:"name"`
	Support string `json:"support"`
	Source  string `json:"source,omitempty"`
	Notes   string `json:"notes,omitempty"`
}

type Profile struct {
	ID             string       `json:"id"`
	Host           string       `json:"host"`
	Version        string       `json:"version,omitempty"`
	AdapterVersion string       `json:"adapterVersion"`
	ObservedAt     string       `json:"observedAt,omitempty"`
	Capabilities   []Capability `json:"capabilities"`
}

type Inventory struct {
	Host           string   `json:"host"`
	Version        string   `json:"version,omitempty"`
	WorkspaceRoots []string `json:"workspaceRoots,omitempty"`
	RepositoryRoot string   `json:"repositoryRoot,omitempty"`
	Realm          string   `json:"realm,omitempty"`
	SkillRoots     []string `json:"skillRoots,omitempty"`
	PluginRoots    []string `json:"pluginRoots,omitempty"`
	ReportedAt     string   `json:"reportedAt,omitempty"`
}

func BuiltinProfiles() []Profile {
	profiles := []Profile{
		profile("claude-code", []Capability{
			capability("mcp.stdio", "supported"), capability("hooks", "supported"), capability("inventory", "adapter"), capability("usage.native", "partial"),
		}),
		profile("codex", []Capability{
			capability("mcp.stdio", "supported"), capability("hooks", "partial"), capability("inventory", "adapter"), capability("usage.native", "partial"),
		}),
		profile("cursor", []Capability{
			capability("mcp.stdio", "supported"), capability("hooks", "partial"), capability("inventory", "adapter"), capability("usage.native", "unknown"),
		}),
		profile("github-copilot-cli", []Capability{
			capability("mcp.stdio", "supported"), capability("hooks", "partial"), capability("inventory", "adapter"), capability("usage.native", "unknown"),
		}),
		profile("vscode", []Capability{
			capability("mcp.stdio", "supported"), capability("hooks", "extension"), capability("inventory", "adapter"), capability("usage.native", "unknown"),
		}),
	}
	return profiles
}

func DefaultInventory(host, version, project string) Inventory {
	home, _ := os.UserHomeDir()
	inventory := Inventory{Host: host, Version: version, RepositoryRoot: project, WorkspaceRoots: []string{project}, Realm: "local"}
	add := func(target *[]string, values ...string) {
		for _, value := range values {
			if value == "" {
				continue
			}
			if info, err := os.Stat(value); err == nil && info.IsDir() {
				*target = append(*target, value)
			}
		}
	}
	add(&inventory.SkillRoots,
		filepath.Join(project, ".agents", "skills"),
		filepath.Join(project, "skills"),
		filepath.Join(home, ".agents", "skills"),
		filepath.Join(home, ".claude", "skills"),
		filepath.Join(home, ".codex", "skills"),
		filepath.Join(home, ".cursor", "skills"),
		filepath.Join(home, ".copilot", "skills"),
		filepath.Join(home, ".vscode", "skills"),
	)
	add(&inventory.PluginRoots,
		project,
		filepath.Join(project, ".claude", "plugins"),
		filepath.Join(project, ".codex", "plugins"),
		filepath.Join(project, ".cursor", "plugins"),
		filepath.Join(home, ".claude", "plugins"),
		filepath.Join(home, ".codex", "plugins"),
		filepath.Join(home, ".cursor", "plugins"),
	)
	inventory.SkillRoots = unique(inventory.SkillRoots)
	inventory.PluginRoots = unique(inventory.PluginRoots)
	return inventory
}

func DecodeInventory(raw []byte) (Inventory, error) {
	var inventory Inventory
	decoder := json.NewDecoder(strings.NewReader(string(raw)))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&inventory); err != nil {
		return Inventory{}, err
	}
	if inventory.Host == "" {
		return Inventory{}, fmt.Errorf("host is required")
	}
	inventory.SkillRoots = unique(inventory.SkillRoots)
	inventory.PluginRoots = unique(inventory.PluginRoots)
	return inventory, nil
}

func profile(host string, capabilities []Capability) Profile {
	return Profile{ID: host + "-builtin", Host: host, AdapterVersion: "v0", Capabilities: capabilities}
}

func capability(name, support string) Capability { return Capability{Name: name, Support: support} }

func unique(values []string) []string {
	seen := map[string]struct{}{}
	var result []string
	for _, value := range values {
		absolute, err := filepath.Abs(value)
		if err != nil {
			absolute = value
		}
		if _, ok := seen[absolute]; ok {
			continue
		}
		seen[absolute] = struct{}{}
		result = append(result, absolute)
	}
	sort.Strings(result)
	return result
}
