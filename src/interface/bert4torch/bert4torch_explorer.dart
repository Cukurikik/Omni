class OmniResult<T, E> {
  final bool isOk; final T? value; final E? error;
  OmniResult.ok(this.value) : isOk = true, error = null;
  OmniResult.error(this.error) : isOk = false, value = null;
}
class Bert4TorchModelExplorer {
  static const int maxLayers = 200;
  OmniResult<bool, String> visualizeLayer(int layerIdx) {
    if (layerIdx >= maxLayers) return OmniResult.error("Layer index out of bounds");
    return OmniResult.ok(true);
  }
}
