// OMNI Divine Memory Integration: Inspired by Promptify
// Interface Layer - Dart strict UI parser for LLM Structured Output

import 'dart:convert';

class OmniError implements Exception {
  final int code;
  final String message;
  OmniError(this.code, this.message);
}

class OmniResult<T> {
  final bool isOk;
  final T? value;
  final OmniError? error;

  OmniResult.ok(this.value) : isOk = true, error = null;
  OmniResult.err(this.error) : isOk = false, value = null;
}

class PromptifyParser {
  static const int MAX_PAYLOAD_CHARS = 1048576; // 1MB text bound limit

  static OmniResult<Map<String, dynamic>> parseStructuredResponse(String rawOutput) {
    if (rawOutput.length > MAX_PAYLOAD_CHARS) {
      return OmniResult.err(OmniError(413, "LLM Response exceeds 1MB UI parsing limits."));
    }

    try {
      // Find JSON bounds in raw LLM output
      final startIndex = rawOutput.indexOf('{');
      final endIndex = rawOutput.lastIndexOf('}');
      
      if (startIndex == -1 || endIndex == -1 || startIndex > endIndex) {
         return OmniResult.err(OmniError(400, "No structured JSON boundaries found in prompt response."));
      }

      final jsonStr = rawOutput.substring(startIndex, endIndex + 1);
      final decoded = jsonDecode(jsonStr) as Map<String, dynamic>;
      
      return OmniResult.ok(decoded);
    } catch (e) {
      return OmniResult.err(OmniError(500, "Structured parsing failure: ${e.toString()}"));
    }
  }
}
