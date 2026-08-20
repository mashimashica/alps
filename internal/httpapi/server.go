package httpapi

import (
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	alpsruntime "github.com/mashimashica/alps/internal/runtime"
	"github.com/mashimashica/alps/internal/web"
)

type Server struct {
	runtime *alpsruntime.Runtime
	server  *http.Server
	static  http.Handler
}

func New(runtime *alpsruntime.Runtime, address string) (*Server, error) {
	staticFS, err := fs.Sub(web.Files, "static")
	if err != nil {
		return nil, err
	}
	server := &Server{runtime: runtime, static: http.FileServer(http.FS(staticFS))}
	server.server = &http.Server{Addr: address, Handler: server, ReadHeaderTimeout: 5 * time.Second}
	return server, nil
}

func (s *Server) ListenAndServe() error {
	err := s.server.ListenAndServe()
	if errors.Is(err, http.ErrServerClosed) {
		return nil
	}
	return err
}

func (s *Server) ServeHTTP(writer http.ResponseWriter, request *http.Request) {
	if request.URL.Path == "/api/health" {
		writeJSON(writer, http.StatusOK, map[string]any{"status": "ok"})
		return
	}
	if request.URL.Path == "/assets/icon.svg" {
		content, err := os.ReadFile("assets/icon.svg")
		if err != nil {
			http.NotFound(writer, request)
			return
		}
		writer.Header().Set("Content-Type", "image/svg+xml")
		_, _ = writer.Write(content)
		return
	}
	if strings.HasPrefix(request.URL.Path, "/api/") && !s.authorized(request) {
		writeError(writer, http.StatusUnauthorized, "unauthorized", "Runtime authorization required", nil)
		return
	}
	if request.Method != http.MethodGet && request.Method != http.MethodHead && strings.HasPrefix(request.URL.Path, "/api/") && !validOrigin(request) {
		writeError(writer, http.StatusForbidden, "invalid_origin", "Request origin is not allowed", nil)
		return
	}
	if strings.HasPrefix(request.URL.Path, "/api/") {
		s.api(writer, request)
		return
	}
	if request.URL.Path == "/" {
		http.SetCookie(writer, &http.Cookie{Name: "alps_session", Value: s.runtime.Token(), Path: "/", HttpOnly: true, SameSite: http.SameSiteStrictMode})
	}
	s.static.ServeHTTP(writer, request)
}

func (s *Server) authorized(request *http.Request) bool {
	if cookie, err := request.Cookie("alps_session"); err == nil && cookie.Value == s.runtime.Token() {
		return true
	}
	return strings.TrimPrefix(request.Header.Get("Authorization"), "Bearer ") == s.runtime.Token()
}

func validOrigin(request *http.Request) bool {
	origin := request.Header.Get("Origin")
	return origin == "" || origin == "http://"+request.Host || origin == "https://"+request.Host
}

func (s *Server) api(writer http.ResponseWriter, request *http.Request) {
	ctx := request.Context()
	path := strings.TrimPrefix(request.URL.Path, "/api")
	switch {
	case path == "/catalog" && request.Method == http.MethodGet:
		value, err := s.runtime.Catalog(ctx)
		respond(writer, value, err)
	case path == "/discovery/scan" && request.Method == http.MethodPost:
		value, err := s.runtime.Scan(ctx)
		respond(writer, value, err)
	case path == "/model" && request.Method == http.MethodGet:
		value, err := s.runtime.Graph(ctx)
		respond(writer, value, err)
	case path == "/runs" && request.Method == http.MethodGet:
		value, err := s.runtime.Runs(ctx)
		respond(writer, value, err)
	case path == "/runs" && request.Method == http.MethodPost:
		var input struct {
			Title   string `json:"title"`
			Process string `json:"process"`
			AssetID string `json:"assetID"`
		}
		if !decode(writer, request, &input) {
			return
		}
		value, err := s.runtime.CreateRun(ctx, input.Title, input.Process, input.AssetID)
		respond(writer, value, err)
	case path == "/gates" && request.Method == http.MethodGet:
		value, err := s.runtime.Gates(ctx)
		respond(writer, value, err)
	case path == "/analysis" && request.Method == http.MethodGet:
		value, err := s.runtime.Analysis(ctx)
		respond(writer, value, err)
	case path == "/events" && request.Method == http.MethodGet:
		s.events(writer, request)
	case path == "/host-observations" && request.Method == http.MethodPost:
		var input struct {
			Host  string          `json:"host"`
			Event string          `json:"event"`
			Raw   json.RawMessage `json:"raw"`
		}
		if !decode(writer, request, &input) {
			return
		}
		respond(writer, map[string]any{"ok": true}, s.runtime.HostObservation(ctx, input.Host, input.Event, input.Raw))
	case path == "/admin/backup" && request.Method == http.MethodPost:
		value, err := s.runtime.Backup(ctx)
		respond(writer, map[string]any{"path": value}, err)
	case strings.HasPrefix(path, "/assets/"):
		s.asset(writer, request, strings.TrimPrefix(path, "/assets/"))
	case strings.HasPrefix(path, "/runs/"):
		s.run(writer, request, strings.TrimPrefix(path, "/runs/"))
	case strings.HasPrefix(path, "/gates/"):
		s.gate(writer, request, strings.TrimPrefix(path, "/gates/"))
	default:
		writeError(writer, http.StatusNotFound, "not_found", "Endpoint not found", nil)
	}
}

