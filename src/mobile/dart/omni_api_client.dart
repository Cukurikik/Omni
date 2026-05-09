// OMNI Framework - API Client (Dart)
// Connects Flutter mobile apps securely to the OMNI Gateway

import 'dart:convert';
import 'package:http/http.dart' as http;

class OmniApiClient {
  final String baseUrl;
  final String apiKey;

  OmniApiClient({required this.baseUrl, required this.apiKey});

  Future<String> generateText(String prompt) async {
    final url = Uri.parse('$baseUrl/v1/generate');
    
    try {
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $apiKey',
        },
        body: jsonEncode({
          'prompt': prompt,
          'max_tokens': 100
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['completion'] ?? '';
      } else {
        throw Exception('OMNI API Error: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('OMNI Network Error: $e');
    }
  }
}
