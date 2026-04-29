import 'package:flutter/material.dart';

/// OMNI Monadic Result
class OmniResult<T> {
  final T? payload;
  final String? error;
  final bool isOk;

  OmniResult.ok(this.payload) : error = null, isOk = true;
  OmniResult.err(this.error) : payload = null, isOk = false;
}

class PaperIndexState {
  final int clusterId;
  final double withinSs;

  PaperIndexState(this.clusterId, this.withinSs);
}

class AwesomeLLM4SEController {
  OmniResult<PaperIndexState> validateClusterData(int clusterId, double wss) {
    if (clusterId < 0 || clusterId > 1000) {
      return OmniResult.err("OMNI_ERROR: Invalid cluster ID range.");
    }
    if (wss < 0) {
      return OmniResult.err("OMNI_ERROR: Within-cluster sum of squares cannot be negative.");
    }
    return OmniResult.ok(PaperIndexState(clusterId, wss));
  }
}

class AwesomeLLM4SEPortalWidget extends StatelessWidget {
  final AwesomeLLM4SEController controller = AwesomeLLM4SEController();
  final int clusterId;
  final double wss;

  AwesomeLLM4SEPortalWidget({required this.clusterId, required this.wss});

  @override
  Widget build(BuildContext context) {
    final result = controller.validateClusterData(clusterId, wss);
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("AwesomeLLM4SE Indexer", style: TextStyle(fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            result.isOk 
              ? Text("Cluster ${result.payload!.clusterId} | WSS: ${result.payload!.withinSs.toStringAsFixed(2)}")
              : Text("Error: ${result.error}", style: TextStyle(color: Colors.red)),
          ],
        ),
      ),
    );
  }
}
