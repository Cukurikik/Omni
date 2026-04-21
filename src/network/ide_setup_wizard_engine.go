/*
OMNI IDE Setup Wizard Engine
==============================
Production-grade automated IDE provisioning, configuration management,
and development environment orchestration engine.

Provides automated setup, configuration syncing, extension management,
and environment health checks for OMNI-compatible IDEs.

Inspired by: github.com/jorcelinojunior/cursor-setup-wizard
OMNI Layer: Network (Go)
*/

package network

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"time"
)

// ─────────────────────────────────────────────
// Section 1: Core Types
// ─────────────────────────────────────────────

// IDEType represents a supported IDE.
type IDEType string

const (
	IDECursor    IDEType = "cursor"
	IDEVSCode    IDEType = "vscode"
	IDEZed       IDEType = "zed"
	IDENeovim    IDEType = "neovim"
	IDEJetBrains IDEType = "jetbrains"
	IDEHelix     IDEType = "helix"
	IDEWindsurf  IDEType = "windsurf"
)

// SetupPhase represents a stage in the IDE setup process.
type SetupPhase string

const (
	PhasePrecheck     SetupPhase = "precheck"
	PhaseDownload     SetupPhase = "download"
	PhaseInstall      SetupPhase = "install"
	PhaseConfigure    SetupPhase = "configure"
	PhaseExtensions   SetupPhase = "extensions"
	PhaseVerify       SetupPhase = "verify"
	PhaseComplete     SetupPhase = "complete"
	PhaseFailed       SetupPhase = "failed"
)

// ExtensionState represents installation status of an extension.
type ExtensionState string

const (
	ExtInstalled   ExtensionState = "installed"
	ExtNotFound    ExtensionState = "not_found"
	ExtOutdated    ExtensionState = "outdated"
	ExtDisabled    ExtensionState = "disabled"
	ExtError       ExtensionState = "error"
)

// ─────────────────────────────────────────────
// Section 2: Data Structures
// ─────────────────────────────────────────────

// IDEExtension represents an IDE extension/plugin.
type IDEExtension struct {
	ID          string         `json:"id"`
	Name        string         `json:"name"`
	Publisher   string         `json:"publisher"`
	Version     string         `json:"version"`
	Description string         `json:"description"`
	State       ExtensionState `json:"state"`
	Required    bool           `json:"required"`
	Category    string         `json:"category"`
}

// IDEConfiguration represents a complete IDE configuration profile.
type IDEConfiguration struct {
	IDE           IDEType                `json:"ide"`
	ProfileName   string                 `json:"profile_name"`
	Settings      map[string]interface{} `json:"settings"`
	KeyBindings   map[string]string      `json:"key_bindings"`
	Extensions    []IDEExtension         `json:"extensions"`
	Snippets      map[string]interface{} `json:"snippets"`
	Theme         string                 `json:"theme"`
	FontFamily    string                 `json:"font_family"`
	FontSize      int                    `json:"font_size"`
	TabSize       int                    `json:"tab_size"`
	UseSpaces     bool                   `json:"use_spaces"`
	AutoSave      bool                   `json:"auto_save"`
	FormatOnSave  bool                   `json:"format_on_save"`
	WordWrap      string                 `json:"word_wrap"`
	TerminalFont  string                 `json:"terminal_font"`
	TerminalSize  int                    `json:"terminal_font_size"`
	CustomPaths   map[string]string      `json:"custom_paths"`
	Version       string                 `json:"version"`
	CreatedAt     string                 `json:"created_at"`
	Checksum      string                 `json:"checksum"`
}

// SystemRequirement represents a system dependency check.
type SystemRequirement struct {
	Name        string `json:"name"`
	Command     string `json:"command"`
	MinVersion  string `json:"min_version"`
	Installed   bool   `json:"installed"`
	Version     string `json:"version"`
	InstallHint string `json:"install_hint"`
	Critical    bool   `json:"critical"`
}

// SetupProgress tracks the setup wizard's progress.
type SetupProgress struct {
	Phase           SetupPhase `json:"phase"`
	StepIndex       int        `json:"step_index"`
	TotalSteps      int        `json:"total_steps"`
	CurrentStep     string     `json:"current_step"`
	ProgressPct     float64    `json:"progress_pct"`
	StartedAt       time.Time  `json:"started_at"`
	ElapsedMs       int64      `json:"elapsed_ms"`
	Messages        []string   `json:"messages"`
	Warnings        []string   `json:"warnings"`
	Errors          []string   `json:"errors"`
}