func (s *Server) asset(writer http.ResponseWriter, request *http.Request, tail string) {
	parts := strings.Split(strings.Trim(tail, "/"), "/")
	id := parts[0]
	if len(parts) == 1 && request.Method == http.MethodGet {
		value, err := s.runtime.Asset(request.Context(), id)
		respond(writer, value, err)
		return
	}
	if len(parts) == 2 && parts[1] == "content" && request.Method == http.MethodGet {
		path, content, err := s.runtime.AssetFile(request.Context(), id, request.URL.Query().Get("path"))
		respond(writer, map[string]any{"path": path, "content": content}, err)
		return
	}
	if len(parts) == 2 && parts[1] == "adopt" && request.Method == http.MethodPost {
		revisionID, err := s.runtime.Adopt(request.Context(), id)
		respond(writer, map[string]any{"revisionId": revisionID}, err)
		return
	}
	writeError(writer, http.StatusNotFound, "not_found", "Asset endpoint not found", nil)
}

func (s *Server) run(writer http.ResponseWriter, request *http.Request, tail string) {
	parts := strings.Split(strings.Trim(tail, "/"), "/")
	id := parts[0]
	if len(parts) == 1 && request.Method == http.MethodGet {
		value, err := s.runtime.RunDetail(request.Context(), id)
		respond(writer, value, err)
		return
	}
	if len(parts) == 2 && parts[1] == "report" && request.Method == http.MethodPost {
		var input struct {
			Actor           string `json:"actor"`
			Message         string `json:"message"`
			Progress        *int   `json:"progress"`
			ExpectedVersion int64  `json:"expectedVersion"`
		}
		if !decode(writer, request, &input) {
			return
		}
		value, err := s.runtime.ReportRun(request.Context(), id, input.Actor, input.Message, input.Progress, input.ExpectedVersion)
		respond(writer, value, err)
		return
	}
	if len(parts) == 2 && parts[1] == "gates" && request.Method == http.MethodPost {
		var input struct {
			Title           string `json:"title"`
			Effect          string `json:"effect"`
			Authority       string `json:"authority"`
			Reversible      bool   `json:"reversible"`
			ExpectedVersion int64  `json:"expectedVersion"`
		}
		if !decode(writer, request, &input) {
			return
		}
		value, err := s.runtime.OpenGate(request.Context(), id, input.Title, input.Effect, input.Authority, input.Reversible, input.ExpectedVersion)
		respond(writer, value, err)
		return
	}
	if len(parts) == 2 && parts[1] == "artifacts" && request.Method == http.MethodPost {
		var input struct {
			Name      string `json:"name"`
			MediaType string `json:"mediaType"`
			Content   string `json:"content"`
			Encoding  string `json:"encoding"`
		}
		if !decode(writer, request, &input) {
			return
		}
		data := []byte(input.Content)
		if input.Encoding == "base64" {
			var err error
			data, err = base64.StdEncoding.DecodeString(input.Content)
			if err != nil {
				writeError(writer, http.StatusBadRequest, "invalid_base64", err.Error(), nil)
				return
			}
		}
		artifactID, err := s.runtime.AddArtifact(request.Context(), id, input.Name, input.MediaType, data)
		respond(writer, map[string]any{"artifactId": artifactID}, err)
		return
	}
	if len(parts) == 2 && parts[1] == "usage" && request.Method == http.MethodPost {
		var input struct {
			Requested  string `json:"requested"`
			Effective  string `json:"effective"`
			Resolved   string `json:"resolved"`
			Effort     string `json:"effort"`
			Source     string `json:"source"`
			Input      *int64 `json:"input"`
			Output     *int64 `json:"output"`
			CacheRead  *int64 `json:"cacheRead"`
			CacheWrite *int64 `json:"cacheWrite"`
			Reasoning  *int64 `json:"reasoning"`
		}
		if !decode(writer, request, &input) {
			return
		}
		err := s.runtime.RecordUsage(request.Context(), id, input.Requested, input.Effective, input.Resolved, input.Effort, input.Source, input.Input, input.Output, input.CacheRead, input.CacheWrite, input.Reasoning)
		respond(writer, map[string]any{"ok": true}, err)
		return
	}
	if len(parts) == 2 && parts[1] == "export" && request.Method == http.MethodGet {
		value, err := s.runtime.ExportRun(request.Context(), id)
		respond(writer, value, err)
		return
	}
	writeError(writer, http.StatusNotFound, "not_found", "Run endpoint not found", nil)
}

