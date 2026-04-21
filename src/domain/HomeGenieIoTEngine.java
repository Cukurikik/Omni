// ===========================================================================
// OMNI DOMAIN LAYER — HOMEGENIE IOT ENGINE
// ===========================================================================
// Source Repo   : github.com/genielabs/HomeGenie
// Domain Layer  : Domain (Smart home automation, IoT orchestration)
// Language      : Java
// Function      : Local-first smart home management — device registry with
//                 multi-protocol abstraction (Z-Wave/Zigbee/WiFi/Matter/BLE),
//                 automation rules with event-driven triggers, room/zone
//                 grouping, cron-based scheduling, agentic AI reasoning for
//                 autonomous device control, energy monitoring, scene
//                 management, inter-device mesh communication, and
//                 privacy-first local processing.
// ===========================================================================

package OmniDomain.HomeGenie;

import java.time.Instant;
import java.time.Duration;
import java.time.LocalTime;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;
import java.util.function.Predicate;

// ---- Device Protocol ------------------------------------------------------

enum DeviceProtocol {
    ZWAVE("Z-Wave", "868/908 MHz mesh"),
    ZIGBEE("Zigbee", "2.4 GHz mesh"),
    WIFI("WiFi", "TCP/IP based"),
    MATTER("Matter", "Thread/WiFi unified"),
    BLE("BLE", "Bluetooth Low Energy"),
    MQTT("MQTT", "Message broker"),
    VIRTUAL("Virtual", "Software-only device"),
    GPIO("GPIO", "GPIO pins direct control");

    final String displayName;
    final String description;
    DeviceProtocol(String name, String desc) {
        this.displayName = name;
        this.description = desc;
    }
}

// ---- Device Type ----------------------------------------------------------

enum DeviceType {
    LIGHT, DIMMER, SWITCH, THERMOSTAT, SENSOR_TEMPERATURE,
    SENSOR_HUMIDITY, SENSOR_MOTION, SENSOR_DOOR, SENSOR_LIGHT,
    LOCK, CAMERA, SPEAKER, MEDIA_PLAYER, BLINDS, FAN,
    POWER_METER, IRRIGATION, ALARM, SMOKE_DETECTOR, GENERIC
}

// ---- Device Status --------------------------------------------------------

enum DeviceStatus {
    ONLINE, OFFLINE, UNREACHABLE, SLEEPING, UPDATING, ERROR
}

// ---- Event Type -----------------------------------------------------------

enum EventType {
    STATUS_CHANGE, PROPERTY_CHANGE, TRIGGER, SCHEDULE,
    SUNRISE, SUNSET, DEVICE_ADDED, DEVICE_REMOVED,
    ENERGY_THRESHOLD, MOTION_DETECTED, DOOR_OPEN, DOOR_CLOSE,
    TEMPERATURE_THRESHOLD, HUMIDITY_THRESHOLD, AI_DECISION
}

// ---- Command Type ---------------------------------------------------------

enum CommandType {
    ON, OFF, TOGGLE, SET_LEVEL, SET_COLOR, SET_TEMPERATURE,
    LOCK, UNLOCK, OPEN, CLOSE, ARM, DISARM, PLAY, PAUSE, STOP
}

// ---- AI Reasoning Level ---------------------------------------------------

enum AIReasoningLevel {
    DISABLED("No AI reasoning"),
    REACTIVE("Simple rule-based responses"),
    PROACTIVE("Anticipates needs from patterns"),
    AUTONOMOUS("Full autonomous decision-making within boundaries");

    final String description;
    AIReasoningLevel(String desc) { this.description = desc; }
}

// ---- Device Property ------------------------------------------------------

class DeviceProperty {
    String name;          // e.g. "Status.Level", "Meter.Watts"
    String value;
    String unit;          // "W", "°C", "%", "lux"
    Instant lastUpdated;

    DeviceProperty(String name, String value, String unit) {
        this.name = name;
        this.value = value;
        this.unit = unit;
        this.lastUpdated = Instant.now();
    }