// HealthCheckResult holds the result of an environment health check.
type HealthCheckResult struct {
	IDE             IDEType                 `json:"ide"`
	Healthy         bool                    `json:"healthy"`
	Score           int                     `json:"score"`
	MaxScore        int                     `json:"max_score"`
	Checks          []HealthCheck           `json:"checks"`
	Recommendations []string                `json:"recommendations"`
	CheckedAt       time.Time               `json:"checked_at"`
}

// HealthCheck represents a single health check item.
type HealthCheck struct {
	Name    string `json:"name"`
	Status  string `json:"status"` // pass, warn, fail
	Message string `json:"message"`
	Score   int    `json:"score"`
}

// DownloadInfo holds metadata about an IDE download.
type DownloadInfo struct {
	IDE          IDEType `json:"ide"`
	Version      string  `json:"version"`
	URL          string  `json:"url"`
	SHA256       string  `json:"sha256"`
	FileSize     int64   `json:"file_size_bytes"`
	Platform     string  `json:"platform"`
	Architecture string  `json:"architecture"`
}

// ─────────────────────────────────────────────
// Section 3: Platform Detection
// ─────────────────────────────────────────────

// PlatformDetector gathers information about the current system.
type PlatformDetector struct{}

func NewPlatformDetector() *PlatformDetector {
	return &PlatformDetector{}
}

// DetectOS returns current OS and architecture.
func (pd *PlatformDetector) DetectOS() (string, string) {
	return runtime.GOOS, runtime.GOARCH
}

// GetIDEPaths returns standard installation paths for an IDE.
func (pd *PlatformDetector) GetIDEPaths(ide IDEType) map[string]string {
	osName, _ := pd.DetectOS()
	home, _ := os.UserHomeDir()
	paths := make(map[string]string)

	switch ide {
	case IDECursor:
		switch osName {
		case "windows":
			paths["binary"] = filepath.Join(os.Getenv("LOCALAPPDATA"), "Programs", "cursor", "Cursor.exe")
			paths["config"] = filepath.Join(os.Getenv("APPDATA"), "Cursor", "User")
			paths["extensions"] = filepath.Join(home, ".cursor", "extensions")
			paths["data"] = filepath.Join(os.Getenv("APPDATA"), "Cursor")
		case "darwin":
			paths["binary"] = "/Applications/Cursor.app/Contents/MacOS/Cursor"
			paths["config"] = filepath.Join(home, "Library", "Application Support", "Cursor", "User")
			paths["extensions"] = filepath.Join(home, ".cursor", "extensions")
			paths["data"] = filepath.Join(home, "Library", "Application Support", "Cursor")
		case "linux":
			paths["binary"] = filepath.Join(home, ".local", "bin", "cursor")
			paths["config"] = filepath.Join(home, ".config", "Cursor", "User")
			paths["extensions"] = filepath.Join(home, ".cursor", "extensions")
			paths["data"] = filepath.Join(home, ".config", "Cursor")
		}
	case IDEVSCode:
		switch osName {
		case "windows":
			paths["binary"] = filepath.Join(os.Getenv("LOCALAPPDATA"), "Programs", "Microsoft VS Code", "Code.exe")
			paths["config"] = filepath.Join(os.Getenv("APPDATA"), "Code", "User")
			paths["extensions"] = filepath.Join(home, ".vscode", "extensions")
			paths["data"] = filepath.Join(os.Getenv("APPDATA"), "Code")
		case "darwin":
			paths["binary"] = "/Applications/Visual Studio Code.app/Contents/MacOS/Electron"
			paths["config"] = filepath.Join(home, "Library", "Application Support", "Code", "User")
			paths["extensions"] = filepath.Join(home, ".vscode", "extensions")
		case "linux":
			paths["binary"] = "/usr/bin/code"
			paths["config"] = filepath.Join(home, ".config", "Code", "User")
			paths["extensions"] = filepath.Join(home, ".vscode", "extensions")
		}
	case IDEZed:
		switch osName {
		case "darwin":
			paths["binary"] = "/Applications/Zed.app/Contents/MacOS/zed"
			paths["config"] = filepath.Join(home, ".config", "zed")
		case "linux":
			paths["binary"] = "/usr/bin/zed"
			paths["config"] = filepath.Join(home, ".config", "zed")
		}
	case IDENeovim:
		switch osName {
		case "windows":
			paths["binary"] = filepath.Join(os.Getenv("LOCALAPPDATA"), "nvim", "bin", "nvim.exe")
			paths["config"] = filepath.Join(os.Getenv("LOCALAPPDATA"), "nvim")
		default:
			paths["binary"] = "/usr/bin/nvim"
			paths["config"] = filepath.Join(home, ".config", "nvim")
		}
	case IDEHelix:
		switch osName {
		case "windows":
			paths["binary"] = filepath.Join(os.Getenv("LOCALAPPDATA"), "helix", "hx.exe")
			paths["config"] = filepath.Join(os.Getenv("APPDATA"), "helix")
		default:
			paths["binary"] = "/usr/bin/hx"
			paths["config"] = filepath.Join(home, ".config", "helix")
		}
	}

	return paths
}

