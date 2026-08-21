package runtime

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"math"
	"sort"
	"time"
)

type AnalysisSummary struct {
	Active    int    `json:"active"`
	Waiting   int    `json:"waiting"`
	Completed int    `json:"completed"`
	Assets    int    `json:"assets"`
	Gates     int    `json:"gates"`
	Tokens    *int64 `json:"tokens"`
}

type AnalysisMetric struct {
	ID         string `json:"id"`
	Label      string `json:"label"`
	Value      any    `json:"value"`
	Unit       string `json:"unit,omitempty"`
	Definition string `json:"definition"`
	Coverage   string `json:"coverage"`
}

type AnalysisPoint struct {
	At    string  `json:"at"`
	Value float64 `json:"value"`
}

type AnalysisSeries struct {
	ID     string          `json:"id"`
	Label  string          `json:"label"`
	Unit   string          `json:"unit,omitempty"`
	Points []AnalysisPoint `json:"points"`
}

type AnalysisFinding struct {
	ID          string `json:"id"`
	Severity    string `json:"severity"`
	Title       string `json:"title"`
	Detail      string `json:"detail"`
	SubjectType string `json:"subjectType,omitempty"`
	SubjectID   string `json:"subjectId,omitempty"`
}

type AnalysisLens struct {
	Lens            string            `json:"lens"`
	Definition      string            `json:"definition"`
	Period          map[string]string `json:"period"`
	Population      string            `json:"population"`
	RevisionFilters []string          `json:"revisionFilters"`
	DataSource      []string          `json:"dataSource"`
	Coverage        string            `json:"coverage"`
	Aggregation     string            `json:"aggregation"`
	MappingRevision string            `json:"mappingRevision"`
	Metrics         []AnalysisMetric  `json:"metrics"`
	Series          []AnalysisSeries  `json:"series"`
	Findings        []AnalysisFinding `json:"findings"`
}

