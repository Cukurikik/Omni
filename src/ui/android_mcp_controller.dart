
// ---- Enums ----------------------------------------------------------------

enum AdbConnectionState { disconnected, connecting, connected, unauthorized }
enum InputAction { tap, longTap, swipe, pinch, keyEvent, text }

// ---- Data Models ----------------------------------------------------------

class AdbDevice {
  final String serial;
  final String model;
  final String androidVersion;
  final int sdkLevel;
  final int screenWidth;
  final int screenHeight;
  AdbConnectionState state;

  AdbDevice({
    required this.serial,
    required this.model,
    required this.androidVersion,
    required this.sdkLevel,
    required this.screenWidth,
    required this.screenHeight,
    this.state = AdbConnectionState.disconnected,
  });
}

class InstalledPackage {
  final String packageName;
  final String versionName;
  final int versionCode;
  final bool isSystemApp;
  final int sizeKb;

  const InstalledPackage({
    required this.packageName,
    required this.versionName,
    required this.versionCode,
    required this.isSystemApp,
    required this.sizeKb,
  });
}

class ScreenElement {
  final String className;
  final String? resourceId;
  final String? text;
  final String? contentDesc;
  final int left, top, right, bottom;
  final bool clickable;
  final bool scrollable;
  final List<ScreenElement> children;

  const ScreenElement({
    required this.className,
    this.resourceId,
    this.text,
    this.contentDesc,
    required this.left,
    required this.top,
    required this.right,
    required this.bottom,
    required this.clickable,
    required this.scrollable,
    this.children = const [],
  });

  int get centerX => left + (right - left) ~/ 2;
  int get centerY => top + (bottom - top) ~/ 2;
  int get nodeCount => 1 + children.fold(0, (sum, c) => sum + c.nodeCount);
}

// ---- ADB Command Builder --------------------------------------------------

class AdbCommandBuilder {
  final String serial;

  AdbCommandBuilder(this.serial);

  /// Build: adb -s <serial> shell <command>
  String shell(String cmd) => 'adb -s $serial shell $cmd';

  String tap(int x, int y) => shell('input tap $x $y');

  String longTap(int x, int y, int durationMs) =>
      shell('input swipe $x $y $x $y $durationMs');

  String swipe(int x1, int y1, int x2, int y2, int durationMs) =>
      shell('input swipe $x1 $y1 $x2 $y2 $durationMs');

  String keyEvent(int keyCode) => shell('input keyevent $keyCode');

  String text(String input) {
    final escaped = input.replaceAll(' ', '%s').replaceAll('&', '\\&');
    return shell('input text "$escaped"');
  }

  String screenshot(String path) => shell('screencap -p $path');

  String pullFile(String remote, String local) =>
      'adb -s $serial pull $remote $local';

  String installApk(String apkPath) =>
      'adb -s $serial install -r $apkPath';

  String uninstallPackage(String pkg) =>
      'adb -s $serial uninstall $pkg';

  String forceStop(String pkg) => shell('am force-stop $pkg');

  String launchActivity(String pkg, String activity) =>
      shell('am start -n $pkg/$activity');

  String dumpUI() => shell('uiautomator dump /sdcard/ui_dump.xml && cat /sdcard/ui_dump.xml');

  String getProperty(String prop) => shell('getprop $prop');

  String listPackages() => shell('pm list packages -3');
}

// ---- Controller -----------------------------------------------------------

class AndroidMCPController {
  final AdbDevice device;
  final AdbCommandBuilder cmd;
  final List<String> _commandHistory = [];

  AndroidMCPController({required this.device})
    : cmd = AdbCommandBuilder(device.serial) {
    print('[ANDROID-MCP-OMNI-DART] Controller initialized for ${device.model} (${device.serial})');
  }

  /// Connect to the device.
  void connect() {
    device.state = AdbConnectionState.connected;
    print('[ANDROID-MCP-OMNI-DART] Connected to ${device.model}');
  }

  /// Execute a tap at coordinates.
  String executeTap(int x, int y) {
    final command = cmd.tap(x, y);
    _commandHistory.add(command);
    print('[ANDROID-MCP-OMNI-DART] Tap: ($x, $y)');
    return command;
  }

  /// Execute a swipe gesture.
  String executeSwipe(int x1, int y1, int x2, int y2, {int durationMs = 300}) {
    final command = cmd.swipe(x1, y1, x2, y2, durationMs);
    _commandHistory.add(command);
    print('[ANDROID-MCP-OMNI-DART] Swipe: ($x1,$y1) → ($x2,$y2) [${durationMs}ms]');
    return command;
  }

  /// Tap on a UI element (uses center coordinates).
  String tapElement(ScreenElement element) {
    return executeTap(element.centerX, element.centerY);
  }

  /// Type text into the focused field.
  String typeText(String input) {
    final command = cmd.text(input);
    _commandHistory.add(command);
    print('[ANDROID-MCP-OMNI-DART] Type: "${input.length > 20 ? "${input.substring(0, 20)}..." : input}"');
    return command;
  }

  /// Capture a screenshot and pull to local.
  List<String> captureScreen(String localPath) {
    final capture = cmd.screenshot('/sdcard/screenshot.png');
    final pull = cmd.pullFile('/sdcard/screenshot.png', localPath);
    _commandHistory.addAll([capture, pull]);
    print('[ANDROID-MCP-OMNI-DART] Screenshot → $localPath');
    return [capture, pull];
  }

  /// Launch an app by package and activity name.
  String launchApp(String packageName, String activity) {
    final command = cmd.launchActivity(packageName, activity);
    _commandHistory.add(command);
    print('[ANDROID-MCP-OMNI-DART] Launch: $packageName/$activity');
    return command;
  }

  /// Install an APK.
  String installApk(String path) {
    final command = cmd.installApk(path);
    _commandHistory.add(command);
    print('[ANDROID-MCP-OMNI-DART] Install: $path');
    return command;
  }

  /// Press hardware key (e.g. HOME=3, BACK=4, POWER=26).
  String pressKey(int keyCode) {
    final command = cmd.keyEvent(keyCode);
    _commandHistory.add(command);
    print('[ANDROID-MCP-OMNI-DART] Key: $keyCode');
    return command;
  }

  int get commandCount => _commandHistory.length;
  List<String> get history => List.unmodifiable(_commandHistory);
}
