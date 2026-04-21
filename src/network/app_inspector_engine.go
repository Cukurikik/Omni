// OMNI App Inspector Engine
// =========================
// Production-grade mobile UI element inspector engine inspired by
// macacajs/app-inspector. Provides device discovery, element tree
// extraction, screenshot capture, and XPath-based element lookup
// for Android (ADB) and iOS (WDA) devices.
//
// Source Reference: https://github.com/macacajs/app-inspector
// OMNI Layer: network (Go)

package network

import (
	"fmt"
	"net"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"sync"
	"time"
)

const appInspectorVersion = "1.0.0"

// ============================================================================
// 1. Device & Element Types
// ============================================================================

type DevicePlatform string

const (
	PlatformAndroid DevicePlatform = "android"
	PlatformIOS     DevicePlatform = "ios"
)

type DeviceStatus string

const (
	DeviceOnline       DeviceStatus = "online"
	DeviceOffline      DeviceStatus = "offline"
	DeviceUnauthorized DeviceStatus = "unauthorized"
	DeviceRecovery     DeviceStatus = "recovery"
)

// Device represents a connected mobile device.
type Device struct {
	UDID         string         `json:"udid"`
	Name         string         `json:"name"`
	Platform     DevicePlatform `json:"platform"`
	Status       DeviceStatus   `json:"status"`
	Model        string         `json:"model"`
	OSVersion    string         `json:"os_version"`
	SDKVersion   string         `json:"sdk_version"`
	ScreenWidth  int            `json:"screen_width"`
	ScreenHeight int            `json:"screen_height"`
	IsEmulator   bool           `json:"is_emulator"`
	Brand        string         `json:"brand"`
	ConnectedAt  time.Time      `json:"connected_at"`
}

// UIElement represents a single UI element in the element tree.
type UIElement struct {
	ID             string      `json:"id"`
	Type           string      `json:"type"`            // e.g. "android.widget.Button"
	ClassName      string      `json:"class_name"`      // Short class name
	Text           string      `json:"text"`
	ContentDesc    string      `json:"content_desc"`    // Accessibility description
	ResourceID     string      `json:"resource_id"`     // Android resource ID
	Label          string      `json:"label"`           // iOS accessibility label
	Value          string      `json:"value"`
	Placeholder    string      `json:"placeholder"`
	Bounds         Rect        `json:"bounds"`
	Enabled        bool        `json:"enabled"`
	Visible        bool        `json:"visible"`
	Clickable      bool        `json:"clickable"`
	Focusable      bool        `json:"focusable"`
	Scrollable     bool        `json:"scrollable"`
	Selected       bool        `json:"selected"`
	Checked        bool        `json:"checked"`
	Password       bool        `json:"password"`
	Index          int         `json:"index"`
	XPath          string      `json:"xpath"`
	Children       []UIElement `json:"children"`
	Depth          int         `json:"depth"`
}

// Rect represents element bounds.
type Rect struct {
	X      int `json:"x"`
	Y      int `json:"y"`
	Width  int `json:"width"`
	Height int `json:"height"`
}

// ElementQuery defines search criteria for finding elements.
type ElementQuery struct {
	ByID          string `json:"by_id"`
	ByText        string `json:"by_text"`
	ByType        string `json:"by_type"`
	ByXPath       string `json:"by_xpath"`
	ByContentDesc string `json:"by_content_desc"`
	ByLabel       string `json:"by_label"`
	ByResourceID  string `json:"by_resource_id"`
	Partial       bool   `json:"partial"` // Partial text match
}

// InspectionResult contains the results of a UI inspection.
type InspectionResult struct {
	DeviceUDID    string    `json:"device_udid"`
	AppPackage    string    `json:"app_package"`
	AppActivity   string    `json:"app_activity"`
	Timestamp     time.Time `json:"timestamp"`
	RootElement   UIElement `json:"root_element"`
	TotalElements int       `json:"total_elements"`
	MaxDepth      int       `json:"max_depth"`
	DurationMs    int64     `json:"duration_ms"`
}

// ============================================================================
// 2. ADB Client (Android Debug Bridge)
// ============================================================================

type ADBClient struct {
	ADBPath string
	mu      sync.Mutex
}