func (r *Runtime) Analysis(ctx context.Context) (AnalysisSummary, error) {
	var result AnalysisSummary
	if err := r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM assets WHERE source_state!='missing'`).Scan(&result.Assets); err != nil {
		return AnalysisSummary{}, err
	}
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM runs WHERE state IN ('created','active')`).Scan(&result.Active)
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM runs WHERE state LIKE 'waiting_%' OR state='completion_requested'`).Scan(&result.Waiting)
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM runs WHERE state='completed'`).Scan(&result.Completed)
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM decision_gates WHERE status='open'`).Scan(&result.Gates)
	var tokenTotal sql.NullInt64
	_ = r.db.QueryRowContext(ctx, `SELECT SUM(COALESCE(input_tokens,0)+COALESCE(output_tokens,0)) FROM usage_observations WHERE status IN ('reported','derived')`).Scan(&tokenTotal)
	if tokenTotal.Valid {
		value := tokenTotal.Int64
		result.Tokens = &value
	}
	return result, nil
}

func (r *Runtime) Analyze(ctx context.Context, lens string, since, until time.Time, revisions []string) (AnalysisLens, error) {
	if until.IsZero() {
		until = time.Now().UTC()
	}
	if since.IsZero() {
		since = until.Add(-30 * 24 * time.Hour)
	}
	base := AnalysisLens{
		Lens:            lens,
		Period:          map[string]string{"from": since.Format(time.RFC3339), "to": until.Format(time.RFC3339)},
		Population:      "Runs whose relevant event or observation falls within the selected period",
		RevisionFilters: append([]string(nil), revisions...),
		Coverage:        "complete for locally recorded fields; external Host observations may be partial",
		MappingRevision: "alps-analysis/1",
	}
	var err error
	switch lens {
	case "flow":
		base.Definition = "Operational flow of Run instances across active, waiting, and terminal states."
		base.DataSource = []string{"runs", "run_state_intervals", "domain_events"}
		base.Aggregation = "Run count and elapsed time by state interval"
		err = r.flowAnalysis(ctx, &base, since, until)
	case "quality":
		base.Definition = "Assessed Outcomes, accepted Handoffs, and recorded rework decisions."
		base.DataSource = []string{"run_outcomes", "assessments", "handoffs", "decisions"}
		base.Aggregation = "Assessed subjects only; unassessed Outcomes are excluded from the rate denominator"
		err = r.qualityAnalysis(ctx, &base, since, until)
	case "oversight":
		base.Definition = "Human Decision Gate volume, wait time, and Decision distribution."
		base.DataSource = []string{"decision_gates", "decisions"}
		base.Aggregation = "Gate and Decision records created in the period"
		err = r.oversightAnalysis(ctx, &base, since, until)
	case "usage":
		base.Definition = "Model invocation and usage observations grouped only when accounting semantics are compatible."
		base.DataSource = []string{"model_invocations", "usage_observations", "cost_observations"}
		base.Aggregation = "Reported and derived observations are separated from estimated and unavailable observations"
		err = r.usageAnalysis(ctx, &base, since, until)
	default:
		return AnalysisLens{}, fmt.Errorf("%w: analysis lens must be flow, quality, oversight, or usage", ErrInvalid)
	}
	return base, err
}

func (r *Runtime) flowAnalysis(ctx context.Context, result *AnalysisLens, since, until time.Time) error {
	var wip, throughput int
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM runs WHERE state NOT IN ('completed','failed','cancelled')`).Scan(&wip)
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM runs WHERE completed_at>=? AND completed_at<?`, since.Format(time.RFC3339Nano), until.Format(time.RFC3339Nano)).Scan(&throughput)
	cycle, cycleCount := r.averageDuration(ctx, `SELECT created_at,completed_at FROM runs WHERE completed_at IS NOT NULL AND completed_at!='' AND completed_at>=? AND completed_at<?`, since, until)
	waiting, waitingCount := r.waitingDuration(ctx, since, until)
	result.Metrics = []AnalysisMetric{
		{ID: "wip", Label: "Work in progress", Value: wip, Unit: "runs", Definition: "Non-terminal Runs at query time", Coverage: "complete"},
		{ID: "throughput", Label: "Throughput", Value: throughput, Unit: "runs", Definition: "Runs completed in the selected period", Coverage: "complete"},
		{ID: "cycle-time", Label: "Median cycle proxy", Value: nullableFloat(cycle, cycleCount), Unit: "seconds", Definition: "Average completed_at minus created_at for completed Runs", Coverage: coverageCount(cycleCount)},
		{ID: "waiting-time", Label: "Waiting time", Value: nullableFloat(waiting, waitingCount), Unit: "seconds", Definition: "Average duration of waiting state intervals", Coverage: coverageCount(waitingCount)},
	}
	result.Series = []AnalysisSeries{r.dailyRunSeries(ctx, since, until)}
	if waitingCount > 0 && waiting > 3600 {
		result.Findings = append(result.Findings, AnalysisFinding{ID: "long-wait", Severity: "warning", Title: "Runs are waiting for extended periods", Detail: "Average recorded waiting time exceeds one hour."})
	}
	return nil
}

func (r *Runtime) qualityAnalysis(ctx context.Context, result *AnalysisLens, since, until time.Time) error {
	var assessed, achieved, handoffDecided, handoffAccepted, rework, runCount int
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM run_outcomes WHERE status IN ('assessed_achieved','not_achieved')`).Scan(&assessed)
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM run_outcomes WHERE status='assessed_achieved'`).Scan(&achieved)
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM handoffs WHERE status IN ('accepted','rejected')`).Scan(&handoffDecided)
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM handoffs WHERE status='accepted'`).Scan(&handoffAccepted)
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(DISTINCT g.run_id) FROM decisions d JOIN decision_gates g ON g.id=d.gate_id WHERE d.decision_type IN ('change','re-execute')`).Scan(&rework)
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM runs`).Scan(&runCount)
	result.Metrics = []AnalysisMetric{
		{ID: "outcome-rate", Label: "Outcome achievement", Value: rate(achieved, assessed), Unit: "ratio", Definition: "Assessed achieved Outcomes divided by assessed Outcomes", Coverage: coverageCount(assessed)},
		{ID: "handoff-acceptance", Label: "Handoff acceptance", Value: rate(handoffAccepted, handoffDecided), Unit: "ratio", Definition: "Accepted Handoffs divided by decided Handoffs", Coverage: coverageCount(handoffDecided)},
		{ID: "rework-rate", Label: "Rework", Value: rate(rework, runCount), Unit: "ratio", Definition: "Runs with change or re-execute Decisions divided by Runs", Coverage: coverageCount(runCount)},
	}
	if assessed == 0 {
		result.Findings = append(result.Findings, AnalysisFinding{ID: "no-assessment", Severity: "info", Title: "No Outcomes have been assessed", Detail: "Agent reports do not count as assessed achievement."})
	}
	return nil
}

func (r *Runtime) oversightAnalysis(ctx context.Context, result *AnalysisLens, since, until time.Time) error {
	var open, decided int
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM decision_gates WHERE status='open'`).Scan(&open)
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM decision_gates WHERE status='decided' AND decided_at>=? AND decided_at<?`, since.Format(time.RFC3339Nano), until.Format(time.RFC3339Nano)).Scan(&decided)
	wait, waitCount := r.averageDuration(ctx, `SELECT created_at,decided_at FROM decision_gates WHERE decided_at IS NOT NULL AND decided_at!='' AND decided_at>=? AND decided_at<?`, since, until)
	distribution := map[string]int{}
	rows, err := r.db.QueryContext(ctx, `SELECT decision_type,COUNT(*) FROM decisions WHERE created_at>=? AND created_at<? GROUP BY decision_type`, since.Format(time.RFC3339Nano), until.Format(time.RFC3339Nano))
	if err == nil {
		for rows.Next() {
			var decision string
			var count int
			if rows.Scan(&decision, &count) == nil {
				distribution[decision] = count
			}
		}
		_ = rows.Close()
	}
	result.Metrics = []AnalysisMetric{
		{ID: "open-gates", Label: "Open gates", Value: open, Unit: "gates", Definition: "Decision Gates currently open", Coverage: "complete"},
		{ID: "decided-gates", Label: "Decided gates", Value: decided, Unit: "gates", Definition: "Decision Gates decided in the selected period", Coverage: "complete"},
		{ID: "gate-wait", Label: "Gate wait", Value: nullableFloat(wait, waitCount), Unit: "seconds", Definition: "Average final decision time minus Gate open time", Coverage: coverageCount(waitCount)},
		{ID: "decision-distribution", Label: "Decisions", Value: distribution, Definition: "Decision type counts in the selected period", Coverage: "complete"},
	}
	if open > 0 {
		result.Findings = append(result.Findings, AnalysisFinding{ID: "open-attention", Severity: "warning", Title: "Human attention is required", Detail: fmt.Sprintf("%d Decision Gate(s) remain open.", open)})
	}
	return nil
}

func (r *Runtime) usageAnalysis(ctx context.Context, result *AnalysisLens, since, until time.Time) error {
	var invocations, reported, unavailable int
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM model_invocations WHERE created_at>=? AND created_at<?`, since.Format(time.RFC3339Nano), until.Format(time.RFC3339Nano)).Scan(&invocations)
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM usage_observations WHERE status IN ('reported','derived') AND COALESCE(observed_at,created_at)>=? AND COALESCE(observed_at,created_at)<?`, since.Format(time.RFC3339Nano), until.Format(time.RFC3339Nano)).Scan(&reported)
	_ = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM usage_observations WHERE status='unavailable' AND COALESCE(observed_at,created_at)>=? AND COALESCE(observed_at,created_at)<?`, since.Format(time.RFC3339Nano), until.Format(time.RFC3339Nano)).Scan(&unavailable)
	totals := map[string]any{}
	rows, err := r.db.QueryContext(ctx, `SELECT COALESCE(accounting_basis,''),SUM(input_tokens),SUM(output_tokens),SUM(cache_read_tokens),SUM(cache_write_tokens),SUM(reasoning_tokens),COUNT(*) FROM usage_observations WHERE status IN ('reported','derived') AND COALESCE(observed_at,created_at)>=? AND COALESCE(observed_at,created_at)<? GROUP BY COALESCE(accounting_basis,'')`, since.Format(time.RFC3339Nano), until.Format(time.RFC3339Nano))
	if err == nil {
		for rows.Next() {
			var basis string
			var input, output, cacheRead, cacheCreation, reasoning sql.NullInt64
			var count int
			if rows.Scan(&basis, &input, &output, &cacheRead, &cacheCreation, &reasoning, &count) == nil {
				key := basis
				if key == "" {
					key = "unspecified"
				}
				totals[key] = map[string]any{"input": nullInt(input), "output": nullInt(output), "cacheRead": nullInt(cacheRead), "cacheCreation": nullInt(cacheCreation), "reasoning": nullInt(reasoning), "observations": count}
			}
		}
		_ = rows.Close()
	}
	result.Metrics = []AnalysisMetric{
		{ID: "invocations", Label: "Model invocations", Value: invocations, Unit: "invocations", Definition: "Model Invocation records in the selected period", Coverage: "complete for Runtime-reported invocations"},
		{ID: "usage-coverage", Label: "Usage coverage", Value: rate(reported, invocations), Unit: "ratio", Definition: "Invocations with reported or derived Usage divided by recorded invocations", Coverage: coverageCount(invocations)},
		{ID: "token-totals", Label: "Token observations", Value: totals, Definition: "Token totals partitioned by accounting basis; incompatible bases are not combined", Coverage: coverageCount(reported)},
		{ID: "unavailable", Label: "Unavailable usage", Value: unavailable, Unit: "observations", Definition: "Explicitly unavailable Usage observations", Coverage: "complete"},
	}
	if invocations > reported {
		result.Findings = append(result.Findings, AnalysisFinding{ID: "usage-gap", Severity: "info", Title: "Usage coverage is incomplete", Detail: "Some recorded model invocations do not have reported or derived Usage observations."})
	}
	return nil
}

