// Omni Libre Chat Mobile (Dart)
// Mobile Layer: Cross-platform chat message validation.
// Ref: vemonet/libre-chat

class ChatValidationResult {
  final bool valid;
  final String error;
  ChatValidationResult._({required this.valid, required this.error});
  factory ChatValidationResult.ok() => ChatValidationResult._(valid: true, error: "");
  factory ChatValidationResult.err(String e) => ChatValidationResult._(valid: false, error: e);
}

class OmniLibreChatValidator {
  static ChatValidationResult validate(String role, String content) {
    if (role.isEmpty || content.isEmpty) return ChatValidationResult.err("Empty fields");
    if (!['system', 'user', 'assistant'].contains(role)) return ChatValidationResult.err("Invalid role");
    return ChatValidationResult.ok();
  }
}
