// OMNI MOTHER — SEMESTER 14 BATCH 36
// Dart — Interface Layer (OMNI Zero-Mock Implementation)
// Implements production-grade Widget Reconciliation engine for Flutter.
// Absorbs patterns from: flutter/flutter framework, RenderObject lifecycle

/// Monadic result for widget operations.
class WidgetResult<T> {
  final T? value;
  final String? error;
  final bool isOk;

  WidgetResult.ok(this.value) : error = null, isOk = true;
  WidgetResult.err(this.error) : value = null, isOk = false;
}

/// Represents a declarative widget description.
class OmniWidget {
  final String type;
  final String key;
  final Map<String, dynamic> props;
  final List<OmniWidget> children;

  OmniWidget({
    required this.type,
    this.key = '',
    this.props = const {},
    this.children = const [],
  });

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    if (other is! OmniWidget) return false;
    return type == other.type && key == other.key;
  }

  @override
  int get hashCode => type.hashCode ^ key.hashCode;
}

/// Patch operation produced by the diff algorithm.
enum PatchOp { insert, remove, update, reorder }

class WidgetPatch {
  final PatchOp operation;
  final String widgetType;
  final String key;
  final int index;
  final Map<String, dynamic>? oldProps;
  final Map<String, dynamic>? newProps;

  WidgetPatch({
    required this.operation,
    required this.widgetType,
    required this.key,
    required this.index,
    this.oldProps,
    this.newProps,
  });
}

/// Production-grade Widget Reconciliation Engine.
///
/// Implements the core diffing algorithm that Flutter uses to determine
/// the minimal set of mutations needed to update the render tree.
///
/// Algorithm:
/// 1. Linear scan O(n) for widget-type + key matching
/// 2. Unmatched old widgets → REMOVE
/// 3. Unmatched new widgets → INSERT
/// 4. Matched with different props → UPDATE
/// 5. Matched in different positions → REORDER
class OmniWidgetReconciler {
  int _totalDiffs = 0;
  int _totalPatches = 0;

  /// Diffs two widget trees and produces a minimal patch list.
  WidgetResult<List<WidgetPatch>> reconcile(
    List<OmniWidget> oldTree,
    List<OmniWidget> newTree,
  ) {
    if (identical(oldTree, newTree)) {
      return WidgetResult.ok([]);
    }

    _totalDiffs++;
    final patches = <WidgetPatch>[];

    // Build key-indexed maps for O(1) lookup
    final oldMap = <String, _IndexedWidget>{};
    for (var i = 0; i < oldTree.length; i++) {
      final w = oldTree[i];
      final mapKey = '${w.type}::${w.key}';
      oldMap[mapKey] = _IndexedWidget(w, i);
    }

    final newMap = <String, _IndexedWidget>{};
    for (var i = 0; i < newTree.length; i++) {
      final w = newTree[i];
      final mapKey = '${w.type}::${w.key}';
      newMap[mapKey] = _IndexedWidget(w, i);
    }

    // Detect REMOVE: in old but not in new
    for (final entry in oldMap.entries) {
      if (!newMap.containsKey(entry.key)) {
        patches.add(WidgetPatch(
          operation: PatchOp.remove,
          widgetType: entry.value.widget.type,
          key: entry.value.widget.key,
          index: entry.value.index,
          oldProps: entry.value.widget.props,
        ));
      }
    }

    // Detect INSERT and UPDATE: in new but possibly not in old
    for (final entry in newMap.entries) {
      if (!oldMap.containsKey(entry.key)) {
        // INSERT: new widget not in old tree
        patches.add(WidgetPatch(
          operation: PatchOp.insert,
          widgetType: entry.value.widget.type,
          key: entry.value.widget.key,
          index: entry.value.index,
          newProps: entry.value.widget.props,
        ));
      } else {
        final oldEntry = oldMap[entry.key]!;
        // Check prop diff
        final propsDiffer = _propsAreDifferent(
          oldEntry.widget.props,
          entry.value.widget.props,
        );

        if (propsDiffer) {
          patches.add(WidgetPatch(
            operation: PatchOp.update,
            widgetType: entry.value.widget.type,
            key: entry.value.widget.key,
            index: entry.value.index,
            oldProps: oldEntry.widget.props,
            newProps: entry.value.widget.props,
          ));
        }

        // Check position change
        if (oldEntry.index != entry.value.index && !propsDiffer) {
          patches.add(WidgetPatch(
            operation: PatchOp.reorder,
            widgetType: entry.value.widget.type,
            key: entry.value.widget.key,
            index: entry.value.index,
          ));
        }
      }
    }

    _totalPatches += patches.length;
    return WidgetResult.ok(patches);
  }

  /// Shallow comparison of two prop maps.
  bool _propsAreDifferent(
    Map<String, dynamic> a,
    Map<String, dynamic> b,
  ) {
    if (a.length != b.length) return true;
    for (final key in a.keys) {
      if (!b.containsKey(key) || a[key] != b[key]) return true;
    }
    return false;
  }

  /// Returns engine diagnostics.
  Map<String, dynamic> diagnostics() => {
        'engine': 'OmniWidgetReconciler',
        'layer': 'ui/dart',
        'totalDiffs': _totalDiffs,
        'totalPatches': _totalPatches,
        'status': 'operational',
        'learnedFrom': 'flutter/flutter (RenderObject lifecycle)',
      };
}

class _IndexedWidget {
  final OmniWidget widget;
  final int index;
  _IndexedWidget(this.widget, this.index);
}