func (r *Runtime) averageDuration(ctx context.Context, query string, since, until time.Time) (float64, int) {
	rows, err := r.db.QueryContext(ctx, query, since.Format(time.RFC3339Nano), until.Format(time.RFC3339Nano))
	if err != nil {
		return 0, 0
	}
	defer rows.Close()
	var total float64
	var count int
	for rows.Next() {
		var startRaw, endRaw string
		if rows.Scan(&startRaw, &endRaw) != nil {
			continue
		}
		start, err1 := time.Parse(time.RFC3339Nano, startRaw)
		end, err2 := time.Parse(time.RFC3339Nano, endRaw)
		if err1 == nil && err2 == nil && !end.Before(start) {
			total += end.Sub(start).Seconds()
			count++
		}
	}
	if count == 0 {
		return 0, 0
	}
	return total / float64(count), count
}

func (r *Runtime) waitingDuration(ctx context.Context, since, until time.Time) (float64, int) {
	rows, err := r.db.QueryContext(ctx, `SELECT started_at,COALESCE(ended_at,?) FROM run_state_intervals WHERE state LIKE 'waiting_%' AND started_at<? AND COALESCE(ended_at,?)>=?`, until.Format(time.RFC3339Nano), until.Format(time.RFC3339Nano), until.Format(time.RFC3339Nano), since.Format(time.RFC3339Nano))
	if err != nil {
		return 0, 0
	}
	defer rows.Close()
	var total float64
	var count int
	for rows.Next() {
		var startRaw, endRaw string
		if rows.Scan(&startRaw, &endRaw) != nil {
			continue
		}
		start, err1 := time.Parse(time.RFC3339Nano, startRaw)
		end, err2 := time.Parse(time.RFC3339Nano, endRaw)
		if err1 == nil && err2 == nil && !end.Before(start) {
			total += end.Sub(start).Seconds()
			count++
		}
	}
	if count == 0 {
		return 0, 0
	}
	return total / float64(count), count
}

