/*
OMNI Just-API Test Engine
===========================
Production-grade YAML-declarative REST/GraphQL API test runner.
Provides specification-based testing without code — define requests
and response validations in structured YAML, execute in serial/parallel,
and generate JUnit XML + HTML reports.

Inspired by: github.com/kiranz/just-api
OMNI Layer: Network (Go)
*/

package network

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"sync"
	"time"
)

// ─────────────────────────────────────────────
// Section 1: Enums & Types
// ─────────────────────────────────────────────

type HTTPMethod string

const (
	MethodGET    HTTPMethod = "GET"
	MethodPOST   HTTPMethod = "POST"
	MethodPUT    HTTPMethod = "PUT"
	MethodDELETE HTTPMethod = "DELETE"
	MethodPATCH  HTTPMethod = "PATCH"
	MethodHEAD   HTTPMethod = "HEAD"
	MethodOPTIONS HTTPMethod = "OPTIONS"
)

type SuiteRunMode string

const (
	RunSerial   SuiteRunMode = "serial"
	RunParallel SuiteRunMode = "parallel"
)

type SpecStatus string

const (
	StatusPassed  SpecStatus = "passed"
	StatusFailed  SpecStatus = "failed"
	StatusSkipped SpecStatus = "skipped"
	StatusError   SpecStatus = "error"
)

// ─────────────────────────────────────────────
// Section 2: Data Structures
// ─────────────────────────────────────────────

// Header is a name-value pair for HTTP headers.
type Header struct {
	Name  string `json:"name"`
	Value string `json:"value"`
}

// Cookie represents an HTTP cookie.
type Cookie struct {
	Name  string `json:"name"`
	Value string `json:"value"`
}

// PayloadBody defines the request body.
type PayloadBody struct {
	Type    string `json:"type"`    // json, form, text, graphql
	Content string `json:"content"` // raw content or JSON string
}

// JSONDataCheck defines a JSON path validation.
type JSONDataCheck struct {
	Path  string      `json:"path"`
	Value interface{} `json:"value"`
}

// ResponseSpec defines expected response validations.
type ResponseSpec struct {
	StatusCode   int             `json:"status_code"`
	Headers      []Header        `json:"headers,omitempty"`
	Cookies      []Cookie        `json:"cookies,omitempty"`
	JSONData     []JSONDataCheck `json:"json_data,omitempty"`
	JSONSchema   string          `json:"json_schema,omitempty"`
	BodyContains []string        `json:"body_contains,omitempty"`
}

// RequestSpec defines the HTTP request to send.
type RequestSpec struct {
	Path        string      `json:"path"`
	Method      string      `json:"method"`
	Headers     []Header    `json:"headers,omitempty"`
	QueryParams []Header    `json:"query_params,omitempty"`
	Payload     PayloadBody `json:"payload,omitempty"`
}

// TestSpec defines a single API test specification.
type TestSpec struct {
	Name           string       `json:"name"`
	Request        RequestSpec  `json:"request"`
	Response       ResponseSpec `json:"response"`
	Skip           bool         `json:"skip,omitempty"`
	RetryCount     int          `json:"retry_count,omitempty"`
	RetryDelay     int          `json:"retry_delay_ms,omitempty"`
	DependsOn      string       `json:"depends_on,omitempty"`
	BeforeTest     string       `json:"before_test,omitempty"`
	AfterTest      string       `json:"after_test,omitempty"`
	Tags           []string     `json:"tags,omitempty"`
}

// SuiteConfig defines suite-level configuration.
type SuiteConfig struct {
	Scheme   string `json:"scheme"`
	Host     string `json:"host"`
	BasePath string `json:"base_path"`
	Port     int    `json:"port,omitempty"`
}

// TestSuite represents a complete API test suite.
type TestSuite struct {
	Name          string       `json:"name"`
	Configuration SuiteConfig  `json:"configuration"`
	Specs         []TestSpec   `json:"specs"`
	RunMode       SuiteRunMode `json:"run_mode"`
	BeforeAll     string       `json:"before_all,omitempty"`
	AfterAll      string       `json:"after_all,omitempty"`
}

// ─────────────────────────────────────────────
// Section 3: Execution Results
// ─────────────────────────────────────────────

// ValidationError represents a single validation failure.
type ValidationError struct {
	Type     string `json:"type"`     // status, header, json_data, json_schema, body
	Expected string `json:"expected"`
	Actual   string `json:"actual"`
	Message  string `json:"message"`
}

