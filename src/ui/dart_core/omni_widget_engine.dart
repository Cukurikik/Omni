// ===========================================================================
// OMNI WIDGET ENGINE (SEMESTER 3 — BATCH 38.8)
// ===========================================================================
// Absorbed From  : Flutter Widget tree + Riverpod + Bloc + Provider
// Logic Inherited: Dart / Interface Layer (Declarative Widget Composition)
// ===========================================================================
//
// By studying Flutter's widget system, Mother learned:
//   1. Everything is a widget: UI = tree of immutable widget descriptions
//   2. StatelessWidget: pure function of props → UI
//   3. StatefulWidget: widget + mutable State that triggers rebuild
//   4. InheritedWidget: implicit dependency injection down the tree
//   5. Keys control widget identity across rebuilds


// ============================================================
// PART 1: Core Widget Abstractions
// ============================================================

/// Base widget class (immutable blueprint).
abstract class OmniWidget {
  final String? key;

  const OmniWidget({this.key});

  /// Build this widget's element representation.
  OmniElement createElement();

  /// Render to string (for testing/SSR).
  String render();
}

/// Element: the instantiated, mutable counterpart of a widget.
abstract class OmniElement {
  OmniWidget widget;
  OmniElement? parent;
  final List<OmniElement> children = [];
  bool _mounted = false;
  bool _dirty = false;

  OmniElement(this.widget);

  void mount(OmniElement? parent) {
    this.parent = parent;
    _mounted = true;
  }

  void unmount() {
    _mounted = false;
    for (final child in children) {
      child.unmount();
    }
  }

  void markDirty() {
    _dirty = true;
  }

  void rebuild() {
    if (_dirty) {
      performRebuild();
      _dirty = false;
    }
  }

  void performRebuild();

  bool get mounted => _mounted;
}

// ============================================================
// PART 2: StatelessWidget
// ============================================================

/// Stateless widget (pure function of config → UI).
abstract class OmniStatelessWidget extends OmniWidget {
  const OmniStatelessWidget({super.key});

  /// Build method: returns the child widget tree.
  OmniWidget build();

  @override
  OmniElement createElement() => StatelessElement(this);

  @override
  String render() => build().render();
}

class StatelessElement extends OmniElement {
  StatelessElement(OmniStatelessWidget super.widget);

  @override
  void performRebuild() {
    final child = (widget as OmniStatelessWidget).build();
    final childElement = child.createElement();
    childElement.mount(this);
    children
      ..clear()
      ..add(childElement);
  }
}

// ============================================================
// PART 3: StatefulWidget
// ============================================================

/// Stateful widget: has mutable State that triggers rebuilds.
abstract class OmniStatefulWidget extends OmniWidget {
  const OmniStatefulWidget({super.key});

  /// Create the mutable State object.
  OmniState createState();

  @override
  OmniElement createElement() => StatefulElement(this);

  @override
  String render() {
    final state = createState();
    state._widget = this;
    return state.build().render();
  }
}

/// Mutable state associated with a StatefulWidget.
abstract class OmniState<T extends OmniStatefulWidget> {
  late T _widget;
  StatefulElement? _element;
  int _rebuildCount = 0;

  T get widget => _widget;

  /// Trigger a rebuild (like Flutter's setState).
  void setState(void Function() fn) {
    fn();
    _rebuildCount++;
    _element?.markDirty();
    _element?.rebuild();
  }

  /// Build the widget tree for current state.
  OmniWidget build();

  /// Lifecycle: called when state is first created.
  void initState() {}

  /// Lifecycle: called when widget is removed.
  void dispose() {}

  int get rebuildCount => _rebuildCount;
}

class StatefulElement extends OmniElement {
  late OmniState _state;

  StatefulElement(OmniStatefulWidget widget) : super(widget) {
    _state = widget.createState();
    _state._widget = widget;
    _state._element = this;
    _state.initState();
  }

  @override
  void performRebuild() {
    final child = _state.build();
    final childElement = child.createElement();
    childElement.mount(this);
    children
      ..clear()
      ..add(childElement);
  }

  @override
  void unmount() {
    _state.dispose();
    super.unmount();
  }
}

// ============================================================
// PART 4: Built-in Widgets
// ============================================================

/// Text widget.
class OmniText extends OmniStatelessWidget {
  final String text;
  final String? style;

