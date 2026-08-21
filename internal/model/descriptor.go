package model

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"gopkg.in/yaml.v3"
)

const APIVersion = "alps.dev/process-model/v1alpha1"

type Descriptor struct {
	APIVersion string   `yaml:"apiVersion" json:"apiVersion"`
	Kind       string   `yaml:"kind" json:"kind"`
	Metadata   Metadata `yaml:"metadata" json:"metadata"`
	Spec       Spec     `yaml:"spec" json:"spec"`
}

type Metadata struct {
	ID          string `yaml:"id" json:"id"`
	Name        string `yaml:"name" json:"name"`
	Version     string `yaml:"version,omitempty" json:"version,omitempty"`
	Description string `yaml:"description,omitempty" json:"description,omitempty"`
}

type Spec struct {
	Processes     []ProcessRef   `yaml:"processes" json:"processes"`
	Interfaces    []Interface    `yaml:"interfaces" json:"interfaces"`
	Bindings      []Binding      `yaml:"bindings" json:"bindings"`
	Handoffs      []Handoff      `yaml:"handoffs,omitempty" json:"handoffs,omitempty"`
	Relationships []Relationship `yaml:"relationships,omitempty" json:"relationships,omitempty"`
	EntryPoints   []EntryPoint   `yaml:"entryPoints,omitempty" json:"entryPoints,omitempty"`
	Labels        map[string]any `yaml:"labels,omitempty" json:"labels,omitempty"`
}

type ProcessRef struct {
	ID  string `yaml:"id" json:"id"`
	Ref string `yaml:"ref" json:"ref"`
}

type Interface struct {
	ID         string   `yaml:"id" json:"id"`
	Name       string   `yaml:"name" json:"name"`
	Kind       string   `yaml:"kind" json:"kind"`
	MediaTypes []string `yaml:"mediaTypes,omitempty" json:"mediaTypes,omitempty"`
	SchemaRef  string   `yaml:"schemaRef,omitempty" json:"schemaRef,omitempty"`
	Required   bool     `yaml:"required,omitempty" json:"required,omitempty"`
}

type Binding struct {
	ID        string `yaml:"id" json:"id"`
	Process   string `yaml:"process" json:"process"`
	Role      string `yaml:"role" json:"role"`
	Item      string `yaml:"item" json:"item"`
	Interface string `yaml:"interface" json:"interface"`
	Optional  bool   `yaml:"optional,omitempty" json:"optional,omitempty"`
}

type Handoff struct {
	ID            string `yaml:"id" json:"id"`
	From          string `yaml:"from" json:"from"`
	To            string `yaml:"to" json:"to"`
	AcceptanceRef string `yaml:"acceptanceRef,omitempty" json:"acceptanceRef,omitempty"`
}

type Relationship struct {
	Type      string   `yaml:"type" json:"type"`
	Processes []string `yaml:"processes" json:"processes"`
}

type EntryPoint struct {
	Process string `yaml:"process" json:"process"`
}

type Issue struct {
	Path     string `json:"path"`
	Code     string `json:"code"`
	Message  string `json:"message"`
	Severity string `json:"severity"`
}

type ProcessResolution struct {
	ID       string `json:"id"`
	Ref      string `json:"ref"`
	Path     string `json:"path"`
	Digest   string `json:"digest"`
	Name     string `json:"name"`
	Revision string `json:"revision,omitempty"`
}

type Resolved struct {
	Descriptor  Descriptor          `json:"descriptor"`
	Root        string              `json:"root"`
	Processes   []ProcessResolution `json:"processes"`
	Digest      string              `json:"digest"`
	SchemaFiles map[string]string   `json:"schemaFiles,omitempty"`
	Criteria    map[string]string   `json:"criteria,omitempty"`
}

func Load(path string) (Descriptor, []Issue, error) {
	content, err := os.ReadFile(path)
	if err != nil {
		return Descriptor{}, nil, err
	}
	var descriptor Descriptor
	decoder := yaml.NewDecoder(strings.NewReader(string(content)))
	decoder.KnownFields(true)
	if err := decoder.Decode(&descriptor); err != nil {
		return Descriptor{}, []Issue{{Path: "$", Code: "invalid_yaml", Message: err.Error(), Severity: "error"}}, nil
	}
	return descriptor, Validate(descriptor), nil
}

