import 'package:flutter/material.dart';

class OpenCVFilterUI extends StatefulWidget {
  @override
  _OpenCVFilterUIState createState() => _OpenCVFilterUIState();
}

class _OpenCVFilterUIState extends State<OpenCVFilterUI> {
  double _blurRadius = 0.0;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(16),
      child: Column(
        children: [
          Text("Gaussian Blur Radius: ${_blurRadius.toStringAsFixed(1)}"),
          Slider(
            value: _blurRadius,
            min: 0,
            max: 50,
            onChanged: (val) {
              setState(() {
                _blurRadius = val;
                // Dispatch to OpenCV FFI Bridge
              });
            },
          ),
          // Container for processed image output
          Container(
             height: 300,
             color: Colors.black12,
             child: Center(child: Text("C++ FFI Output Stream Here")),
          )
        ],
      ),
    );
  }
}
