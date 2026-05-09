// =============================================================================
// OMNI FRAMEWORK — CHIEF AI TASK ORCHESTRATOR ENGINE
// Layer: Network | Language: Go | Source: github.com/MiniCodeMonkey/chief
// =============================================================================
// Production-grade AI-driven project task orchestration engine. Implements the
// "Ralph Wiggum loop" pattern: break large projects into tasks, run an AI agent
// (Claude/Codex/OpenCode) in a context-refresh loop until each task is done,
// and produce one clean git commit per task.
// =============================================================================

package network

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"strings"
	"sync"
	"time"
)

// ---------------------------------------------------------------------------
// Section 1: Core Types
// ---------------------------------------------------------------------------

// AgentProvider identifies which AI coding CLI is used.
type AgentProvider string

const (
	AgentClaude   AgentProvider = "claude"
	AgentCodex    AgentProvider = "codex"
	AgentOpenCode AgentProvider = "opencode"
)

// TaskStatus represents the lifecycle state of a task.
type TaskStatus string

const (
	TaskPending    TaskStatus = "pending"
	TaskInProgress TaskStatus = "in_progress"
	TaskCompleted  TaskStatus = "completed"
	TaskFailed     TaskStatus = "failed"
	TaskSkipped    TaskStatus = "skipped"
	TaskBlocked    TaskStatus = "blocked"
)

// IterationStatus represents the result of a single loop iteration.
type IterationStatus string

const (
	IterationSuccess    IterationStatus = "success"
	IterationContinue   IterationStatus = "continue"
	IterationFailed     IterationStatus = "failed"
	IterationContextHit IterationStatus = "context_limit"
)

// ChiefProjectConfig defines a project's task orchestration config.
type ChiefProjectConfig struct {
	ProjectID     string            `json:"project_id"`
	ProjectName   string            `json:"project_name"`
	Description   string            `json:"description"`
	WorkingDir    string            `json:"working_dir"`
	AgentProvider AgentProvider     `json:"agent_provider"`
	AgentCLIPath  string            `json:"agent_cli_path,omitempty"`
	MaxIterations int               `json:"max_iterations"`  // max loops per task
	CommitPerTask bool              `json:"commit_per_task"` // one commit per completed task
	AutoReview    bool              `json:"auto_review"`     // auto-review after each task
	GitBranch     string            `json:"git_branch"`
	SystemPrompt  string            `json:"system_prompt,omitempty"`
	Environment   map[string]string `json:"environment,omitempty"`
	CreatedAt     time.Time         `json:"created_at"`
}

// ChiefTask represents a single task in a project.
type ChiefTask struct {
	TaskID         string            `json:"task_id"`
	ProjectID      string            `json:"project_id"`
	Title          string            `json:"title"`
	Description    string            `json:"description"`
	Status         TaskStatus        `json:"status"`
	Priority       int               `json:"priority"` // 1=highest
	DependsOn      []string          `json:"depends_on,omitempty"`
	AcceptCriteria []string          `json:"accept_criteria,omitempty"`
	FilesToTouch   []string          `json:"files_to_touch,omitempty"`
	Tags           []string          `json:"tags,omitempty"`
	CreatedAt      time.Time         `json:"created_at"`
	StartedAt      time.Time         `json:"started_at,omitempty"`
	CompletedAt    time.Time         `json:"completed_at,omitempty"`
	Iterations     []TaskIteration   `json:"iterations"`
	CommitHash     string            `json:"commit_hash,omitempty"`
	ErrorMessage   string            `json:"error_message,omitempty"`
	Metadata       map[string]string `json:"metadata,omitempty"`
}

// TaskIteration records one loop iteration of the Ralph pattern.
type TaskIteration struct {
	IterationID  string          `json:"iteration_id"`
	IterationNum int             `json:"iteration_num"`
	StartedAt    time.Time       `json:"started_at"`
	FinishedAt   time.Time       `json:"finished_at"`
	Status       IterationStatus `json:"status"`
	Prompt       string          `json:"prompt"`
	AgentOutput  string          `json:"agent_output"`
	TokensUsed   int64           `json:"tokens_used"`
	FilesChanged []string        `json:"files_changed,omitempty"`
	ErrorMsg     string          `json:"error_message,omitempty"`
}