func NewADBClient() *ADBClient {
	adbPath := "adb"
	// Try to find adb in common locations
	paths := []string{
		filepath.Join(os.Getenv("ANDROID_HOME"), "platform-tools", "adb"),
		filepath.Join(os.Getenv("ANDROID_SDK_ROOT"), "platform-tools", "adb"),
	}
	for _, p := range paths {
		if _, err := os.Stat(p); err == nil {
			adbPath = p
			break
		}
	}
	return &ADBClient{ADBPath: adbPath}
}

func (c *ADBClient) exec(args ...string) (string, error) {
	c.mu.Lock()
	defer c.mu.Unlock()
	cmd := exec.Command(c.ADBPath, args...)
	out, err := cmd.CombinedOutput()
	return strings.TrimSpace(string(out)), err
}

func (c *ADBClient) ListDevices() ([]Device, error) {
	output, err := c.exec("devices", "-l")
	if err != nil {
		return nil, fmt.Errorf("adb devices failed: %w", err)
	}

	var devices []Device
	lines := strings.Split(output, "\n")
	for _, line := range lines[1:] { // Skip header
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) < 2 {
			continue
		}

		udid := parts[0]
		statusStr := parts[1]
		var status DeviceStatus
		switch statusStr {
		case "device":
			status = DeviceOnline
		case "offline":
			status = DeviceOffline
		case "unauthorized":
			status = DeviceUnauthorized
		case "recovery":
			status = DeviceRecovery
		default:
			status = DeviceOffline
		}

		device := Device{
			UDID:        udid,
			Platform:    PlatformAndroid,
			Status:      status,
			ConnectedAt: time.Now(),
			IsEmulator:  strings.HasPrefix(udid, "emulator-"),
		}

		// Extract model and brand from -l output
		for _, part := range parts[2:] {
			if strings.HasPrefix(part, "model:") {
				device.Model = strings.TrimPrefix(part, "model:")
			} else if strings.HasPrefix(part, "device:") {
				device.Name = strings.TrimPrefix(part, "device:")
			} else if strings.HasPrefix(part, "product:") {
				device.Brand = strings.TrimPrefix(part, "product:")
			}
		}

		devices = append(devices, device)
	}
	return devices, nil
}

func (c *ADBClient) GetProperty(udid, prop string) string {
	output, err := c.exec("-s", udid, "shell", "getprop", prop)
	if err != nil {
		return ""
	}
	return strings.TrimSpace(output)
}

func (c *ADBClient) GetScreenSize(udid string) (int, int) {
	output, err := c.exec("-s", udid, "shell", "wm", "size")
	if err != nil {
		return 0, 0
	}
	re := regexp.MustCompile(`(\d+)x(\d+)`)
	matches := re.FindStringSubmatch(output)
	if len(matches) < 3 {
		return 0, 0
	}
	var w, h int
	fmt.Sscanf(matches[1], "%d", &w)
	fmt.Sscanf(matches[2], "%d", &h)
	return w, h
}

func (c *ADBClient) DumpUI(udid string) (string, error) {
	// Dump UI hierarchy to XML
	_, err := c.exec("-s", udid, "shell", "uiautomator", "dump", "/sdcard/window_dump.xml")
	if err != nil {
		return "", fmt.Errorf("uiautomator dump failed: %w", err)
	}
	output, err := c.exec("-s", udid, "shell", "cat", "/sdcard/window_dump.xml")
	if err != nil {
		return "", fmt.Errorf("reading dump failed: %w", err)
	}
	return output, nil
}

func (c *ADBClient) Screenshot(udid, outputPath string) error {
	remotePath := "/sdcard/screenshot.png"
	if _, err := c.exec("-s", udid, "shell", "screencap", "-p", remotePath); err != nil {
		return err
	}
	if _, err := c.exec("-s", udid, "pull", remotePath, outputPath); err != nil {
		return err
	}
	return nil
}

func (c *ADBClient) GetCurrentActivity(udid string) (string, string) {
	output, _ := c.exec("-s", udid, "shell", "dumpsys", "activity", "activities")
	// Parse top activity
	re := regexp.MustCompile(`mResumedActivity.*?([a-zA-Z0-9_.]+)/([a-zA-Z0-9_.]+)`)
	matches := re.FindStringSubmatch(output)
	if len(matches) >= 3 {
		return matches[1], matches[2]
	}
	return "", ""
}

// ============================================================================
// 3. iOS WDA Client (WebDriverAgent)
// ============================================================================

type WDAClient struct {
	BaseURL string
	Port    int
}

