package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	goruntime "runtime"
	"strings"

	"github.com/mashimashica/alps/internal/httpapi"
	"github.com/mashimashica/alps/internal/mcp"
	alpsruntime "github.com/mashimashica/alps/internal/runtime"
)

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}
	var err error
	switch os.Args[1] {
	case "serve":
		err = serve(os.Args[2:])
	case "scan":
		err = postCommand(os.Args[2:], "/api/discovery/scan", map[string]any{})
	case "mcp":
		err = runMCP(os.Args[2:])
	case "hook":
		err = runHook(os.Args[2:])
	case "backup":
		err = postCommand(os.Args[2:], "/api/admin/backup", map[string]any{})
	case "export":
		err = exportRun(os.Args[2:])
	case "version", "--version", "-v":
		fmt.Println("alps local-runtime-v0 experimental")
	default:
		usage()
		os.Exit(2)
	}
	if err != nil {
		fmt.Fprintln(os.Stderr, "alps:", err)
		os.Exit(1)
	}
}

func usage() {
	fmt.Fprintln(os.Stderr, `Usage: alps <command>

Commands:
  serve   run the local runtime and web UI
  scan    rescan configured Skill and Plugin roots
  mcp     expose the runtime as an MCP stdio server
  hook    forward a host hook observation to the runtime
  backup  create a consistent SQLite backup
  export  export a Run audit bundle
  version print the experimental version`)
}

func serve(args []string) error {
	fs := flag.NewFlagSet("serve", flag.ContinueOnError)
	workspace := fs.String("workspace", defaultWorkspace(), "runtime workspace")
	root := fs.String("root", ".", "project root to discover")
	addr := fs.String("addr", "127.0.0.1:8787", "listen address")
	openBrowser := fs.Bool("open", false, "open the UI in the default browser")
	if err := fs.Parse(args); err != nil {
		return err
	}

	rt, err := alpsruntime.Open(*workspace)
	if err != nil {
		return err
	}
	defer rt.Close()
	absRoot, err := filepath.Abs(*root)
	if err != nil {
		return err
	}
	rt.SetRoots(alpsruntime.DefaultRoots(absRoot))
	if _, err := rt.Scan(context.Background()); err != nil {
		fmt.Fprintln(os.Stderr, "initial discovery:", err)
	}
	server, err := httpapi.New(rt, *addr)
	if err != nil {
		return err
	}
	if err := rt.WriteEndpoint("http://" + *addr); err != nil {
		return err
	}
	fmt.Printf("ALPS Local Runtime: http://%s\nWorkspace: %s\n", *addr, *workspace)
	if *openBrowser {
		go openURL("http://" + *addr)
	}
	return server.ListenAndServe()
}

func runMCP(args []string) error {
	fs := flag.NewFlagSet("mcp", flag.ContinueOnError)
	workspace := fs.String("workspace", defaultWorkspace(), "runtime workspace")
	endpoint := fs.String("endpoint", "", "runtime URL")
	if err := fs.Parse(args); err != nil {
		return err
	}
	url := *endpoint
	if url == "" {
		var err error
		url, err = alpsruntime.ReadEndpoint(*workspace)
		if err != nil {
			return fmt.Errorf("runtime endpoint not found; start `alps serve`: %w", err)
		}
	}
	token, _ := os.ReadFile(filepath.Join(*workspace, "runtime", "access.token"))
	return mcp.Serve(context.Background(), os.Stdin, os.Stdout, url, strings.TrimSpace(string(token)))
}

func runHook(args []string) error {
	fs := flag.NewFlagSet("hook", flag.ContinueOnError)
	workspace := fs.String("workspace", defaultWorkspace(), "runtime workspace")
	host := fs.String("host", "unknown", "host name")
	event := fs.String("event", "unknown", "host event name")
	if err := fs.Parse(args); err != nil {
		return err
	}
	endpoint, err := alpsruntime.ReadEndpoint(*workspace)
	if err != nil {
		return err
	}
	raw, err := io.ReadAll(io.LimitReader(os.Stdin, 1<<20))
	if err != nil {
		return err
	}
	payload := map[string]any{"host": *host, "event": *event, "raw": json.RawMessage(raw)}
	token, _ := os.ReadFile(filepath.Join(*workspace, "runtime", "access.token"))
	return postJSON(endpoint+"/api/host-observations", payload, strings.TrimSpace(string(token)))
}

func postCommand(args []string, path string, payload any) error {
	fs := flag.NewFlagSet(strings.Trim(path, "/"), flag.ContinueOnError)
	workspace := fs.String("workspace", defaultWorkspace(), "runtime workspace")
	if err := fs.Parse(args); err != nil {
		return err
	}
	endpoint, err := alpsruntime.ReadEndpoint(*workspace)
	if err != nil {
		return err
	}
	token, _ := os.ReadFile(filepath.Join(*workspace, "runtime", "access.token"))
	return postJSON(endpoint+path, payload, strings.TrimSpace(string(token)))
}

func exportRun(args []string) error {
	fs := flag.NewFlagSet("export", flag.ContinueOnError)
	workspace := fs.String("workspace", defaultWorkspace(), "runtime workspace")
	runID := fs.String("run", "", "Run ID")
	out := fs.String("out", "", "output JSON path")
	if err := fs.Parse(args); err != nil {
		return err
	}
	if *runID == "" {
		return fmt.Errorf("--run is required")
	}
	endpoint, err := alpsruntime.ReadEndpoint(*workspace)
	if err != nil {
		return err
	}
	req, _ := http.NewRequest(http.MethodGet, endpoint+"/api/runs/"+*runID+"/export", nil)
	token, _ := os.ReadFile(filepath.Join(*workspace, "runtime", "access.token"))
	req.Header.Set("Authorization", "Bearer "+strings.TrimSpace(string(token)))
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 300 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("%s: %s", resp.Status, body)
	}
	dst := *out
	if dst == "" {
		dst = "alps-run-" + *runID + ".json"
	}
	file, err := os.Create(dst)
	if err != nil {
		return err
	}
	defer file.Close()
	_, err = io.Copy(file, resp.Body)
	return err
}

func postJSON(url string, payload any, token string) error {
	body, _ := json.Marshal(payload)
	req, _ := http.NewRequest(http.MethodPost, url, strings.NewReader(string(body)))
	req.Header.Set("Content-Type", "application/json")
	if token != "" {
		req.Header.Set("Authorization", "Bearer "+token)
	}
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 300 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("%s: %s", resp.Status, body)
	}
	_, _ = io.Copy(os.Stdout, resp.Body)
	return nil
}

func defaultWorkspace() string {
	if value := os.Getenv("ALPS_WORKSPACE"); value != "" {
		return value
	}
	home, _ := os.UserHomeDir()
	if home == "" {
		return ".alps-runtime"
	}
	return filepath.Join(home, ".alps", "runtime-v0")
}

func openURL(url string) {
	var command *exec.Cmd
	switch goruntime.GOOS {
	case "darwin":
		command = exec.Command("open", url)
	case "windows":
		command = exec.Command("rundll32", "url.dll,FileProtocolHandler", url)
	default:
		command = exec.Command("xdg-open", url)
	}
	_ = command.Start()
}