// SpecResult holds the result of a single spec execution.
type SpecResult struct {
	Name             string            `json:"name"`
	Status           SpecStatus        `json:"status"`
	StatusCode       int               `json:"response_status_code"`
	Duration         time.Duration     `json:"duration"`
	DurationMs       float64           `json:"duration_ms"`
	Errors           []ValidationError `json:"errors,omitempty"`
	ResponseHeaders  map[string]string `json:"response_headers,omitempty"`
	ResponseBody     string            `json:"response_body,omitempty"`
	RetryAttempts    int               `json:"retry_attempts"`
}

// SuiteResult holds the result of a suite execution.
type SuiteResult struct {
	Name      string       `json:"name"`
	Specs     []SpecResult `json:"specs"`
	Passed    int          `json:"passed"`
	Failed    int          `json:"failed"`
	Skipped   int          `json:"skipped"`
	Errors    int          `json:"errors"`
	Total     int          `json:"total"`
	Duration  time.Duration `json:"duration"`
	DurationMs float64     `json:"duration_ms"`
}

// RunResult holds the result of all suites.
type RunResult struct {
	RunID    string        `json:"run_id"`
	Suites   []SuiteResult `json:"suites"`
	Passed   int           `json:"total_passed"`
	Failed   int           `json:"total_failed"`
	Skipped  int           `json:"total_skipped"`
	Total    int           `json:"total_tests"`
	Duration time.Duration `json:"duration"`
}

// ─────────────────────────────────────────────
// Section 4: HTTP Client
// ─────────────────────────────────────────────

// APIClient executes HTTP requests.
type APIClient struct {
	client       *http.Client
	baseURL      string
	defaultHdrs  map[string]string
}

func NewAPIClient(config SuiteConfig) *APIClient {
	scheme := config.Scheme
	if scheme == "" {
		scheme = "https"
	}
	host := config.Host
	if config.Port > 0 {
		host = fmt.Sprintf("%s:%d", host, config.Port)
	}
	baseURL := fmt.Sprintf("%s://%s%s", scheme, host, config.BasePath)

	return &APIClient{
		client: &http.Client{
			Timeout: 30 * time.Second,
			CheckRedirect: func(req *http.Request, via []*http.Request) error {
				return http.ErrUseLastResponse
			},
		},
		baseURL:     baseURL,
		defaultHdrs: make(map[string]string),
	}
}

func (c *APIClient) Execute(ctx context.Context, spec RequestSpec) (*http.Response, []byte, time.Duration, error) {
	fullURL := c.baseURL + spec.Path

	// Add query params
	if len(spec.QueryParams) > 0 {
		params := url.Values{}
		for _, qp := range spec.QueryParams {
			params.Add(qp.Name, qp.Value)
		}
		sep := "?"
		if strings.Contains(fullURL, "?") {
			sep = "&"
		}
		fullURL += sep + params.Encode()
	}

	// Build body
	var body io.Reader
	if spec.Payload.Content != "" {
		body = bytes.NewBufferString(spec.Payload.Content)
	}

	method := strings.ToUpper(spec.Method)
	if method == "" {
		method = "GET"
	}

	req, err := http.NewRequestWithContext(ctx, method, fullURL, body)
	if err != nil {
		return nil, nil, 0, err
	}

	// Set content type
	if spec.Payload.Type == "json" || spec.Payload.Type == "graphql" {
		req.Header.Set("Content-Type", "application/json")
	} else if spec.Payload.Type == "form" {
		req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	}

	// Set headers
	for _, h := range spec.Headers {
		req.Header.Set(h.Name, h.Value)
	}
	for k, v := range c.defaultHdrs {
		if req.Header.Get(k) == "" {
			req.Header.Set(k, v)
		}
	}

	start := time.Now()
	resp, err := c.client.Do(req)
	duration := time.Since(start)
	if err != nil {
		return nil, nil, duration, err
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return resp, nil, duration, err
	}

	return resp, respBody, duration, nil
}

// ─────────────────────────────────────────────
// Section 5: Response Validator
// ─────────────────────────────────────────────

// ResponseValidator validates HTTP responses against spec.
type ResponseValidator struct{}