  const OmniText(this.text, {this.style, super.key});

  @override
  OmniWidget build() => this;

  @override
  String render() {
    final styleAttr = style != null ? ' style="$style"' : '';
    return '<span$styleAttr>$text</span>';
  }
}

/// Container widget (analogous to Flutter's Container).
class OmniContainer extends OmniStatelessWidget {
  final OmniWidget? child;
  final String? width;
  final String? height;
  final String? padding;
  final String? margin;
  final String? color;

  const OmniContainer({
    this.child,
    this.width,
    this.height,
    this.padding,
    this.margin,
    this.color,
    super.key,
  });

  @override
  OmniWidget build() => this;

  @override
  String render() {
    final styles = <String>[];
    if (width != null) styles.add('width: $width');
    if (height != null) styles.add('height: $height');
    if (padding != null) styles.add('padding: $padding');
    if (margin != null) styles.add('margin: $margin');
    if (color != null) styles.add('background-color: $color');

    final styleAttr = styles.isNotEmpty ? ' style="${styles.join('; ')}"' : '';
    final inner = child?.render() ?? '';
    return '<div$styleAttr>$inner</div>';
  }
}

/// Column/Row layout widget.
class OmniColumn extends OmniStatelessWidget {
  final List<OmniWidget> children;
  final String? gap;

  const OmniColumn({required this.children, this.gap, super.key});

  @override
  OmniWidget build() => this;

  @override
  String render() {
    final gapStyle = gap != null ? 'gap: $gap; ' : '';
    final inner = children.map((w) => w.render()).join('\n');
    return '<div style="display: flex; flex-direction: column; $gapStyle">$inner</div>';
  }
}

class OmniRow extends OmniStatelessWidget {
  final List<OmniWidget> children;
  final String? gap;

  const OmniRow({required this.children, this.gap, super.key});

  @override
  OmniWidget build() => this;

  @override
  String render() {
    final gapStyle = gap != null ? 'gap: $gap; ' : '';
    final inner = children.map((w) => w.render()).join('\n');
    return '<div style="display: flex; flex-direction: row; $gapStyle">$inner</div>';
  }
}

/// ListView with builder pattern.
class OmniListView extends OmniStatelessWidget {
  final int itemCount;
  final OmniWidget Function(int index) itemBuilder;

  const OmniListView({
    required this.itemCount,
    required this.itemBuilder,
    super.key,
  });

  @override
  OmniWidget build() => this;

  @override
  String render() {
    final items = List.generate(itemCount, (i) => itemBuilder(i).render());
    return '<div style="overflow-y: auto;">${items.join('\n')}</div>';
  }
}

// ============================================================
// PART 5: State Management (Provider-inspired)
// ============================================================

/// Simple value notifier (ChangeNotifier equivalent).
class ValueNotifier<T> {
  T _value;
  final List<void Function(T)> _listeners = [];
  int _notifyCount = 0;

  ValueNotifier(this._value);

  T get value => _value;

  set value(T newValue) {
    if (_value != newValue) {
      _value = newValue;
      _notifyCount++;
      for (final listener in _listeners) {
        listener(_value);
      }
    }
  }

  void addListener(void Function(T) listener) {
    _listeners.add(listener);
  }

  void removeListener(void Function(T) listener) {
    _listeners.remove(listener);
  }

  void dispose() {
    _listeners.clear();
  }

  int get listenerCount => _listeners.length;
  int get notifyCount => _notifyCount;
}

// ============================================================
// Diagnostics
// ============================================================

Map<String, dynamic> widgetDiagnostics() {
  return {
    'engine': 'OmniWidgetEngine',
    'layer': 'Dart Interface',
    'components': [
      'OmniWidget', 'OmniElement', 'OmniStatelessWidget',
      'OmniStatefulWidget', 'OmniState', 'ValueNotifier',
    ],
    'widgets': [
      'OmniText', 'OmniContainer', 'OmniColumn', 'OmniRow', 'OmniListView',
    ],
    'learned_logic': [
      'widget-element-separation',
      'stateless-pure-build-function',
      'stateful-setState-rebuild',
      'element-mount-unmount-lifecycle',
      'key-based-identity',
      'builder-pattern-listview',
      'value-notifier-change-notify',
      'declarative-widget-composition',
    ],
  };
}