func Validate(descriptor Descriptor) []Issue {
	var issues []Issue
	add := func(path, code, message string) {
		issues = append(issues, Issue{Path: path, Code: code, Message: message, Severity: "error"})
	}
	if descriptor.APIVersion != APIVersion {
		add("apiVersion", "unsupported_api_version", "apiVersion must be "+APIVersion)
	}
	if descriptor.Kind != "SkillModel" {
		add("kind", "unsupported_kind", "kind must be SkillModel")
	}
	if strings.TrimSpace(descriptor.Metadata.ID) == "" {
		add("metadata.id", "required", "metadata.id is required")
	}
	if strings.TrimSpace(descriptor.Metadata.Name) == "" {
		add("metadata.name", "required", "metadata.name is required")
	}

	processes := map[string]ProcessRef{}
	for index, process := range descriptor.Spec.Processes {
		path := fmt.Sprintf("spec.processes[%d]", index)
		if process.ID == "" || process.Ref == "" {
			add(path, "required", "process id and ref are required")
			continue
		}
		if _, exists := processes[process.ID]; exists {
			add(path+".id", "duplicate", "process id must be unique")
		}
		processes[process.ID] = process
	}
	if len(processes) == 0 {
		add("spec.processes", "required", "at least one process is required")
	}

	interfaces := map[string]Interface{}
	for index, item := range descriptor.Spec.Interfaces {
		path := fmt.Sprintf("spec.interfaces[%d]", index)
		if item.ID == "" || item.Name == "" {
			add(path, "required", "interface id and name are required")
		}
		if item.Kind != "artifact" && item.Kind != "information" {
			add(path+".kind", "invalid_kind", "interface kind must be artifact or information")
		}
		if _, exists := interfaces[item.ID]; exists {
			add(path+".id", "duplicate", "interface id must be unique")
		}
		interfaces[item.ID] = item
	}

	bindings := map[string]Binding{}
	for index, binding := range descriptor.Spec.Bindings {
		path := fmt.Sprintf("spec.bindings[%d]", index)
		if binding.ID == "" || binding.Process == "" || binding.Interface == "" {
			add(path, "required", "binding id, process, and interface are required")
		}
		if binding.Role != "input" && binding.Role != "output" {
			add(path+".role", "invalid_role", "binding role must be input or output")
		}
		if _, exists := processes[binding.Process]; !exists {
			add(path+".process", "unresolved_process", "binding references an unknown process")
		}
		if _, exists := interfaces[binding.Interface]; !exists {
			add(path+".interface", "unresolved_interface", "binding references an unknown interface")
		}
		if _, exists := bindings[binding.ID]; exists {
			add(path+".id", "duplicate", "binding id must be unique")
		}
		bindings[binding.ID] = binding
	}

	for index, handoff := range descriptor.Spec.Handoffs {
		path := fmt.Sprintf("spec.handoffs[%d]", index)
		from, fromOK := bindings[handoff.From]
		to, toOK := bindings[handoff.To]
		if handoff.ID == "" || handoff.From == "" || handoff.To == "" {
			add(path, "required", "handoff id, from, and to are required")
		}
		if !fromOK || !toOK {
			add(path, "unresolved_binding", "handoff references an unknown binding")
			continue
		}
		if from.Role != "output" || to.Role != "input" {
			add(path, "invalid_direction", "handoff must map an output binding to an input binding")
		}
		if from.Interface != to.Interface {
			add(path, "interface_mismatch", "handoff bindings must use the same interface")
		}
	}

	for index, relationship := range descriptor.Spec.Relationships {
		path := fmt.Sprintf("spec.relationships[%d]", index)
		switch relationship.Type {
		case "iteration", "recursion", "concurrency", "integration":
		default:
			add(path+".type", "unsupported_relationship", "unsupported relationship type")
		}
		for _, process := range relationship.Processes {
			if _, exists := processes[process]; !exists {
				add(path+".processes", "unresolved_process", "relationship references an unknown process")
			}
		}
	}
	for index, entry := range descriptor.Spec.EntryPoints {
		if _, exists := processes[entry.Process]; !exists {
			add(fmt.Sprintf("spec.entryPoints[%d].process", index), "unresolved_process", "entry point references an unknown process")
		}
	}
	return issues
}

