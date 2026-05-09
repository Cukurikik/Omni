// =============================================================================
// OMNI FRAMEWORK — LNXLINK MQTT SYSTEM MONITOR ENGINE
// Layer: Network | Language: Go | Source: github.com/bkbilly/lnxlink
// =============================================================================
// Production-grade Linux system monitoring and control engine via MQTT.
// Provides Home Assistant integration with MQTT autodiscovery, modular sensor
// architecture, and remote command execution for fleet-wide Linux management.
// =============================================================================

package network

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"strings"
	"sync"
	"time"
)

// ---------------------------------------------------------------------------
// Section 1: Core Data Structures
// ---------------------------------------------------------------------------

// MQTTBrokerConfig holds MQTT broker connection parameters.
type MQTTBrokerConfig struct {
	Host         string `json:"host"`
	Port         int    `json:"port"`
	Username     string `json:"username"`
	Password     string `json:"password"`
	TLSEnabled   bool   `json:"tls_enabled"`
	TLSCertPath  string `json:"tls_cert_path"`
	ClientID     string `json:"client_id"`
	KeepAlive    int    `json:"keep_alive_seconds"`
	CleanSession bool   `json:"clean_session"`
	QoS          int    `json:"qos"` // 0, 1, or 2
}

// LNXlinkMachineConfig represents a monitored Linux machine.
type LNXlinkMachineConfig struct {
	MachineID   string            `json:"machine_id"`
	Hostname    string            `json:"hostname"`
	TopicPrefix string            `json:"topic_prefix"` // e.g., "lnxlink/desktop1"
	Modules     []string          `json:"modules"`      // enabled sensor modules
	Interval    int               `json:"interval_sec"` // poll interval
	Labels      map[string]string `json:"labels"`
	Registered  time.Time         `json:"registered_at"`
}

// SensorType enumerates the types of sensors LNXlink supports.
type SensorType string

const (
	SensorCPU         SensorType = "cpu"
	SensorMemory      SensorType = "memory"
	SensorDisk        SensorType = "disk"
	SensorNetwork     SensorType = "network_stats"
	SensorBattery     SensorType = "battery"
	SensorTemperature SensorType = "temperature"
	SensorUptime      SensorType = "uptime"
	SensorDisplay     SensorType = "display"
	SensorAudio       SensorType = "audio"
	SensorMedia       SensorType = "media_player"
	SensorBluetooth   SensorType = "bluetooth"
	SensorNotify      SensorType = "notify"
	SensorScreenshot  SensorType = "screenshot"
	SensorSuspend     SensorType = "suspend"
	SensorShutdown    SensorType = "shutdown"
	SensorReboot      SensorType = "reboot"
	SensorBash        SensorType = "bash_command"
	SensorCamera      SensorType = "camera"
	SensorMicrophone  SensorType = "microphone"
	SensorGPU         SensorType = "gpu"
	SensorDocker      SensorType = "docker"
	SensorSystemD     SensorType = "systemd"
	SensorPackages    SensorType = "packages"
	SensorIdletime    SensorType = "idle_time"
	SensorKeepAlive   SensorType = "keep_alive"
)

// SensorReading represents a single sensor data point.
type SensorReading struct {
	SensorName string                 `json:"sensor_name"`
	SensorType SensorType             `json:"sensor_type"`
	Value      interface{}            `json:"value"`
	Unit       string                 `json:"unit,omitempty"`
	Attributes map[string]interface{} `json:"attributes,omitempty"`
	Timestamp  time.Time              `json:"timestamp"`
	MachineID  string                 `json:"machine_id"`
	Available  bool                   `json:"available"`
}

// HASSDiscoveryPayload is the MQTT autodiscovery payload for Home Assistant.
type HASSDiscoveryPayload struct {
	Name                string         `json:"name"`
	UniqueID            string         `json:"unique_id"`
	StateTopic          string         `json:"state_topic"`
	CommandTopic        string         `json:"command_topic,omitempty"`
	AvailabilityTopic   string         `json:"availability_topic"`
	DeviceClass         string         `json:"device_class,omitempty"`
	UnitOfMeasurement   string         `json:"unit_of_measurement,omitempty"`
	ValueTemplate       string         `json:"value_template,omitempty"`
	Icon                string         `json:"icon,omitempty"`
	PayloadAvailable    string         `json:"payload_available"`
	PayloadNotAvailable string         `json:"payload_not_available"`
	Device              HASSDeviceInfo `json:"device"`
}

