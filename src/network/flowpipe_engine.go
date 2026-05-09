// ===========================================================================
// OMNI NETWORK LAYER — FLOWPIPE WORKFLOW ENGINE
// ===========================================================================
// Source Repo   : github.com/turbot/flowpipe
// Domain Layer  : Network (Cloud scripting, workflow automation)
// Language      : Go
// Function      : Cloud workflow engine — HCL-like pipeline definitions,
//                 typed steps (HTTP/transform/query/input/message/pipeline),
//                 triggers (webhook/schedule/query), step dependency DAG,
//                 execution with retry/error handling, and mod registry
// ===========================================================================

package network

import (
	"fmt"
	"strings"
	"sync"
	"time"
)

// ---- Step Types -----------------------------------------------------------

type StepType int

const (
	StepHTTP StepType = iota
	StepTransform
	StepQuery
	StepInput
	StepMessage
	StepPipeline
	StepFunction
)

func (s StepType) String() string {
	return [...]string{"http", "transform", "query", "input", "message", "pipeline", "function"}[s]
}

// ---- Trigger Types --------------------------------------------------------

type TriggerType int

const (
	TriggerWebhook TriggerType = iota
	TriggerSchedule
	TriggerQuery
)

func (t TriggerType) String() string {
	return [...]string{"webhook", "schedule", "query"}[t]
}

// ---- Pipeline Step --------------------------------------------------------

type PipelineStep struct {
	Name      string
	Type      StepType
	Config    map[string]interface{}
	DependsOn []string
	ErrorMode string // "ignore" or "fail" (default)
	RetryMax  int
	Outputs   map[string]interface{}
	Completed bool
	Failed    bool
	Duration  time.Duration
}

func (ps *PipelineStep) Execute() error {
	start := time.Now()
	defer func() { ps.Duration = time.Since(start) }()

	fmt.Printf("  [%s.%s] Starting %s\n", ps.Name, ps.Type, ps.Type)

	switch ps.Type {
	case StepHTTP:
		return ps.execHTTP()
	case StepTransform:
		return ps.execTransform()
	case StepQuery:
		return ps.execQuery()
	case StepInput:
		return ps.execInput()
	case StepMessage:
		return ps.execMessage()
	case StepPipeline:
		return ps.execSubPipeline()
	case StepFunction:
		return ps.execFunction()
	}
	return fmt.Errorf("unknown step type: %d", ps.Type)
}

func (ps *PipelineStep) execHTTP() error {
	url, _ := ps.Config["url"].(string)
	method, _ := ps.Config["method"].(string)
	if method == "" {
		method = "GET"
	}
	if url == "" {
		return fmt.Errorf("http step requires 'url'")
	}

	// Real: net/http request. Here we record the intent.
	ps.Outputs = map[string]interface{}{
		"status_code": 200,
		"url":         url,
		"method":      method,
	}
	fmt.Printf("  [%s] %s %s -> 200\n", ps.Name, method, url)
	return nil
}

func (ps *PipelineStep) execTransform() error {
	// Evaluate expressions and produce outputs
	for k, v := range ps.Config {
		ps.Outputs[k] = v
	}
	for k, v := range ps.Outputs {
		fmt.Printf("  [%s] Output %s = %v\n", ps.Name, k, v)
	}
	return nil
}

func (ps *PipelineStep) execQuery() error {
	sql, _ := ps.Config["sql"].(string)
	if sql == "" {
		return fmt.Errorf("query step requires 'sql'")
	}
	ps.Outputs = map[string]interface{}{"rows": []interface{}{}, "sql": sql}
	fmt.Printf("  [%s] Query: %s\n", ps.Name, sql[:min(60, len(sql))])
	return nil
}

func (ps *PipelineStep) execInput() error {
	prompt, _ := ps.Config["prompt"].(string)
	fmt.Printf("  [%s] Awaiting human input: %s\n", ps.Name, prompt)
	// In real Flowpipe, this pauses execution and waits for user response
	ps.Outputs = map[string]interface{}{"response": "(pending)"}
	return nil
}

func (ps *PipelineStep) execMessage() error {
	channel, _ := ps.Config["channel"].(string)
	text, _ := ps.Config["text"].(string)
	fmt.Printf("  [%s] Message to %s: %s\n", ps.Name, channel, text[:min(50, len(text))])
	ps.Outputs = map[string]interface{}{"sent": true, "channel": channel}
	return nil
}