func Resolve(path string, revisionFor func(string) string) (Resolved, []Issue, error) {
	descriptor, issues, err := Load(path)
	if err != nil || hasErrors(issues) {
		return Resolved{}, issues, err
	}
	base := filepath.Dir(path)
	root := modelAssetRoot(path)
	resolved := Resolved{Descriptor: descriptor, Root: root, SchemaFiles: map[string]string{}, Criteria: map[string]string{}}
	for index, process := range descriptor.Spec.Processes {
		absolute, issue := resolveFile(base, root, process.Ref)
		if issue != nil {
			issue.Path = fmt.Sprintf("spec.processes[%d].ref", index)
			issues = append(issues, *issue)
			continue
		}
		digest, err := digestFile(absolute)
		if err != nil {
			issues = append(issues, Issue{Path: fmt.Sprintf("spec.processes[%d].ref", index), Code: "read_failed", Message: err.Error(), Severity: "error"})
			continue
		}
		name := filepath.Base(filepath.Dir(absolute))
		if content, readErr := os.ReadFile(absolute); readErr == nil {
			if parsed := frontmatterName(string(content)); parsed != "" {
				name = parsed
			}
		}
		resolved.Processes = append(resolved.Processes, ProcessResolution{ID: process.ID, Ref: process.Ref, Path: absolute, Digest: digest, Name: name, Revision: revisionFor(absolute)})
	}
	for index, item := range descriptor.Spec.Interfaces {
		if item.SchemaRef == "" {
			continue
		}
		absolute, issue := resolveFile(base, root, item.SchemaRef)
		if issue != nil {
			issue.Path = fmt.Sprintf("spec.interfaces[%d].schemaRef", index)
			issues = append(issues, *issue)
			continue
		}
		digest, err := digestFile(absolute)
		if err != nil {
			issues = append(issues, Issue{Path: fmt.Sprintf("spec.interfaces[%d].schemaRef", index), Code: "read_failed", Message: err.Error(), Severity: "error"})
			continue
		}
		resolved.SchemaFiles[item.ID] = digest
	}
	for index, handoff := range descriptor.Spec.Handoffs {
		if handoff.AcceptanceRef == "" {
			continue
		}
		absolute, issue := resolveFile(base, root, handoff.AcceptanceRef)
		if issue != nil {
			issue.Path = fmt.Sprintf("spec.handoffs[%d].acceptanceRef", index)
			issues = append(issues, *issue)
			continue
		}
		digest, err := digestFile(absolute)
		if err != nil {
			issues = append(issues, Issue{Path: fmt.Sprintf("spec.handoffs[%d].acceptanceRef", index), Code: "read_failed", Message: err.Error(), Severity: "error"})
			continue
		}
		resolved.Criteria[handoff.ID] = digest
	}
	if hasErrors(issues) {
		return Resolved{}, issues, nil
	}
	resolved.Digest = resolvedDigest(resolved)
	return resolved, issues, nil
}

func hasErrors(issues []Issue) bool {
	for _, issue := range issues {
		if issue.Severity == "error" {
			return true
		}
	}
	return false
}

func modelAssetRoot(path string) string {
	directory := filepath.Dir(path)
	if filepath.Base(directory) == ".alps" {
		return filepath.Dir(directory)
	}
	if filepath.Base(filepath.Dir(directory)) == ".alps" && filepath.Base(directory) == "process-models" {
		return filepath.Dir(filepath.Dir(directory))
	}
	return directory
}

func resolveFile(base, root, reference string) (string, *Issue) {
	if reference == "" || filepath.IsAbs(reference) {
		return "", &Issue{Code: "invalid_reference", Message: "reference must be relative", Severity: "error"}
	}
	clean := filepath.Clean(filepath.FromSlash(reference))
	if clean == "." {
		return "", &Issue{Code: "invalid_reference", Message: "reference must identify a file", Severity: "error"}
	}
	candidate := filepath.Join(base, clean)
	rootReal, err := filepath.EvalSymlinks(root)
	if err != nil {
		rootReal, _ = filepath.Abs(root)
	}
	candidateReal, err := filepath.EvalSymlinks(candidate)
	if err != nil {
		return "", &Issue{Code: "reference_not_found", Message: err.Error(), Severity: "error"}
	}
	if candidateReal != rootReal && !strings.HasPrefix(candidateReal, rootReal+string(filepath.Separator)) {
		return "", &Issue{Code: "symlink_outside_root", Message: "reference resolves outside the descriptor root", Severity: "error"}
	}
	return candidateReal, nil
}

func digestFile(path string) (string, error) {
	content, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	digest := sha256.Sum256(content)
	return "sha256:" + hex.EncodeToString(digest[:]), nil
}

func resolvedDigest(resolved Resolved) string {
	clone := resolved
	clone.Digest = ""
	sort.Slice(clone.Processes, func(i, j int) bool { return clone.Processes[i].ID < clone.Processes[j].ID })
	encoded, _ := json.Marshal(clone)
	digest := sha256.Sum256(encoded)
	return "sha256:" + hex.EncodeToString(digest[:])
}

func frontmatterName(content string) string {
	lines := strings.Split(content, "\n")
	if len(lines) < 3 || strings.TrimSpace(lines[0]) != "---" {
		return ""
	}
	for _, line := range lines[1:] {
		if strings.TrimSpace(line) == "---" {
			break
		}
		key, value, ok := strings.Cut(line, ":")
		if ok && strings.TrimSpace(key) == "name" {
			return strings.Trim(strings.TrimSpace(value), "\"")
		}
	}
	return ""
}

func MarshalCanonical(descriptor Descriptor) ([]byte, error) {
	if issues := Validate(descriptor); hasErrors(issues) {
		return nil, errors.New("descriptor is invalid")
	}
	return json.Marshal(descriptor)
}
