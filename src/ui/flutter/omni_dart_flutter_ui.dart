import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

// Omni Flutter App UI (Dart)
// Interface Layer
// Cross-platform mobile/desktop application to interact with the Omni 
// Transformer inference endpoints.

void main() {
  runApp(const OmniApp());
}

class OmniApp extends StatelessWidget {
  const OmniApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Omni Mother Nexus',
      theme: ThemeData(
        primarySwatch: Colors.deepPurple,
        brightness: Brightness.dark,
      ),
      home: const InferenceScreen(),
    );
  }
}

class InferenceScreen extends StatefulWidget {
  const InferenceScreen({Key? key}) : super(key: key);

  @override
  _InferenceScreenState createState() => _InferenceScreenState();
}

class _InferenceScreenState extends State<InferenceScreen> {
  final TextEditingController _promptController = TextEditingController();
  String _responseText = '';
  bool _isLoading = false;

  Future<void> _runInference() async {
    if (_promptController.text.isEmpty) return;

    setState(() {
      _isLoading = true;
      _responseText = '';
    });

    try {
      // In a real scenario, this connects to the Omni gRPC or GraphQL endpoint
      final response = await http.post(
        Uri.parse('https://api.omni-nexus.dev/v1/generate'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'modelId': 'Omni-GPT4o-Multimodal',
          'prompt': _promptController.text,
          'maxTokens': 256
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _responseText = data['text'] ?? 'No output generated.';
        });
      } else {
        setState(() {
          _responseText = 'Error: \${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _responseText = 'Connection failed: \$e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Omni Inference Engine'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _promptController,
              decoration: const InputDecoration(
                labelText: 'Enter Prompt',
                border: OutlineInputBorder(),
              ),
              maxLines: 4,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _isLoading ? null : _runInference,
              child: _isLoading 
                ? const CircularProgressIndicator(color: Colors.white) 
                : const Text('Generate'),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 50),
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: SingleChildScrollView(
                child: Text(
                  _responseText,
                  style: const TextStyle(fontSize: 16, height: 1.5),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
