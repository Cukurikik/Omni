import SwiftUI
struct OmniResult<T, E: Error> { let isOk: Bool; let value: T?; let error: E? }
enum TTSError: Error { case tooLong }
struct MOSSTTSDPlayerView: View {
    @State private var isPlaying = false
    let maxDurationMin = 60
    var body: some View {
        VStack { Text("MOSS-TTSD Player").font(.title); Text(isPlaying ? "Playing..." : "Stopped") }
    }
    func startPlayback(durationMin: Int) -> OmniResult<Bool, TTSError> {
        if durationMin > maxDurationMin { return OmniResult(isOk: false, value: nil, error: .tooLong) }
        return OmniResult(isOk: true, value: true, error: nil)
    }
}
