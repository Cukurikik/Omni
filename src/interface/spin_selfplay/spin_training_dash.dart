class OmniResult<T, E> {
  final bool isOk; final T? value; final E? error;
  OmniResult.ok(this.value) : isOk = true, error = null;
  OmniResult.error(this.error) : isOk = false, value = null;
}
class SPINTrainingDashboard {
  static const int maxIterations = 100;
  OmniResult<bool, String> renderIteration(int iter) {
    if (iter > maxIterations) return OmniResult.error("Exceeds display iterations");
    return OmniResult.ok(true);
  }
}