func (ps *PipelineStep) execSubPipeline() error {
	pipeline, _ := ps.Config["pipeline"].(string)
	fmt.Printf("  [%s] Running sub-pipeline: %s\n", ps.Name, pipeline)
	ps.Outputs = map[string]interface{}{"pipeline": pipeline, "status": "complete"}
	return nil
}

func (ps *PipelineStep) execFunction() error {
	fn, _ := ps.Config["function"].(string)
	fmt.Printf("  [%s] Executing function: %s\n", ps.Name, fn)
	ps.Outputs = map[string]interface{}{"function": fn, "result": "ok"}
	return nil
}

// ---- Trigger --------------------------------------------------------------

type Trigger struct {
	Name         string
	Type         TriggerType
	PipelineName string
	Config       map[string]string // schedule: cron expr; webhook: path; query: sql
}

func (t *Trigger) ShouldFire(event string) bool {
	switch t.Type {
	case TriggerWebhook:
		return event == t.Config["path"]
	case TriggerSchedule:
		// Real: check cron expression against current time
		return false
	case TriggerQuery:
		// Real: execute query and check for new rows
		return false
	}
	return false
}

// ---- Pipeline Definition --------------------------------------------------

type Pipeline struct {
	Name        string
	Description string
	ModName     string
	Steps       []*PipelineStep
	Triggers    []Trigger
	Outputs     map[string]interface{}
}

// ---- Flowpipe Execution Engine --------------------------------------------

type FlowpipeEngine struct {
	mu        sync.RWMutex
	pipelines map[string]*Pipeline
	mods      map[string][]string // mod name -> pipeline names
	execCount uint64
}

func NewFlowpipeEngine() *FlowpipeEngine {
	fmt.Println("[FLOWPIPE-OMNI-GO] Workflow engine initialized.")
	return &FlowpipeEngine{
		pipelines: make(map[string]*Pipeline),
		mods:      make(map[string][]string),
	}
}

func (fe *FlowpipeEngine) RegisterPipeline(p *Pipeline) {
	fe.mu.Lock()
	defer fe.mu.Unlock()
	key := fmt.Sprintf("%s.%s", p.ModName, p.Name)
	fe.pipelines[key] = p
	fe.mods[p.ModName] = append(fe.mods[p.ModName], p.Name)
	fmt.Printf("[FLOWPIPE-OMNI-GO] Pipeline registered: %s (%d steps, %d triggers)\n",
		key, len(p.Steps), len(p.Triggers))
}

func (fe *FlowpipeEngine) ListPipelines() []string {
	fe.mu.RLock()
	defer fe.mu.RUnlock()
	names := make([]string, 0, len(fe.pipelines))
	for k := range fe.pipelines {
		names = append(names, k)
	}
	return names
}

func (fe *FlowpipeEngine) Run(pipelineKey string) (*ExecutionResult, error) {
	fe.mu.Lock()
	fe.execCount++
	execID := fmt.Sprintf("exec_%d_%d", time.Now().UnixMilli(), fe.execCount)
	fe.mu.Unlock()

	fe.mu.RLock()
	p, ok := fe.pipelines[pipelineKey]
	fe.mu.RUnlock()
	if !ok {
		return nil, fmt.Errorf("pipeline %s not found", pipelineKey)
	}

	fmt.Printf("\n[FLOWPIPE-OMNI-GO] Execution ID: %s\n", execID)
	fmt.Printf("[%s] Starting pipeline\n", p.Name)
	start := time.Now()

	// Build dependency graph and execute in order
	completed := make(map[string]bool)
	stepOutputs := make(map[string]map[string]interface{})
	var stepResults []StepResult

	for _, step := range p.Steps {
		// Check dependencies
		for _, dep := range step.DependsOn {
			if !completed[dep] {
				return nil, fmt.Errorf("dependency %s not satisfied for step %s", dep, step.Name)
			}
		}

		// Initialize outputs map
		if step.Outputs == nil {
			step.Outputs = make(map[string]interface{})
		}

		// Execute with retry
		var lastErr error
		attempts := max(1, step.RetryMax+1)
		for attempt := 1; attempt <= attempts; attempt++ {
			lastErr = step.Execute()
			if lastErr == nil {
				break
			}
			if attempt < attempts {
				fmt.Printf("  [%s] Retry %d/%d...\n", step.Name, attempt, step.RetryMax)
			}
		}

		sr := StepResult{
			Name:     step.Name,
			Type:     step.Type.String(),
			Duration: step.Duration,
		}

		if lastErr != nil {
			step.Failed = true
			sr.Error = lastErr.Error()
			if step.ErrorMode == "ignore" {
				fmt.Printf("  [%s] FAILED (ignored): %s\n", step.Name, lastErr)
			} else {
				fmt.Printf("  [%s] FAILED: %s\n", step.Name, lastErr)
				sr.Success = false
				stepResults = append(stepResults, sr)
				return &ExecutionResult{
					ID:       execID,
					Pipeline: pipelineKey,
					Steps:    stepResults,
					Duration: time.Since(start),
					Success:  false,
					Error:    lastErr.Error(),
				}, nil
			}
		} else {
			step.Completed = true
			completed[step.Name] = true
			stepOutputs[step.Name] = step.Outputs
			sr.Success = true
			sr.Outputs = step.Outputs
		}

		stepResults = append(stepResults, sr)
		fmt.Printf("  [%s] Complete %dms\n", step.Name, step.Duration.Milliseconds())
	}

	totalDuration := time.Since(start)
	fmt.Printf("[%s] Complete %dms\n", p.Name, totalDuration.Milliseconds())
	fmt.Printf("%s\n", execID)

	return &ExecutionResult{
		ID:       execID,
		Pipeline: pipelineKey,
		Steps:    stepResults,
		Duration: totalDuration,
		Success:  true,
		Outputs:  stepOutputs,
	}, nil
}