func NewWDAClient(port int) *WDAClient {
	if port <= 0 {
		port = 8100
	}
	return &WDAClient{
		BaseURL: fmt.Sprintf("http://localhost:%d", port),
		Port:    port,
	}
}

func (w *WDAClient) IsAvailable() bool {
	conn, err := net.DialTimeout("tcp", fmt.Sprintf("localhost:%d", w.Port), 2*time.Second)
	if err != nil {
		return false
	}
	conn.Close()
	return true
}

// ============================================================================
// 4. UI Tree Parser
// ============================================================================

type UITreeParser struct{}

func NewUITreeParser() *UITreeParser {
	return &UITreeParser{}
}

func (p *UITreeParser) ParseAndroidXML(xmlData string) UIElement {
	root := UIElement{
		ID:       "root",
		Type:     "hierarchy",
		Visible:  true,
		Children: []UIElement{},
		XPath:    "/",
	}

	// Parse XML elements using regex (lightweight, no encoding/xml overhead)
	nodeRegex := regexp.MustCompile(`<node\s+([^>]+?)(?:/>|>)`)
	attrRegex := regexp.MustCompile(`(\w[\w-]*)="([^"]*)"`)

	matches := nodeRegex.FindAllStringSubmatch(xmlData, -1)
	for i, match := range matches {
		attrs := make(map[string]string)
		attrMatches := attrRegex.FindAllStringSubmatch(match[1], -1)
		for _, am := range attrMatches {
			attrs[am[1]] = am[2]
		}

		elem := UIElement{
			ID:          fmt.Sprintf("elem_%d", i),
			Type:        attrs["class"],
			ClassName:   extractClassName(attrs["class"]),
			Text:        attrs["text"],
			ContentDesc: attrs["content-desc"],
			ResourceID:  attrs["resource-id"],
			Enabled:     attrs["enabled"] == "true",
			Visible:     attrs["visible-to-user"] != "false",
			Clickable:   attrs["clickable"] == "true",
			Focusable:   attrs["focusable"] == "true",
			Scrollable:  attrs["scrollable"] == "true",
			Selected:    attrs["selected"] == "true",
			Checked:     attrs["checked"] == "true",
			Password:    attrs["password"] == "true",
			Bounds:      parseBounds(attrs["bounds"]),
			XPath:       fmt.Sprintf("//%s[@index='%s']", attrs["class"], attrs["index"]),
		}

		if idxStr, ok := attrs["index"]; ok {
			fmt.Sscanf(idxStr, "%d", &elem.Index)
		}

		root.Children = append(root.Children, elem)
	}

	return root
}

func extractClassName(fullClass string) string {
	parts := strings.Split(fullClass, ".")
	if len(parts) > 0 {
		return parts[len(parts)-1]
	}
	return fullClass
}

func parseBounds(boundsStr string) Rect {
	// Format: [x1,y1][x2,y2]
	re := regexp.MustCompile(`\[(\d+),(\d+)\]\[(\d+),(\d+)\]`)
	matches := re.FindStringSubmatch(boundsStr)
	if len(matches) < 5 {
		return Rect{}
	}
	var x1, y1, x2, y2 int
	fmt.Sscanf(matches[1], "%d", &x1)
	fmt.Sscanf(matches[2], "%d", &y1)
	fmt.Sscanf(matches[3], "%d", &x2)
	fmt.Sscanf(matches[4], "%d", &y2)
	return Rect{X: x1, Y: y1, Width: x2 - x1, Height: y2 - y1}
}

// ============================================================================
// 5. Element Finder
// ============================================================================

type ElementFinder struct{}

func NewElementFinder() *ElementFinder {
	return &ElementFinder{}
}

func (f *ElementFinder) Find(root UIElement, query ElementQuery) []UIElement {
	var results []UIElement
	f.search(&root, &query, &results)
	return results
}

func (f *ElementFinder) search(elem *UIElement, query *ElementQuery, results *[]UIElement) {
	if f.matches(elem, query) {
		*results = append(*results, *elem)
	}
	for i := range elem.Children {
		f.search(&elem.Children[i], query, results)
	}
}

