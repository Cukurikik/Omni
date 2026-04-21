// ===========================================================================
// OMNI WIDGET TREE ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.7)
// ===========================================================================
// Absorbed From  : Flutter framework + React fiber + virtual DOM concepts
// Logic Inherited: Dart / UI Layer (Declarative Widget Tree with Diffing)
// Domain Layer   : UI (Dart Core)
// ===========================================================================
//
// By studying Flutter's Element tree and React Fiber, Mother learned
// that modern UI frameworks require a three-layer architecture:
//   1. Widget layer: immutable configuration (what to render)
//   2. Element layer: stateful instance tree (actual UI state)
//   3. Render layer: layout + painting (how to render)
//
// Dart's strong typing + mixin composition allows clean separation
// of these concerns. The diff algorithm compares old and new widget
// trees by type and key, producing a minimal set of DOM mutations.

/// Abstract base class for all widgets (immutable configuration).
/// Widgets describe WHAT the UI should look like, but don't hold state.
abstract class Widget {
  final String? key;
  const Widget({this.key});

  /// Create the element that will manage this widget's lifecycle.
  Element createElement();

  /// Whether this widget can update the given old widget without rebuild.
  bool canUpdate(Widget oldWidget) {
    return runtimeType == oldWidget.runtimeType && key == oldWidget.key;
  }
}

/// Widget with no children.
class LeafWidget extends Widget {
  final String type;
  final Map<String, dynamic> props;

  const LeafWidget({
    super.key,
    required this.type,
    this.props = const {},
  });

  @override
  Element createElement() => LeafElement(this);
}

/// Widget with a single child.
class SingleChildWidget extends Widget {
  final String type;
  final Map<String, dynamic> props;
  final Widget child;

  const SingleChildWidget({
    super.key,
    required this.type,
    required this.child,
    this.props = const {},
  });

  @override
  Element createElement() => SingleChildElement(this);
}

/// Widget with multiple children.
class MultiChildWidget extends Widget {
  final String type;
  final Map<String, dynamic> props;
  final List<Widget> children;

  const MultiChildWidget({
    super.key,
    required this.type,
    required this.children,
    this.props = const {},
  });

  @override
  Element createElement() => MultiChildElement(this);
}

/// Stateful widget: holds mutable state that persists across rebuilds.
abstract class StatefulWidget extends Widget {
  const StatefulWidget({super.key});

  /// Create the state object.
  State createState();

  @override
  Element createElement() => StatefulElement(this);
}

/// State object associated with a StatefulWidget.
abstract class State<T extends StatefulWidget> {
  late StatefulElement _element;
  T get widget => _element.widget as T;

  /// Build the widget tree for this state.
  Widget build();

  /// Called when the widget is first created.
  void initState() {}

  /// Called when the widget is removed from the tree.
  void dispose() {}

  /// Request a rebuild of this widget.
  void setState(void Function() fn) {
    fn();
    _element.markNeedsBuild();
  }
}

// ===========================================================================
// ELEMENT LAYER — Stateful instances that manage widget lifecycle
// ===========================================================================

/// Represents a mutation to the render tree.
enum MutationType { insert, update, remove, move }

class Mutation {
  final MutationType type;
  final String description;
  final int depth;

  Mutation(this.type, this.description, this.depth);

  @override
  String toString() => '[$type] $description (depth: $depth)';
}

/// Base element — manages the lifecycle of a widget instance.
abstract class Element {
  Widget widget;
  Element? parent;
  int depth = 0;
  bool _dirty = true;

  Element(this.widget);

  /// Mount this element into the tree.
  void mount(Element? parent, int depth) {
    this.parent = parent;
    this.depth = depth;
  }

  /// Update this element with a new widget.
  void update(Widget newWidget) {
    widget = newWidget;
  }

  /// Mark this element as needing rebuild.
  void markNeedsBuild() {
    _dirty = true;
  }

  /// Check if this element needs rebuild.
  bool get isDirty => _dirty;

  /// Unmount this element from the tree.
  void unmount() {}

  /// Collect all child elements.
  List<Element> get children;
}

/// Element for LeafWidget (no children).
class LeafElement extends Element {
  LeafElement(LeafWidget super.widget);

  @override
  List<Element> get children => const [];
}

/// Element for SingleChildWidget.
class SingleChildElement extends Element {
  Element? childElement;

  SingleChildElement(SingleChildWidget super.widget);

  @override
  void mount(Element? parent, int depth) {
    super.mount(parent, depth);
    final w = (widget as SingleChildWidget).child;
    childElement = w.createElement();
    childElement!.mount(this, depth + 1);
  }

  @override
  void update(Widget newWidget) {
    super.update(newWidget);
    final newChild = (newWidget as SingleChildWidget).child;

    if (childElement != null && childElement!.widget.canUpdate(newChild)) {
      childElement!.update(newChild);
    } else {
      childElement?.unmount();
      childElement = newChild.createElement();
      childElement!.mount(this, depth + 1);
    }
  }

  @override
  void unmount() {
    childElement?.unmount();
    super.unmount();
  }

  @override
  List<Element> get children => childElement != null ? [childElement!] : [];
}

/// Element for MultiChildWidget — performs list diffing.
class MultiChildElement extends Element {
  List<Element> childElements = [];

  MultiChildElement(MultiChildWidget super.widget);

  @override
  void mount(Element? parent, int depth) {
    super.mount(parent, depth);
    final children = (widget as MultiChildWidget).children;
    childElements = children.map((w) {
      final el = w.createElement();
      el.mount(this, depth + 1);
      return el;
    }).toList();
  }

  @override
  void update(Widget newWidget) {
    super.update(newWidget);
    final newChildren = (newWidget as MultiChildWidget).children;
    childElements = _diffChildren(childElements, newChildren);
  }

