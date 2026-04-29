// Omni Shot2Story Video Viewer (Dart)
class ShotCaption { final int shotId; final double start; final double end; final String caption;
  ShotCaption({required this.shotId, required this.start, required this.end, required this.caption}); }
class OmniShot2StoryWidget {
  static List<ShotCaption> parseShots(List<Map<String,dynamic>> shots) =>
    shots.asMap().entries.map((e) => ShotCaption(
      shotId: e.key, start: (e.value['start'] as num).toDouble(),
      end: (e.value['end'] as num).toDouble(), caption: e.value['text'] ?? ''
    )).toList();
  static String videoSummary(List<String> captions) => captions.take(20).join(' ');
}
