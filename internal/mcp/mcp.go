package mcp

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
)

type request struct {
	JSONRPC string          `json:"jsonrpc"`
	ID      json.RawMessage `json:"id"`
	Method  string          `json:"method"`
	Params  json.RawMessage `json:"params"`
}

type response struct {
	JSONRPC string          `json:"jsonrpc"`
	ID      json.RawMessage `json:"id,omitempty"`
	Result  any             `json:"result,omitempty"`
	Error   *rpcError       `json:"error,omitempty"`
}

type rpcError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

func Serve(ctx context.Context, input io.Reader, output io.Writer, endpoint, token string) error {
	scanner := bufio.NewScanner(input)
	scanner.Buffer(make([]byte, 64<<10), 4<<20)
	encoder := json.NewEncoder(output)
	for scanner.Scan() {
		var request request
		if err := json.Unmarshal(scanner.Bytes(), &request); err != nil || len(request.ID) == 0 {
			continue
		}
		if err := encoder.Encode(handle(ctx, endpoint, token, request)); err != nil {
			return err
		}
	}
	return scanner.Err()
}

func handle(ctx context.Context, endpoint, token string, request request) response {
	result := response{JSONRPC: "2.0", ID: request.ID}
	switch request.Method {
	case "initialize":
		result.Result = map[string]any{
			"protocolVersion": "2025-11-25",
			"capabilities":    map[string]any{"tools": map[string]any{}},
			"serverInfo":      map[string]any{"name": "alps-local-runtime", "version": "0.0.0-experimental"},
		}
	case "ping":
		result.Result = map[string]any{}
	case "tools/list":
		result.Result = map[string]any{"tools": tools()}
	case "tools/call":
		var params struct {
			Name      string         `json:"name"`
			Arguments map[string]any `json:"arguments"`
		}
		if err := json.Unmarshal(request.Params, &params); err != nil {
			return fail(request.ID, -32602, err.Error())
		}
		value, err := call(ctx, endpoint, token, params.Name, params.Arguments)
		if err != nil {
			return fail(request.ID, -32000, err.Error())
		}
		text, _ := json.MarshalIndent(value, "", "  ")
		result.Result = map[string]any{
			"content":           []map[string]any{{"type": "text", "text": string(text)}},
			"structuredContent": value,
		}
	default:
		return fail(request.ID, -32601, "method not found")
	}
	return result
}

func fail(id json.RawMessage, code int, message string) response {
	return response{JSONRPC: "2.0", ID: id, Error: &rpcError{Code: code, Message: message}}
}

func tools() []map[string]any {
	return []map[string]any{
		{
			"name":        "alps_catalog_list",
			"description": "List discovered ALPS Skills, Plugins, and Process Models.",
			"inputSchema": map[string]any{"type": "object", "properties": map[string]any{}},
		},
		{
			"name":        "alps_run_start",
			"description": "Start an ALPS Run for a Skill or Process.",
			"inputSchema": schema([]string{"title", "process"}, map[string]any{"title": stringSchema(), "process": stringSchema(), "assetId": stringSchema()}),
		},
		{
			"name":        "alps_run_report",
			"description": "Report Agent-observed progress without asserting assessed Outcome achievement.",
			"inputSchema": schema([]string{"runId", "message", "expectedVersion"}, map[string]any{
				"runId":           stringSchema(),
				"actor":           stringSchema(),
				"message":         stringSchema(),
				"progress":        map[string]any{"type": "integer", "minimum": 0, "maximum": 100},
				"expectedVersion": map[string]any{"type": "integer"},
			}),
		},
		{
			"name":        "alps_gate_open",
			"description": "Open a Human Decision Gate for a Run.",
			"inputSchema": schema([]string{"runId", "title", "effect", "expectedVersion"}, map[string]any{
				"runId":           stringSchema(),
				"title":           stringSchema(),
				"effect":          stringSchema(),
				"authority":       stringSchema(),
				"reversible":      map[string]any{"type": "boolean"},
				"expectedVersion": map[string]any{"type": "integer"},
			}),
		},
		{
			"name":        "alps_usage_report",
			"description": "Record a model invocation and token usage observation.",
			"inputSchema": schema([]string{"runId", "source"}, map[string]any{
				"runId":     stringSchema(),
				"requested": stringSchema(),
				"effective": stringSchema(),
				"resolved":  stringSchema(),
				"effort":    stringSchema(),
				"source":    stringSchema(),
				"input":     map[string]any{"type": "integer"},
				"output":    map[string]any{"type": "integer"},
			}),
		},
	}
}

func stringSchema() map[string]any { return map[string]any{"type": "string"} }

func schema(required []string, properties map[string]any) map[string]any {
	return map[string]any{"type": "object", "required": required, "properties": properties}
}

func call(ctx context.Context, endpoint, token, name string, arguments map[string]any) (any, error) {
	method, path := http.MethodGet, ""
	var body any
	switch name {
	case "alps_catalog_list":
		path = "/api/catalog"
	case "alps_run_start":
		method, path, body = http.MethodPost, "/api/runs", arguments
	case "alps_run_report":
		method, path, body = http.MethodPost, "/api/runs/"+text(arguments, "runId")+"/report", without(arguments, "runId")
	case "alps_gate_open":
		method, path, body = http.MethodPost, "/api/runs/"+text(arguments, "runId")+"/gates", without(arguments, "runId")
	case "alps_usage_report":
		method, path, body = http.MethodPost, "/api/runs/"+text(arguments, "runId")+"/usage", without(arguments, "runId")
	default:
		return nil, fmt.Errorf("unknown tool %q", name)
	}
	var reader io.Reader
	if body != nil {
		encoded, _ := json.Marshal(body)
		reader = bytes.NewReader(encoded)
	}
	request, _ := http.NewRequestWithContext(ctx, method, endpoint+path, reader)
	if body != nil {
		request.Header.Set("Content-Type", "application/json")
	}
	if token != "" {
		request.Header.Set("Authorization", "Bearer "+token)
	}
	response, err := http.DefaultClient.Do(request)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()
	raw, _ := io.ReadAll(io.LimitReader(response.Body, 4<<20))
	if response.StatusCode >= 300 {
		return nil, fmt.Errorf("runtime %s: %s", response.Status, strings.TrimSpace(string(raw)))
	}
	var value any
	if err := json.Unmarshal(raw, &value); err != nil {
		return string(raw), nil
	}
	return value, nil
}

func text(values map[string]any, key string) string {
	value, _ := values[key].(string)
	return value
}

func without(values map[string]any, key string) map[string]any {
	result := map[string]any{}
	for name, value := range values {
		if name != key {
			result[name] = value
		}
	}
	return result
}