// CheckSystemRequirements verifies required tools are installed.
func (pd *PlatformDetector) CheckSystemRequirements() []SystemRequirement {
	reqs := []SystemRequirement{
		{Name: "Git", Command: "git --version", Critical: true, InstallHint: "https://git-scm.com/downloads"},
		{Name: "Node.js", Command: "node --version", Critical: false, InstallHint: "https://nodejs.org"},
		{Name: "Go", Command: "go version", Critical: false, InstallHint: "https://go.dev/dl"},
		{Name: "Python", Command: "python --version", Critical: false, InstallHint: "https://www.python.org/downloads"},
		{Name: "Rust", Command: "rustc --version", Critical: false, InstallHint: "https://rustup.rs"},
		{Name: "Docker", Command: "docker --version", Critical: false, InstallHint: "https://docs.docker.com/get-docker"},
	}

	for i := range reqs {
		parts := strings.Fields(reqs[i].Command)
		cmd := exec.Command(parts[0], parts[1:]...)
		output, err := cmd.CombinedOutput()
		if err == nil {
			reqs[i].Installed = true
			reqs[i].Version = strings.TrimSpace(string(output))
		}
	}

	return reqs
}

// ─────────────────────────────────────────────
// Section 4: Configuration Profiles
// ─────────────────────────────────────────────

// ConfigProfileManager manages IDE configuration profiles.
type ConfigProfileManager struct {
	mu          sync.Mutex
	profilesDir string
	profiles    map[string]*IDEConfiguration
}

func NewConfigProfileManager(profilesDir string) *ConfigProfileManager {
	os.MkdirAll(profilesDir, 0755)
	return &ConfigProfileManager{
		profilesDir: profilesDir,
		profiles:    make(map[string]*IDEConfiguration),
	}
}

// CreateOmniProfile creates the default OMNI-optimized IDE profile.
func (cpm *ConfigProfileManager) CreateOmniProfile(ide IDEType) *IDEConfiguration {
	config := &IDEConfiguration{
		IDE:          ide,
		ProfileName:  "omni-production",
		Theme:        "One Dark Pro",
		FontFamily:   "'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace",
		FontSize:     14,
		TabSize:      2,
		UseSpaces:    true,
		AutoSave:     true,
		FormatOnSave: true,
		WordWrap:     "off",
		TerminalFont: "JetBrains Mono",
		TerminalSize: 13,
		Version:      "1.0.0",
		CreatedAt:    time.Now().UTC().Format(time.RFC3339),
	}

	config.Settings = map[string]interface{}{
		"editor.fontSize":                 config.FontSize,
		"editor.fontFamily":               config.FontFamily,
		"editor.fontLigatures":            true,
		"editor.tabSize":                  config.TabSize,
		"editor.insertSpaces":             config.UseSpaces,
		"editor.formatOnSave":             config.FormatOnSave,
		"editor.minimap.enabled":          false,
		"editor.renderWhitespace":         "boundary",
		"editor.bracketPairColorization.enabled": true,
		"editor.guides.bracketPairs":      "active",
		"editor.stickyScroll.enabled":     true,
		"editor.inlineSuggest.enabled":    true,
		"editor.linkedEditing":            true,
		"editor.suggest.showStatusBar":    true,
		"editor.accessibilitySupport":     "off",
		"editor.cursorBlinking":           "smooth",
		"editor.cursorSmoothCaretAnimation": "on",
		"editor.smoothScrolling":          true,
		"terminal.integrated.fontSize":    config.TerminalSize,
		"terminal.integrated.fontFamily":  config.TerminalFont,
		"terminal.integrated.cursorBlinking": true,
		"files.autoSave":                  "afterDelay",
		"files.autoSaveDelay":             1000,
		"files.trimTrailingWhitespace":    true,
		"files.insertFinalNewline":        true,
		"workbench.colorTheme":            config.Theme,
		"workbench.iconTheme":             "material-icon-theme",
		"workbench.startupEditor":         "none",
		"workbench.sideBar.location":      "left",
		"workbench.tree.indent":           16,
		"explorer.confirmDelete":          false,
		"explorer.confirmDragAndDrop":     false,
		"search.smartCase":                true,
		"telemetry.telemetryLevel":        "off",
		"security.workspace.trust.enabled": false,
	}

	config.KeyBindings = map[string]string{
		"ctrl+shift+p":       "workbench.action.showCommands",
		"ctrl+`":             "workbench.action.terminal.toggleTerminal",
		"ctrl+shift+`":       "workbench.action.terminal.new",
		"ctrl+b":             "workbench.action.toggleSidebarVisibility",
		"ctrl+shift+e":       "workbench.view.explorer",
		"ctrl+shift+f":       "workbench.view.search",
		"ctrl+shift+g":       "workbench.view.scm",
		"ctrl+shift+d":       "workbench.view.debug",
		"ctrl+shift+x":       "workbench.view.extensions",
	}

	config.Extensions = cpm.getOmniExtensions(ide)

	// Compute checksum
	data, _ := json.Marshal(config)
	hash := sha256.Sum256(data)
	config.Checksum = hex.EncodeToString(hash[:])

	return config
}

