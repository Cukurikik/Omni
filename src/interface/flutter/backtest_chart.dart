import 'package:flutter/material.dart';

class VectorbtChart extends StatelessWidget {
  final List<double> equityCurve;

  VectorbtChart({required this.equityCurve});

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: _ChartPainter(equityCurve),
      size: Size(double.infinity, 200),
    );
  }
}

class _ChartPainter extends CustomPainter {
  final List<double> data;
  _ChartPainter(this.data);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = Colors.green..strokeWidth = 2.0;
    // Drawing math stub
    canvas.drawLine(Offset(0, size.height), Offset(size.width, 0), paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
