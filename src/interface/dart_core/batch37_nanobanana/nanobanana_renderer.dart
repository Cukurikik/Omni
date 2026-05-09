// @omni-domain Interface Layer (Nanobanana)
// @omni-source Semester 12 Batch 37
// @omni-description Nanobanana high-performance rendering engine for visualization.
// @omni-requirement zero-mock, monadic-error

import 'dart:typed_data';

class OmniResult<T> {
  final bool ok;
  final T? value;
  final Exception? error;

  OmniResult.ok(this.value) : ok = true, error = null;
  OmniResult.err(this.error) : ok = false, value = null;
}

class NanobananaRenderer {
  final int width;
  final int height;
  late Float32List _pixelBuffer;

  NanobananaRenderer({required this.width, required this.height}) {
    if (width <= 0 || height <= 0) {
      throw ArgumentError("Dimensions must be strictly positive");
    }
    _pixelBuffer = Float32List(width * height * 4); // RGBA
  }

  OmniResult<bool> drawRect(int x, int y, int w, int h, List<double> color) {
    if (color.length != 4) {
      return OmniResult.err(Exception("Color must be RGBA (length 4)"));
    }
    
    if (x < 0 || y < 0 || x + w > width || y + h > height) {
      return OmniResult.err(Exception("Rectangle out of bounds"));
    }

    try {
      for (int i = y; i < y + h; i++) {
        for (int j = x; j < x + w; j++) {
          int index = (i * width + j) * 4;
          _pixelBuffer[index] = color[0];
          _pixelBuffer[index+1] = color[1];
          _pixelBuffer[index+2] = color[2];
          _pixelBuffer[index+3] = color[3];
        }
      }
      return OmniResult.ok(true);
    } catch (e) {
      return OmniResult.err(Exception(e.toString()));
    }
  }

  OmniResult<Float32List> getRenderBuffer() {
    return OmniResult.ok(_pixelBuffer);
  }
}