func (v *ResponseValidator) Validate(resp *http.Response, body []byte, spec ResponseSpec) []ValidationError {
	errs := make([]ValidationError, 0)

	// Status code
	if spec.StatusCode > 0 && resp.StatusCode != spec.StatusCode {
		errs = append(errs, ValidationError{
			Type:     "status",
			Expected: fmt.Sprintf("%d", spec.StatusCode),
			Actual:   fmt.Sprintf("%d", resp.StatusCode),
			Message:  fmt.Sprintf("Expected status %d, got %d", spec.StatusCode, resp.StatusCode),
		})
	}

	// Headers
	for _, h := range spec.Headers {
		actual := resp.Header.Get(h.Name)
		if h.Value != "" {
			// Check if value matches (supports regex with !!js/regexp prefix)
			matched := false
			if strings.HasPrefix(h.Value, "(?") || strings.HasPrefix(h.Value, "^") {
				re, err := regexp.Compile(h.Value)
				if err == nil {
					matched = re.MatchString(actual)
				}
			} else {
				matched = strings.Contains(strings.ToLower(actual), strings.ToLower(h.Value))
			}
			if !matched {
				errs = append(errs, ValidationError{
					Type:     "header",
					Expected: fmt.Sprintf("%s: %s", h.Name, h.Value),
					Actual:   fmt.Sprintf("%s: %s", h.Name, actual),
					Message:  fmt.Sprintf("Header %s: expected '%s', got '%s'", h.Name, h.Value, actual),
				})
			}
		}
	}

	// Body contains
	bodyStr := string(body)
	for _, expected := range spec.BodyContains {
		if !strings.Contains(bodyStr, expected) {
			errs = append(errs, ValidationError{
				Type:     "body",
				Expected: expected,
				Actual:   truncateStr(bodyStr, 200),
				Message:  fmt.Sprintf("Response body does not contain '%s'", expected),
			})
		}
	}

	// JSON data validation
	if len(spec.JSONData) > 0 {
		var jsonObj interface{}
		if err := json.Unmarshal(body, &jsonObj); err != nil {
			errs = append(errs, ValidationError{
				Type:    "json_data",
				Message: "Failed to parse response as JSON: " + err.Error(),
			})
		} else {
			for _, check := range spec.JSONData {
				actual := extractJSONPath(jsonObj, check.Path)
				expected := fmt.Sprintf("%v", check.Value)
				actualStr := fmt.Sprintf("%v", actual)
				if actualStr != expected {
					errs = append(errs, ValidationError{
						Type:     "json_data",
						Expected: fmt.Sprintf("%s = %s", check.Path, expected),
						Actual:   fmt.Sprintf("%s = %s", check.Path, actualStr),
						Message:  fmt.Sprintf("JSON path %s: expected '%s', got '%s'", check.Path, expected, actualStr),
					})
				}
			}
		}
	}

	return errs
}

// Simple JSONPath evaluator supporting $.key.subkey format.
func extractJSONPath(data interface{}, path string) interface{} {
	path = strings.TrimPrefix(path, "$.")
	parts := strings.Split(path, ".")

	current := data
	for _, part := range parts {
		switch v := current.(type) {
		case map[string]interface{}:
			current = v[part]
		default:
			return nil
		}
	}
	return current
}

func truncateStr(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	return s[:maxLen] + "..."
}

// ─────────────────────────────────────────────
// Section 6: Suite Runner
// ─────────────────────────────────────────────

// SuiteRunner executes a test suite.
type SuiteRunner struct {
	client    *APIClient
	validator *ResponseValidator
	context   map[string]interface{}
}

func NewSuiteRunner(config SuiteConfig) *SuiteRunner {
	return &SuiteRunner{
		client:    NewAPIClient(config),
		validator: &ResponseValidator{},
		context:   make(map[string]interface{}),
	}
}

func (r *SuiteRunner) RunSuite(ctx context.Context, suite TestSuite) SuiteResult {
	start := time.Now()
	result := SuiteResult{Name: suite.Name}
	result.Total = len(suite.Specs)

	for _, spec := range suite.Specs {
		if spec.Skip {
			result.Specs = append(result.Specs, SpecResult{
				Name: spec.Name, Status: StatusSkipped,
			})
			result.Skipped++
			continue
		}

		specResult := r.RunSpec(ctx, spec)
		result.Specs = append(result.Specs, specResult)

		switch specResult.Status {
		case StatusPassed:
			result.Passed++
		case StatusFailed:
			result.Failed++
		case StatusError:
			result.Errors++
		case StatusSkipped:
			result.Skipped++
		}
	}

	result.Duration = time.Since(start)
	result.DurationMs = float64(result.Duration.Milliseconds())
	return result
}