// TaskTemplate is a reusable template for creating tasks.
type TaskTemplate struct {
	TemplateID      string   `json:"template_id"`
	Name            string   `json:"name"`
	DescTemplate    string   `json:"description_template"`
	DefaultCriteria []string `json:"default_criteria"`
	Tags            []string `json:"tags"`
}

// ---------------------------------------------------------------------------
// Section 2: Chief Engine
// ---------------------------------------------------------------------------

// ChiefTaskOrchestrator is the production-grade engine for AI task orchestration.
type ChiefTaskOrchestrator struct {
	mu sync.RWMutex

	// Projects registry
	projects map[string]*ChiefProjectConfig

	// Tasks per project: projectID -> taskID -> task
	tasks map[string]map[string]*ChiefTask

	// Task execution queue: projectID -> ordered task IDs
	taskQueues map[string][]string

	// Templates
	templates map[string]*TaskTemplate

	// Global iteration counter
	totalIterations int64

	// Stats
	stats ChiefStats

	// Engine metadata
	engineVersion string
	startedAt     time.Time
}

// ChiefStats tracks orchestration metrics.
type ChiefStats struct {
	TotalProjects      int       `json:"total_projects"`
	TotalTasks         int       `json:"total_tasks"`
	TasksCompleted     int       `json:"tasks_completed"`
	TasksFailed        int       `json:"tasks_failed"`
	TasksPending       int       `json:"tasks_pending"`
	TotalIterations    int64     `json:"total_iterations"`
	TotalTokensUsed    int64     `json:"total_tokens_used"`
	TotalCommits       int       `json:"total_commits"`
	AverageIterPerTask float64   `json:"avg_iterations_per_task"`
	LastActivity       time.Time `json:"last_activity"`
}

// NewChiefTaskOrchestrator creates a new orchestrator engine.
func NewChiefTaskOrchestrator() *ChiefTaskOrchestrator {
	return &ChiefTaskOrchestrator{
		projects:      make(map[string]*ChiefProjectConfig),
		tasks:         make(map[string]map[string]*ChiefTask),
		taskQueues:    make(map[string][]string),
		templates:     make(map[string]*TaskTemplate),
		engineVersion: "0.8.0-omni",
		startedAt:     time.Now(),
	}
}

// ---------------------------------------------------------------------------
// Section 3: Project Management
// ---------------------------------------------------------------------------

// CreateProject initializes a new project for task orchestration.
func (e *ChiefTaskOrchestrator) CreateProject(cfg ChiefProjectConfig) (string, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	if cfg.ProjectID == "" {
		b := make([]byte, 6)
		rand.Read(b)
		cfg.ProjectID = "proj-" + hex.EncodeToString(b)
	}
	if cfg.ProjectName == "" {
		return "", fmt.Errorf("project_name is required")
	}
	if cfg.WorkingDir == "" {
		return "", fmt.Errorf("working_dir is required")
	}
	if cfg.AgentProvider == "" {
		cfg.AgentProvider = AgentClaude
	}
	if cfg.MaxIterations <= 0 {
		cfg.MaxIterations = 25
	}
	if cfg.GitBranch == "" {
		cfg.GitBranch = "main"
	}
	cfg.CommitPerTask = true
	cfg.CreatedAt = time.Now()

	e.projects[cfg.ProjectID] = &cfg
	e.tasks[cfg.ProjectID] = make(map[string]*ChiefTask)
	e.taskQueues[cfg.ProjectID] = []string{}
	e.stats.TotalProjects = len(e.projects)

	return cfg.ProjectID, nil
}

// GetProject retrieves a project config.
func (e *ChiefTaskOrchestrator) GetProject(projectID string) (*ChiefProjectConfig, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	proj, exists := e.projects[projectID]
	if !exists {
		return nil, fmt.Errorf("project %s not found", projectID)
	}
	return proj, nil
}