func (cpm *ConfigProfileManager) getOmniExtensions(ide IDEType) []IDEExtension {
	base := []IDEExtension{
		{ID: "esbenp.prettier-vscode", Name: "Prettier", Publisher: "esbenp", Category: "formatter", Required: true},
		{ID: "dbaeumer.vscode-eslint", Name: "ESLint", Publisher: "dbaeumer", Category: "linter", Required: true},
		{ID: "eamodio.gitlens", Name: "GitLens", Publisher: "eamodio", Category: "git", Required: true},
		{ID: "PKief.material-icon-theme", Name: "Material Icon Theme", Publisher: "PKief", Category: "theme", Required: true},
		{ID: "zhuangtongfa.material-theme", Name: "One Dark Pro", Publisher: "zhuangtongfa", Category: "theme", Required: true},
		{ID: "ms-python.python", Name: "Python", Publisher: "Microsoft", Category: "language", Required: true},
		{ID: "golang.go", Name: "Go", Publisher: "Go Team", Category: "language", Required: true},
		{ID: "rust-lang.rust-analyzer", Name: "Rust Analyzer", Publisher: "rust-lang", Category: "language", Required: false},
		{ID: "ms-vscode.cpptools", Name: "C/C++", Publisher: "Microsoft", Category: "language", Required: false},
		{ID: "bradlc.vscode-tailwindcss", Name: "Tailwind CSS IntelliSense", Publisher: "bradlc", Category: "css", Required: false},
		{ID: "formulahendry.auto-rename-tag", Name: "Auto Rename Tag", Publisher: "formulahendry", Category: "html", Required: false},
		{ID: "streetsidesoftware.code-spell-checker", Name: "Code Spell Checker", Publisher: "streetsidesoftware", Category: "utility", Required: false},
		{ID: "usernamehw.errorlens", Name: "Error Lens", Publisher: "usernamehw", Category: "utility", Required: true},
		{ID: "christian-kohler.path-intellisense", Name: "Path Intellisense", Publisher: "christian-kohler", Category: "utility", Required: false},
		{ID: "ms-azuretools.vscode-docker", Name: "Docker", Publisher: "Microsoft", Category: "devops", Required: false},
		{ID: "GitHub.copilot", Name: "GitHub Copilot", Publisher: "GitHub", Category: "ai", Required: false},
	}

	if ide == IDECursor {
		base = append(base, IDEExtension{
			ID: "cursor.cursor-ai", Name: "Cursor AI", Publisher: "Cursor", Category: "ai", Required: true,
		})
	}

	return base
}

// SaveProfile saves a configuration profile to disk.
func (cpm *ConfigProfileManager) SaveProfile(config *IDEConfiguration) error {
	cpm.mu.Lock()
	defer cpm.mu.Unlock()

	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return err
	}

	filename := fmt.Sprintf("%s_%s.json", config.IDE, config.ProfileName)
	path := filepath.Join(cpm.profilesDir, filename)
	if err := os.WriteFile(path, data, 0644); err != nil {
		return err
	}

	cpm.profiles[config.ProfileName] = config
	return nil
}

// LoadProfile loads a saved configuration profile.
func (cpm *ConfigProfileManager) LoadProfile(name string) (*IDEConfiguration, error) {
	cpm.mu.Lock()
	defer cpm.mu.Unlock()

	if config, ok := cpm.profiles[name]; ok {
		return config, nil
	}

	// Try loading from disk
	files, err := os.ReadDir(cpm.profilesDir)
	if err != nil {
		return nil, err
	}
	for _, f := range files {
		if strings.Contains(f.Name(), name) {
			data, err := os.ReadFile(filepath.Join(cpm.profilesDir, f.Name()))
			if err != nil {
				return nil, err
			}
			var config IDEConfiguration
			if err := json.Unmarshal(data, &config); err != nil {
				return nil, err
			}
			cpm.profiles[name] = &config
			return &config, nil
		}
	}

	return nil, fmt.Errorf("profile not found: %s", name)
}

