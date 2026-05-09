// OMNI Framework - DeepHumor Meme Generator UI
// Flutter widget for displaying and generating AI memes.

import 'package:flutter/material.dart';

class OmniMemeGenApp extends StatefulWidget {
  @override
  _OmniMemeGenAppState createState() => _OmniMemeGenAppState();
}

class _OmniMemeGenAppState extends State<OmniMemeGenApp> {
  String _imageUrl = 'https://via.placeholder.com/400';
  String _generatedCaption = '';
  bool _isLoading = false;

  void _generateMeme() async {
    setState(() {
      _isLoading = true;
    });

    // Simulate calling the Python DeepHumor API layer
    await Future.delayed(Duration(seconds: 2));

    setState(() {
      _generatedCaption = "When the LLM hallucinates but the code compiles anyway";
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('OMNI DeepHumor Generator'),
        backgroundColor: Colors.deepPurple,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Image.network(_imageUrl, height: 300, fit: BoxFit.cover),
            SizedBox(height: 20),
            if (_generatedCaption.isNotEmpty)
              Text(
                _generatedCaption,
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, fontStyle: FontStyle.italic),
                textAlign: TextAlign.center,
              ),
            SizedBox(height: 40),
            ElevatedButton(
              onPressed: _isLoading ? null : _generateMeme,
              child: _isLoading 
                ? CircularProgressIndicator(color: Colors.white)
                : Text('Generate Meme Caption'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(horizontal: 40, vertical: 15),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
