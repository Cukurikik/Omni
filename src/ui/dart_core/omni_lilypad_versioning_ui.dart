import 'package:flutter/material.dart';

// Omni Lilypad Versioning UI (Dart/Flutter)
// Zero-mock, strongly typed widget for LLM prompt versioning control.

class OmniLilypadVersioningUI extends StatelessWidget {
  final String currentPromptHash;
  final bool isSynced;

  const OmniLilypadVersioningUI({
    Key? key,
    required this.currentPromptHash,
    required this.isSynced,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (currentPromptHash.isEmpty) {
      return const Center(child: Text("Error: Hash cannot be empty", style: TextStyle(color: Colors.red)));
    }

    return Container(
      padding: const EdgeInsets.all(16.0),
      color: const Color(0xFF0D1117),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("Lilypad Prompt State", style: TextStyle(color: Colors.white, fontSize: 18)),
          const SizedBox(height: 10),
          Text("Hash: $currentPromptHash", style: const TextStyle(color: Colors.greenAccent)),
          Text("Sync Status: ${isSynced ? 'SYNCHRONIZED' : 'PENDING'}", style: const TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }
}
