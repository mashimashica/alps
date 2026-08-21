package httpapi

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"net"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/mashimashica/alps/internal/domain"
	"github.com/mashimashica/alps/internal/hooks"
	"github.com/mashimashica/alps/internal/hosts"
	alpsruntime "github.com/mashimashica/alps/internal/runtime"
	"github.com/mashimashica/alps/internal/web"
)

type Server struct {
	runtime *alpsruntime.Runtime
	server  *http.Server
	static  http.Handler
	files   fs.FS
}

func New(runtime *alpsruntime.Runtime, address string) (*Server, error) {
	host, _, err := net.SplitHostPort(address)
	if err != nil {
		return nil, fmt.Errorf("invalid listen address: %w", err)
	}
	ip := net.ParseIP(strings.Trim(host, "[]"))
	if host != "localhost" && (ip == nil || !ip.IsLoopback()) {
		return nil, fmt.Errorf("ALPS Local Runtime only binds to loopback addresses")
	}
	staticFS, err := fs.Sub(web.Files, "static")
	if err != nil {
		return nil, err
	}
	server := &Server{runtime: runtime, static: http.FileServer(http.FS(staticFS)), files: staticFS}
	server.server = &http.Server{
		Addr:              address,
		Handler:           server,
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       30 * time.Second,
		WriteTimeout:      0,
		IdleTimeout:       90 * time.Second,
		MaxHeaderBytes:    64 << 10,
	}
	return server, nil
}

func (s *Server) ListenAndServe() error {
	err := s.server.ListenAndServe()
	if errors.Is(err, http.ErrServerClosed) {
		return nil
	}
	return err
}

func (s *Server) Shutdown(ctx context.Context) error { return s.server.Shutdown(ctx) }

func (s *Server) ServeHTTP(writer http.ResponseWriter, request *http.Request) {
	securityHeaders(writer)
	if request.URL.Path == "/api/health" || request.URL.Path == "/v1/health" {
		writeJSON(writer, http.StatusOK, map[string]any{"status": "ok", "version": "v0-conformance"})
		return
	}
	if request.URL.Path == "/" {
		http.SetCookie(writer, &http.Cookie{Name: "alps_session", Value: s.runtime.Token(), Path: "/", HttpOnly: true, SameSite: http.SameSiteStrictMode, Secure: false, MaxAge: 86400})
	}
	if strings.HasPrefix(request.URL.Path, "/api/") || strings.HasPrefix(request.URL.Path, "/v1/") {
		if !s.authorized(request) {
			writeError(writer, http.StatusUnauthorized, "unauthorized", "Runtime authorization required", nil)
			return
		}
		if request.Method != http.MethodGet && request.Method != http.MethodHead && !validOrigin(request) {
			writeError(writer, http.StatusForbidden, "invalid_origin", "Request Origin is not allowed", nil)
			return
		}
		request = request.WithContext(actorContext(request))
		if strings.HasPrefix(request.URL.Path, "/v1/") {
			s.v1(writer, request)
		} else {
			s.legacy(writer, request)
		}
		return
	}
	s.serveStatic(writer, request)
}