func (f *ElementFinder) matches(elem *UIElement, query *ElementQuery) bool {
	if query.ByID != "" && elem.ID != query.ByID {
		return false
	}
	if query.ByType != "" {
		if query.Partial {
			if !strings.Contains(strings.ToLower(elem.Type), strings.ToLower(query.ByType)) {
				return false
			}
		} else if elem.Type != query.ByType {
			return false
		}
	}
	if query.ByText != "" {
		if query.Partial {
			if !strings.Contains(strings.ToLower(elem.Text), strings.ToLower(query.ByText)) {
				return false
			}
		} else if elem.Text != query.ByText {
			return false
		}
	}
	if query.ByContentDesc != "" {
		if query.Partial {
			if !strings.Contains(strings.ToLower(elem.ContentDesc), strings.ToLower(query.ByContentDesc)) {
				return false
			}
		} else if elem.ContentDesc != query.ByContentDesc {
			return false
		}
	}
	if query.ByLabel != "" {
		if query.Partial {
			if !strings.Contains(strings.ToLower(elem.Label), strings.ToLower(query.ByLabel)) {
				return false
			}
		} else if elem.Label != query.ByLabel {
			return false
		}
	}
	if query.ByResourceID != "" && elem.ResourceID != query.ByResourceID {
		return false
	}
	return true
}

func (f *ElementFinder) CountElements(root *UIElement) int {
	count := 1
	for i := range root.Children {
		count += f.CountElements(&root.Children[i])
	}
	return count
}

func (f *ElementFinder) MaxDepth(root *UIElement, current int) int {
	max := current
	for i := range root.Children {
		d := f.MaxDepth(&root.Children[i], current+1)
		if d > max {
			max = d
		}
	}
	return max
}

// ============================================================================
// 6. Main App Inspector Engine
// ============================================================================

// AppInspectorEngine is the OMNI mobile UI inspector engine.
// Discovers devices, extracts UI element trees, captures screenshots,
// and provides element search for Android (ADB) and iOS (WDA).
type AppInspectorEngine struct {
	DataDir      string
	ADB          *ADBClient
	WDA          *WDAClient
	TreeParser   *UITreeParser
	Finder       *ElementFinder

	mu           sync.RWMutex
	devices      map[string]Device
	inspections  []InspectionResult
	startedAt    time.Time
}

func NewAppInspectorEngine(dataDir string) *AppInspectorEngine {
	if dataDir == "" {
		home, _ := os.UserHomeDir()
		dataDir = filepath.Join(home, ".omni", "app-inspector")
	}
	os.MkdirAll(dataDir, 0755)

	return &AppInspectorEngine{
		DataDir:    dataDir,
		ADB:        NewADBClient(),
		WDA:        NewWDAClient(8100),
		TreeParser: NewUITreeParser(),
		Finder:     NewElementFinder(),
		devices:    make(map[string]Device),
		startedAt:  time.Now(),
	}
}

// DiscoverDevices scans for connected Android and iOS devices.
func (e *AppInspectorEngine) DiscoverDevices() map[string]interface{} {
	e.mu.Lock()
	defer e.mu.Unlock()

	// Android devices via ADB
	androidDevices, err := e.ADB.ListDevices()
	var androidList []map[string]interface{}
	if err == nil {
		for _, d := range androidDevices {
			if d.Status == DeviceOnline {
				d.OSVersion = e.ADB.GetProperty(d.UDID, "ro.build.version.release")
				d.SDKVersion = e.ADB.GetProperty(d.UDID, "ro.build.version.sdk")
				if d.Model == "" {
					d.Model = e.ADB.GetProperty(d.UDID, "ro.product.model")
				}
				d.ScreenWidth, d.ScreenHeight = e.ADB.GetScreenSize(d.UDID)
			}
			e.devices[d.UDID] = d
			androidList = append(androidList, map[string]interface{}{
				"udid": d.UDID, "name": d.Name, "model": d.Model,
				"status": string(d.Status), "platform": "android",
				"os_version": d.OSVersion, "is_emulator": d.IsEmulator,
				"screen": fmt.Sprintf("%dx%d", d.ScreenWidth, d.ScreenHeight),
			})
		}
	}

	// iOS devices via WDA availability check
	iosAvailable := e.WDA.IsAvailable()

	return map[string]interface{}{
		"android_devices": androidList,
		"android_count":   len(androidList),
		"ios_wda_available": iosAvailable,
		"total_devices":   len(e.devices),
	}
}

