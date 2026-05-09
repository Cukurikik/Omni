// OMNI Interface Layer: WebRTC Streamer
export class OmniWebRTC {
    private pc: RTCPeerConnection;
    
    constructor() {
        this.pc = new RTCPeerConnection();
    }
    
    public addStream(stream: MediaStream) {
        stream.getTracks().forEach(track => this.pc.addTrack(track, stream));
    }
}
