// OMNI Interface Layer: graphrag_explorer.dart
// Flutter component for navigating GraphRAG knowledge graphs.
// Bound: Max 500 nodes rendered at once.

import 'dart:ui';

const int MAX_RENDER_NODES = 500;

class OmniError {
  final int code;
  final String message;
  OmniError(this.code, this.message);
}

class OmniResult<T> {
  final T? data;
  final OmniError? error;
  OmniResult(this.data, [this.error]);
}

class GraphNode {
  final String id;
  final Offset position;
  GraphNode(this.id, this.position);
}

class GraphExplorer {
  List<GraphNode> _visibleNodes = [];

  OmniResult<bool> updateViewport(List<GraphNode> nodesInView) {
    if (nodesInView.length > MAX_RENDER_NODES) {
      return OmniResult(null, OmniError(1, "Cannot render more than 500 GraphRAG nodes simultaneously."));
    }
    
    _visibleNodes = List.from(nodesInView);
    return OmniResult(true);
  }

  List<GraphNode> get currentNodes => _visibleNodes;
}
