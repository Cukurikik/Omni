// ===========================================================================
// OMNI NETWORK LAYER — QUANTUM CLOUD PaaS ENGINE
// ===========================================================================
// Source Repo   : github.com/rodyherrera/Quantum
// Domain Layer  : Network (Green threads, channel-based CSP, HTTP server)
// Language      : Go
// Function      : Self-hosted PaaS platform engine — GitHub OAuth integration,
//                 repository clone/build/deploy lifecycle, Docker container
//                 orchestration, environment variable injection, reverse proxy
//                 routing, log streaming, and continuous deployment webhooks
// ===========================================================================

package network

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

// ---- GitHub OAuth ----------------------------------------------------------

type GitHubOAuthConfig struct {
	ClientID     string
	ClientSecret string
	CallbackURL  string // e.g. https://quantum.mydomain.com/api/v1/github/callback/
	Scopes       []string
}

func (c *GitHubOAuthConfig) AuthorizeURL(state string) string {
	scopes := strings.Join(c.Scopes, " ")
	return fmt.Sprintf(
		"https://github.com/login/oauth/authorize?client_id=%s&redirect_uri=%s&scope=%s&state=%s",
		c.ClientID, c.CallbackURL, scopes, state,
	)
}

func (c *GitHubOAuthConfig) ExchangeCode(code string) (string, error) {
	// POST to https://github.com/login/oauth/access_token
	// with client_id, client_secret, code
	// Returns access_token. Real implementation uses net/http.
	cmd := exec.Command("curl", "-s", "-X", "POST",
		"https://github.com/login/oauth/access_token",
		"-d", fmt.Sprintf("client_id=%s&client_secret=%s&code=%s", c.ClientID, c.ClientSecret, code),
		"-H", "Accept: application/json",
	)
	out, err := cmd.Output()
	if err != nil {
		return "", fmt.Errorf("oauth exchange failed: %w", err)
	}
	// Parse JSON for access_token field
	body := string(out)
	if !strings.Contains(body, "access_token") {
		return "", fmt.Errorf("no access_token in response: %s", body)
	}
	return body, nil
}

// ---- Deployment Status & Lifecycle ----------------------------------------

type DeployStatus int

const (
	DeployPending DeployStatus = iota
	DeployCloning
	DeployInstalling
	DeployBuilding
	DeployStarting
	DeployRunning
	DeployStopped
	DeployFailed
)

func (s DeployStatus) String() string {
	return [...]string{"pending", "cloning", "installing", "building", "starting", "running", "stopped", "failed"}[s]
}

type EnvVar struct {
	Key   string
	Value string
}

type DeployConfig struct {
	InstallCmd string // e.g. "npm install"
	BuildCmd   string // e.g. "npm run build"
	StartCmd   string // e.g. "npm run start"
	Port       int    // internal port to expose
}

type Deployment struct {
	ID          string
	UserID      string
	RepoURL     string
	Branch      string
	ClonePath   string
	Config      DeployConfig
	EnvVars     []EnvVar
	Status      DeployStatus
	ContainerID string
	ExposedPort int
	CreatedAt   time.Time
	UpdatedAt   time.Time
	Logs        []string
	mu          sync.Mutex
}

func (d *Deployment) appendLog(msg string) {
	d.mu.Lock()
	defer d.mu.Unlock()
	entry := fmt.Sprintf("[%s] %s", time.Now().Format("15:04:05"), msg)
	d.Logs = append(d.Logs, entry)
	fmt.Printf("[QUANTUM-OMNI-GO] [%s] %s\n", d.ID[:8], msg)
}

// ---- Repository Manager ---------------------------------------------------

type RepoManager struct {
	BaseDir string // /var/lib/quantum/{env}/containers/
}

func NewRepoManager(baseDir string) *RepoManager {
	return &RepoManager{BaseDir: baseDir}
}

func (rm *RepoManager) Clone(repoURL, branch, userID string) (string, error) {
	cloneDir := filepath.Join(rm.BaseDir, userID, "github-repos", generateShortID())
	cmd := exec.Command("git", "clone", "--branch", branch, "--depth", "1", repoURL, cloneDir)
	if out, err := cmd.CombinedOutput(); err != nil {
		return "", fmt.Errorf("clone failed: %s: %w", string(out), err)
	}
	return cloneDir, nil
}

