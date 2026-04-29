import 'package:flutter/material.dart';

class DetectionBox {
  final double x, y, w, h;
  final String label;
  final double confidence;
  DetectionBox(this.x, this.y, this.w, this.h, this.label, this.confidence);
}

class RFDetrOverlay extends StatelessWidget {
  final List<DetectionBox> detections;

  RFDetrOverlay({required this.detections});

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: detections.map((box) {
        return Positioned(
          left: box.x, top: box.y, width: box.w, height: box.h,
          child: Container(
            decoration: BoxDecoration(
              border: Border.all(color: Colors.red, width: 2),
            ),
            child: Text('${box.label} ${(box.confidence * 100).toStringAsFixed(1)}%',
                style: TextStyle(backgroundColor: Colors.red, color: Colors.white)),
          ),
        );
      }).toList(),
    );
  }
}
