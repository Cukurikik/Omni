// OMNI Interface Layer: Flutter State Management
import 'package:flutter/foundation.dart';

class OmniStateManager extends ChangeNotifier {
  int _omniCount = 0;
  int get count => _omniCount;

  void increment() {
    _omniCount++;
    notifyListeners();
  }
}