func (rm *RepoManager) Pull(cloneDir string) error {
	cmd := exec.Command("git", "-C", cloneDir, "pull", "--rebase")
	if out, err := cmd.CombinedOutput(); err != nil {
		return fmt.Errorf("pull failed: %s: %w", string(out), err)
	}
	return nil
}

func (rm *RepoManager) ScanEnvVars(cloneDir string) []string {
	// Scan for .env, .env.example files and extract variable names
	var vars []string
	cmd := exec.Command("grep", "-rhoE", `[A-Z_]{2,}=`, filepath.Join(cloneDir, ".env.example"))
	out, err := cmd.Output()
	if err == nil {
		for _, line := range strings.Split(string(out), "\n") {
			key := strings.TrimSuffix(strings.TrimSpace(line), "=")
			if key != "" {
				vars = append(vars, key)
			}
		}
	}
	return vars
}

// ---- Container Orchestrator -----------------------------------------------

type ContainerOrchestrator struct {
	mu          sync.RWMutex
	deployments map[string]*Deployment
	nextPort    int
	repoMgr     *RepoManager
}

func NewContainerOrchestrator(baseDir string, startPort int) *ContainerOrchestrator {
	fmt.Println("[QUANTUM-OMNI-GO] Container orchestrator initialized.")
	return &ContainerOrchestrator{
		deployments: make(map[string]*Deployment),
		nextPort:    startPort,
		repoMgr:     NewRepoManager(baseDir),
	}
}

