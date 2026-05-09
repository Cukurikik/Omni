//=============================================================================
// OMNI INTERFACE LAYER — AURA EMOTION MUSIC RECOMMENDER (DART)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Flutter cross-platform UI for emotion-aware music recommendation.
// INSPIRED BY: muhdshahan/Aura-Emotion-Based-Song-Recommender
//=============================================================================

import 'package:flutter/material.dart';
import 'package:omni_bridge_network/omni_client.dart';
import 'package:omni_bridge_domain/monadic_result.dart';

// OMNI IDIOM: dart::widget
class AuraEmotionRecommender extends StatefulWidget {
  const AuraEmotionRecommender({Key? key}) : super(key: key);

  @override
  _AuraEmotionRecommenderState createState() => _AuraEmotionRecommenderState();
}

class _AuraEmotionRecommenderState extends State<AuraEmotionRecommender> {
  final TextEditingController _moodController = TextEditingController();
  String _recommendedSong = "";
  String _detectedEmotion = "";
  bool _isLoading = false;

  Future<void> _analyzeMood() async {
    final text = _moodController.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _isLoading = true;
      _recommendedSong = "";
      _detectedEmotion = "";
    });

    // OMNI IDIOM: Monadic Network call
    final Result<Map<String, dynamic>> response = 
        await OmniClient.invokeCommand('aura.detect_and_recommend', {"text": text});

    setState(() {
      _isLoading = false;
      if (response.isOk) {
        final data = response.unwrap();
        _detectedEmotion = data['emotion'];
        _recommendedSong = data['song_recommendation']['title'] + 
            " by " + data['song_recommendation']['artist'];
      } else {
        _detectedEmotion = "Error";
        _recommendedSong = response.getError().message;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24.0),
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("How are you feeling today?", 
              style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          TextField(
            controller: _moodController,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: "E.g., I'm feeling a bit down after work...",
              hintStyle: const TextStyle(color: Colors.white54),
              filled: true,
              fillColor: Colors.white10,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
            ),
            maxLines: 3,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _isLoading ? null : _analyzeMood,
            child: _isLoading ? const CircularProgressIndicator() : const Text("Find My Aura"),
          ),
          const SizedBox(height: 24),
          if (_detectedEmotion.isNotEmpty) ...[
            Text("Detected Aura: $_detectedEmotion", style: const TextStyle(color: Colors.cyanAccent, fontSize: 18)),
            const SizedBox(height: 8),
            Text("Suggested Track: $_recommendedSong", style: const TextStyle(color: Colors.greenAccent, fontSize: 16)),
          ]
        ],
      ),
    );
  }
}
