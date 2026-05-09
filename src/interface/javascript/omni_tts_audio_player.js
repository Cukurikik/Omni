// OMNI MOTHER: Audio playback wrapper for TTS

export class OmniAudioPlayer {
    static playBuffer(arrayBuffer) {
        if (!arrayBuffer) return;
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        audioCtx.decodeAudioData(arrayBuffer, (buffer) => {
            const source = audioCtx.createBufferSource();
            source.buffer = buffer;
            source.connect(audioCtx.destination);
            source.start(0);
        });
    }
}
