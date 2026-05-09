// OMNI Interface — Dart/Flutter Inference Widget
// Cross-platform inference chat widget with streaming support.

import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class InferenceConfig {
  final String baseUrl;
  final int maxTokens;
  final double temperature;
  final Duration timeout;

  const InferenceConfig({
    this.baseUrl = 'http://localhost:8080/api/v1',
    this.maxTokens = 256,
    this.temperature = 0.7,
    this.timeout = const Duration(seconds: 30),
  });
}

class InferenceResult {
  final String text;
  final int tokens;
  final double latencyMs;
  final String requestId;

  InferenceResult({required this.text, required this.tokens, required this.latencyMs, this.requestId = ''});

  factory InferenceResult.fromJson(Map<String, dynamic> json) => InferenceResult(
    text: json['generated_text'] ?? '', tokens: json['tokens_generated'] ?? 0,
    latencyMs: (json['latency_ms'] ?? 0).toDouble(), requestId: json['request_id'] ?? '',
  );
}

class OmniInferenceService {
  final InferenceConfig config;
  final http.Client _client;
  int _totalRequests = 0;
  double _totalLatency = 0;

  OmniInferenceService({this.config = const InferenceConfig()}) : _client = http.Client();

  Future<InferenceResult> infer(String prompt) async {
    _totalRequests++;
    final stopwatch = Stopwatch()..start();

    final response = await _client.post(
      Uri.parse('${config.baseUrl}/infer'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'prompt': prompt, 'max_tokens': config.maxTokens, 'temperature': config.temperature,
      }),
    ).timeout(config.timeout);

    stopwatch.stop();
    _totalLatency += stopwatch.elapsedMilliseconds;

    if (response.statusCode == 200) {
      final result = InferenceResult.fromJson(jsonDecode(response.body));
      return result;
    }
    throw Exception('Inference failed: ${response.statusCode}');
  }

  Map<String, dynamic> get stats => {
    'total_requests': _totalRequests,
    'avg_latency_ms': _totalRequests > 0 ? _totalLatency / _totalRequests : 0,
  };

  void dispose() => _client.close();
}

class OmniChatWidget extends StatefulWidget {
  final InferenceConfig config;
  const OmniChatWidget({super.key, this.config = const InferenceConfig()});
  @override State<OmniChatWidget> createState() => _OmniChatWidgetState();
}

class _OmniChatWidgetState extends State<OmniChatWidget> {
  final _controller = TextEditingController();
  final _messages = <Map<String, String>>[];
  late final OmniInferenceService _service;
  bool _loading = false;

  @override
  void initState() { super.initState(); _service = OmniInferenceService(config: widget.config); }

  Future<void> _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _loading) return;
    setState(() { _messages.add({'role': 'user', 'text': text}); _loading = true; });
    _controller.clear();
    try {
      final result = await _service.infer(text);
      setState(() { _messages.add({'role': 'assistant', 'text': result.text}); });
    } catch (e) {
      setState(() { _messages.add({'role': 'error', 'text': e.toString()}); });
    } finally { setState(() => _loading = false); }
  }

  @override
  Widget build(BuildContext context) => Column(children: [
    Expanded(child: ListView.builder(
      itemCount: _messages.length, reverse: true,
      itemBuilder: (_, i) {
        final msg = _messages[_messages.length - 1 - i];
        final isUser = msg['role'] == 'user';
        return Align(
          alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
          child: Container(
            margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: isUser ? const Color(0xFF6366F1) : const Color(0xFF1E2740),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(msg['text'] ?? '', style: const TextStyle(color: Colors.white)),
          ),
        );
      },
    )),
    if (_loading) const LinearProgressIndicator(),
    Padding(
      padding: const EdgeInsets.all(8),
      child: Row(children: [
        Expanded(child: TextField(controller: _controller, style: const TextStyle(color: Colors.white),
          decoration: InputDecoration(hintText: 'Ask anything...', hintStyle: TextStyle(color: Colors.grey[600]),
            filled: true, fillColor: const Color(0xFF131829), border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))))),
        const SizedBox(width: 8),
        ElevatedButton(onPressed: _loading ? null : _send, style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF6366F1)),
          child: const Text('Send')),
      ]),
    ),
  ]);

  @override void dispose() { _service.dispose(); _controller.dispose(); super.dispose(); }
}