    void update(String newValue) {
        this.value = newValue;
        this.lastUpdated = Instant.now();
    }
}

// ---- Smart Device ---------------------------------------------------------

class SmartDevice {
    final String id;
    String name;
    DeviceType type;
    DeviceProtocol protocol;
    DeviceStatus status;
    String roomId;
    String address;               // Protocol-specific address
    Map<String, DeviceProperty> properties;
    List<CommandType> supportedCommands;
    Instant lastSeen;
    Instant addedAt;
    double level;                 // 0.0 - 1.0 (brightness, position, etc.)
    boolean reachable;

    SmartDevice(String id, String name, DeviceType type, DeviceProtocol protocol) {
        this.id = id;
        this.name = name;
        this.type = type;
        this.protocol = protocol;
        this.status = DeviceStatus.ONLINE;
        this.properties = new ConcurrentHashMap<>();
        this.supportedCommands = new ArrayList<>();
        this.lastSeen = Instant.now();
        this.addedAt = Instant.now();
        this.level = 0.0;
        this.reachable = true;

        // Set default supported commands based on type
        initDefaultCommands();
    }

    private void initDefaultCommands() {
        switch (type) {
            case LIGHT:
            case SWITCH:
                supportedCommands.addAll(List.of(CommandType.ON, CommandType.OFF, CommandType.TOGGLE));
                break;
            case DIMMER:
                supportedCommands.addAll(List.of(
                        CommandType.ON, CommandType.OFF, CommandType.TOGGLE, CommandType.SET_LEVEL));
                break;
            case THERMOSTAT:
                supportedCommands.addAll(List.of(
                        CommandType.ON, CommandType.OFF, CommandType.SET_TEMPERATURE));
                break;
            case LOCK:
                supportedCommands.addAll(List.of(CommandType.LOCK, CommandType.UNLOCK));
                break;
            case BLINDS:
                supportedCommands.addAll(List.of(
                        CommandType.OPEN, CommandType.CLOSE, CommandType.SET_LEVEL));
                break;
            case ALARM:
                supportedCommands.addAll(List.of(CommandType.ARM, CommandType.DISARM));
                break;
            case MEDIA_PLAYER:
                supportedCommands.addAll(List.of(
                        CommandType.PLAY, CommandType.PAUSE, CommandType.STOP));
                break;
            case FAN:
                supportedCommands.addAll(List.of(
                        CommandType.ON, CommandType.OFF, CommandType.SET_LEVEL));
                break;
            default:
                supportedCommands.addAll(List.of(CommandType.ON, CommandType.OFF));
        }
    }

    void setProperty(String name, String value, String unit) {
        properties.compute(name, (k, existing) -> {
            if (existing != null) { existing.update(value); return existing; }
            return new DeviceProperty(name, value, unit);
        });
    }

    String getPropertyValue(String name) {
        DeviceProperty p = properties.get(name);
        return p != null ? p.value : null;
    }

    boolean executeCommand(CommandType cmd, String... params) {
        if (!supportedCommands.contains(cmd)) return false;
        lastSeen = Instant.now();

        switch (cmd) {
            case ON:
                level = 1.0;
                setProperty("Status.Level", "1.0", "");
                break;
            case OFF:
                level = 0.0;
                setProperty("Status.Level", "0.0", "");
                break;
            case TOGGLE:
                level = level > 0 ? 0.0 : 1.0;
                setProperty("Status.Level", String.valueOf(level), "");
                break;
            case SET_LEVEL:
                if (params.length > 0) {
                    level = Double.parseDouble(params[0]);
                    setProperty("Status.Level", params[0], "%");
                }
                break;
            case SET_TEMPERATURE:
                if (params.length > 0) {
                    setProperty("Thermostat.SetPoint", params[0], "°C");
                }
                break;
            case LOCK:
                setProperty("Status.Lock", "locked", "");
                break;
            case UNLOCK:
                setProperty("Status.Lock", "unlocked", "");
                break;
            default:
                setProperty("Status.Command", cmd.name(), "");
        }

        System.out.printf("[HOMEGENIE-OMNI-JAVA] %s -> %s (level=%.2f)%n", name, cmd, level);
        return true;
    }
}

