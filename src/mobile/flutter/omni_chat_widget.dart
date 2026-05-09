// OMNI Mobile — Flutter Chat Widget
import 'package:flutter/material.dart';

class OmniChatWidget extends StatefulWidget {
  final String apiEndpoint;
  
  const OmniChatWidget({Key? key, required this.apiEndpoint}) : super(key: key);

  @override
  _OmniChatWidgetState createState() => _OmniChatWidgetState();
}

class _OmniChatWidgetState extends State<OmniChatWidget> {
  final List<String> _messages = [];
  final TextEditingController _controller = TextEditingController();

  void _sendMessage() {
    if (_controller.text.isEmpty) return;
    
    setState(() {
      _messages.add("User: ${_controller.text}");
    });
    
    // Simulate API Call
    Future.delayed(Duration(seconds: 1), () {
      setState(() {
        _messages.add("Omni: Acknowledged. Processing request.");
      });
    });
    
    _controller.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            itemCount: _messages.length,
            itemBuilder: (context, index) {
              return ListTile(title: Text(_messages[index]));
            },
          ),
        ),
        Row(
          children: [
            Expanded(child: TextField(controller: _controller)),
            IconButton(icon: Icon(Icons.send), onPressed: _sendMessage),
          ],
        )
      ],
    );
  }
}