// ListProjects returns all projects.
func (e *ChiefTaskOrchestrator) ListProjects() []*ChiefProjectConfig {
	e.mu.RLock()
	defer e.mu.RUnlock()

	result := make([]*ChiefProjectConfig, 0, len(e.projects))
	for _, p := range e.projects {
		result = append(result, p)
	}
	return result
}

// DeleteProject removes a project and all its tasks.
func (e *ChiefTaskOrchestrator) DeleteProject(projectID string) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	if _, exists := e.projects[projectID]; !exists {
		return fmt.Errorf("project %s not found", projectID)
	}
	delete(e.projects, projectID)
	delete(e.tasks, projectID)
	delete(e.taskQueues, projectID)
	e.stats.TotalProjects = len(e.projects)
	return nil
}

// ---------------------------------------------------------------------------
// Section 4: Task Management
// ---------------------------------------------------------------------------

// AddTask creates a new task in a project.
func (e *ChiefTaskOrchestrator) AddTask(projectID string, task ChiefTask) (string, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	if _, exists := e.projects[projectID]; !exists {
		return "", fmt.Errorf("project %s not found", projectID)
	}
	if task.Title == "" {
		return "", fmt.Errorf("task title is required")
	}

	if task.TaskID == "" {
		b := make([]byte, 6)
		rand.Read(b)
		task.TaskID = "task-" + hex.EncodeToString(b)
	}
	task.ProjectID = projectID
	task.Status = TaskPending
	task.CreatedAt = time.Now()
	task.Iterations = make([]TaskIteration, 0)
	if task.Priority <= 0 {
		task.Priority = len(e.tasks[projectID]) + 1
	}

	e.tasks[projectID][task.TaskID] = &task
	e.taskQueues[projectID] = append(e.taskQueues[projectID], task.TaskID)
	e.recalculateStats()

	return task.TaskID, nil
}

// AddTasksFromDescriptions is a bulk task creation method.
func (e *ChiefTaskOrchestrator) AddTasksFromDescriptions(projectID string, descriptions []string) ([]string, error) {
	ids := make([]string, 0, len(descriptions))
	for i, desc := range descriptions {
		parts := strings.SplitN(desc, ":", 2)
		title := strings.TrimSpace(desc)
		description := ""
		if len(parts) == 2 {
			title = strings.TrimSpace(parts[0])
			description = strings.TrimSpace(parts[1])
		}

		id, err := e.AddTask(projectID, ChiefTask{
			Title:       title,
			Description: description,
			Priority:    i + 1,
		})
		if err != nil {
			return ids, fmt.Errorf("failed to add task %d: %w", i+1, err)
		}
		ids = append(ids, id)
	}
	return ids, nil
}

// GetTask retrieves a specific task.
func (e *ChiefTaskOrchestrator) GetTask(projectID, taskID string) (*ChiefTask, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	projectTasks, exists := e.tasks[projectID]
	if !exists {
		return nil, fmt.Errorf("project %s not found", projectID)
	}
	task, exists := projectTasks[taskID]
	if !exists {
		return nil, fmt.Errorf("task %s not found in project %s", taskID, projectID)
	}
	return task, nil
}

// ListTasks returns all tasks in a project, ordered by priority.
func (e *ChiefTaskOrchestrator) ListTasks(projectID string) ([]*ChiefTask, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	projectTasks, exists := e.tasks[projectID]
	if !exists {
		return nil, fmt.Errorf("project %s not found", projectID)
	}

	result := make([]*ChiefTask, 0, len(projectTasks))
	// Follow queue order
	for _, taskID := range e.taskQueues[projectID] {
		if task, exists := projectTasks[taskID]; exists {
			result = append(result, task)
		}
	}
	return result, nil
}

