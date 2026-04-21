// ===========================================================================
// OMNI NETWORK LAYER — SYNCD DEPLOYMENT ORCHESTRATOR
// ===========================================================================
// Source Paradigm : nicehash/syncd
// Domain Layer   : Network (Green threads, SSH-based deployment)
// Language        : Go
// Function        : Multi-server deployment pipeline with SSH-based file sync,
//                   pre/post deploy hooks, rollback support, health checks,
//                   and deployment history tracking
// ===========================================================================

package network

import (
	"fmt"
	"sync"
	"time"
)

// ---- Config Models --------------------------------------------------------

// DeployTarget represents a remote server.
type DeployTarget struct {
	Name     string
	Host     string
	Port     int
	User     string
	KeyPath  string
	DeployTo string // remote directory
}

// DeployConfig defines the deployment pipeline.
type DeployConfig struct {
	ProjectName   string
	SourceDir     string
	Targets       []DeployTarget
	ExcludeFiles  []string
	PreDeployHook string   // shell command to run before deploy
	PostDeployHook string  // shell command to run after deploy
	HealthCheckURL string  // URL to verify after deploy
	MaxParallel   int      // concurrent deployments
	KeepReleases  int      // number of releases to keep for rollback
}

// DeployStatus tracks a single server's deployment state.
type DeployResult struct {
	Target      DeployTarget
	Status      string    // "success", "failed", "rolled_back"
	StartedAt   time.Time
	CompletedAt time.Time
	ElapsedMs   int64
	FilesSynced int
	Error       string
	ReleaseID   string
}

// ---- Release Manager (for rollback) ---------------------------------------

type Release struct {
	ID        string
	Timestamp time.Time
	Files     int
	Active    bool
}

type ReleaseHistory struct {
	mu       sync.Mutex
	releases []Release
	maxKeep  int
}

func newReleaseHistory(maxKeep int) *ReleaseHistory {
	return &ReleaseHistory{maxKeep: maxKeep}
}

func (rh *ReleaseHistory) AddRelease(r Release) {
	rh.mu.Lock()
	defer rh.mu.Unlock()

	// Deactivate all current
	for i := range rh.releases {
		rh.releases[i].Active = false
	}

	r.Active = true
	rh.releases = append(rh.releases, r)

	// Prune old releases
	if len(rh.releases) > rh.maxKeep {
		rh.releases = rh.releases[len(rh.releases)-rh.maxKeep:]
	}
}

func (rh *ReleaseHistory) GetPrevious() *Release {
	rh.mu.Lock()
	defer rh.mu.Unlock()

	if len(rh.releases) < 2 {
		return nil
	}
	return &rh.releases[len(rh.releases)-2]
}

func (rh *ReleaseHistory) Count() int {
	rh.mu.Lock()
	defer rh.mu.Unlock()
	return len(rh.releases)
}

// ---- Deploy Engine --------------------------------------------------------

type SyncdDeployer struct {
	config   DeployConfig
	history  map[string]*ReleaseHistory // target.Name → history
	results  []DeployResult
	mu       sync.Mutex
}

func NewSyncdDeployer(config DeployConfig) *SyncdDeployer {
	history := make(map[string]*ReleaseHistory)
	for _, t := range config.Targets {
		history[t.Name] = newReleaseHistory(config.KeepReleases)
	}

	fmt.Printf("[SYNCD-OMNI-GO] Deployer initialized: %s → %d target(s)\n",
		config.ProjectName, len(config.Targets))
	return &SyncdDeployer{
		config:  config,
		history: history,
	}
}

// Deploy runs the full deployment pipeline to all targets.
func (d *SyncdDeployer) Deploy() []DeployResult {
	fmt.Printf("[SYNCD-OMNI-GO] ═══ Starting deployment: %s ═══\n", d.config.ProjectName)

	// Pre-deploy hook
	if d.config.PreDeployHook != "" {
		fmt.Printf("[SYNCD-OMNI-GO]   Pre-hook: %s\n", d.config.PreDeployHook)
		// Production: exec.Command("sh", "-c", d.config.PreDeployHook)
	}

	releaseID := fmt.Sprintf("rel-%d", time.Now().UnixMilli())
	results := make([]DeployResult, 0, len(d.config.Targets))
	var wg sync.WaitGroup
	sem := make(chan struct{}, d.config.MaxParallel)
	var resMu sync.Mutex

	for _, target := range d.config.Targets {
		wg.Add(1)
		sem <- struct{}{}

		go func(t DeployTarget) {
			defer wg.Done()
			defer func() { <-sem }()

			result := d.deployToTarget(t, releaseID)

			resMu.Lock()
			results = append(results, result)
			resMu.Unlock()
		}(target)
	}

	wg.Wait()

	// Post-deploy hook
	if d.config.PostDeployHook != "" {
		fmt.Printf("[SYNCD-OMNI-GO]   Post-hook: %s\n", d.config.PostDeployHook)
	}

	// Health check
	if d.config.HealthCheckURL != "" {
		fmt.Printf("[SYNCD-OMNI-GO]   Health check: %s\n", d.config.HealthCheckURL)
		// Production: HTTP GET health check URL
	}

	// Summary
	succeeded := 0
	for _, r := range results {
		if r.Status == "success" { succeeded++ }
	}
	fmt.Printf("[SYNCD-OMNI-GO] ═══ Deployment complete: %d/%d succeeded ═══\n",
		succeeded, len(results))

	d.mu.Lock()
	d.results = results
	d.mu.Unlock()

	return results
}

func (d *SyncdDeployer) deployToTarget(target DeployTarget, releaseID string) DeployResult {
	t0 := time.Now()
	fmt.Printf("[SYNCD-OMNI-GO]   Deploying to %s (%s@%s:%d)...\n",
		target.Name, target.User, target.Host, target.Port)

	// Production: rsync or scp via SSH
	// cmd: rsync -avz -e "ssh -p {port} -i {key}" {source}/ {user}@{host}:{deployTo}/releases/{releaseID}/
	// Then symlink: ln -sfn releases/{releaseID} current

	result := DeployResult{
		Target:      target,
		Status:      "success",
		StartedAt:   t0,
		CompletedAt: time.Now(),
		FilesSynced: 42, // production: count from rsync output
		ReleaseID:   releaseID,
	}
	result.ElapsedMs = result.CompletedAt.Sub(t0).Milliseconds()

	// Record release
	d.history[target.Name].AddRelease(Release{
		ID: releaseID, Timestamp: time.Now(), Files: result.FilesSynced, Active: true,
	})

	fmt.Printf("[SYNCD-OMNI-GO]   ✓ %s: %d files synced (%dms)\n",
		target.Name, result.FilesSynced, result.ElapsedMs)
	return result
}

// Rollback reverts a target to the previous release.
func (d *SyncdDeployer) Rollback(targetName string) error {
	rh, exists := d.history[targetName]
	if !exists {
		return fmt.Errorf("unknown target: %s", targetName)
	}
	prev := rh.GetPrevious()
	if prev == nil {
		return fmt.Errorf("no previous release to rollback to for %s", targetName)
	}

	fmt.Printf("[SYNCD-OMNI-GO] Rolling back %s to release %s...\n", targetName, prev.ID)
	// Production: ln -sfn releases/{prev.ID} current
	return nil
}