func (s *Server) gate(writer http.ResponseWriter, request *http.Request, tail string) {
	parts := strings.Split(strings.Trim(tail, "/"), "/")
	if len(parts) == 2 && parts[1] == "decisions" && request.Method == http.MethodPost {
		var input struct {
			Decision        string `json:"decision"`
			Actor           string `json:"actor"`
			Rationale       string `json:"rationale"`
			ExpectedVersion int64  `json:"expectedVersion"`
		}
		if !decode(writer, request, &input) {
			return
		}
		err := s.runtime.Decide(request.Context(), parts[0], input.Decision, input.Actor, input.Rationale, input.ExpectedVersion)
		respond(writer, map[string]any{"ok": true}, err)
		return
	}
	writeError(writer, http.StatusNotFound, "not_found", "Gate endpoint not found", nil)
}

func (s *Server) events(writer http.ResponseWriter, request *http.Request) {
	flusher, ok := writer.(http.Flusher)
	if !ok {
		writeError(writer, http.StatusInternalServerError, "streaming_unsupported", "Streaming unsupported", nil)
		return
	}
	writer.Header().Set("Content-Type", "text/event-stream")
	writer.Header().Set("Cache-Control", "no-cache")
	sequence, _ := strconv.ParseInt(request.Header.Get("Last-Event-ID"), 10, 64)
	history, _ := s.runtime.EventsAfter(request.Context(), sequence)
	for _, event := range history {
		sendEvent(writer, event)
	}
	flusher.Flush()
	channel, cancel := s.runtime.Subscribe()
	defer cancel()
	ticker := time.NewTicker(20 * time.Second)
	defer ticker.Stop()
	for {
		select {
		case <-request.Context().Done():
			return
		case event := <-channel:
			sendEvent(writer, event)
			flusher.Flush()
		case <-ticker.C:
			fmt.Fprint(writer, ": keepalive\n\n")
			flusher.Flush()
		}
	}
}

func sendEvent(writer io.Writer, event alpsruntime.Event) {
	content, _ := json.Marshal(event)
	fmt.Fprintf(writer, "id: %d\nevent: %s\ndata: %s\n\n", event.Sequence, event.Type, content)
}

func decode(writer http.ResponseWriter, request *http.Request, value any) bool {
	request.Body = http.MaxBytesReader(writer, request.Body, 2<<20)
	if err := json.NewDecoder(request.Body).Decode(value); err != nil {
		writeError(writer, http.StatusBadRequest, "invalid_json", err.Error(), nil)
		return false
	}
	return true
}

func respond(writer http.ResponseWriter, value any, err error) {
	if err != nil {
		switch {
		case errors.Is(err, alpsruntime.ErrStale):
			writeError(writer, http.StatusConflict, "stale_version", err.Error(), nil)
		case strings.Contains(err.Error(), "no rows"):
			writeError(writer, http.StatusNotFound, "not_found", err.Error(), nil)
		default:
			writeError(writer, http.StatusInternalServerError, "internal_error", err.Error(), nil)
		}
		return
	}
	writeJSON(writer, http.StatusOK, value)
}

func writeJSON(writer http.ResponseWriter, status int, value any) {
	writer.Header().Set("Content-Type", "application/json")
	writer.WriteHeader(status)
	_ = json.NewEncoder(writer).Encode(value)
}

func writeError(writer http.ResponseWriter, status int, code, message string, details any) {
	writeJSON(writer, status, map[string]any{"error": map[string]any{"code": code, "message": message, "details": details}})
}