// ListProfiles returns all available profile names.
func (cpm *ConfigProfileManager) ListProfiles() []string {
	cpm.mu.Lock()
	defer cpm.mu.Unlock()
	names := make([]string, 0)
	for n := range cpm.profiles {
		names = append(names, n)
	}
	return names
}

// ─────────────────────────────────────────────
// Section 5: Extension Manager
// ─────────────────────────────────────────────

// ExtensionManager handles IDE extension installation and management.
type ExtensionManager struct {
	ide     IDEType
	cliPath string
}

func NewExtensionManager(ide IDEType) *ExtensionManager {
	em := &ExtensionManager{ide: ide}
	em.cliPath = em.findCLI()
	return em
}

func (em *ExtensionManager) findCLI() string {
	switch em.ide {
	case IDECursor:
		if runtime.GOOS == "windows" {
			return filepath.Join(os.Getenv("LOCALAPPDATA"), "Programs", "cursor", "resources", "app", "bin", "cursor")
		}
		return "cursor"
	case IDEVSCode:
		return "code"
	default:
		return ""
	}
}

// InstallExtension installs a single extension by ID.
func (em *ExtensionManager) InstallExtension(extensionID string) error {
	if em.cliPath == "" {
		return fmt.Errorf("no CLI available for %s", em.ide)
	}
	cmd := exec.Command(em.cliPath, "--install-extension", extensionID, "--force")
	output, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("install %s failed: %s — %w", extensionID, string(output), err)
	}
	log.Printf("[SetupWizard] Installed extension: %s", extensionID)
	return nil
}

// UninstallExtension removes an extension.
func (em *ExtensionManager) UninstallExtension(extensionID string) error {
	if em.cliPath == "" {
		return fmt.Errorf("no CLI for %s", em.ide)
	}
	cmd := exec.Command(em.cliPath, "--uninstall-extension", extensionID)
	_, err := cmd.CombinedOutput()
	return err
}

// ListInstalled returns currently installed extension IDs.
func (em *ExtensionManager) ListInstalled() ([]string, error) {
	if em.cliPath == "" {
		return nil, fmt.Errorf("no CLI for %s", em.ide)
	}
	cmd := exec.Command(em.cliPath, "--list-extensions")
	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil, err
	}
	lines := strings.Split(strings.TrimSpace(string(output)), "\n")
	result := make([]string, 0)
	for _, l := range lines {
		l = strings.TrimSpace(l)
		if l != "" {
			result = append(result, l)
		}
	}
	return result, nil
}

// SyncExtensions installs missing extensions from a config profile.
func (em *ExtensionManager) SyncExtensions(required []IDEExtension) (installed int, skipped int, failed int) {
	existing, err := em.ListInstalled()
	if err != nil {
		log.Printf("[SetupWizard] Cannot list extensions: %v", err)
		failed = len(required)
		return
	}

	existingSet := make(map[string]bool)
	for _, e := range existing {
		existingSet[strings.ToLower(e)] = true
	}

	for _, ext := range required {
		if existingSet[strings.ToLower(ext.ID)] {
			skipped++
			continue
		}
		if err := em.InstallExtension(ext.ID); err != nil {
			log.Printf("[SetupWizard] Failed to install %s: %v", ext.ID, err)
			failed++
		} else {
			installed++
		}
	}
	return
}

// ─────────────────────────────────────────────
// Section 6: Config Applicator
// ─────────────────────────────────────────────

// ConfigApplicator writes IDE configuration to the filesystem.
type ConfigApplicator struct {
	detector *PlatformDetector
}

func NewConfigApplicator() *ConfigApplicator {
	return &ConfigApplicator{detector: NewPlatformDetector()}
}

// ApplySettings writes settings.json for VS Code-based IDEs.
func (ca *ConfigApplicator) ApplySettings(config *IDEConfiguration) error {
	paths := ca.detector.GetIDEPaths(config.IDE)
	configDir, ok := paths["config"]
	if !ok {
		return fmt.Errorf("config path not found for %s", config.IDE)
	}

	os.MkdirAll(configDir, 0755)

	// Write settings.json
	settingsPath := filepath.Join(configDir, "settings.json")
	settingsData, err := json.MarshalIndent(config.Settings, "", "  ")
	if err != nil {
		return err
	}

	// Backup existing settings
	if _, err := os.Stat(settingsPath); err == nil {
		backupPath := settingsPath + ".bak." + time.Now().Format("20060102_150405")
		data, _ := os.ReadFile(settingsPath)
		os.WriteFile(backupPath, data, 0644)
		log.Printf("[SetupWizard] Backed up existing settings to %s", backupPath)
	}

	if err := os.WriteFile(settingsPath, settingsData, 0644); err != nil {
		return fmt.Errorf("write settings: %w", err)
	}
	log.Printf("[SetupWizard] Applied settings to %s", settingsPath)

	// Write keybindings.json
	if len(config.KeyBindings) > 0 {
		kbPath := filepath.Join(configDir, "keybindings.json")
		bindings := make([]map[string]string, 0)
		for key, command := range config.KeyBindings {
			bindings = append(bindings, map[string]string{"key": key, "command": command})
		}
		kbData, _ := json.MarshalIndent(bindings, "", "  ")
		os.WriteFile(kbPath, kbData, 0644)
	}

	return nil
}