// GetNextTask returns the next pending task that has all dependencies met.
func (e *ChiefTaskOrchestrator) GetNextTask(projectID string) (*ChiefTask, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	projectTasks, exists := e.tasks[projectID]
	if !exists {
		return nil, fmt.Errorf("project %s not found", projectID)
	}

	for _, taskID := range e.taskQueues[projectID] {
		task := projectTasks[taskID]
		if task.Status != TaskPending {
			continue
		}

		// Check dependencies
		allDepsmet := true
		for _, depID := range task.DependsOn {
			if dep, ok := projectTasks[depID]; ok {
				if dep.Status != TaskCompleted {
					allDepsmet = false
					break
				}
			}
		}
		if allDepsmet {
			return task, nil
		}
	}

	return nil, fmt.Errorf("no pending tasks with met dependencies in project %s", projectID)
}

// UpdateTaskStatus changes a task's status.
func (e *ChiefTaskOrchestrator) UpdateTaskStatus(projectID, taskID string, status TaskStatus) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	task, exists := e.tasks[projectID][taskID]
	if !exists {
		return fmt.Errorf("task %s not found", taskID)
	}

	task.Status = status
	switch status {
	case TaskInProgress:
		task.StartedAt = time.Now()
	case TaskCompleted:
		task.CompletedAt = time.Now()
	}

	e.recalculateStats()
	return nil
}

// ---------------------------------------------------------------------------
// Section 5: Ralph Wiggum Loop Execution
// ---------------------------------------------------------------------------

// StartRalphLoop begins executing a task using the Ralph Wiggum loop pattern.
// Each iteration starts with a fresh context window but progress is persisted.
func (e *ChiefTaskOrchestrator) StartRalphLoop(projectID, taskID string) (*ChiefTask, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	project, pExists := e.projects[projectID]
	if !pExists {
		return nil, fmt.Errorf("project %s not found", projectID)
	}
	task, tExists := e.tasks[projectID][taskID]
	if !tExists {
		return nil, fmt.Errorf("task %s not found", taskID)
	}

	if task.Status != TaskPending && task.Status != TaskFailed {
		return nil, fmt.Errorf("task %s is in state %s, cannot start", taskID, task.Status)
	}

	task.Status = TaskInProgress
	task.StartedAt = time.Now()

	// Build the prompt for the first iteration
	prompt := e.buildIterationPrompt(project, task, 1)

	// Create first iteration
	b := make([]byte, 6)
	rand.Read(b)
	iteration := TaskIteration{
		IterationID:  "iter-" + hex.EncodeToString(b),
		IterationNum: 1,
		StartedAt:    time.Now(),
		Status:       IterationContinue,
		Prompt:       prompt,
	}
	task.Iterations = append(task.Iterations, iteration)
	e.totalIterations++
	e.stats.TotalIterations = e.totalIterations
	e.stats.LastActivity = time.Now()

	return task, nil
}

// RecordIterationResult processes the result of a loop iteration.
func (e *ChiefTaskOrchestrator) RecordIterationResult(
	projectID, taskID string,
	iterationNum int,
	status IterationStatus,
	output string,
	tokensUsed int64,
	filesChanged []string,
) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	task, exists := e.tasks[projectID][taskID]
	if !exists {
		return fmt.Errorf("task %s not found", taskID)
	}

	// Find and update the iteration
	for i := range task.Iterations {
		if task.Iterations[i].IterationNum == iterationNum {
			task.Iterations[i].FinishedAt = time.Now()
			task.Iterations[i].Status = status
			task.Iterations[i].AgentOutput = output
			task.Iterations[i].TokensUsed = tokensUsed
			task.Iterations[i].FilesChanged = filesChanged
			e.stats.TotalTokensUsed += tokensUsed
			break
		}
	}

	project := e.projects[projectID]

	switch status {
	case IterationSuccess:
		// Task completed successfully
		task.Status = TaskCompleted
		task.CompletedAt = time.Now()
		e.recalculateStats()

	case IterationContinue, IterationContextHit:
		// Need more iterations — check max
		if len(task.Iterations) >= project.MaxIterations {
			task.Status = TaskFailed
			task.ErrorMessage = fmt.Sprintf("exceeded max iterations (%d)", project.MaxIterations)
			e.recalculateStats()
		} else {
			// Queue next iteration with fresh context
			nextNum := len(task.Iterations) + 1
			prompt := e.buildIterationPrompt(project, task, nextNum)
			b := make([]byte, 6)
			rand.Read(b)
			nextIter := TaskIteration{
				IterationID:  "iter-" + hex.EncodeToString(b),
				IterationNum: nextNum,
				StartedAt:    time.Now(),
				Status:       IterationContinue,
				Prompt:       prompt,
			}
			task.Iterations = append(task.Iterations, nextIter)
			e.totalIterations++
			e.stats.TotalIterations = e.totalIterations
		}

	case IterationFailed:
		task.Status = TaskFailed
		task.ErrorMessage = "iteration failed: " + output
		e.recalculateStats()
	}

	e.stats.LastActivity = time.Now()
	return nil
}