func securityHeaders(writer http.ResponseWriter) {
	writer.Header().Set("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
	writer.Header().Set("Referrer-Policy", "no-referrer")
	writer.Header().Set("X-Content-Type-Options", "nosniff")
	writer.Header().Set("X-Frame-Options", "DENY")
	writer.Header().Set("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
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

func actorContext(request *http.Request) context.Context {
	actorType := request.Header.Get("X-ALPS-Actor-Type")
	channel := request.Header.Get("X-ALPS-Channel")
	if actorType == "" {
		if request.Header.Get("Authorization") != "" {
			actorType, channel = domain.ActorAgent, domain.ChannelMCP
		} else {
			actorType, channel = domain.ActorHuman, domain.ChannelWeb
		}
	}
	if channel == "" {
		channel = domain.ChannelInternal
	}
	actor := domain.Actor{Type: actorType, ID: request.Header.Get("X-ALPS-Actor-ID"), Authority: request.Header.Get("X-ALPS-Authority"), Channel: channel}
	if actor.ID == "" && actor.Type == domain.ActorHuman {
		actor.ID = "local-user"
	}
	if actor.Authority == "" && actor.Type == domain.ActorHuman {
		actor.Authority = "operator"
	}
	return alpsruntime.WithActor(request.Context(), actor)
}

func (s *Server) serveStatic(writer http.ResponseWriter, request *http.Request) {
	clean := strings.TrimPrefix(request.URL.Path, "/")
	if clean == "" {
		clean = "index.html"
	}
	if _, err := fs.Stat(s.files, clean); err == nil {
		s.static.ServeHTTP(writer, request)
		return
	}
	content, err := fs.ReadFile(s.files, "index.html")
	if err != nil {
		http.NotFound(writer, request)
		return
	}
	writer.Header().Set("Content-Type", "text/html; charset=utf-8")
	_, _ = writer.Write(content)
}

func (s *Server) v1(writer http.ResponseWriter, request *http.Request) {
	path := strings.TrimPrefix(request.URL.Path, "/v1")
	switch {
	case path == "/catalog" && request.Method == http.MethodGet:
		value161, err161 := s.runtime.Catalog(request.Context())
		respond(writer, value161, err161)
	case path == "/discovery/scan" && request.Method == http.MethodPost:
		s.mutate(writer, request, "discovery.scan", func(body []byte) (any, error) { return s.runtime.Scan(request.Context()) })
	case path == "/process-models" && request.Method == http.MethodGet:
		value165, err165 := s.runtime.ProcessModels(request.Context())
		respond(writer, value165, err165)
	case strings.HasPrefix(path, "/process-models/"):
		s.processModel(writer, request, strings.TrimPrefix(path, "/process-models/"))
	case path == "/runs" && request.Method == http.MethodGet:
		value169, err169 := s.runtime.Runs(request.Context())
		respond(writer, value169, err169)
	case path == "/runs" && request.Method == http.MethodPost:
		mutateJSON(s, writer, request, "run.start", func(input alpsruntime.StartRunInput) (any, error) {
			return s.runtime.StartRun(request.Context(), input)
		})
	case path == "/board" && request.Method == http.MethodGet:
		runs, err := s.runtime.Runs(request.Context())
		if err != nil {
			respond(writer, nil, err)
			return
		}
		respond(writer, boardProjection(runs), nil)
	case path == "/gates" && request.Method == http.MethodGet:
		value182, err182 := s.runtime.Gates(request.Context())
		respond(writer, value182, err182)
	case path == "/assessments" && request.Method == http.MethodPost:
		mutateJSON(s, writer, request, "assessment.record", func(input alpsruntime.AssessmentInput) (any, error) {
			return s.runtime.RecordAssessment(request.Context(), input)
		})
	case path == "/handoffs" && request.Method == http.MethodPost:
		mutateJSON(s, writer, request, "handoff.create", func(input alpsruntime.HandoffInput) (any, error) {
			return s.runtime.CreateHandoff(request.Context(), input)
		})
	case strings.HasPrefix(path, "/handoffs/"):
		s.handoff(writer, request, strings.TrimPrefix(path, "/handoffs/"))
	case path == "/model-catalogs" && request.Method == http.MethodPost:
		var input struct {
			Host   string           `json:"host"`
			Scope  string           `json:"scope"`
			Models []map[string]any `json:"models"`
		}
		mutateJSON(s, writer, request, "model_catalog.record", func(value struct {
			Host   string           `json:"host"`
			Scope  string           `json:"scope"`
			Models []map[string]any `json:"models"`
		}) (any, error) {
			return s.runtime.RecordModelCatalog(request.Context(), value.Host, value.Scope, value.Models)
		}, &input)
	case path == "/model-invocations" && request.Method == http.MethodPost:
		mutateJSON(s, writer, request, "model_invocation.record", func(input alpsruntime.ModelInvocationInput) (any, error) {
			return s.runtime.RecordModelInvocation(request.Context(), input)
		})
	case path == "/usage-observations" && request.Method == http.MethodPost:
		mutateJSON(s, writer, request, "usage.record", func(input alpsruntime.UsageInput) (any, error) {
			return s.runtime.RecordUsageObservation(request.Context(), input)
		})
	case path == "/cost-observations" && request.Method == http.MethodPost:
		mutateJSON(s, writer, request, "cost.record", func(input alpsruntime.CostInput) (any, error) {
			return s.runtime.RecordCostObservation(request.Context(), input)
		})
	case path == "/hosts/inventory" && request.Method == http.MethodPost:
		mutateJSON(s, writer, request, "host_inventory.register", func(input hosts.Inventory) (any, error) {
			return s.runtime.RegisterHostInventory(request.Context(), input)
		})
	case path == "/hosts/capabilities" && request.Method == http.MethodGet:
		value223, err223 := s.runtime.HostCapabilityProfiles(request.Context())
		respond(writer, value223, err223)
	case path == "/host-observations" && request.Method == http.MethodPost:
		var input struct {
			Envelope     hooks.Envelope `json:"envelope"`
			RawReference string         `json:"rawReference"`
		}
		mutateJSON(s, writer, request, "host_observation.record", func(value struct {
			Envelope     hooks.Envelope `json:"envelope"`
			RawReference string         `json:"rawReference"`
		}) (any, error) {
			return s.runtime.RecordHostObservation(request.Context(), value.Envelope, value.RawReference)
		}, &input)
	case path == "/hook-bindings" && request.Method == http.MethodPost:
		var input struct {
			Binding      hooks.Binding  `json:"binding"`
			Generated    map[string]any `json:"generated"`
			Capabilities map[string]any `json:"capabilities"`
		}
		mutateJSON(s, writer, request, "hook_binding.record", func(value struct {
			Binding      hooks.Binding  `json:"binding"`
			Generated    map[string]any `json:"generated"`
			Capabilities map[string]any `json:"capabilities"`
		}) (any, error) {
			id, err := s.runtime.RecordHookBinding(request.Context(), value.Binding, value.Generated, value.Capabilities)
			return map[string]string{"revisionId": id}, err
		}, &input)
	case strings.HasPrefix(path, "/analysis/") && request.Method == http.MethodGet:
		s.analysis(writer, request, strings.TrimPrefix(path, "/analysis/"))
	case path == "/events/stream" && request.Method == http.MethodGet:
		s.events(writer, request)
	case path == "/admin/backup" && request.Method == http.MethodPost:
		s.mutate(writer, request, "backup.create", func(body []byte) (any, error) { return s.runtime.CreateBackup(request.Context()) })
	case path == "/admin/integrity" && request.Method == http.MethodGet:
		err := s.runtime.DatabaseIntegrity(request.Context())
		respond(writer, map[string]any{"status": "ok"}, err)
	case strings.HasPrefix(path, "/assets/"):
		s.asset(writer, request, strings.TrimPrefix(path, "/assets/"), true)
	case strings.HasPrefix(path, "/runs/"):
		s.run(writer, request, strings.TrimPrefix(path, "/runs/"), true)
	case strings.HasPrefix(path, "/gates/"):
		s.gate(writer, request, strings.TrimPrefix(path, "/gates/"), true)
	default:
		writeError(writer, http.StatusNotFound, "not_found", "Endpoint not found", nil)
	}
}

// legacy keeps the alpha client and validation scripts operational while v1 is canonical.
func (s *Server) legacy(writer http.ResponseWriter, request *http.Request) {
	path := strings.TrimPrefix(request.URL.Path, "/api")
	switch {
	case path == "/catalog" && request.Method == http.MethodGet:
		value274, err274 := s.runtime.Catalog(request.Context())
		respond(writer, value274, err274)
	case path == "/discovery/scan" && request.Method == http.MethodPost:
		value276, err276 := s.runtime.Scan(request.Context())
		respond(writer, value276, err276)
	case path == "/model" && request.Method == http.MethodGet:
		value278, err278 := s.runtime.ProcessModelGraph(request.Context(), "", request.URL.Query().Get("mode"))
		respond(writer, value278, err278)
	case path == "/runs" && request.Method == http.MethodGet:
		value280, err280 := s.runtime.Runs(request.Context())
		respond(writer, value280, err280)
	case path == "/runs" && request.Method == http.MethodPost:
		var input alpsruntime.StartRunInput
		if !decode(writer, request, &input) {
			return
		}
		value286, err286 := s.runtime.StartRun(request.Context(), input)
		respond(writer, value286, err286)
	case path == "/gates" && request.Method == http.MethodGet:
		value288, err288 := s.runtime.Gates(request.Context())
		respond(writer, value288, err288)
	case path == "/analysis" && request.Method == http.MethodGet:
		value290, err290 := s.runtime.Analysis(request.Context())
		respond(writer, value290, err290)
	case path == "/events" && request.Method == http.MethodGet:
		s.events(writer, request)
	case path == "/admin/backup" && request.Method == http.MethodPost:
		value, err := s.runtime.Backup(request.Context())
		respond(writer, map[string]any{"path": value}, err)
	case path == "/host-observations" && request.Method == http.MethodPost:
		var input struct {
			Host  string          `json:"host"`
			Event string          `json:"event"`
			Raw   json.RawMessage `json:"raw"`
		}
		if !decode(writer, request, &input) {
			return
		}
		respond(writer, map[string]any{"ok": true}, s.runtime.HostObservation(request.Context(), input.Host, input.Event, input.Raw))
	case strings.HasPrefix(path, "/assets/"):
		s.asset(writer, request, strings.TrimPrefix(path, "/assets/"), false)
	case strings.HasPrefix(path, "/runs/"):
		s.run(writer, request, strings.TrimPrefix(path, "/runs/"), false)
	case strings.HasPrefix(path, "/gates/"):
		s.gate(writer, request, strings.TrimPrefix(path, "/gates/"), false)
	default:
		writeError(writer, http.StatusNotFound, "not_found", "Endpoint not found", nil)
	}
}

func (s *Server) asset(writer http.ResponseWriter, request *http.Request, tail string, canonical bool) {
	parts := strings.Split(strings.Trim(tail, "/"), "/")
	id := parts[0]
	if len(parts) == 1 && request.Method == http.MethodGet {
		value321, err321 := s.runtime.Asset(request.Context(), id)
		respond(writer, value321, err321)
		return
	}
	if len(parts) == 2 && parts[1] == "tree" && request.Method == http.MethodGet {
		detail, err := s.runtime.Asset(request.Context(), id)
		if err != nil {
			respond(writer, nil, err)
			return
		}
		respond(writer, map[string]any{"assetId": id, "files": detail.Files, "manifest": detail.Manifest}, nil)
		return
	}
	if len(parts) == 2 && parts[1] == "content" && request.Method == http.MethodGet {
		path, content, err := s.runtime.AssetFile(request.Context(), id, request.URL.Query().Get("path"))
		respond(writer, map[string]any{"path": path, "content": content}, err)
		return
	}
	if len(parts) == 2 && parts[1] == "validate" && request.Method == http.MethodPost {
		if canonical {
			s.mutate(writer, request, "asset.validate", func(body []byte) (any, error) { return s.runtime.ValidateAsset(request.Context(), id) })
		} else {
			value342, err342 := s.runtime.ValidateAsset(request.Context(), id)
			respond(writer, value342, err342)
		}
		return
	}
	if len(parts) == 2 && parts[1] == "diff" && request.Method == http.MethodGet {
		value347, err347 := s.runtime.DiffAsset(request.Context(), id)
		respond(writer, value347, err347)
		return
	}
	if len(parts) == 2 && parts[1] == "adopt" && request.Method == http.MethodPost {
		operation := func(body []byte) (any, error) {
			revision, err := s.runtime.Adopt(request.Context(), id)
			return map[string]string{"revisionId": revision}, err
		}
		if canonical {
			s.mutate(writer, request, "asset.adopt", operation)
		} else {
			value, err := operation(nil)
			respond(writer, value, err)
		}
		return
	}
	writeError(writer, http.StatusNotFound, "not_found", "Asset endpoint not found", nil)
}

func (s *Server) processModel(writer http.ResponseWriter, request *http.Request, tail string) {
	parts := strings.Split(strings.Trim(tail, "/"), "/")
	if len(parts) == 2 && parts[1] == "graph" && request.Method == http.MethodGet {
		value369, err369 := s.runtime.ProcessModelGraph(request.Context(), parts[0], request.URL.Query().Get("mode"))
		respond(writer, value369, err369)
		return
	}
	writeError(writer, http.StatusNotFound, "not_found", "Process Model endpoint not found", nil)
}

func (s *Server) run(writer http.ResponseWriter, request *http.Request, tail string, canonical bool) {
	parts := strings.Split(strings.Trim(tail, "/"), "/")
	id := parts[0]
	if len(parts) == 1 && request.Method == http.MethodGet {
		value379, err379 := s.runtime.RunDetail(request.Context(), id)
		respond(writer, value379, err379)
		return
	}
	if len(parts) == 2 && (parts[1] == "reports" || parts[1] == "report") && request.Method == http.MethodPost {
		var input alpsruntime.ReportRunInput
		handler := func(body []byte) (any, error) {
			if err := json.Unmarshal(body, &input); err != nil {
				return nil, err
			}
			return s.runtime.Report(request.Context(), id, input)
		}
		if canonical {
			s.mutate(writer, request, "run.report", handler)
		} else {
			if !decode(writer, request, &input) {
				return
			}
			value396, err396 := s.runtime.Report(request.Context(), id, input)
			respond(writer, value396, err396)
		}
		return
	}
	if len(parts) == 2 && parts[1] == "completion-requests" && request.Method == http.MethodPost {
		var input struct {
			ExpectedVersion int64 `json:"expectedVersion"`
		}
		mutateJSON(s, writer, request, "run.completion_requested", func(value struct {
			ExpectedVersion int64 `json:"expectedVersion"`
		}) (any, error) {
			return s.runtime.RequestCompletion(request.Context(), id, value.ExpectedVersion)
		}, &input)
		return
	}
	if len(parts) == 2 && parts[1] == "complete" && request.Method == http.MethodPost {
		var input struct {
			ExpectedVersion int64 `json:"expectedVersion"`
		}
		mutateJSON(s, writer, request, "run.complete", func(value struct {
			ExpectedVersion int64 `json:"expectedVersion"`
		}) (any, error) {
			return s.runtime.CompleteRun(request.Context(), id, value.ExpectedVersion)
		}, &input)
		return
	}
	if len(parts) == 2 && parts[1] == "gates" && request.Method == http.MethodPost {
		var input alpsruntime.OpenGateInput
		handler := func(body []byte) (any, error) {
			if err := json.Unmarshal(body, &input); err != nil {
				return nil, err
			}
			return s.runtime.CreateGate(request.Context(), id, input)
		}
		if canonical {
			s.mutate(writer, request, "gate.open", handler)
		} else {
			if !decode(writer, request, &input) {
				return
			}
			value436, err436 := s.runtime.CreateGate(request.Context(), id, input)
			respond(writer, value436, err436)
		}
		return
	}
	if len(parts) == 2 && parts[1] == "artifacts" && request.Method == http.MethodPost {
		var input struct {
			Name           string         `json:"name"`
			MediaType      string         `json:"mediaType"`
			Role           string         `json:"role"`
			ProcessElement string         `json:"processElement"`
			Provenance     map[string]any `json:"provenance"`
			Content        string         `json:"content"`
			Encoding       string         `json:"encoding"`
		}
		handler := func(body []byte) (any, error) {
			if err := json.Unmarshal(body, &input); err != nil {
				return nil, err
			}
			data := []byte(input.Content)
			if input.Encoding == "base64" {
				decoded, err := base64.StdEncoding.DecodeString(input.Content)
				if err != nil {
					return nil, fmt.Errorf("invalid base64: %w", err)
				}
				data = decoded
			}
			return s.runtime.CommitArtifact(request.Context(), id, alpsruntime.ArtifactInput{Name: input.Name, MediaType: input.MediaType, Role: input.Role, ProcessElement: input.ProcessElement, Provenance: input.Provenance, Content: data})
		}
		if canonical {
			s.mutate(writer, request, "artifact.commit", handler)
		} else {
			body, ok := readBody(writer, request)
			if !ok {
				return
			}
			value, err := handler(body)
			if artifact, yes := value.(alpsruntime.Artifact); yes {
				value = map[string]any{"artifactId": artifact.ID, "artifact": artifact}
			}
			respond(writer, value, err)
		}
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
		value500, err500 := s.runtime.RunAuditBundle(request.Context(), id)
		respond(writer, value500, err500)
		return
	}
	writeError(writer, http.StatusNotFound, "not_found", "Run endpoint not found", nil)
}

func (s *Server) gate(writer http.ResponseWriter, request *http.Request, tail string, canonical bool) {
	parts := strings.Split(strings.Trim(tail, "/"), "/")
	if len(parts) == 1 && request.Method == http.MethodGet {
		value509, err509 := s.runtime.Gate(request.Context(), parts[0])
		respond(writer, value509, err509)
		return
	}
	if len(parts) == 2 && parts[1] == "decisions" && request.Method == http.MethodPost {
		var input alpsruntime.DecisionInput
		handler := func(body []byte) (any, error) {
			if err := json.Unmarshal(body, &input); err != nil {
				return nil, err
			}
			return s.runtime.RecordDecision(request.Context(), parts[0], input)
		}
		if canonical {
			s.mutate(writer, request, "decision.record", handler)
		} else {
			if !decode(writer, request, &input) {
				return
			}
			value, err := s.runtime.RecordDecision(request.Context(), parts[0], input)
			respond(writer, map[string]any{"ok": err == nil, "decision": value}, err)
		}
		return
	}
	writeError(writer, http.StatusNotFound, "not_found", "Gate endpoint not found", nil)
}

func (s *Server) handoff(writer http.ResponseWriter, request *http.Request, tail string) {
	parts := strings.Split(strings.Trim(tail, "/"), "/")
	if len(parts) == 1 && request.Method == http.MethodPatch {
		var input struct {
			Status   string               `json:"status"`
			Evidence []domain.EvidenceRef `json:"evidence"`
		}
		mutateJSON(s, writer, request, "handoff.update", func(value struct {
			Status   string               `json:"status"`
			Evidence []domain.EvidenceRef `json:"evidence"`
		}) (any, error) {
			return s.runtime.UpdateHandoff(request.Context(), parts[0], value.Status, value.Evidence)
		}, &input)
		return
	}
	writeError(writer, http.StatusNotFound, "not_found", "Handoff endpoint not found", nil)
}

func (s *Server) analysis(writer http.ResponseWriter, request *http.Request, lens string) {
	parse := func(name string) time.Time {
		value, _ := time.Parse(time.RFC3339, request.URL.Query().Get(name))
		return value
	}
	revisions := request.URL.Query()["revision"]
	value, err := s.runtime.Analyze(request.Context(), lens, parse("from"), parse("to"), revisions)
	respond(writer, value, err)
}

func boardProjection(runs []alpsruntime.Run) map[string]any {
	lanes := map[string][]alpsruntime.Run{"now": {}, "waiting": {}, "done": {}}
	for _, run := range runs {
		switch {
		case run.State == alpsruntime.RunCreated || run.State == alpsruntime.RunActive:
			lanes["now"] = append(lanes["now"], run)
		case strings.HasPrefix(run.State, "waiting_") || run.State == alpsruntime.RunCompletionRequested:
			lanes["waiting"] = append(lanes["waiting"], run)
		default:
			lanes["done"] = append(lanes["done"], run)
		}
	}
	return map[string]any{"lanes": lanes, "generatedAt": time.Now().UTC().Format(time.RFC3339Nano)}
}

func (s *Server) events(writer http.ResponseWriter, request *http.Request) {
	flusher, ok := writer.(http.Flusher)
	if !ok {
		writeError(writer, http.StatusInternalServerError, "streaming_unsupported", "Streaming unsupported", nil)
		return
	}
	writer.Header().Set("Content-Type", "text/event-stream")
	writer.Header().Set("Cache-Control", "no-cache")
	writer.Header().Set("Connection", "keep-alive")
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
		case event, open := <-channel:
			if !open {
				return
			}
			sendEvent(writer, event)
			flusher.Flush()
		case <-ticker.C:
			fmt.Fprint(writer, ": keepalive\n\n")
			flusher.Flush()
		}
	}
}

func sendEvent(writer io.Writer, event domain.Event) {
	content, _ := json.Marshal(event)
	fmt.Fprintf(writer, "id: %d\nevent: %s\ndata: %s\n\n", event.GlobalSequence, event.EventType, content)
}

func (s *Server) mutate(writer http.ResponseWriter, request *http.Request, command string, operation func([]byte) (any, error)) {
	body, ok := readBody(writer, request)
	if !ok {
		return
	}
	key := request.Header.Get("Idempotency-Key")
	result, err := s.runtime.Idempotent(request.Context(), key, command, alpsruntime.RequestDigest(request.Method, request.URL.Path, body), func() (alpsruntime.CommandResult, error) {
		value, err := operation(body)
		if err != nil {
			return alpsruntime.CommandResult{}, err
		}
		encoded, err := json.Marshal(value)
		if err != nil {
			return alpsruntime.CommandResult{}, err
		}
		return alpsruntime.CommandResult{Status: http.StatusOK, Body: encoded}, nil
	})
	if err != nil {
		respond(writer, nil, err)
		return
	}
	writer.Header().Set("Content-Type", "application/json")
	writer.WriteHeader(result.Status)
	_, _ = writer.Write(result.Body)
}

func mutateJSON[T any](s *Server, writer http.ResponseWriter, request *http.Request, command string, operation func(T) (any, error), target ...*T) {
	s.mutate(writer, request, command, func(body []byte) (any, error) {
		var input T
		if len(target) > 0 && target[0] != nil {
			input = *target[0]
		}
		if len(body) > 0 {
			if err := json.Unmarshal(body, &input); err != nil {
				return nil, fmt.Errorf("%w: %v", alpsruntime.ErrInvalid, err)
			}
		}
		return operation(input)
	})
}

func readBody(writer http.ResponseWriter, request *http.Request) ([]byte, bool) {
	request.Body = http.MaxBytesReader(writer, request.Body, 64<<20)
	body, err := io.ReadAll(request.Body)
	if err != nil {
		writeError(writer, http.StatusBadRequest, "invalid_body", err.Error(), nil)
		return nil, false
	}
	if len(body) == 0 {
		body = []byte(`{}`)
	}
	return body, true
}

func decode(writer http.ResponseWriter, request *http.Request, value any) bool {
	body, ok := readBody(writer, request)
	if !ok {
		return false
	}
	if err := json.Unmarshal(body, value); err != nil {
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
		case errors.Is(err, alpsruntime.ErrNotFound), errors.Is(err, fs.ErrNotExist):
			writeError(writer, http.StatusNotFound, "not_found", err.Error(), nil)
		case errors.Is(err, alpsruntime.ErrInvalid):
			writeError(writer, http.StatusBadRequest, "invalid_input", err.Error(), nil)
		case errors.Is(err, alpsruntime.ErrForbidden):
			writeError(writer, http.StatusForbidden, "forbidden", err.Error(), nil)
		case errors.Is(err, alpsruntime.ErrConflict), errors.Is(err, alpsruntime.ErrCompletionBlocked):
			writeError(writer, http.StatusConflict, "conflict", err.Error(), nil)
		default:
			writeError(writer, http.StatusInternalServerError, "internal_error", err.Error(), nil)
		}
		return
	}
	writeJSON(writer, http.StatusOK, value)
}

func writeJSON(writer http.ResponseWriter, status int, value any) {
	writer.Header().Set("Content-Type", "application/json; charset=utf-8")
	writer.WriteHeader(status)
	_ = json.NewEncoder(writer).Encode(value)
}

func writeError(writer http.ResponseWriter, status int, code, message string, details any) {
	writeJSON(writer, status, map[string]any{"error": map[string]any{"code": code, "message": message, "details": details}})
}
