/// ===========================================================================
/// OMNI UI LAYER — SCRAPECRAFT VISUAL SCRAPING GRAPH EDITOR
/// ===========================================================================
/// Source Paradigm : ScrapeGraphAI/scrapecraft
/// Domain Layer   : UI (Cross-platform mobile & web UI)
/// Language        : Dart
/// Function        : Visual node-graph editor for building AI-powered web
///                   scraping pipelines. Defines a typed node system
///                   (Source → Selector → Transform → Output), validates DAG
///                   connections, and generates executable scraping code.
/// ===========================================================================

import 'dart:convert';

// ---- Node Types -----------------------------------------------------------

enum NodeType { source, selector, transformer, output }

/// Abstract base class for all pipeline nodes.
abstract class PipelineNode {
  final String id;
  final String label;
  final NodeType type;
  final Map<String, dynamic> config;
  final List<String> inputPorts;
  final List<String> outputPorts;

  PipelineNode({
    required this.id,
    required this.label,
    required this.type,
    this.config = const {},
    this.inputPorts = const [],
    this.outputPorts = const ['out'],
  });

  Map<String, dynamic> toJson() => {
    'id': id, 'label': label, 'type': type.name,
    'config': config, 'inputs': inputPorts, 'outputs': outputPorts,
  };
}

class SourceNode extends PipelineNode {
  SourceNode({required String id, required String url})
    : super(
        id: id, label: 'URL Source', type: NodeType.source,
        config: {'url': url, 'method': 'GET', 'headers': <String, String>{}},
        inputPorts: [],
        outputPorts: ['html'],
      );
}

class SelectorNode extends PipelineNode {
  SelectorNode({required String id, String selectorType = 'css', String expression = ''})
    : super(
        id: id, label: 'Selector', type: NodeType.selector,
        config: {'selector_type': selectorType, 'expression': expression, 'attribute': 'text'},
        inputPorts: ['html'],
        outputPorts: ['elements'],
      );
}

class TransformerNode extends PipelineNode {
  TransformerNode({required String id, String operation = 'trim'})
    : super(
        id: id, label: 'Transform', type: NodeType.transformer,
        config: {'operation': operation, 'regex': '', 'replacement': ''},
        inputPorts: ['elements'],
        outputPorts: ['data'],
      );
}

class OutputNode extends PipelineNode {
  OutputNode({required String id, String format = 'json'})
    : super(
        id: id, label: 'Output', type: NodeType.output,
        config: {'format': format, 'file_path': 'output.$format'},
        inputPorts: ['data'],
        outputPorts: [],
      );
}

// ---- Edge / Connection ----------------------------------------------------

class PipelineEdge {
  final String fromNodeId;
  final String fromPort;
  final String toNodeId;
  final String toPort;

  const PipelineEdge({
    required this.fromNodeId,
    required this.fromPort,
    required this.toNodeId,
    required this.toPort,
  });

  Map<String, String> toJson() => {
    'from': '$fromNodeId.$fromPort',
    'to': '$toNodeId.$toPort',
  };
}

// ---- Pipeline Graph -------------------------------------------------------

class ScrapingPipeline {
  final String name;
  final List<PipelineNode> nodes;
  final List<PipelineEdge> edges;

  ScrapingPipeline({required this.name, List<PipelineNode>? nodes, List<PipelineEdge>? edges})
    : nodes = nodes ?? [], edges = edges ?? [];

  /// Add a node to the graph.
  void addNode(PipelineNode node) {
    print('[SCRAPECRAFT-OMNI-DART] Added node: ${node.label} (${node.id})');
    nodes.add(node);
  }

  /// Connect two nodes via a typed edge.
  void connect(String fromId, String fromPort, String toId, String toPort) {
    // Validate port existence
    final fromNode = nodes.firstWhere((n) => n.id == fromId);
    final toNode = nodes.firstWhere((n) => n.id == toId);

    if (!fromNode.outputPorts.contains(fromPort)) {
      throw StateError('Node $fromId has no output port "$fromPort"');
    }
    if (!toNode.inputPorts.contains(toPort)) {
      throw StateError('Node $toId has no input port "$toPort"');
    }

    print('[SCRAPECRAFT-OMNI-DART] Connected: $fromId.$fromPort → $toId.$toPort');
    edges.add(PipelineEdge(fromNodeId: fromId, fromPort: fromPort, toNodeId: toId, toPort: toPort));
  }

  /// Validate the pipeline is a proper DAG (no cycles).
  bool validateDAG() {
    final visited = <String>{};
    final stack = <String>{};

    bool hasCycle(String nodeId) {
      if (stack.contains(nodeId)) return true;
      if (visited.contains(nodeId)) return false;
      visited.add(nodeId);
      stack.add(nodeId);

      for (final edge in edges.where((e) => e.fromNodeId == nodeId)) {
        if (hasCycle(edge.toNodeId)) return true;
      }

      stack.remove(nodeId);
      return false;
    }

    for (final node in nodes) {
      if (hasCycle(node.id)) {
        print('[SCRAPECRAFT-OMNI-DART] ⚠ Cycle detected — invalid pipeline!');
        return false;
      }
    }

    print('[SCRAPECRAFT-OMNI-DART] ✓ Pipeline is a valid DAG.');
    return true;
  }

  /// Export the entire pipeline as a JSON schema.
  String toJson() {
    final map = {
      'name': name,
      'nodes': nodes.map((n) => n.toJson()).toList(),
      'edges': edges.map((e) => e.toJson()).toList(),
    };
    return const JsonEncoder.withIndent('  ').convert(map);
  }
}

// ---- FFI Test Harness (commented) -----------------------------------------
// void main() {
//   final pipeline = ScrapingPipeline(name: 'Product Scraper');
//   pipeline.addNode(SourceNode(id: 'src', url: 'https://example.com/products'));
//   pipeline.addNode(SelectorNode(id: 'sel', expression: '.product-card h2'));
//   pipeline.addNode(TransformerNode(id: 'trim', operation: 'trim'));
//   pipeline.addNode(OutputNode(id: 'out', format: 'json'));
//   pipeline.connect('src', 'html', 'sel', 'html');
//   pipeline.connect('sel', 'elements', 'trim', 'elements');
//   pipeline.connect('trim', 'data', 'out', 'data');
//   pipeline.validateDAG();
//   print(pipeline.toJson());
// }