// RecordCommit records a git commit hash for a completed task.
func (e *ChiefTaskOrchestrator) RecordCommit(projectID, taskID, commitHash string) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	task, exists := e.tasks[projectID][taskID]
	if !exists {
		return fmt.Errorf("task %s not found", taskID)
	}
	task.CommitHash = commitHash
	e.stats.TotalCommits++
	return nil
}

// buildIterationPrompt constructs the prompt for a fresh-context iteration.
func (e *ChiefTaskOrchestrator) buildIterationPrompt(project *ChiefProjectConfig, task *ChiefTask, iterNum int) string {
	var sb strings.Builder

	sb.WriteString(fmt.Sprintf("# Task: %s\n\n", task.Title))
	if task.Description != "" {
		sb.WriteString(fmt.Sprintf("## Description\n%s\n\n", task.Description))
	}

	// Acceptance criteria
	if len(task.AcceptCriteria) > 0 {
		sb.WriteString("## Acceptance Criteria\n")
		for _, c := range task.AcceptCriteria {
			sb.WriteString(fmt.Sprintf("- [ ] %s\n", c))
		}
		sb.WriteString("\n")
	}

	// Files hint
	if len(task.FilesToTouch) > 0 {
		sb.WriteString("## Relevant Files\n")
		for _, f := range task.FilesToTouch {
			sb.WriteString(fmt.Sprintf("- %s\n", f))
		}
		sb.WriteString("\n")
	}

	// Progress from previous iterations
	if iterNum > 1 {
		sb.WriteString("## Previous Progress\n")
		sb.WriteString(fmt.Sprintf("This is iteration %d of %d maximum.\n", iterNum, project.MaxIterations))
		sb.WriteString("Previous iterations have been working on this task.\n")
		sb.WriteString("Check the current state of the code to continue from where the last iteration left off.\n\n")

		// Summarize files changed in previous iterations
		changedFiles := make(map[string]bool)
		for _, iter := range task.Iterations {
			for _, f := range iter.FilesChanged {
				changedFiles[f] = true
			}
		}
		if len(changedFiles) > 0 {
			sb.WriteString("### Previously Modified Files\n")
			for f := range changedFiles {
				sb.WriteString(fmt.Sprintf("- %s\n", f))
			}
			sb.WriteString("\n")
		}
	}

	// System prompt override
	if project.SystemPrompt != "" {
		sb.WriteString(fmt.Sprintf("## Additional Context\n%s\n\n", project.SystemPrompt))
	}

	sb.WriteString("## Instructions\n")
	sb.WriteString("Complete this task. When done, output 'TASK_COMPLETE' on a new line.\n")
	sb.WriteString("If you cannot complete it in this iteration, make as much progress as possible.\n")

	return sb.String()
}

// ---------------------------------------------------------------------------
// Section 6: Task Templates
// ---------------------------------------------------------------------------

// RegisterTemplate stores a reusable task template.
func (e *ChiefTaskOrchestrator) RegisterTemplate(tmpl TaskTemplate) (string, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	if tmpl.Name == "" {
		return "", fmt.Errorf("template name is required")
	}
	if tmpl.TemplateID == "" {
		b := make([]byte, 6)
		rand.Read(b)
		tmpl.TemplateID = "tmpl-" + hex.EncodeToString(b)
	}
	e.templates[tmpl.TemplateID] = &tmpl
	return tmpl.TemplateID, nil
}