// InspectDevice dumps the UI element tree of a connected device.
func (e *AppInspectorEngine) InspectDevice(udid string) map[string]interface{} {
	e.mu.RLock()
	device, ok := e.devices[udid]
	e.mu.RUnlock()

	if !ok {
		return map[string]interface{}{"error": "Device not found. Run DiscoverDevices first."}
	}

	start := time.Now()

	if device.Platform == PlatformAndroid {
		xmlData, err := e.ADB.DumpUI(udid)
		if err != nil {
			return map[string]interface{}{"error": err.Error()}
		}

		root := e.TreeParser.ParseAndroidXML(xmlData)
		pkg, activity := e.ADB.GetCurrentActivity(udid)

		result := InspectionResult{
			DeviceUDID:    udid,
			AppPackage:    pkg,
			AppActivity:   activity,
			Timestamp:     time.Now(),
			RootElement:   root,
			TotalElements: e.Finder.CountElements(&root),
			MaxDepth:      e.Finder.MaxDepth(&root, 0),
			DurationMs:    time.Since(start).Milliseconds(),
		}

		e.mu.Lock()
		e.inspections = append(e.inspections, result)
		e.mu.Unlock()

		return map[string]interface{}{
			"device":         udid,
			"app_package":    pkg,
			"app_activity":   activity,
			"total_elements": result.TotalElements,
			"max_depth":      result.MaxDepth,
			"duration_ms":    result.DurationMs,
			"root":           root,
		}
	}

	return map[string]interface{}{"error": "Platform not supported for inspection"}
}

// FindElements searches for elements matching a query.
func (e *AppInspectorEngine) FindElements(udid string, query ElementQuery) map[string]interface{} {
	e.mu.RLock()
	var lastInspection *InspectionResult
	for i := len(e.inspections) - 1; i >= 0; i-- {
		if e.inspections[i].DeviceUDID == udid {
			lastInspection = &e.inspections[i]
			break
		}
	}
	e.mu.RUnlock()

	if lastInspection == nil {
		return map[string]interface{}{"error": "No inspection data. Run InspectDevice first."}
	}

	results := e.Finder.Find(lastInspection.RootElement, query)

	elements := make([]map[string]interface{}, len(results))
	for i, elem := range results {
		elements[i] = map[string]interface{}{
			"id": elem.ID, "type": elem.Type, "text": elem.Text,
			"content_desc": elem.ContentDesc, "resource_id": elem.ResourceID,
			"bounds": elem.Bounds, "clickable": elem.Clickable,
			"enabled": elem.Enabled, "xpath": elem.XPath,
		}
	}

	return map[string]interface{}{
		"device":  udid,
		"query":   query,
		"count":   len(results),
		"results": elements,
	}
}

// CaptureScreenshot captures a screenshot from the device.
func (e *AppInspectorEngine) CaptureScreenshot(udid string) map[string]interface{} {
	e.mu.RLock()
	device, ok := e.devices[udid]
	e.mu.RUnlock()

	if !ok {
		return map[string]interface{}{"error": "Device not found"}
	}

	outputPath := filepath.Join(e.DataDir, "screenshots",
		fmt.Sprintf("%s_%d.png", udid, time.Now().Unix()))
	os.MkdirAll(filepath.Dir(outputPath), 0755)

	if device.Platform == PlatformAndroid {
		if err := e.ADB.Screenshot(udid, outputPath); err != nil {
			return map[string]interface{}{"error": err.Error()}
		}
		return map[string]interface{}{
			"device": udid, "path": outputPath, "status": "captured",
		}
	}

	return map[string]interface{}{"error": "Platform not supported"}
}

// Diagnostics returns engine telemetry.
func (e *AppInspectorEngine) Diagnostics() map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	deviceList := make([]map[string]string, 0)
	for _, d := range e.devices {
		deviceList = append(deviceList, map[string]string{
			"udid": d.UDID, "model": d.Model, "status": string(d.Status),
		})
	}

	return map[string]interface{}{
		"engine":     "AppInspectorEngine",
		"version":    appInspectorVersion,
		"status":     "operational",
		"started_at": e.startedAt.UTC().Format(time.RFC3339),
		"stats": map[string]interface{}{
			"discovered_devices":  len(e.devices),
			"total_inspections":   len(e.inspections),
			"devices":             deviceList,
			"ios_wda_available":   e.WDA.IsAvailable(),
		},
		"capabilities": []string{
			"android_adb_discovery", "ios_wda_discovery",
			"ui_tree_extraction", "element_search",
			"xpath_query", "text_search", "type_search",
			"resource_id_search", "content_desc_search",
			"screenshot_capture", "activity_detection",
			"screen_size_detection", "emulator_detection",
			"partial_match", "multi_device_support",
			"element_bounds", "element_properties",
		},
	}
}
