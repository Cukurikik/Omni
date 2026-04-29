export interface SpeechPacket {
    audioData: Float32Array;
    sampleRate: number;
}

export class OmniMOSSSpeechAPI {
    /** OMNI Interface Layer: MOSS-Speech API */
    public static validatePacket(packet: SpeechPacket): boolean {
        return packet.audioData.length > 0 && packet.sampleRate > 8000;
    }

    public static getDurationMs(packet: SpeechPacket): number {
        return (packet.audioData.length / packet.sampleRate) * 1000;
    }
}