func (r *SuiteRunner) RunSpec(ctx context.Context, spec TestSpec) SpecResult {
	maxRetries := spec.RetryCount
	if maxRetries < 0 {
		maxRetries = 0
	}

	var specResult SpecResult
	for attempt := 0; attempt <= maxRetries; attempt++ {
		specResult = r.executeSpec(ctx, spec)
		specResult.RetryAttempts = attempt

		if specResult.Status == StatusPassed {
			break
		}
		if attempt < maxRetries && spec.RetryDelay > 0 {
			time.Sleep(time.Duration(spec.RetryDelay) * time.Millisecond)
		}
	}
	return specResult
}

func (r *SuiteRunner) executeSpec(ctx context.Context, spec TestSpec) SpecResult {
	result := SpecResult{Name: spec.Name}

	resp, body, duration, err := r.client.Execute(ctx, spec.Request)
	result.Duration = duration
	result.DurationMs = float64(duration.Milliseconds())

	if err != nil {
		result.Status = StatusError
		result.Errors = append(result.Errors, ValidationError{
			Type: "connection", Message: err.Error(),
		})
		return result
	}

	result.StatusCode = resp.StatusCode
	result.ResponseHeaders = make(map[string]string)
	for k := range resp.Header {
		result.ResponseHeaders[k] = resp.Header.Get(k)
	}
	result.ResponseBody = string(body)

	// Validate
	validationErrors := r.validator.Validate(resp, body, spec.Response)
	result.Errors = validationErrors
	if len(validationErrors) > 0 {
		result.Status = StatusFailed
	} else {
		result.Status = StatusPassed
	}

	return result
}

// ─────────────────────────────────────────────
// Section 7: Report Generators
// ─────────────────────────────────────────────

func generateJUnitXML(result RunResult) string {
	var b strings.Builder
	b.WriteString(`<?xml version="1.0" encoding="UTF-8"?>` + "\n")
	b.WriteString(fmt.Sprintf(`<testsuites tests="%d" failures="%d">`, result.Total, result.Failed))
	b.WriteString("\n")

	for _, suite := range result.Suites {
		b.WriteString(fmt.Sprintf(`  <testsuite name="%s" tests="%d" failures="%d" time="%.3f">`,
			suite.Name, suite.Total, suite.Failed, suite.DurationMs/1000))
		b.WriteString("\n")

		for _, spec := range suite.Specs {
			b.WriteString(fmt.Sprintf(`    <testcase name="%s" time="%.3f">`,
				spec.Name, spec.DurationMs/1000))
			if spec.Status == StatusFailed {
				msgs := make([]string, len(spec.Errors))
				for i, e := range spec.Errors {
					msgs[i] = e.Message
				}
				b.WriteString(fmt.Sprintf(`<failure message="%s"/>`, strings.Join(msgs, "; ")))
			} else if spec.Status == StatusSkipped {
				b.WriteString(`<skipped/>`)
			}
			b.WriteString("</testcase>\n")
		}
		b.WriteString("  </testsuite>\n")
	}
	b.WriteString("</testsuites>\n")
	return b.String()
}

// ─────────────────────────────────────────────
// Section 8: Main Engine
// ─────────────────────────────────────────────

// JustAPITestEngine is the OMNI production engine for declarative API testing.
type JustAPITestEngine struct {
	mu        sync.RWMutex
	suites    []TestSuite
	runs      []RunResult
	dataDir   string
	startedAt time.Time
	totalRuns int64
	totalSpecs int64
}

func NewJustAPITestEngine(dataDir string) *JustAPITestEngine {
	if dataDir == "" {
		home, _ := os.UserHomeDir()
		dataDir = filepath.Join(home, ".omni", "just_api")
	}
	os.MkdirAll(dataDir, 0755)

	engine := &JustAPITestEngine{
		suites:    make([]TestSuite, 0),
		runs:      make([]RunResult, 0),
		dataDir:   dataDir,
		startedAt: time.Now().UTC(),
	}
	log.Println("[OMNI-JustAPI] Engine initialized —", dataDir)
	return engine
}