// ---- Room/Zone ------------------------------------------------------------

class Room {
    final String id;
    String name;
    List<String> deviceIds;
    String zone;       // "Ground Floor", "First Floor", "Outdoor"

    Room(String id, String name, String zone) {
        this.id = id;
        this.name = name;
        this.zone = zone;
        this.deviceIds = new ArrayList<>();
    }

    void addDevice(String deviceId) {
        if (!deviceIds.contains(deviceId)) deviceIds.add(deviceId);
    }

    void removeDevice(String deviceId) {
        deviceIds.remove(deviceId);
    }
}

// ---- Scene ----------------------------------------------------------------

class Scene {
    final String id;
    String name;
    List<SceneAction> actions;
    boolean active;

    Scene(String id, String name) {
        this.id = id;
        this.name = name;
        this.actions = new ArrayList<>();
        this.active = true;
    }

    void addAction(String deviceId, CommandType command, String... params) {
        actions.add(new SceneAction(deviceId, command, params));
    }
}

class SceneAction {
    String deviceId;
    CommandType command;
    String[] params;

    SceneAction(String deviceId, CommandType command, String... params) {
        this.deviceId = deviceId;
        this.command = command;
        this.params = params;
    }
}

// ---- Automation Rule (Program) --------------------------------------------

class AutomationRule {
    final String id;
    String name;
    String description;
    boolean enabled;
    EventType triggerEvent;
    String triggerDeviceId;     // "*" for any device
    String triggerCondition;    // Expression: "value > 25.0"
    List<SceneAction> actions;
    String cronSchedule;       // For scheduled rules: "0 7 * * 1-5"
    int executionCount;
    Instant lastExecuted;
    Instant createdAt;

    AutomationRule(String id, String name, EventType trigger) {
        this.id = id;
        this.name = name;
        this.triggerEvent = trigger;
        this.triggerDeviceId = "*";
        this.enabled = true;
        this.actions = new ArrayList<>();
        this.executionCount = 0;
        this.createdAt = Instant.now();
    }

    void addAction(String deviceId, CommandType command, String... params) {
        actions.add(new SceneAction(deviceId, command, params));
    }

    boolean evaluateCondition(String currentValue) {
        if (triggerCondition == null || triggerCondition.isEmpty()) return true;

        try {
            // Simple numeric comparison parsing
            if (triggerCondition.contains(">")) {
                double threshold = Double.parseDouble(
                        triggerCondition.substring(triggerCondition.indexOf(">") + 1).trim());
                return Double.parseDouble(currentValue) > threshold;
            }
            if (triggerCondition.contains("<")) {
                double threshold = Double.parseDouble(
                        triggerCondition.substring(triggerCondition.indexOf("<") + 1).trim());
                return Double.parseDouble(currentValue) < threshold;
            }
            if (triggerCondition.contains("==")) {
                String expected = triggerCondition.substring(
                        triggerCondition.indexOf("==") + 2).trim();
                return currentValue.equals(expected);
            }
        } catch (NumberFormatException e) {
            return false;
        }
        return true;
    }
}

// ---- AI Decision Log ------------------------------------------------------

class AIDecision {
    final Instant timestamp;
    final String reasoning;
    final String action;
    final String deviceId;
    final AIReasoningLevel level;
    boolean executed;

    AIDecision(String reasoning, String action, String deviceId, AIReasoningLevel level) {
        this.timestamp = Instant.now();
        this.reasoning = reasoning;
        this.action = action;
        this.deviceId = deviceId;
        this.level = level;
        this.executed = false;
    }
}

// ---- Energy Monitor -------------------------------------------------------

class EnergyReading {
    String deviceId;
    double watts;
    double kwhTotal;
    Instant timestamp;