// CreateTaskFromTemplate creates a new task based on a template.
func (e *ChiefTaskOrchestrator) CreateTaskFromTemplate(projectID, templateID string, variables map[string]string) (string, error) {
	e.mu.RLock()
	tmpl, exists := e.templates[templateID]
	e.mu.RUnlock()

	if !exists {
		return "", fmt.Errorf("template %s not found", templateID)
	}

	desc := tmpl.DescTemplate
	for k, v := range variables {
		desc = strings.ReplaceAll(desc, "{{"+k+"}}", v)
	}

	return e.AddTask(projectID, ChiefTask{
		Title:          tmpl.Name,
		Description:    desc,
		AcceptCriteria: tmpl.DefaultCriteria,
		Tags:           tmpl.Tags,
	})
}

// ---------------------------------------------------------------------------
// Section 7: Project Progress & Analytics
// ---------------------------------------------------------------------------

// GetProjectProgress returns a summary of project completion.
func (e *ChiefTaskOrchestrator) GetProjectProgress(projectID string) (map[string]interface{}, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	project, pExists := e.projects[projectID]
	if !pExists {
		return nil, fmt.Errorf("project %s not found", projectID)
	}

	projectTasks := e.tasks[projectID]
	total := len(projectTasks)
	statusCounts := map[TaskStatus]int{
		TaskPending: 0, TaskInProgress: 0, TaskCompleted: 0,
		TaskFailed: 0, TaskSkipped: 0, TaskBlocked: 0,
	}

	var totalIters int
	var totalTokens int64
	for _, task := range projectTasks {
		statusCounts[task.Status]++
		totalIters += len(task.Iterations)
		for _, iter := range task.Iterations {
			totalTokens += iter.TokensUsed
		}
	}

	pct := float64(0)
	if total > 0 {
		pct = float64(statusCounts[TaskCompleted]) / float64(total) * 100
	}

	avgIters := float64(0)
	if statusCounts[TaskCompleted] > 0 {
		avgIters = float64(totalIters) / float64(statusCounts[TaskCompleted])
	}

	return map[string]interface{}{
		"project_id":         projectID,
		"project_name":       project.ProjectName,
		"total_tasks":        total,
		"completed":          statusCounts[TaskCompleted],
		"in_progress":        statusCounts[TaskInProgress],
		"pending":            statusCounts[TaskPending],
		"failed":             statusCounts[TaskFailed],
		"skipped":            statusCounts[TaskSkipped],
		"blocked":            statusCounts[TaskBlocked],
		"completion_pct":     fmt.Sprintf("%.1f%%", pct),
		"total_iterations":   totalIters,
		"total_tokens":       totalTokens,
		"avg_iters_per_task": fmt.Sprintf("%.1f", avgIters),
		"agent_provider":     project.AgentProvider,
	}, nil
}

// ---------------------------------------------------------------------------
// Section 8: Batch Operations
// ---------------------------------------------------------------------------

// RunAllPending starts the Ralph loop for all pending tasks in order.
func (e *ChiefTaskOrchestrator) RunAllPending(projectID string) ([]*ChiefTask, error) {
	started := make([]*ChiefTask, 0)

	for {
		task, err := e.GetNextTask(projectID)
		if err != nil {
			break // No more pending tasks
		}
		result, err := e.StartRalphLoop(projectID, task.TaskID)
		if err != nil {
			break
		}
		started = append(started, result)
	}

	if len(started) == 0 {
		return nil, fmt.Errorf("no pending tasks found in project %s", projectID)
	}
	return started, nil
}