// HASSDeviceInfo identifies the device for HA grouping.
type HASSDeviceInfo struct {
	Identifiers  []string `json:"identifiers"`
	Name         string   `json:"name"`
	Model        string   `json:"model"`
	Manufacturer string   `json:"manufacturer"`
	SWVersion    string   `json:"sw_version,omitempty"`
}

// RemoteCommand is a command to execute on a managed machine.
type RemoteCommand struct {
	CommandID   string            `json:"command_id"`
	MachineID   string            `json:"machine_id"`
	CommandType string            `json:"command_type"` // bash, shutdown, reboot, suspend, notify, etc.
	Payload     string            `json:"payload"`
	Parameters  map[string]string `json:"parameters,omitempty"`
	IssuedAt    time.Time         `json:"issued_at"`
	Timeout     int               `json:"timeout_seconds"`
}

// CommandResult captures the result of a remote command execution.
type CommandResult struct {
	CommandID  string    `json:"command_id"`
	MachineID  string    `json:"machine_id"`
	ExitCode   int       `json:"exit_code"`
	Stdout     string    `json:"stdout"`
	Stderr     string    `json:"stderr"`
	StartedAt  time.Time `json:"started_at"`
	FinishedAt time.Time `json:"finished_at"`
	Success    bool      `json:"success"`
}

// MQTTMessage represents an MQTT message to publish or that was received.
type MQTTMessage struct {
	Topic    string    `json:"topic"`
	Payload  []byte    `json:"payload"`
	QoS      int       `json:"qos"`
	Retained bool      `json:"retained"`
	RecvAt   time.Time `json:"received_at"`
}