  /// Key-based O(N) list diff algorithm.
  /// Minimizes element creation by reusing elements with matching keys/types.
  List<Element> _diffChildren(
      List<Element> oldElements, List<Widget> newWidgets) {
    // Build key→element map from old list
    final Map<String, Element> oldKeyMap = {};
    final List<Element> oldUnkeyed = [];

    for (final el in oldElements) {
      if (el.widget.key != null) {
        oldKeyMap[el.widget.key!] = el;
      } else {
        oldUnkeyed.add(el);
      }
    }

    int unkeyedIndex = 0;
    final result = <Element>[];

    for (final newWidget in newWidgets) {
      Element? reused;

      if (newWidget.key != null && oldKeyMap.containsKey(newWidget.key)) {
        reused = oldKeyMap.remove(newWidget.key);
      } else if (newWidget.key == null && unkeyedIndex < oldUnkeyed.length) {
        final candidate = oldUnkeyed[unkeyedIndex];
        if (candidate.widget.canUpdate(newWidget)) {
          reused = candidate;
        }
        unkeyedIndex++;
      }

      if (reused != null && reused.widget.canUpdate(newWidget)) {
        reused.update(newWidget);
        result.add(reused);
      } else {
        reused?.unmount();
        final fresh = newWidget.createElement();
        fresh.mount(this, depth + 1);
        result.add(fresh);
      }
    }

    // Unmount remaining old elements
    for (final remaining in oldKeyMap.values) {
      remaining.unmount();
    }
    for (int i = unkeyedIndex; i < oldUnkeyed.length; i++) {
      oldUnkeyed[i].unmount();
    }

    return result;
  }

  @override
  void unmount() {
    for (final child in childElements) {
      child.unmount();
    }
    super.unmount();
  }

  @override
  List<Element> get children => childElements;
}

/// Element for StatefulWidget.
class StatefulElement extends Element {
  late State _state;
  Element? _childElement;

  StatefulElement(StatefulWidget super.widget);

  @override
  void mount(Element? parent, int depth) {
    super.mount(parent, depth);
    _state = (widget as StatefulWidget).createState();
    _state._element = this;
    _state.initState();
    _rebuild();
  }

  @override
  void update(Widget newWidget) {
    super.update(newWidget);
    _rebuild();
  }

  void _rebuild() {
    final childWidget = _state.build();

    if (_childElement != null &&
        _childElement!.widget.canUpdate(childWidget)) {
      _childElement!.update(childWidget);
    } else {
      _childElement?.unmount();
      _childElement = childWidget.createElement();
      _childElement!.mount(this, depth + 1);
    }
    _dirty = false;
  }

  @override
  void unmount() {
    _state.dispose();
    _childElement?.unmount();
    super.unmount();
  }

  @override
  List<Element> get children =>
      _childElement != null ? [_childElement!] : [];
}

// ===========================================================================
// CORE ENGINE — Tree management and diagnostics
// ===========================================================================

/// Production widget tree engine with diff, mount/unmount lifecycle,
/// and tree traversal utilities.
class OmniWidgetTreeEngine {
  Element? _rootElement;
  int _totalMounts = 0;
  int _totalUpdates = 0;
  int _totalUnmounts = 0;
  int _totalRebuilds = 0;

  /// Mount a widget tree as the root.
  void mount(Widget rootWidget) {
    _rootElement?.unmount();
    _rootElement = rootWidget.createElement();
    _rootElement!.mount(null, 0);
    _totalMounts++;
  }

  /// Update the root with a new widget tree (triggers diffing).
  void update(Widget newRootWidget) {
    if (_rootElement == null) {
      mount(newRootWidget);
      return;
    }

    if (_rootElement!.widget.canUpdate(newRootWidget)) {
      _rootElement!.update(newRootWidget);
      _totalUpdates++;
    } else {
      _rootElement!.unmount();
      _totalUnmounts++;
      _rootElement = newRootWidget.createElement();
      _rootElement!.mount(null, 0);
      _totalMounts++;
    }
    _totalRebuilds++;
  }

  /// Unmount the entire tree.
  void unmount() {
    _rootElement?.unmount();
    _rootElement = null;
    _totalUnmounts++;
  }

  /// Get the root element.
  Element? get root => _rootElement;

  /// Count total elements in the tree.
  int get elementCount => _countElements(_rootElement);

  int _countElements(Element? el) {
    if (el == null) return 0;
    int count = 1;
    for (final child in el.children) {
      count += _countElements(child);
    }
    return count;
  }

  /// Get the maximum depth of the tree.
  int get maxDepth => _maxDepth(_rootElement);

  int _maxDepth(Element? el) {
    if (el == null) return 0;
    int max = el.depth;
    for (final child in el.children) {
      final d = _maxDepth(child);
      if (d > max) max = d;
    }
    return max;
  }

  /// Diagnostics for OMNI Engine Registry.
  Map<String, dynamic> diagnostics() {
    return {
      'engine': 'OmniWidgetTreeEngine',
      'layer': 'Dart UI',
      'element_count': elementCount,
      'max_depth': maxDepth,
      'has_root': _rootElement != null,
      'total_mounts': _totalMounts,
      'total_updates': _totalUpdates,
      'total_unmounts': _totalUnmounts,
      'total_rebuilds': _totalRebuilds,
      'learned_logic': [
        'flutter-three-layer-architecture',
        'widget-element-render-separation',
        'key-based-list-diffing-on',
        'can-update-type-key-matching',
        'stateful-widget-state-lifecycle',
        'set-state-mark-dirty-rebuild',
        'mount-unmount-lifecycle-hooks',
      ],
    };
  }
}