// ─────────────────────────────────────────────
// Section 7: Health Checker
// ─────────────────────────────────────────────

// HealthChecker performs comprehensive environment health checks.
type HealthChecker struct {
	detector *PlatformDetector
}

func NewHealthChecker() *HealthChecker {
	return &HealthChecker{detector: NewPlatformDetector()}
}

// RunHealthCheck performs a full health check for an IDE.
func (hc *HealthChecker) RunHealthCheck(ide IDEType) *HealthCheckResult {
	result := &HealthCheckResult{
		IDE:       ide,
		Healthy:   true,
		MaxScore:  100,
		CheckedAt: time.Now().UTC(),
	}

	// Check 1: IDE installed
	paths := hc.detector.GetIDEPaths(ide)
	binaryPath := paths["binary"]
	if _, err := os.Stat(binaryPath); err != nil {
		result.Checks = append(result.Checks, HealthCheck{
			Name: "IDE Binary", Status: "fail",
			Message: fmt.Sprintf("%s not found at %s", ide, binaryPath),
		})
		result.Recommendations = append(result.Recommendations, fmt.Sprintf("Install %s from official website", ide))
	} else {
		result.Checks = append(result.Checks, HealthCheck{
			Name: "IDE Binary", Status: "pass",
			Message: fmt.Sprintf("%s found at %s", ide, binaryPath), Score: 20,
		})
		result.Score += 20
	}

	// Check 2: Config directory exists
	configDir := paths["config"]
	if configDir != "" {
		if _, err := os.Stat(configDir); err != nil {
			result.Checks = append(result.Checks, HealthCheck{
				Name: "Config Directory", Status: "warn",
				Message: "Config directory not found — IDE may not be initialized",
			})
		} else {
			result.Checks = append(result.Checks, HealthCheck{
				Name: "Config Directory", Status: "pass",
				Message: "Config directory exists", Score: 10,
			})
			result.Score += 10
		}
	}

	// Check 3: Settings exist
	if configDir != "" {
		settingsPath := filepath.Join(configDir, "settings.json")
		if _, err := os.Stat(settingsPath); err == nil {
			result.Checks = append(result.Checks, HealthCheck{
				Name: "Settings File", Status: "pass",
				Message: "settings.json found", Score: 10,
			})
			result.Score += 10
		} else {
			result.Checks = append(result.Checks, HealthCheck{
				Name: "Settings File", Status: "warn",
				Message: "No settings.json — using defaults",
			})
			result.Recommendations = append(result.Recommendations, "Run OMNI setup wizard to apply optimized settings")
		}
	}

	// Check 4: System requirements
	sysReqs := hc.detector.CheckSystemRequirements()
	for _, req := range sysReqs {
		if req.Installed {
			result.Checks = append(result.Checks, HealthCheck{
				Name: req.Name, Status: "pass",
				Message: req.Version, Score: 10,
			})
			result.Score += 10
		} else if req.Critical {
			result.Checks = append(result.Checks, HealthCheck{
				Name: req.Name, Status: "fail",
				Message: "Not installed (required)",
			})
			result.Healthy = false
			result.Recommendations = append(result.Recommendations,
				fmt.Sprintf("Install %s: %s", req.Name, req.InstallHint))
		} else {
			result.Checks = append(result.Checks, HealthCheck{
				Name: req.Name, Status: "warn",
				Message: "Not installed (optional)",
			})
		}
	}

	if result.Score < 50 {
		result.Healthy = false
	}

	return result
}

// ─────────────────────────────────────────────
// Section 8: Download Manager
// ─────────────────────────────────────────────

// DownloadManager handles IDE binary downloads with integrity verification.
type DownloadManager struct {
	httpClient *http.Client
	cacheDir   string
}

func NewDownloadManager(cacheDir string) *DownloadManager {
	os.MkdirAll(cacheDir, 0755)
	return &DownloadManager{
		httpClient: &http.Client{Timeout: 300 * time.Second},
		cacheDir:   cacheDir,
	}
}