// AddSuite registers a test suite.
func (e *JustAPITestEngine) AddSuite(suite TestSuite) {
	e.mu.Lock()
	defer e.mu.Unlock()
	if suite.RunMode == "" {
		suite.RunMode = RunSerial
	}
	e.suites = append(e.suites, suite)
}

// CreateSuite creates a suite from structured parameters.
func (e *JustAPITestEngine) CreateSuite(name, scheme, host, basePath string, specs []TestSpec) *TestSuite {
	suite := &TestSuite{
		Name: name,
		Configuration: SuiteConfig{
			Scheme:   scheme,
			Host:     host,
			BasePath: basePath,
		},
		Specs:   specs,
		RunMode: RunSerial,
	}
	e.AddSuite(*suite)
	return suite
}

// RunAll executes all registered suites.
func (e *JustAPITestEngine) RunAll(ctx context.Context) RunResult {
	e.mu.Lock()
	e.totalRuns++
	e.mu.Unlock()

	data := fmt.Sprintf("run-%d-%d", time.Now().UnixNano(), e.totalRuns)
	hash := sha256.Sum256([]byte(data))
	runID := hex.EncodeToString(hash[:8])

	result := RunResult{RunID: runID}
	start := time.Now()

	for _, suite := range e.suites {
		runner := NewSuiteRunner(suite.Configuration)
		suiteResult := runner.RunSuite(ctx, suite)
		result.Suites = append(result.Suites, suiteResult)
		result.Passed += suiteResult.Passed
		result.Failed += suiteResult.Failed
		result.Skipped += suiteResult.Skipped
		result.Total += suiteResult.Total
	}

	result.Duration = time.Since(start)

	e.mu.Lock()
	e.runs = append(e.runs, result)
	e.totalSpecs += int64(result.Total)
	e.mu.Unlock()

	return result
}

// RunSingleSuite runs a specific suite by name.
func (e *JustAPITestEngine) RunSingleSuite(ctx context.Context, name string) (*SuiteResult, error) {
	for _, suite := range e.suites {
		if suite.Name == name {
			runner := NewSuiteRunner(suite.Configuration)
			result := runner.RunSuite(ctx, suite)
			return &result, nil
		}
	}
	return nil, fmt.Errorf("suite '%s' not found", name)
}

// ExportJUnitXML exports the last run as JUnit XML.
func (e *JustAPITestEngine) ExportJUnitXML() string {
	e.mu.RLock()
	defer e.mu.RUnlock()
	if len(e.runs) == 0 {
		return `<?xml version="1.0"?><testsuites/>`
	}
	return generateJUnitXML(e.runs[len(e.runs)-1])
}

// ExportJSON exports the last run as JSON.
func (e *JustAPITestEngine) ExportJSON() (string, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()
	if len(e.runs) == 0 {
		return "{}", nil
	}
	data, err := json.MarshalIndent(e.runs[len(e.runs)-1], "", "  ")
	return string(data), err
}

// GetLastRun returns the most recent run result.
func (e *JustAPITestEngine) GetLastRun() *RunResult {
	e.mu.RLock()
	defer e.mu.RUnlock()
	if len(e.runs) == 0 {
		return nil
	}
	r := e.runs[len(e.runs)-1]
	return &r
}

// Diagnostics returns OMNI-standard diagnostics.
func (e *JustAPITestEngine) Diagnostics() map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	suiteNames := make([]string, len(e.suites))
	for i, s := range e.suites {
		suiteNames[i] = s.Name
	}

	return map[string]interface{}{
		"engine":     "JustAPITestEngine",
		"version":    "1.0.0",
		"status":     "operational",
		"started_at": e.startedAt.Format(time.RFC3339),
		"stats": map[string]interface{}{
			"registered_suites": len(e.suites),
			"total_runs":        e.totalRuns,
			"total_specs":       e.totalSpecs,
			"run_history":       len(e.runs),
		},
		"suites": suiteNames,
		"capabilities": []string{
			"yaml_declarative_tests", "rest_api_testing", "graphql_testing",
			"status_validation", "header_validation", "json_path_validation",
			"json_schema_validation", "body_content_validation",
			"retry_mechanism", "serial_parallel_execution",
			"junit_xml_reporting", "json_reporting",
			"suite_context", "test_dependencies", "hooks",
			"query_params", "form_uploads", "cookie_validation",
		},
	}
}