// AutomationRule defines a rule for automated actions based on sensor data.
type AutomationRule struct {
	RuleID      string                 `json:"rule_id"`
	Name        string                 `json:"name"`
	MachineID   string                 `json:"machine_id"`
	SensorType  SensorType             `json:"sensor_type"`
	Condition   string                 `json:"condition"` // gt, lt, eq, ne, contains
	Threshold   interface{}            `json:"threshold"`
	Action      RemoteCommand          `json:"action"`
	Cooldown    int                    `json:"cooldown_seconds"`
	LastTrigged time.Time              `json:"last_triggered"`
	Enabled     bool                   `json:"enabled"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
}

// ---------------------------------------------------------------------------
// Section 2: LNXlink MQTT Engine
// ---------------------------------------------------------------------------

// LNXlinkMQTTEngine is the production-grade engine for Linux fleet monitoring.
type LNXlinkMQTTEngine struct {
	mu sync.RWMutex

	// Broker connection config
	brokerConfig MQTTBrokerConfig

	// Machine registry
	machines map[string]*LNXlinkMachineConfig

	// Sensor data store: machineID -> sensorType -> latest reading
	sensorData map[string]map[SensorType]*SensorReading

	// HA autodiscovery payloads published
	discoveryPayloads map[string]*HASSDiscoveryPayload

	// Remote command history
	commandHistory []CommandResult
	pendingCmds    map[string]*RemoteCommand

	// Automation rules
	automationRules map[string]*AutomationRule

	// Message bus: all published/received messages log
	messageLog []MQTTMessage

	// Subscriptions: topic -> list of callback IDs
	subscriptions map[string][]string

	// Statistics
	stats LNXlinkStats

	// Engine metadata
	engineVersion string
	startedAt     time.Time
}

// LNXlinkStats tracks engine-level statistics.
type LNXlinkStats struct {
	TotalMachines       int       `json:"total_machines"`
	TotalReadings       int64     `json:"total_readings"`
	TotalCommandsSent   int64     `json:"total_commands_sent"`
	TotalCommandsOK     int64     `json:"total_commands_ok"`
	TotalCommandsFailed int64     `json:"total_commands_failed"`
	TotalMessagesIn     int64     `json:"total_messages_in"`
	TotalMessagesOut    int64     `json:"total_messages_out"`
	TotalAutomations    int       `json:"total_automations"`
	TotalRulesFired     int64     `json:"total_rules_fired"`
	DiscoveryPublished  int       `json:"discovery_published"`
	LastActivity        time.Time `json:"last_activity"`
}

// NewLNXlinkMQTTEngine creates a new fleet monitoring engine.
func NewLNXlinkMQTTEngine(broker MQTTBrokerConfig) *LNXlinkMQTTEngine {
	if broker.ClientID == "" {
		b := make([]byte, 6)
		rand.Read(b)
		broker.ClientID = "omni-lnxlink-" + hex.EncodeToString(b)
	}
	if broker.Port == 0 {
		broker.Port = 1883
	}
	if broker.KeepAlive == 0 {
		broker.KeepAlive = 60
	}
	if broker.QoS < 0 || broker.QoS > 2 {
		broker.QoS = 1
	}

	return &LNXlinkMQTTEngine{
		brokerConfig:      broker,
		machines:          make(map[string]*LNXlinkMachineConfig),
		sensorData:        make(map[string]map[SensorType]*SensorReading),
		discoveryPayloads: make(map[string]*HASSDiscoveryPayload),
		commandHistory:    make([]CommandResult, 0, 1000),
		pendingCmds:       make(map[string]*RemoteCommand),
		automationRules:   make(map[string]*AutomationRule),
		messageLog:        make([]MQTTMessage, 0, 5000),
		subscriptions:     make(map[string][]string),
		engineVersion:     "2026.4.0-omni",
		startedAt:         time.Now(),
	}
}

// ---------------------------------------------------------------------------
// Section 3: Machine Registration
// ---------------------------------------------------------------------------

// RegisterMachine adds a Linux machine to the monitoring fleet.
func (e *LNXlinkMQTTEngine) RegisterMachine(cfg LNXlinkMachineConfig) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	if cfg.MachineID == "" {
		return fmt.Errorf("machine_id is required")
	}
	if cfg.Hostname == "" {
		return fmt.Errorf("hostname is required for machine %s", cfg.MachineID)
	}
	if cfg.TopicPrefix == "" {
		cfg.TopicPrefix = "lnxlink/" + cfg.Hostname
	}
	if cfg.Interval <= 0 {
		cfg.Interval = 15
	}
	if len(cfg.Modules) == 0 {
		cfg.Modules = []string{"cpu", "memory", "disk", "network_stats", "uptime", "keep_alive"}
	}
	cfg.Registered = time.Now()

	e.machines[cfg.MachineID] = &cfg
	e.sensorData[cfg.MachineID] = make(map[SensorType]*SensorReading)
	e.stats.TotalMachines = len(e.machines)

	// Publish HA autodiscovery for each enabled module
	for _, mod := range cfg.Modules {
		e.publishDiscovery(cfg, SensorType(mod))
	}

	return nil
}

// UnregisterMachine removes a machine from monitoring and publishes offline status.
func (e *LNXlinkMQTTEngine) UnregisterMachine(machineID string) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	_, exists := e.machines[machineID]
	if !exists {
		return fmt.Errorf("machine %s not found", machineID)
	}

	// Publish offline availability
	e.publishMessage(e.machines[machineID].TopicPrefix+"/availability", []byte("offline"), true)

	delete(e.machines, machineID)
	delete(e.sensorData, machineID)
	e.stats.TotalMachines = len(e.machines)
	return nil
}

// ListMachines returns all registered machines.
func (e *LNXlinkMQTTEngine) ListMachines() []*LNXlinkMachineConfig {
	e.mu.RLock()
	defer e.mu.RUnlock()

	result := make([]*LNXlinkMachineConfig, 0, len(e.machines))
	for _, m := range e.machines {
		result = append(result, m)
	}
	return result
}

// ---------------------------------------------------------------------------
// Section 4: Home Assistant MQTT Autodiscovery
// ---------------------------------------------------------------------------

// publishDiscovery generates and stores the HA autodiscovery payload for a sensor.
func (e *LNXlinkMQTTEngine) publishDiscovery(cfg LNXlinkMachineConfig, sType SensorType) {
	uniqueID := fmt.Sprintf("lnxlink_%s_%s", cfg.MachineID, sType)
	discoveryTopic := fmt.Sprintf("homeassistant/sensor/%s/%s/config", cfg.MachineID, sType)

	payload := &HASSDiscoveryPayload{
		Name:                fmt.Sprintf("%s %s", cfg.Hostname, humanizeSensorType(sType)),
		UniqueID:            uniqueID,
		StateTopic:          fmt.Sprintf("%s/%s/state", cfg.TopicPrefix, sType),
		AvailabilityTopic:   cfg.TopicPrefix + "/availability",
		DeviceClass:         mapSensorDeviceClass(sType),
		UnitOfMeasurement:   mapSensorUnit(sType),
		ValueTemplate:       "{{ value_json.value }}",
		Icon:                mapSensorIcon(sType),
		PayloadAvailable:    "online",
		PayloadNotAvailable: "offline",
		Device: HASSDeviceInfo{
			Identifiers:  []string{cfg.MachineID},
			Name:         cfg.Hostname,
			Model:        "Linux Workstation",
			Manufacturer: "OMNI LNXlink",
			SWVersion:    "2026.4.0-omni",
		},
	}

	// For controllable sensors, add command topic
	if isControllableSensor(sType) {
		payload.CommandTopic = fmt.Sprintf("%s/%s/set", cfg.TopicPrefix, sType)
	}

	e.discoveryPayloads[discoveryTopic] = payload
	e.stats.DiscoveryPublished++

	data, _ := json.Marshal(payload)
	e.publishMessage(discoveryTopic, data, true)
}

// PublishAllDiscovery re-publishes all discovery payloads (useful after reconnect).
func (e *LNXlinkMQTTEngine) PublishAllDiscovery() int {
	e.mu.Lock()
	defer e.mu.Unlock()

	count := 0
	for _, machine := range e.machines {
		for _, mod := range machine.Modules {
			e.publishDiscovery(*machine, SensorType(mod))
			count++
		}
	}
	return count
}

// ---------------------------------------------------------------------------
// Section 5: Sensor Data Ingestion
// ---------------------------------------------------------------------------

// IngestSensorReading processes an incoming sensor reading from a machine.
func (e *LNXlinkMQTTEngine) IngestSensorReading(reading SensorReading) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	if reading.MachineID == "" {
		return fmt.Errorf("machine_id is required in sensor reading")
	}
	_, exists := e.machines[reading.MachineID]
	if !exists {
		return fmt.Errorf("machine %s is not registered", reading.MachineID)
	}

	if reading.Timestamp.IsZero() {
		reading.Timestamp = time.Now()
	}
	reading.Available = true

	e.sensorData[reading.MachineID][reading.SensorType] = &reading
	e.stats.TotalReadings++
	e.stats.LastActivity = time.Now()

	// Publish to MQTT state topic
	stateTopic := fmt.Sprintf("%s/%s/state", e.machines[reading.MachineID].TopicPrefix, reading.SensorType)
	data, _ := json.Marshal(reading)
	e.publishMessage(stateTopic, data, false)

	// Evaluate automation rules
	e.evaluateRules(reading)

	return nil
}

// GetLatestReading retrieves the latest sensor reading for a machine/sensor combo.
func (e *LNXlinkMQTTEngine) GetLatestReading(machineID string, sType SensorType) (*SensorReading, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	machineData, ok := e.sensorData[machineID]
	if !ok {
		return nil, fmt.Errorf("machine %s not found", machineID)
	}
	reading, ok := machineData[sType]
	if !ok {
		return nil, fmt.Errorf("no reading for sensor %s on machine %s", sType, machineID)
	}
	return reading, nil
}

// GetAllReadings returns all latest readings for a machine.
func (e *LNXlinkMQTTEngine) GetAllReadings(machineID string) (map[SensorType]*SensorReading, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	data, ok := e.sensorData[machineID]
	if !ok {
		return nil, fmt.Errorf("machine %s not found", machineID)
	}
	result := make(map[SensorType]*SensorReading, len(data))
	for k, v := range data {
		result[k] = v
	}
	return result, nil
}

// ---------------------------------------------------------------------------
// Section 6: Remote Command Execution
// ---------------------------------------------------------------------------

// SendCommand dispatches a remote command to a managed machine via MQTT.
func (e *LNXlinkMQTTEngine) SendCommand(cmd RemoteCommand) (string, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	machine, exists := e.machines[cmd.MachineID]
	if !exists {
		return "", fmt.Errorf("machine %s not registered", cmd.MachineID)
	}

	if cmd.CommandID == "" {
		b := make([]byte, 8)
		rand.Read(b)
		cmd.CommandID = "cmd-" + hex.EncodeToString(b)
	}
	if cmd.Timeout <= 0 {
		cmd.Timeout = 30
	}
	cmd.IssuedAt = time.Now()

	// Determine MQTT topic for command
	cmdTopic := fmt.Sprintf("%s/commands/%s", machine.TopicPrefix, cmd.CommandType)

	data, _ := json.Marshal(cmd)
	e.publishMessage(cmdTopic, data, false)

	e.pendingCmds[cmd.CommandID] = &cmd
	e.stats.TotalCommandsSent++
	e.stats.LastActivity = time.Now()

	return cmd.CommandID, nil
}

// ExecuteBashCommand is a convenience method for sending a bash command.
func (e *LNXlinkMQTTEngine) ExecuteBashCommand(machineID, script string, timeout int) (string, error) {
	return e.SendCommand(RemoteCommand{
		MachineID:   machineID,
		CommandType: "bash_command",
		Payload:     script,
		Timeout:     timeout,
	})
}

// SendNotification sends a desktop notification to a managed machine.
func (e *LNXlinkMQTTEngine) SendNotification(machineID, title, message, icon string) (string, error) {
	return e.SendCommand(RemoteCommand{
		MachineID:   machineID,
		CommandType: "notify",
		Payload:     message,
		Parameters: map[string]string{
			"title": title,
			"icon":  icon,
		},
	})
}

// SendPowerCommand sends shutdown/reboot/suspend commands.
func (e *LNXlinkMQTTEngine) SendPowerCommand(machineID string, action string) (string, error) {
	validActions := map[string]bool{"shutdown": true, "reboot": true, "suspend": true, "hibernate": true}
	if !validActions[action] {
		return "", fmt.Errorf("invalid power action: %s, must be shutdown/reboot/suspend/hibernate", action)
	}
	return e.SendCommand(RemoteCommand{
		MachineID:   machineID,
		CommandType: action,
		Payload:     action,
		Timeout:     10,
	})
}

// RecordCommandResult processes the result of a command execution.
func (e *LNXlinkMQTTEngine) RecordCommandResult(result CommandResult) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	if result.FinishedAt.IsZero() {
		result.FinishedAt = time.Now()
	}
	result.Success = result.ExitCode == 0

	if result.Success {
		e.stats.TotalCommandsOK++
	} else {
		e.stats.TotalCommandsFailed++
	}

	// Remove from pending
	delete(e.pendingCmds, result.CommandID)

	// Cap command history at 1000
	if len(e.commandHistory) >= 1000 {
		e.commandHistory = e.commandHistory[1:]
	}
	e.commandHistory = append(e.commandHistory, result)

	return nil
}

// GetCommandHistory returns recent command results.
func (e *LNXlinkMQTTEngine) GetCommandHistory(machineID string, limit int) []CommandResult {
	e.mu.RLock()
	defer e.mu.RUnlock()

	if limit <= 0 {
		limit = 50
	}

	var results []CommandResult
	for i := len(e.commandHistory) - 1; i >= 0 && len(results) < limit; i-- {
		if machineID == "" || e.commandHistory[i].MachineID == machineID {
			results = append(results, e.commandHistory[i])
		}
	}
	return results
}

// ---------------------------------------------------------------------------
// Section 7: Automation Rules
// ---------------------------------------------------------------------------

// AddAutomationRule registers a rule that triggers actions based on sensor data.
func (e *LNXlinkMQTTEngine) AddAutomationRule(rule AutomationRule) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	if rule.RuleID == "" {
		b := make([]byte, 6)
		rand.Read(b)
		rule.RuleID = "rule-" + hex.EncodeToString(b)
	}
	if rule.MachineID == "" {
		return fmt.Errorf("machine_id is required for automation rule")
	}
	if _, exists := e.machines[rule.MachineID]; !exists {
		return fmt.Errorf("machine %s not registered", rule.MachineID)
	}
	if rule.Cooldown <= 0 {
		rule.Cooldown = 60
	}
	rule.Enabled = true

	e.automationRules[rule.RuleID] = &rule
	e.stats.TotalAutomations = len(e.automationRules)
	return nil
}

// RemoveAutomationRule deletes a rule.
func (e *LNXlinkMQTTEngine) RemoveAutomationRule(ruleID string) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	if _, exists := e.automationRules[ruleID]; !exists {
		return fmt.Errorf("rule %s not found", ruleID)
	}
	delete(e.automationRules, ruleID)
	e.stats.TotalAutomations = len(e.automationRules)
	return nil
}

// evaluateRules checks if a new reading triggers any automation rules.
func (e *LNXlinkMQTTEngine) evaluateRules(reading SensorReading) {
	for _, rule := range e.automationRules {
		if !rule.Enabled {
			continue
		}
		if rule.MachineID != reading.MachineID || rule.SensorType != reading.SensorType {
			continue
		}
		// Cooldown check
		if time.Since(rule.LastTrigged) < time.Duration(rule.Cooldown)*time.Second {
			continue
		}

		if e.evaluateCondition(reading.Value, rule.Condition, rule.Threshold) {
			rule.LastTrigged = time.Now()
			e.stats.TotalRulesFired++

			// Fire the action (enqueue command)
			cmd := rule.Action
			cmd.MachineID = rule.MachineID
			cmd.IssuedAt = time.Now()
			b := make([]byte, 8)
			rand.Read(b)
			cmd.CommandID = "auto-" + hex.EncodeToString(b)
			e.pendingCmds[cmd.CommandID] = &cmd
			e.stats.TotalCommandsSent++
		}
	}
}

// evaluateCondition checks a value against a condition and threshold.
func (e *LNXlinkMQTTEngine) evaluateCondition(value interface{}, condition string, threshold interface{}) bool {
	valFloat, valOK := toFloat64(value)
	thrFloat, thrOK := toFloat64(threshold)

	if valOK && thrOK {
		switch condition {
		case "gt":
			return valFloat > thrFloat
		case "lt":
			return valFloat < thrFloat
		case "gte":
			return valFloat >= thrFloat
		case "lte":
			return valFloat <= thrFloat
		case "eq":
			return valFloat == thrFloat
		case "ne":
			return valFloat != thrFloat
		}
	}

	// String comparison
	valStr := fmt.Sprintf("%v", value)
	thrStr := fmt.Sprintf("%v", threshold)
	switch condition {
	case "eq":
		return valStr == thrStr
	case "ne":
		return valStr != thrStr
	case "contains":
		return strings.Contains(valStr, thrStr)
	}

	return false
}

// ---------------------------------------------------------------------------
// Section 8: MQTT Message Bus
// ---------------------------------------------------------------------------

// publishMessage simulates publishing to MQTT broker and logs the message.
func (e *LNXlinkMQTTEngine) publishMessage(topic string, payload []byte, retained bool) {
	msg := MQTTMessage{
		Topic:    topic,
		Payload:  payload,
		QoS:      e.brokerConfig.QoS,
		Retained: retained,
		RecvAt:   time.Now(),
	}

	// Cap log at 5000
	if len(e.messageLog) >= 5000 {
		e.messageLog = e.messageLog[100:]
	}
	e.messageLog = append(e.messageLog, msg)
	e.stats.TotalMessagesOut++
}

// Subscribe registers a topic subscription.
func (e *LNXlinkMQTTEngine) Subscribe(topic string, callbackID string) {
	e.mu.Lock()
	defer e.mu.Unlock()

	e.subscriptions[topic] = append(e.subscriptions[topic], callbackID)
}

// Unsubscribe removes a topic subscription.
func (e *LNXlinkMQTTEngine) Unsubscribe(topic string) {
	e.mu.Lock()
	defer e.mu.Unlock()
	delete(e.subscriptions, topic)
}

// HandleIncomingMessage processes a received MQTT message.
func (e *LNXlinkMQTTEngine) HandleIncomingMessage(msg MQTTMessage) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	msg.RecvAt = time.Now()
	e.stats.TotalMessagesIn++
	e.stats.LastActivity = time.Now()

	if len(e.messageLog) >= 5000 {
		e.messageLog = e.messageLog[100:]
	}
	e.messageLog = append(e.messageLog, msg)

	// Parse topic to determine action
	parts := strings.Split(msg.Topic, "/")
	if len(parts) < 3 {
		return fmt.Errorf("invalid topic format: %s", msg.Topic)
	}

	// Check if it's a command result
	if len(parts) >= 4 && parts[len(parts)-2] == "result" {
		var result CommandResult
		if err := json.Unmarshal(msg.Payload, &result); err == nil {
			return e.recordResultInternal(result)
		}
	}

	// Check if it's a sensor reading
	if len(parts) >= 3 && parts[len(parts)-1] == "state" {
		var reading SensorReading
		if err := json.Unmarshal(msg.Payload, &reading); err == nil {
			e.sensorData[reading.MachineID][reading.SensorType] = &reading
			e.stats.TotalReadings++
		}
	}

	return nil
}

func (e *LNXlinkMQTTEngine) recordResultInternal(result CommandResult) error {
	if result.FinishedAt.IsZero() {
		result.FinishedAt = time.Now()
	}
	result.Success = result.ExitCode == 0
	if result.Success {
		e.stats.TotalCommandsOK++
	} else {
		e.stats.TotalCommandsFailed++
	}
	delete(e.pendingCmds, result.CommandID)
	if len(e.commandHistory) >= 1000 {
		e.commandHistory = e.commandHistory[1:]
	}
	e.commandHistory = append(e.commandHistory, result)
	return nil
}

// ---------------------------------------------------------------------------
// Section 9: Media Player Control (via MQTT)
// ---------------------------------------------------------------------------

// MediaAction represents a media player control action.
type MediaAction string

const (
	MediaPlay       MediaAction = "play"
	MediaPause      MediaAction = "pause"
	MediaStop       MediaAction = "stop"
	MediaNext       MediaAction = "next"
	MediaPrevious   MediaAction = "previous"
	MediaVolumeUp   MediaAction = "volume_up"
	MediaVolumeDown MediaAction = "volume_down"
	MediaVolumeMute MediaAction = "volume_mute"
	MediaSetVolume  MediaAction = "set_volume"
)

// ControlMediaPlayer sends a media player command to a machine.
func (e *LNXlinkMQTTEngine) ControlMediaPlayer(machineID string, action MediaAction, value string) (string, error) {
	params := map[string]string{"action": string(action)}
	if value != "" {
		params["value"] = value
	}
	return e.SendCommand(RemoteCommand{
		MachineID:   machineID,
		CommandType: "media_player",
		Payload:     string(action),
		Parameters:  params,
	})
}

// ---------------------------------------------------------------------------
// Section 10: Display & Audio Control
// ---------------------------------------------------------------------------

// SetBrightness adjusts the display brightness on a managed machine.
func (e *LNXlinkMQTTEngine) SetBrightness(machineID string, level int) (string, error) {
	if level < 0 || level > 100 {
		return "", fmt.Errorf("brightness level must be 0-100, got %d", level)
	}
	return e.SendCommand(RemoteCommand{
		MachineID:   machineID,
		CommandType: "display",
		Payload:     fmt.Sprintf("%d", level),
		Parameters:  map[string]string{"action": "set_brightness"},
	})
}

// SetAudioVolume adjusts the system audio volume.
func (e *LNXlinkMQTTEngine) SetAudioVolume(machineID string, level int) (string, error) {
	if level < 0 || level > 100 {
		return "", fmt.Errorf("volume level must be 0-100, got %d", level)
	}
	return e.SendCommand(RemoteCommand{
		MachineID:   machineID,
		CommandType: "audio",
		Payload:     fmt.Sprintf("%d", level),
		Parameters:  map[string]string{"action": "set_volume"},
	})
}

// ---------------------------------------------------------------------------
// Section 11: Docker & SystemD Service Management
// ---------------------------------------------------------------------------

// ManageDockerContainer sends a Docker container management command.
func (e *LNXlinkMQTTEngine) ManageDockerContainer(machineID, containerName, action string) (string, error) {
	validActions := map[string]bool{"start": true, "stop": true, "restart": true, "pause": true, "unpause": true, "remove": true}
	if !validActions[action] {
		return "", fmt.Errorf("invalid docker action: %s", action)
	}
	return e.SendCommand(RemoteCommand{
		MachineID:   machineID,
		CommandType: "docker",
		Payload:     containerName,
		Parameters:  map[string]string{"action": action},
	})
}

// ManageSystemDService sends a systemd service management command.
func (e *LNXlinkMQTTEngine) ManageSystemDService(machineID, serviceName, action string) (string, error) {
	validActions := map[string]bool{"start": true, "stop": true, "restart": true, "enable": true, "disable": true, "status": true}
	if !validActions[action] {
		return "", fmt.Errorf("invalid systemd action: %s", action)
	}
	return e.SendCommand(RemoteCommand{
		MachineID:   machineID,
		CommandType: "systemd",
		Payload:     serviceName,
		Parameters:  map[string]string{"action": action},
	})
}

// ---------------------------------------------------------------------------
// Section 12: Fleet Diagnostics & Statistics
// ---------------------------------------------------------------------------

// GetStats returns the current engine statistics.
func (e *LNXlinkMQTTEngine) GetStats() LNXlinkStats {
	e.mu.RLock()
	defer e.mu.RUnlock()
	return e.stats
}

// GetFleetHealth returns the health status of all machines.
func (e *LNXlinkMQTTEngine) GetFleetHealth() map[string]map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	fleet := make(map[string]map[string]interface{})
	for id, machine := range e.machines {
		health := map[string]interface{}{
			"hostname":      machine.Hostname,
			"topic_prefix":  machine.TopicPrefix,
			"modules":       machine.Modules,
			"registered_at": machine.Registered,
			"sensor_count":  len(e.sensorData[id]),
		}

		// Check if we have recent data (within 2x the interval)
		hasRecentData := false
		for _, reading := range e.sensorData[id] {
			if time.Since(reading.Timestamp) < time.Duration(machine.Interval*2)*time.Second {
				hasRecentData = true
				break
			}
		}
		health["online"] = hasRecentData
		fleet[id] = health
	}
	return fleet
}

// Diagnostics returns engine self-check information.
func (e *LNXlinkMQTTEngine) Diagnostics() map[string]interface{} {
	e.mu.RLock()
	defer e.mu.RUnlock()

	return map[string]interface{}{
		"engine":            "OmniLNXlinkMQTTEngine",
		"version":           e.engineVersion,
		"uptime":            time.Since(e.startedAt).String(),
		"started_at":        e.startedAt,
		"broker_host":       e.brokerConfig.Host,
		"broker_port":       e.brokerConfig.Port,
		"broker_tls":        e.brokerConfig.TLSEnabled,
		"total_machines":    e.stats.TotalMachines,
		"total_readings":    e.stats.TotalReadings,
		"total_cmds_sent":   e.stats.TotalCommandsSent,
		"total_cmds_ok":     e.stats.TotalCommandsOK,
		"total_cmds_failed": e.stats.TotalCommandsFailed,
		"total_msgs_in":     e.stats.TotalMessagesIn,
		"total_msgs_out":    e.stats.TotalMessagesOut,
		"total_automations": e.stats.TotalAutomations,
		"total_rules_fired": e.stats.TotalRulesFired,
		"discovery_count":   e.stats.DiscoveryPublished,
		"pending_commands":  len(e.pendingCmds),
		"subscriptions":     len(e.subscriptions),
		"message_log_size":  len(e.messageLog),
		"last_activity":     e.stats.LastActivity,
		"status":            "OPERATIONAL",
	}
}

// ---------------------------------------------------------------------------
// Section 13: Helper Functions
// ---------------------------------------------------------------------------

func humanizeSensorType(s SensorType) string {
	names := map[SensorType]string{
		SensorCPU: "CPU Usage", SensorMemory: "Memory Usage", SensorDisk: "Disk Usage",
		SensorNetwork: "Network Stats", SensorBattery: "Battery", SensorTemperature: "Temperature",
		SensorUptime: "Uptime", SensorDisplay: "Display", SensorAudio: "Audio",
		SensorMedia: "Media Player", SensorBluetooth: "Bluetooth", SensorNotify: "Notification",
		SensorScreenshot: "Screenshot", SensorSuspend: "Suspend", SensorShutdown: "Shutdown",
		SensorReboot: "Reboot", SensorBash: "Bash Command", SensorCamera: "Camera",
		SensorMicrophone: "Microphone", SensorGPU: "GPU", SensorDocker: "Docker",
		SensorSystemD: "SystemD", SensorPackages: "Packages", SensorIdletime: "Idle Time",
		SensorKeepAlive: "Keep Alive",
	}
	if n, ok := names[s]; ok {
		return n
	}
	return string(s)
}

func mapSensorDeviceClass(s SensorType) string {
	classes := map[SensorType]string{
		SensorCPU: "power_factor", SensorMemory: "data_size", SensorDisk: "data_size",
		SensorBattery: "battery", SensorTemperature: "temperature", SensorUptime: "duration",
	}
	return classes[s]
}

func mapSensorUnit(s SensorType) string {
	units := map[SensorType]string{
		SensorCPU: "%", SensorMemory: "%", SensorDisk: "%",
		SensorBattery: "%", SensorTemperature: "°C", SensorUptime: "s",
		SensorGPU: "%", SensorIdletime: "s",
	}
	return units[s]
}

func mapSensorIcon(s SensorType) string {
	icons := map[SensorType]string{
		SensorCPU: "mdi:cpu-64-bit", SensorMemory: "mdi:memory", SensorDisk: "mdi:harddisk",
		SensorNetwork: "mdi:lan", SensorBattery: "mdi:battery", SensorTemperature: "mdi:thermometer",
		SensorUptime: "mdi:clock-outline", SensorDisplay: "mdi:monitor", SensorAudio: "mdi:volume-high",
		SensorMedia: "mdi:play-circle", SensorBluetooth: "mdi:bluetooth", SensorNotify: "mdi:bell",
		SensorScreenshot: "mdi:camera", SensorGPU: "mdi:expansion-card", SensorDocker: "mdi:docker",
		SensorSystemD: "mdi:cog", SensorPackages: "mdi:package-variant",
		SensorKeepAlive: "mdi:heart-pulse",
	}
	if icon, ok := icons[s]; ok {
		return icon
	}
	return "mdi:eye"
}

func isControllableSensor(s SensorType) bool {
	controllable := map[SensorType]bool{
		SensorDisplay: true, SensorAudio: true, SensorMedia: true,
		SensorSuspend: true, SensorShutdown: true, SensorReboot: true,
		SensorBash: true, SensorNotify: true, SensorDocker: true,
		SensorSystemD: true, SensorCamera: true, SensorMicrophone: true,
	}
	return controllable[s]
}

func toFloat64(val interface{}) (float64, bool) {
	switch v := val.(type) {
	case float64:
		return v, true
	case float32:
		return float64(v), true
	case int:
		return float64(v), true
	case int64:
		return float64(v), true
	case int32:
		return float64(v), true
	default:
		return 0, false
	}
}