func (r *Runtime) dailyRunSeries(ctx context.Context, since, until time.Time) AnalysisSeries {
	series := AnalysisSeries{ID: "completed-runs", Label: "Completed Runs", Unit: "runs"}
	rows, err := r.db.QueryContext(ctx, `SELECT substr(completed_at,1,10),COUNT(*) FROM runs WHERE completed_at>=? AND completed_at<? GROUP BY substr(completed_at,1,10) ORDER BY substr(completed_at,1,10)`, since.Format(time.RFC3339Nano), until.Format(time.RFC3339Nano))
	if err != nil {
		return series
	}
	defer rows.Close()
	for rows.Next() {
		var day string
		var count float64
		if rows.Scan(&day, &count) == nil {
			series.Points = append(series.Points, AnalysisPoint{At: day, Value: count})
		}
	}
	return series
}

func rate(numerator, denominator int) any {
	if denominator == 0 {
		return nil
	}
	return math.Round((float64(numerator)/float64(denominator))*10000) / 10000
}

func coverageCount(count int) string {
	if count == 0 {
		return "unavailable"
	}
	return fmt.Sprintf("%d observed subject(s)", count)
}

func nullableFloat(value float64, count int) any {
	if count == 0 {
		return nil
	}
	return math.Round(value*100) / 100
}

func nullInt(value sql.NullInt64) any {
	if !value.Valid {
		return nil
	}
	return value.Int64
}

func SortFindings(findings []AnalysisFinding) {
	order := map[string]int{"error": 0, "warning": 1, "info": 2}
	sort.SliceStable(findings, func(i, j int) bool { return order[findings[i].Severity] < order[findings[j].Severity] })
}

func MarshalAnalysis(value AnalysisLens) json.RawMessage {
	encoded, _ := json.Marshal(value)
	return encoded
}