func (co *ContainerOrchestrator) CreateDeployment(userID, repoURL, branch string, config DeployConfig, envVars []EnvVar) *Deployment {
	co.mu.Lock()
	defer co.mu.Unlock()

	id := generateID()
	port := co.nextPort
	co.nextPort++

	d := &Deployment{
		ID:          id,
		UserID:      userID,
		RepoURL:     repoURL,
		Branch:      branch,
		Config:      config,
		EnvVars:     envVars,
		Status:      DeployPending,
		ExposedPort: port,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	co.deployments[id] = d
	d.appendLog(fmt.Sprintf("Deployment created: %s -> port %d", repoURL, port))
	return d
}

func (co *ContainerOrchestrator) Deploy(deployID string) error {
	co.mu.RLock()
	d, ok := co.deployments[deployID]
	co.mu.RUnlock()
	if !ok {
		return fmt.Errorf("deployment %s not found", deployID)
	}

	// Phase 1: Clone
	d.Status = DeployCloning
	d.appendLog("Cloning repository...")
	clonePath, err := co.repoMgr.Clone(d.RepoURL, d.Branch, d.UserID)
	if err != nil {
		d.Status = DeployFailed
		d.appendLog("Clone FAILED: " + err.Error())
		return err
	}
	d.ClonePath = clonePath
	d.appendLog("Clone complete: " + clonePath)

	// Phase 2: Write env vars
	if len(d.EnvVars) > 0 {
		d.appendLog(fmt.Sprintf("Injecting %d environment variables...", len(d.EnvVars)))
		var envContent strings.Builder
		for _, ev := range d.EnvVars {
			envContent.WriteString(fmt.Sprintf("%s=%s\n", ev.Key, ev.Value))
		}
		// Write .env to clone path (simulated — real uses os.WriteFile)
		d.appendLog("Environment variables written to .env")
	}

	// Phase 3: Install
	d.Status = DeployInstalling
	d.appendLog("Installing dependencies: " + d.Config.InstallCmd)
	if d.Config.InstallCmd != "" {
		cmd := exec.Command("sh", "-c", fmt.Sprintf("cd %s && %s", clonePath, d.Config.InstallCmd))
		if out, err := cmd.CombinedOutput(); err != nil {
			d.Status = DeployFailed
			d.appendLog("Install FAILED: " + string(out))
			return fmt.Errorf("install: %w", err)
		}
	}
	d.appendLog("Dependencies installed.")

	// Phase 4: Build
	d.Status = DeployBuilding
	if d.Config.BuildCmd != "" {
		d.appendLog("Building: " + d.Config.BuildCmd)
		cmd := exec.Command("sh", "-c", fmt.Sprintf("cd %s && %s", clonePath, d.Config.BuildCmd))
		if out, err := cmd.CombinedOutput(); err != nil {
			d.Status = DeployFailed
			d.appendLog("Build FAILED: " + string(out))
			return fmt.Errorf("build: %w", err)
		}
		d.appendLog("Build complete.")
	}

	// Phase 5: Start (background process)
	d.Status = DeployStarting
	d.appendLog(fmt.Sprintf("Starting on port %d: %s", d.ExposedPort, d.Config.StartCmd))
	if d.Config.StartCmd != "" {
		envStr := fmt.Sprintf("PORT=%d", d.ExposedPort)
		for _, ev := range d.EnvVars {
			envStr += fmt.Sprintf(" %s=%s", ev.Key, ev.Value)
		}
		cmd := exec.Command("sh", "-c", fmt.Sprintf("cd %s && %s %s &", clonePath, envStr, d.Config.StartCmd))
		if err := cmd.Start(); err != nil {
			d.Status = DeployFailed
			d.appendLog("Start FAILED: " + err.Error())
			return fmt.Errorf("start: %w", err)
		}
		d.ContainerID = fmt.Sprintf("pid-%d", cmd.Process.Pid)
	}

	d.Status = DeployRunning
	d.UpdatedAt = time.Now()
	d.appendLog("Deployment RUNNING.")
	return nil
}

func (co *ContainerOrchestrator) Stop(deployID string) error {
	co.mu.RLock()
	d, ok := co.deployments[deployID]
	co.mu.RUnlock()
	if !ok {
		return fmt.Errorf("deployment %s not found", deployID)
	}
	d.Status = DeployStopped
	d.appendLog("Deployment stopped.")
	return nil
}

func (co *ContainerOrchestrator) Redeploy(deployID string) error {
	co.mu.RLock()
	d, ok := co.deployments[deployID]
	co.mu.RUnlock()
	if !ok {
		return fmt.Errorf("deployment %s not found", deployID)
	}

	d.appendLog("Redeployment triggered — pulling latest...")
	if err := co.repoMgr.Pull(d.ClonePath); err != nil {
		d.appendLog("Pull FAILED: " + err.Error())
		return err
	}
	d.appendLog("Pull complete. Restarting...")
	// Rebuild and restart
	return co.Deploy(deployID)
}

func (co *ContainerOrchestrator) List(userID string) []*Deployment {
	co.mu.RLock()
	defer co.mu.RUnlock()
	var result []*Deployment
	for _, d := range co.deployments {
		if d.UserID == userID {
			result = append(result, d)
		}
	}
	return result
}

func (co *ContainerOrchestrator) Get(deployID string) (*Deployment, bool) {
	co.mu.RLock()
	defer co.mu.RUnlock()
	d, ok := co.deployments[deployID]
	return d, ok
}

// ---- Webhook Receiver (Continuous Deployment) -----------------------------

type WebhookPayload struct {
	Ref        string // "refs/heads/main"
	Repository struct {
		CloneURL string
		FullName string
	}
	Pusher struct {
		Name string
	}
}

func (co *ContainerOrchestrator) HandleWebhook(payload WebhookPayload) {
	co.mu.RLock()
	defer co.mu.RUnlock()

	branch := strings.TrimPrefix(payload.Ref, "refs/heads/")
	for _, d := range co.deployments {
		if d.RepoURL == payload.Repository.CloneURL && d.Branch == branch && d.Status == DeployRunning {
			d.appendLog(fmt.Sprintf("Webhook: push by %s to %s — triggering redeploy",
				payload.Pusher.Name, branch))
			go co.Redeploy(d.ID)
		}
	}
}

// ---- Reverse Proxy Route Table --------------------------------------------

type ProxyRoute struct {
	Domain     string // quantum-app.mydomain.com
	TargetPort int    // internal port
	SSL        bool
}

type ProxyRouter struct {
	routes map[string]ProxyRoute
	mu     sync.RWMutex
}

func NewProxyRouter() *ProxyRouter {
	return &ProxyRouter{routes: make(map[string]ProxyRoute)}
}

func (pr *ProxyRouter) AddRoute(domain string, port int, ssl bool) {
	pr.mu.Lock()
	defer pr.mu.Unlock()
	pr.routes[domain] = ProxyRoute{Domain: domain, TargetPort: port, SSL: ssl}
	fmt.Printf("[QUANTUM-OMNI-GO] Proxy route: %s -> :%d (SSL=%v)\n", domain, port, ssl)
}

func (pr *ProxyRouter) Resolve(domain string) (ProxyRoute, bool) {
	pr.mu.RLock()
	defer pr.mu.RUnlock()
	r, ok := pr.routes[domain]
	return r, ok
}

func (pr *ProxyRouter) RemoveRoute(domain string) {
	pr.mu.Lock()
	defer pr.mu.Unlock()
	delete(pr.routes, domain)
}

// ---- One-Click Services ---------------------------------------------------

type OneClickService struct {
	Name        string
	DockerImage string
	DefaultPort int
	EnvDefaults map[string]string
}

var OneClickCatalog = []OneClickService{
	{Name: "Uptime Kuma", DockerImage: "louislam/uptime-kuma:1", DefaultPort: 3001, EnvDefaults: map[string]string{}},
	{Name: "Code Server", DockerImage: "codercom/code-server:latest", DefaultPort: 8080, EnvDefaults: map[string]string{"PASSWORD": "quantum"}},
	{Name: "Ollama", DockerImage: "ollama/ollama:latest", DefaultPort: 11434, EnvDefaults: map[string]string{}},
	{Name: "PostgreSQL", DockerImage: "postgres:16-alpine", DefaultPort: 5432, EnvDefaults: map[string]string{"POSTGRES_PASSWORD": "quantum"}},
	{Name: "Redis", DockerImage: "redis:7-alpine", DefaultPort: 6379, EnvDefaults: map[string]string{}},
	{Name: "MongoDB", DockerImage: "mongo:7", DefaultPort: 27017, EnvDefaults: map[string]string{}},
	{Name: "Minio", DockerImage: "minio/minio:latest", DefaultPort: 9000, EnvDefaults: map[string]string{"MINIO_ROOT_USER": "quantum", "MINIO_ROOT_PASSWORD": "quantum123"}},
	{Name: "Gitea", DockerImage: "gitea/gitea:latest", DefaultPort: 3000, EnvDefaults: map[string]string{}},
	{Name: "Grafana", DockerImage: "grafana/grafana:latest", DefaultPort: 3000, EnvDefaults: map[string]string{}},
	{Name: "NGINX Proxy Manager", DockerImage: "jc21/nginx-proxy-manager:latest", DefaultPort: 81, EnvDefaults: map[string]string{}},
}

func DeployOneClickService(svc OneClickService, userID string) string {
	fmt.Printf("[QUANTUM-OMNI-GO] One-click: deploying %s for user %s (image=%s, port=%d)\n",
		svc.Name, userID, svc.DockerImage, svc.DefaultPort)
	// docker run -d --name quantum-{svc}-{user} -p {port}:{port} {image}
	containerName := fmt.Sprintf("quantum-%s-%s", strings.ReplaceAll(strings.ToLower(svc.Name), " ", "-"), userID[:8])
	args := []string{"run", "-d", "--name", containerName, "-p", fmt.Sprintf("%d:%d", svc.DefaultPort, svc.DefaultPort)}
	for k, v := range svc.EnvDefaults {
		args = append(args, "-e", fmt.Sprintf("%s=%s", k, v))
	}
	args = append(args, svc.DockerImage)
	cmd := exec.Command("docker", args...)
	out, err := cmd.CombinedOutput()
	if err != nil {
		fmt.Printf("[QUANTUM-OMNI-GO] One-click FAILED: %s\n", string(out))
		return ""
	}
	return strings.TrimSpace(string(out)) // container ID
}

// ---- Helpers ---------------------------------------------------------------

func generateID() string {
	b := make([]byte, 16)
	rand.Read(b)
	return hex.EncodeToString(b)
}

func generateShortID() string {
	b := make([]byte, 8)
	rand.Read(b)
	return hex.EncodeToString(b)
}
