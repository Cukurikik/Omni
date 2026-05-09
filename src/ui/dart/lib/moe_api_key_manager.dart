import 'package:flutter/material.dart';

/// OMNI Framework - API Key Manager Widget (Flutter)
/// Allows users in the desktop app to view, copy, and rotate their Tenant API keys.

class MoeApiKeyManager extends StatelessWidget {
  final String currentApiKey;
  final VoidCallback onRotatePressed;

  const MoeApiKeyManager({
    Key? key,
    required this.currentApiKey,
    required this.onRotatePressed,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF161b22),
        border: Border.all(color: const Color(0xFF30363d)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "Authentication",
            style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: Colors.black, borderRadius: BorderRadius.circular(4)),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(currentApiKey, style: const TextStyle(color: Color(0xFF3fb950), fontFamily: 'monospace')),
                IconButton(
                  icon: const Icon(Icons.copy, color: Colors.white54, size: 18),
                  onPressed: () { /* Copy to Clipboard */ },
                )
              ],
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF238636)),
            onPressed: onRotatePressed,
            child: const Text("Rotate Key", style: TextStyle(color: Colors.white)),
          )
        ],
      ),
    );
  }
}