    EnergyReading(String deviceId, double watts, double kwhTotal) {
        this.deviceId = deviceId;
        this.watts = watts;
        this.kwhTotal = kwhTotal;
        this.timestamp = Instant.now();
    }
}

// ---- HomeGenie IoT Engine (Main Orchestrator) -----------------------------

public class HomeGenieIoTEngine {
    private final Map<String, SmartDevice> devices = new ConcurrentHashMap<>();
    private final Map<String, Room> rooms = new ConcurrentHashMap<>();
    private final Map<String, Scene> scenes = new ConcurrentHashMap<>();
    private final Map<String, AutomationRule> automations = new ConcurrentHashMap<>();
    private final List<AIDecision> aiDecisions = new CopyOnWriteArrayList<>();
    private final List<EnergyReading> energyHistory = new CopyOnWriteArrayList<>();

    private AIReasoningLevel aiLevel = AIReasoningLevel.REACTIVE;
    private int idCounter = 5000;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);

    public HomeGenieIoTEngine() {
        System.out.println("[HOMEGENIE-OMNI-JAVA] IoT engine initialized (local-first, privacy-focused).");
        startPeriodicTasks();
    }

    private String nextId(String prefix) {
        return prefix + "-" + (++idCounter);
    }

    // ---- Device Registry --------------------------------------------------

    public SmartDevice registerDevice(
            String name, DeviceType type, DeviceProtocol protocol, String address) {
        String id = nextId("dev");
        SmartDevice device = new SmartDevice(id, name, type, protocol);
        device.address = address;
        devices.put(id, device);
        System.out.printf("[HOMEGENIE-OMNI-JAVA] Device registered: %s (%s/%s) addr=%s%n",
                name, type, protocol.displayName, address);
        return device;
    }

    public SmartDevice getDevice(String deviceId) {
        return devices.get(deviceId);
    }

    public List<SmartDevice> listDevices() {
        return new ArrayList<>(devices.values());
    }

    public List<SmartDevice> devicesByRoom(String roomId) {
        Room room = rooms.get(roomId);
        if (room == null) return Collections.emptyList();
        return room.deviceIds.stream()
                .map(devices::get)
                .filter(Objects::nonNull)
                .collect(Collectors.toList());
    }

    public List<SmartDevice> devicesByType(DeviceType type) {
        return devices.values().stream()
                .filter(d -> d.type == type)
                .collect(Collectors.toList());
    }

    // ---- Command Execution ------------------------------------------------

    public boolean sendCommand(String deviceId, CommandType command, String... params) {
        SmartDevice device = devices.get(deviceId);
        if (device == null) return false;

        boolean result = device.executeCommand(command, params);
        if (result) {
            // Trigger automation rules
            processEvent(EventType.STATUS_CHANGE, deviceId, String.valueOf(device.level));
        }
        return result;
    }

    public int sendCommandToRoom(String roomId, CommandType command, String... params) {
        Room room = rooms.get(roomId);
        if (room == null) return 0;

        int count = 0;
        for (String devId : room.deviceIds) {
            if (sendCommand(devId, command, params)) count++;
        }
        System.out.printf("[HOMEGENIE-OMNI-JAVA] Room command %s -> %s: %d devices%n",
                command, room.name, count);
        return count;
    }

    // ---- Room Management --------------------------------------------------

    public Room createRoom(String name, String zone) {
        String id = nextId("room");
        Room room = new Room(id, name, zone);
        rooms.put(id, room);
        System.out.printf("[HOMEGENIE-OMNI-JAVA] Room created: %s (%s)%n", name, zone);
        return room;
    }

    public void assignDeviceToRoom(String deviceId, String roomId) {
        Room room = rooms.get(roomId);
        SmartDevice device = devices.get(deviceId);
        if (room != null && device != null) {
            room.addDevice(deviceId);
            device.roomId = roomId;
        }
    }

    public List<Room> listRooms() {
        return new ArrayList<>(rooms.values());
    }

    // ---- Scene Management -------------------------------------------------

    public Scene createScene(String name) {
        String id = nextId("scene");
        Scene scene = new Scene(id, name);
        scenes.put(id, scene);
        System.out.printf("[HOMEGENIE-OMNI-JAVA] Scene created: %s%n", name);
        return scene;
    }

    public boolean activateScene(String sceneId) {
        Scene scene = scenes.get(sceneId);
        if (scene == null || !scene.active) return false;

        int executed = 0;
        for (SceneAction action : scene.actions) {
            if (sendCommand(action.deviceId, action.command, action.params)) {
                executed++;
            }
        }
        System.out.printf("[HOMEGENIE-OMNI-JAVA] Scene '%s' activated: %d/%d actions%n",
                scene.name, executed, scene.actions.size());
        return true;
    }

    // ---- Automation Rules -------------------------------------------------

    public AutomationRule createAutomation(String name, EventType trigger) {
        String id = nextId("auto");
        AutomationRule rule = new AutomationRule(id, name, trigger);
        automations.put(id, rule);
        System.out.printf("[HOMEGENIE-OMNI-JAVA] Automation created: %s (trigger=%s)%n",
                name, trigger);
        return rule;
    }

    public void processEvent(EventType eventType, String deviceId, String value) {
        for (AutomationRule rule : automations.values()) {
            if (!rule.enabled) continue;
            if (rule.triggerEvent != eventType) continue;
            if (!rule.triggerDeviceId.equals("*") && !rule.triggerDeviceId.equals(deviceId)) continue;
            if (!rule.evaluateCondition(value)) continue;

            // Fire automation actions
            for (SceneAction action : rule.actions) {
                sendCommand(action.deviceId, action.command, action.params);
            }
            rule.executionCount++;
            rule.lastExecuted = Instant.now();
            System.out.printf("[HOMEGENIE-OMNI-JAVA] Automation fired: %s (count=%d)%n",
                    rule.name, rule.executionCount);
        }

        // AI reasoning
        if (aiLevel.ordinal() >= AIReasoningLevel.PROACTIVE.ordinal()) {
            runAIReasoning(eventType, deviceId, value);
        }
    }

    // ---- AI Reasoning Engine ----------------------------------------------

    public void setAILevel(AIReasoningLevel level) {
        this.aiLevel = level;
        System.out.printf("[HOMEGENIE-OMNI-JAVA] AI reasoning level: %s%n", level);
    }

    private void runAIReasoning(EventType event, String deviceId, String value) {
        SmartDevice device = devices.get(deviceId);
        if (device == null) return;

        String reasoning = "";
        String action = "";

        // Pattern-based proactive reasoning
        if (event == EventType.TEMPERATURE_THRESHOLD && device.type == DeviceType.SENSOR_TEMPERATURE) {
            double temp = Double.parseDouble(value);
            if (temp > 28.0) {
                reasoning = String.format("Temperature %.1f°C exceeds comfort zone. Activating cooling.", temp);
                action = "activate_cooling";
                // Find and activate fans/AC
                for (SmartDevice d : devices.values()) {
                    if (d.type == DeviceType.FAN || d.type == DeviceType.THERMOSTAT) {
                        if (d.roomId != null && d.roomId.equals(device.roomId)) {
                            sendCommand(d.id, CommandType.ON);
                        }
                    }
                }
            } else if (temp < 18.0) {
                reasoning = String.format("Temperature %.1f°C below comfort zone. Activating heating.", temp);
                action = "activate_heating";
                for (SmartDevice d : devices.values()) {
                    if (d.type == DeviceType.THERMOSTAT && Objects.equals(d.roomId, device.roomId)) {
                        sendCommand(d.id, CommandType.SET_TEMPERATURE, "22.0");
                    }
                }
            }
        }

        if (event == EventType.MOTION_DETECTED) {
            // Check time of day for appropriate response
            LocalTime now = LocalTime.now();
            if (now.isAfter(LocalTime.of(22, 0)) || now.isBefore(LocalTime.of(6, 0))) {
                reasoning = "Motion detected at night. Activating dim lights for safety.";
                action = "night_light";
                for (SmartDevice d : devices.values()) {
                    if ((d.type == DeviceType.DIMMER || d.type == DeviceType.LIGHT)
                            && Objects.equals(d.roomId, device.roomId)) {
                        sendCommand(d.id, CommandType.SET_LEVEL, "0.2");
                    }
                }
            } else {
                reasoning = "Motion detected during daytime. No action needed.";
                action = "none";
            }
        }

        if (!reasoning.isEmpty()) {
            AIDecision decision = new AIDecision(reasoning, action, deviceId, aiLevel);
            decision.executed = !action.equals("none");
            aiDecisions.add(decision);
            System.out.printf("[HOMEGENIE-OMNI-JAVA] AI Decision: %s%n", reasoning);
        }
    }

    // ---- Energy Monitoring ------------------------------------------------

    public void recordEnergyReading(String deviceId, double watts, double kwhTotal) {
        energyHistory.add(new EnergyReading(deviceId, watts, kwhTotal));
    }

    public Map<String, Object> energySummary() {
        double totalWatts = energyHistory.stream()
                .filter(e -> Duration.between(e.timestamp, Instant.now()).toMinutes() < 60)
                .mapToDouble(e -> e.watts)
                .sum();
        double totalKwh = energyHistory.stream()
                .mapToDouble(e -> e.kwhTotal)
                .max().orElse(0);
        int metered = (int) energyHistory.stream()
                .map(e -> e.deviceId)
                .distinct()
                .count();

        Map<String, Object> summary = new HashMap<>();
        summary.put("current_watts", totalWatts);
        summary.put("total_kwh", totalKwh);
        summary.put("metered_devices", metered);
        summary.put("readings_count", energyHistory.size());
        return summary;
    }

    // ---- Periodic Tasks ---------------------------------------------------

    private void startPeriodicTasks() {
        // Device health check every 30 seconds
        scheduler.scheduleAtFixedRate(() -> {
            for (SmartDevice device : devices.values()) {
                Duration since = Duration.between(device.lastSeen, Instant.now());
                if (since.toMinutes() > 5 && device.status == DeviceStatus.ONLINE) {
                    device.status = DeviceStatus.UNREACHABLE;
                    device.reachable = false;
                }
            }
        }, 30, 30, TimeUnit.SECONDS);
    }

    // ---- Shutdown ---------------------------------------------------------

    public void shutdown() {
        scheduler.shutdown();
        System.out.println("[HOMEGENIE-OMNI-JAVA] IoT engine shutdown complete.");
    }

    // ---- Engine Stats -----------------------------------------------------

    public Map<String, Object> engineStats() {
        long online = devices.values().stream()
                .filter(d -> d.status == DeviceStatus.ONLINE).count();
        long automationsEnabled = automations.values().stream()
                .filter(a -> a.enabled).count();

        Map<String, Object> stats = new HashMap<>();
        stats.put("engine", "HomeGenie IoT Engine");
        stats.put("version", "1.0.0-omni");
        stats.put("total_devices", devices.size());
        stats.put("online_devices", online);
        stats.put("rooms", rooms.size());
        stats.put("scenes", scenes.size());
        stats.put("automations", automations.size());
        stats.put("automations_enabled", automationsEnabled);
        stats.put("ai_level", aiLevel.name());
        stats.put("ai_decisions", aiDecisions.size());
        stats.put("energy_readings", energyHistory.size());

        // Protocol distribution
        Map<String, Long> protocols = devices.values().stream()
                .collect(Collectors.groupingBy(d -> d.protocol.displayName, Collectors.counting()));
        stats.put("protocols", protocols);

        // Device type distribution
        Map<String, Long> types = devices.values().stream()
                .collect(Collectors.groupingBy(d -> d.type.name(), Collectors.counting()));
        stats.put("device_types", types);

        return stats;
    }
}
