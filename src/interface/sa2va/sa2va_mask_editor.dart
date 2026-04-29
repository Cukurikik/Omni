// Sa2VA segmentation mask editor
// Web/Mobile rendering via Flutter engine

class OmniResult<T, E> {
  final bool isOk;
  final T? value;
  final E? error;

  OmniResult.ok(this.value) : isOk = true, error = null;
  OmniResult.error(this.error) : isOk = false, value = null;
}

class MaskEditor {
  static const int maxMaskLayers = 16; // Hard limit for pixel shaders

  OmniResult<bool, String> addMaskLayer(int currentLayers) {
    if (currentLayers >= maxMaskLayers) {
      return OmniResult.error("Maximum mask layers ($maxMaskLayers) reached. Hardware limit.");
    }
    
    return OmniResult.ok(true);
  }
}