// DownloadIDE downloads an IDE installer with integrity verification.
func (dm *DownloadManager) DownloadIDE(info *DownloadInfo) (string, error) {
	filename := filepath.Base(info.URL)
	destPath := filepath.Join(dm.cacheDir, filename)

	// Check cache
	if _, err := os.Stat(destPath); err == nil {
		if dm.verifyChecksum(destPath, info.SHA256) {
			log.Printf("[SetupWizard] Using cached download: %s", destPath)
			return destPath, nil
		}
		os.Remove(destPath)
	}

	log.Printf("[SetupWizard] Downloading %s from %s", info.IDE, info.URL)
	resp, err := dm.httpClient.Get(info.URL)
	if err != nil {
		return "", fmt.Errorf("download failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("download failed: HTTP %d", resp.StatusCode)
	}

	out, err := os.Create(destPath)
	if err != nil {
		return "", err
	}
	defer out.Close()

	_, err = io.Copy(out, resp.Body)
	if err != nil {
		os.Remove(destPath)
		return "", err
	}

	// Verify checksum
	if info.SHA256 != "" && !dm.verifyChecksum(destPath, info.SHA256) {
		os.Remove(destPath)
		return "", fmt.Errorf("checksum verification failed")
	}

	return destPath, nil
}

func (dm *DownloadManager) verifyChecksum(filePath string, expected string) bool {
	if expected == "" {
		return true
	}
	f, err := os.Open(filePath)
	if err != nil {
		return false
	}
	defer f.Close()
	h := sha256.New()
	io.Copy(h, f)
	actual := hex.EncodeToString(h.Sum(nil))
	return actual == expected
}

// ─────────────────────────────────────────────
// Section 9: Main Engine
// ─────────────────────────────────────────────

// IDESetupWizardEngine is the OMNI production engine for IDE provisioning.
type IDESetupWizardEngine struct {
	mu           sync.RWMutex
	detector     *PlatformDetector
	profiles     *ConfigProfileManager
	applicator   *ConfigApplicator
	healthCheck  *HealthChecker
	downloads    *DownloadManager
	startedAt    time.Time

	// Stats
	totalSetups     int
	totalHealthChecks int
	totalExtensions int
	totalProfiles   int
	errors          []string
}

// NewIDESetupWizardEngine creates a new wizard engine.
func NewIDESetupWizardEngine(dataDir string) *IDESetupWizardEngine {
	if dataDir == "" {
		home, _ := os.UserHomeDir()
		dataDir = filepath.Join(home, ".omni", "ide_wizard")
	}
	os.MkdirAll(dataDir, 0755)

	engine := &IDESetupWizardEngine{
		detector:    NewPlatformDetector(),
		profiles:    NewConfigProfileManager(filepath.Join(dataDir, "profiles")),
		applicator:  NewConfigApplicator(),
		healthCheck: NewHealthChecker(),
		downloads:   NewDownloadManager(filepath.Join(dataDir, "downloads")),
		startedAt:   time.Now().UTC(),
	}

	log.Println("[OMNI-IDESetupWizard] Engine initialized —", dataDir)
	return engine
}

// SetupIDE performs complete IDE setup: precheck, configure, extensions, verify.
func (engine *IDESetupWizardEngine) SetupIDE(ide IDEType, profileName string) (*SetupProgress, error) {
	progress := &SetupProgress{
		Phase:      PhasePrecheck,
		TotalSteps: 5,
		StartedAt:  time.Now().UTC(),
	}

	// Step 1: Precheck
	progress.CurrentStep = "System requirements check"
	progress.StepIndex = 1
	reqs := engine.detector.CheckSystemRequirements()
	for _, r := range reqs {
		if r.Critical && !r.Installed {
			progress.Errors = append(progress.Errors, fmt.Sprintf("Missing critical dependency: %s", r.Name))
		}
	}
	progress.Messages = append(progress.Messages, fmt.Sprintf("System check complete: %d tools verified", len(reqs)))

	// Step 2: Create configuration
	progress.Phase = PhaseConfigure
	progress.CurrentStep = "Creating OMNI configuration profile"
	progress.StepIndex = 2
	var config *IDEConfiguration
	if profileName == "" || profileName == "omni-production" {
		config = engine.profiles.CreateOmniProfile(ide)
	} else {
		loaded, err := engine.profiles.LoadProfile(profileName)
		if err != nil {
			config = engine.profiles.CreateOmniProfile(ide)
			progress.Warnings = append(progress.Warnings, fmt.Sprintf("Profile '%s' not found, using default", profileName))
		} else {
			config = loaded
		}
	}

	// Step 3: Apply settings
	progress.CurrentStep = "Applying IDE settings"
	progress.StepIndex = 3
	if err := engine.applicator.ApplySettings(config); err != nil {
		progress.Warnings = append(progress.Warnings, fmt.Sprintf("Settings apply warning: %v", err))
	} else {
		progress.Messages = append(progress.Messages, "IDE settings applied successfully")
	}

	// Step 4: Install extensions
	progress.Phase = PhaseExtensions
	progress.CurrentStep = "Installing extensions"
	progress.StepIndex = 4
	extMgr := NewExtensionManager(ide)
	installed, skipped, failed := extMgr.SyncExtensions(config.Extensions)
	progress.Messages = append(progress.Messages,
		fmt.Sprintf("Extensions: %d installed, %d skipped, %d failed", installed, skipped, failed))

	// Step 5: Verify
	progress.Phase = PhaseVerify
	progress.CurrentStep = "Running health check"
	progress.StepIndex = 5
	healthResult := engine.healthCheck.RunHealthCheck(ide)
	progress.Messages = append(progress.Messages,
		fmt.Sprintf("Health score: %d/%d", healthResult.Score, healthResult.MaxScore))

	// Finalize
	if len(progress.Errors) == 0 {
		progress.Phase = PhaseComplete
	} else {
		progress.Phase = PhaseFailed
	}
	progress.ElapsedMs = time.Since(progress.StartedAt).Milliseconds()
	progress.ProgressPct = 100.0

	// Save profile
	engine.profiles.SaveProfile(config)

	engine.mu.Lock()
	engine.totalSetups++
	engine.totalExtensions += installed
	engine.totalProfiles++
	engine.mu.Unlock()

	return progress, nil
}

// RunHealthCheck performs environment health check.
func (engine *IDESetupWizardEngine) RunHealthCheck(ide IDEType) *HealthCheckResult {
	engine.mu.Lock()
	engine.totalHealthChecks++
	engine.mu.Unlock()
	return engine.healthCheck.RunHealthCheck(ide)
}

// GetSystemInfo returns current system information.
func (engine *IDESetupWizardEngine) GetSystemInfo() map[string]interface{} {
	osName, arch := engine.detector.DetectOS()
	reqs := engine.detector.CheckSystemRequirements()

	tools := make(map[string]interface{})
	for _, r := range reqs {
		tools[r.Name] = map[string]interface{}{
			"installed": r.Installed,
			"version":   r.Version,
		}
	}

	return map[string]interface{}{
		"os":           osName,
		"architecture": arch,
		"tools":        tools,
	}
}

// CreateProfile creates and saves a new config profile.
func (engine *IDESetupWizardEngine) CreateProfile(ide IDEType, name string) (*IDEConfiguration, error) {
	config := engine.profiles.CreateOmniProfile(ide)
	config.ProfileName = name
	if err := engine.profiles.SaveProfile(config); err != nil {
		return nil, err
	}
	return config, nil
}

// ListProfiles returns available configuration profiles.
func (engine *IDESetupWizardEngine) ListProfiles() []string {
	return engine.profiles.ListProfiles()
}

// ExportConfig exports an IDE's current settings as JSON.
func (engine *IDESetupWizardEngine) ExportConfig(ide IDEType) (string, error) {
	paths := engine.detector.GetIDEPaths(ide)
	configDir := paths["config"]
	if configDir == "" {
		return "", fmt.Errorf("config path not found for %s", ide)
	}

	settingsPath := filepath.Join(configDir, "settings.json")
	data, err := os.ReadFile(settingsPath)
	if err != nil {
		return "", fmt.Errorf("cannot read settings: %w", err)
	}

	return string(data), nil
}

// Diagnostics returns OMNI-standard diagnostics.
func (engine *IDESetupWizardEngine) Diagnostics() map[string]interface{} {
	engine.mu.RLock()
	defer engine.mu.RUnlock()

	osName, arch := engine.detector.DetectOS()

	return map[string]interface{}{
		"engine":     "IDESetupWizardEngine",
		"version":    "1.0.0",
		"status":     "operational",
		"started_at": engine.startedAt.Format(time.RFC3339),
		"platform": map[string]string{
			"os":   osName,
			"arch": arch,
		},
		"stats": map[string]interface{}{
			"total_setups":        engine.totalSetups,
			"total_health_checks": engine.totalHealthChecks,
			"total_extensions":    engine.totalExtensions,
			"total_profiles":      engine.totalProfiles,
			"errors":              len(engine.errors),
		},
		"capabilities": []string{
			"ide_setup", "config_profiles", "extension_management",
			"health_check", "system_detection", "settings_backup",
			"settings_apply", "download_verify", "config_export",
			"keybinding_sync", "multi_ide_support",
		},
		"supported_ides": []string{
			"cursor", "vscode", "zed", "neovim", "jetbrains", "helix", "windsurf",
		},
	}
}