// HandleWebhook checks all triggers and fires matching pipelines.
func (fe *FlowpipeEngine) HandleWebhook(path string) []string {
	fe.mu.RLock()
	defer fe.mu.RUnlock()

	var fired []string
	for key, p := range fe.pipelines {
		for _, t := range p.Triggers {
			if t.Type == TriggerWebhook && t.ShouldFire(path) {
				fmt.Printf("[FLOWPIPE-OMNI-GO] Webhook trigger: %s -> %s\n", path, key)
				fired = append(fired, key)
				go fe.Run(key)
			}
		}
	}
	return fired
}

// ---- Execution Result -----------------------------------------------------

type StepResult struct {
	Name     string
	Type     string
	Success  bool
	Duration time.Duration
	Outputs  map[string]interface{}
	Error    string
}

type ExecutionResult struct {
	ID       string
	Pipeline string
	Steps    []StepResult
	Duration time.Duration
	Success  bool
	Outputs  map[string]map[string]interface{}
	Error    string
}

func (er *ExecutionResult) String() string {
	status := "SUCCESS"
	if !er.Success {
		status = "FAILED"
	}
	return fmt.Sprintf("Execution[%s] %s: %s (%d steps, %dms)",
		er.ID, er.Pipeline, status, len(er.Steps), er.Duration.Milliseconds())
}

// ---- Mod Registry ---------------------------------------------------------

type FlowpipeMod struct {
	Name        string
	Description string
	Version     string
	Pipelines   []string
}

var BuiltInMods = []FlowpipeMod{
	{Name: "aws", Description: "AWS automation pipelines", Version: "0.8.0"},
	{Name: "azure", Description: "Azure automation pipelines", Version: "0.6.0"},
	{Name: "gcp", Description: "GCP automation pipelines", Version: "0.5.0"},
	{Name: "github", Description: "GitHub automation pipelines", Version: "0.4.0"},
	{Name: "jira", Description: "Jira automation pipelines", Version: "0.3.0"},
	{Name: "slack", Description: "Slack messaging pipelines", Version: "0.5.0"},
	{Name: "pagerduty", Description: "PagerDuty incident pipelines", Version: "0.2.0"},
	{Name: "okta", Description: "Okta identity pipelines", Version: "0.3.0"},
	{Name: "sendgrid", Description: "SendGrid email pipelines", Version: "0.2.0"},
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// ---- Convenience Builder (Fluent API) -------------------------------------

func NewHTTPStep(name, method, url string) *PipelineStep {
	return &PipelineStep{
		Name:   name,
		Type:   StepHTTP,
		Config: map[string]interface{}{"method": strings.ToUpper(method), "url": url},
	}
}

func NewTransformStep(name string, exprs map[string]interface{}) *PipelineStep {
	return &PipelineStep{
		Name:   name,
		Type:   StepTransform,
		Config: exprs,
	}
}

func NewQueryStep(name, sql string) *PipelineStep {
	return &PipelineStep{
		Name:   name,
		Type:   StepQuery,
		Config: map[string]interface{}{"sql": sql},
	}
}

func NewMessageStep(name, channel, text string) *PipelineStep {
	return &PipelineStep{
		Name:   name,
		Type:   StepMessage,
		Config: map[string]interface{}{"channel": channel, "text": text},
	}
}
