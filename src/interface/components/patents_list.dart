//=============================================================================
// OMNI INTERFACE LAYER — PATENT LISTING VIEW (DART)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Flutter UI for displaying AI Patent classifications.
// INSPIRED BY: MIRICMILAN/US-AI-Patents
//=============================================================================

import 'package:flutter/material.dart';
import 'package:omni_bridge_network/omni_client.dart';

class PatentModel {
  final String id;
  final String title;
  final bool isAiRelated;
  final double confidence;

  PatentModel(this.id, this.title, this.isAiRelated, this.confidence);
}

// OMNI IDIOM: dart::widget
class PatentListingView extends StatefulWidget {
  const PatentListingView({Key? key}) : super(key: key);

  @override
  _PatentListingViewState createState() => _PatentListingViewState();
}

class _PatentListingViewState extends State<PatentListingView> {
  List<PatentModel> patents = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchPatents();
  }

  Future<void> _fetchPatents() async {
    // OMNI IDIOM: Cross-layer invocation
    final result = await OmniClient.invokeCommand('domain.patents.list_all', {});
    
    if (result.isOk) {
      final data = result.unwrap() as List<dynamic>;
      setState(() {
        patents = data.map((p) => PatentModel(
          p['id'], p['title'], p['is_ai_related'], p['confidence']
        )).toList();
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return ListView.builder(
      itemCount: patents.length,
      itemBuilder: (context, index) {
        final p = patents[index];
        return Card(
          color: p.isAiRelated ? Colors.blue.withOpacity(0.1) : Colors.grey.shade900,
          child: ListTile(
            leading: Icon(
              p.isAiRelated ? Icons.smart_toy : Icons.description,
              color: p.isAiRelated ? Colors.cyan : Colors.grey,
            ),
            title: Text(p.title, style: const TextStyle(color: Colors.white)),
            subtitle: Text("Confidence: ${(p.confidence * 100).toStringAsFixed(1)}%"),
            trailing: Text(p.id),
          ),
        );
      },
    );
  }
}
