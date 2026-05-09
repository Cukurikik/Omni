export class DeepfakeVideoPlayer {
    private videoElement: HTMLVideoElement;

    constructor(elementId: string) {
        const el = document.getElementById(elementId) as HTMLVideoElement;
        if (!el) throw new Error("Video element not found");
        this.videoElement = el;
    }

    public highlightFakeSegments(timestamps: number[]): void {
        this.videoElement.ontimeupdate = () => {
            if (timestamps.includes(Math.floor(this.videoElement.currentTime))) {
                this.videoElement.style.border = "5px solid red";
            } else {
                this.videoElement.style.border = "none";
            }
        };
    }
}
