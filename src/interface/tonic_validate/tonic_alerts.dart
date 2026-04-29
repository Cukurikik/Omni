import 'package:flutter/material.dart';

class OmniResult<T> {
  final T? payload;
  final String? error;
  final bool isOk;

  OmniResult.ok(this.payload) : error = null, isOk = true;
  OmniResult.err(this.error) : payload = null, isOk = false;
}

class TonicAlertController {
  OmniResult<bool> validateAlertThreshold(double variance) {
    if (variance < 0) return OmniResult.err("OMNI_ERROR: Variance cannot be negative.");
    if (variance > 0.05) {
      // Trigger alert
      return OmniResult.ok(true);
    }
    return OmniResult.ok(false);
  }
}

class TonicAlertWidget extends StatelessWidget {
  final double currentVariance;
  final TonicAlertController _controller = TonicAlertController();

  TonicAlertWidget({required this.currentVariance});

  @override
  Widget build(BuildContext context) {
    final result = _controller.validateAlertThreshold(currentVariance);
    
    return Container(
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: result.isOk && result.payload == true ? Colors.red.shade100 : Colors.green.shade100,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            result.isOk && result.payload == true ? Icons.warning : Icons.check_circle,
            color: result.isOk && result.payload == true ? Colors.red : Colors.green,
          ),
          SizedBox(width: 8),
          Text(
            result.isOk 
              ? (result.payload == true ? "ALERT: High Variance" : "System Stable")
              : "Error: ${result.error}",
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }
}
