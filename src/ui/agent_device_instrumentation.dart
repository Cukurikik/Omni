
// ---- Device Info ----------------------------------------------------------

enum DevicePlatform { android, ios, desktop, web }
enum ConnectionType { wifi, cellular, ethernet, bluetooth, none }
enum BatteryState { charging, discharging, full, notCharging, unknown }

class DeviceInfo {
  final String deviceId;
  final String model;
  final String manufacturer;
  final String osVersion;
  final DevicePlatform platform;
  final int screenWidth;
  final int screenHeight;
  final double screenDensity;
  final String locale;
  final String timezone;

  const DeviceInfo({
    required this.deviceId,
    required this.model,
    required this.manufacturer,
    required this.osVersion,
    required this.platform,
    required this.screenWidth,
    required this.screenHeight,
    required this.screenDensity,
    required this.locale,
    required this.timezone,
  });

  Map<String, dynamic> toJson() => {
    'deviceId': deviceId, 'model': model, 'manufacturer': manufacturer,
    'osVersion': osVersion, 'platform': platform.name,
    'screen': '${screenWidth}x$screenHeight @${screenDensity}x',
    'locale': locale, 'timezone': timezone,
  };
}

// ---- Battery Monitor ------------------------------------------------------

class BatteryInfo {
  final int level;        // 0-100
  final BatteryState state;
  final double temperature; // Celsius
  final String technology;
  final int voltage;       // mV

  const BatteryInfo({
    required this.level,
    required this.state,
    required this.temperature,
    required this.technology,
    required this.voltage,
  });

  bool get isLow => level < 15;
  bool get isCritical => level < 5;

  Map<String, dynamic> toJson() => {
    'level': level, 'state': state.name,
    'temperature': temperature, 'technology': technology, 'voltage': voltage,
  };
}

// ---- Network State --------------------------------------------------------

class NetworkInfo {
  final ConnectionType type;
  final String ssid;
  final String ipAddress;
  final int signalStrength; // dBm
  final bool isVpnActive;
  final int downloadSpeed;  // Kbps
  final int uploadSpeed;    // Kbps

  const NetworkInfo({
    required this.type,
    required this.ssid,
    required this.ipAddress,
    required this.signalStrength,
    required this.isVpnActive,
    required this.downloadSpeed,
    required this.uploadSpeed,
  });

  Map<String, dynamic> toJson() => {
    'type': type.name, 'ssid': ssid, 'ip': ipAddress,
    'signal': signalStrength, 'vpn': isVpnActive,
    'down': '${downloadSpeed}Kbps', 'up': '${uploadSpeed}Kbps',
  };
}

// ---- Sensor Data Collection -----------------------------------------------

class SensorReading {
  final String sensorName;  // "accelerometer", "gyroscope", "proximity", etc.
  final double x;
  final double y;
  final double z;
  final DateTime timestamp;

  const SensorReading({
    required this.sensorName,
    required this.x,
    required this.y,
    required this.z,
    required this.timestamp,
  });
}

// ---- Accessibility Tree ---------------------------------------------------

class AccessibilityNode {
  final String className;
  final String? resourceId;
  final String? text;
  final String? contentDescription;
  final bool isClickable;
  final bool isScrollable;
  final bool isFocused;
  final Map<String, int> bounds; // left, top, right, bottom
  final List<AccessibilityNode> children;

  const AccessibilityNode({
    required this.className,
    this.resourceId,
    this.text,
    this.contentDescription,
    required this.isClickable,
    required this.isScrollable,
    required this.isFocused,
    required this.bounds,
    this.children = const [],
  });

  int get depth => children.isEmpty ? 0 : 1 + children.map((c) => c.depth).reduce((a, b) => a > b ? a : b);
  int get totalNodes => 1 + children.fold(0, (sum, c) => sum + c.totalNodes);

  /// Find all clickable elements in the tree.
  List<AccessibilityNode> findClickable() {
    final result = <AccessibilityNode>[];
    if (isClickable) result.add(this);
    for (final child in children) {
      result.addAll(child.findClickable());
    }
    return result;
  }

  /// Find element by resource ID.
  AccessibilityNode? findById(String id) {
    if (resourceId == id) return this;
    for (final child in children) {
      final found = child.findById(id);
      if (found != null) return found;
    }
    return null;
  }

  /// Find elements by text content.
  List<AccessibilityNode> findByText(String query) {
    final result = <AccessibilityNode>[];
    if (text != null && text!.toLowerCase().contains(query.toLowerCase())) {
      result.add(this);
    }
    for (final child in children) {
      result.addAll(child.findByText(query));
    }
    return result;
  }
}

// ---- Instrumentation Engine -----------------------------------------------

class InstrumentationEngine {
  final DeviceInfo deviceInfo;
  BatteryInfo? _lastBattery;
  NetworkInfo? _lastNetwork;
  final List<SensorReading> _sensorBuffer = [];
  AccessibilityNode? _cachedTree;

  InstrumentationEngine({required this.deviceInfo}) {
    print('[INSTRUMENT-OMNI-DART] Engine initialized for ${deviceInfo.model} (${deviceInfo.platform.name})');
  }

  /// Collect a full device snapshot.
  Map<String, dynamic> collectSnapshot() {
    print('[INSTRUMENT-OMNI-DART] Collecting device snapshot...');
    return {
      'device': deviceInfo.toJson(),
      'battery': _lastBattery?.toJson(),
      'network': _lastNetwork?.toJson(),
      'sensors': _sensorBuffer.length,
      'accessibilityDepth': _cachedTree?.depth ?? 0,
      'accessibilityNodes': _cachedTree?.totalNodes ?? 0,
      'timestamp': DateTime.now().toIso8601String(),
    };
  }

  void updateBattery(BatteryInfo info) {
    _lastBattery = info;
    if (info.isCritical) {
      print('[INSTRUMENT-OMNI-DART] ⚠ CRITICAL battery: ${info.level}%');
    }
  }

  void updateNetwork(NetworkInfo info) {
    _lastNetwork = info;
  }

  void recordSensor(SensorReading reading) {
    _sensorBuffer.add(reading);
    if (_sensorBuffer.length > 1000) _sensorBuffer.removeAt(0);
  }

  void updateAccessibilityTree(AccessibilityNode root) {
    _cachedTree = root;
    print('[INSTRUMENT-OMNI-DART] Accessibility tree updated: ${root.totalNodes} nodes, depth ${root.depth}');
  }
}