// RetryFailedTasks resets failed tasks to pending and starts them.
func (e *ChiefTaskOrchestrator) RetryFailedTasks(projectID string) (int, error) {
	e.mu.Lock()
	projectTasks, exists := e.tasks[projectID]
	if !exists {
		e.mu.Unlock()
		return 0, fmt.Errorf("project %s not found", projectID)
	}

	count := 0
	for _, task := range projectTasks {
		if task.Status == TaskFailed {
			task.Status = TaskPending
			task.ErrorMessage = ""
			task.Iterations = make([]TaskIteration, 0)
			count++
		}
	}
	e.mu.Unlock()

	e.recalculateStats()
	return count, nil
}

// SkipTask marks a task as skipped.
func (e *ChiefTaskOrchestrator) SkipTask(projectID, taskID string) error {
	return e.UpdateTaskStatus(projectID, taskID, TaskSkipped)
}

// ---------------------------------------------------------------------------
// Section 9: Configuration Helpers
// ---------------------------------------------------------------------------

// SetAgentProvider changes the AI CLI provider for a project.
func (e *ChiefTaskOrchestrator) SetAgentProvider(projectID string, provider AgentProvider, cliPath string) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	project, exists := e.projects[projectID]
	if !exists {
		return fmt.Errorf("project %s not found", projectID)
	}

	validProviders := map[AgentProvider]bool{AgentClaude: true, AgentCodex: true, AgentOpenCode: true}
	if !validProviders[provider] {
		return fmt.Errorf("invalid agent provider: %s", provider)
	}

	project.AgentProvider = provider
	if cliPath != "" {
		project.AgentCLIPath = cliPath
	}
	return nil
}

// SetMaxIterations changes the max iteration limit for a project.
func (e *ChiefTaskOrchestrator) SetMaxIterations(projectID string, max int) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	project, exists := e.projects[projectID]
	if !exists {
		return fmt.Errorf("project %s not found", projectID)
	}
	if max < 1 || max > 100 {
		return fmt.Errorf("max iterations must be 1-100, got %d", max)
	}
	project.MaxIterations = max
	return nil
}

// ---------------------------------------------------------------------------
// Section 10: Diagnostics
// ---------------------------------------------------------------------------

func (e *ChiefTaskOrchestrator) recalculateStats() {
	totalTasks := 0
	completed := 0
	failed := 0
	pending := 0
	totalIters := int64(0)

	for _, projectTasks := range e.tasks {
		for _, task := range projectTasks {
			totalTasks++
			switch task.Status {
			case TaskCompleted:
				completed++
			case TaskFailed:
				failed++
			case TaskPending:
				pending++
			}
			totalIters += int64(len(task.Iterations))
		}
	}

	e.stats.TotalTasks = totalTasks
	e.stats.TasksCompleted = completed
	e.stats.TasksFailed = failed
	e.stats.TasksPending = pending
	e.stats.TotalIterations = totalIters

	if completed > 0 {
		e.stats.AverageIterPerTask = float64(totalIters) / float64(completed)
	}
}

// GetStats returns current orchestration statistics.
func (e *ChiefTaskOrchestrator) GetStats() ChiefStats {
	e.mu.RLock()
	defer e.mu.RUnlock()
	e.recalculateStats()
	return e.stats
}

// Diagnostics returns engine health information.
func (e *ChiefTaskOrchestrator) Diagnostics() map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	return map[string]interface{}{
		"engine":            "OmniChiefTaskOrchestrator",
		"version":           e.engineVersion,
		"uptime":            time.Since(e.startedAt).String(),
		"started_at":        e.startedAt,
		"total_projects":    e.stats.TotalProjects,
		"total_tasks":       e.stats.TotalTasks,
		"tasks_completed":   e.stats.TasksCompleted,
		"tasks_failed":      e.stats.TasksFailed,
		"tasks_pending":     e.stats.TasksPending,
		"total_iterations":  e.stats.TotalIterations,
		"total_tokens_used": e.stats.TotalTokensUsed,
		"total_commits":     e.stats.TotalCommits,
		"avg_iter_per_task": e.stats.AverageIterPerTask,
		"templates_count":   len(e.templates),
		"last_activity":     e.stats.LastActivity,
		"status":            "OPERATIONAL",
	}
}
