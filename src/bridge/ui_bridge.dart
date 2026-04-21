/**
 * ===========================================================================
 * OMNI BRIDGE — UI ↔ ALL LAYERS INTERFACE
 * ===========================================================================
 * Dart interface contracts for UI-layer engines. Any UI engine
 * (TypeScript, Dart, Swift, HTML) must satisfy these interfaces to safely
 * consume data from Domain/Compute/Network layers via the OMNI bridge.
 *
 * KEY RULE: UI bridge may NEVER import system-layer memory primitives.
 * ===========================================================================
 */

/// Canonical UI data payload received from Domain/Compute layers.
class UIDataPayload {
  final String sourceLayer;    // "domain", "compute", "network"
  final String sourceEngine;   // e.g. "auto_anime_organizer"
  final Map<String, dynamic> data;
  final DateTime receivedAt;

  const UIDataPayload({
    required this.sourceLayer,
    required this.sourceEngine,
    required this.data,
    required this.receivedAt,
  });
}

/// Render command dispatched from UI to the rendering surface.
class UIRenderCommand {
  final String componentId;
  final String action;         // "mount", "update", "unmount"
  final Map<String, dynamic> props;

  const UIRenderCommand({
    required this.componentId,
    required this.action,
    this.props = const {},
  });
}

/// Result of a UI render operation.
class UIRenderResult {
  final bool success;
  final String? error;
  final int renderTimeMs;

  const UIRenderResult({required this.success, this.error, this.renderTimeMs = 0});
}

/// All UI engines must implement this interface.
abstract class UIBridge {
  /// Receive data from a lower layer and render it.
  Future<UIRenderResult> render(UIDataPayload payload);

  /// Dispatch a render command.
  Future<UIRenderResult> dispatch(UIRenderCommand command);

  /// Return the engine name.
  String get name;

  /// Health check.
  bool healthcheck();
}
