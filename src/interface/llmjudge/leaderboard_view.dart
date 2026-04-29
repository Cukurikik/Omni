class OmniResult<T> {
  final T? value;
  final String? error;
  final bool isOk;

  OmniResult({this.value, this.error}) : isOk = error == null;
}

class LeaderboardViewUI {
  OmniResult<bool> renderEloRankings(List<Map<String, dynamic>> models) {
    if (models.isEmpty) {
      return OmniResult(error: 'No models to display');
    }

    // Dart frontend logic for rendering MT-Bench / LLM-Judge style leaderboard
    print('Rendering leaderboard with ${models.length} models');
    
    return OmniResult(value: true);
  }
}
