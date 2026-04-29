// Omni API for VisionQA Multimodal
export interface VisionQAResponse {
    questionId: string;
    answerText: string;
    groundingBoxes: number[][]; // [x1, y1, x2, y2]
}

export class OmniVisionQAAPI {
    static constructOverlayPayload(response: VisionQAResponse, imgWidth: number, imgHeight: number): object {
        const normalizedBoxes = response.groundingBoxes.map(b => ({
            x: b[0] / imgWidth,
            y: b[1] / imgHeight,
            w: (b[2] - b[0]) / imgWidth,
            h: (b[3] - b[1]) / imgHeight
        }));
        
        return {
            text: response.answerText,
            highlights: normalizedBoxes
        };
    }
}
