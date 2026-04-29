export interface Slide {
    slideId: string;
    title: string;
    content: string;
}

export class OmniOdinSlidesAPI {
    /** OMNI Interface Layer: Odin Slides API */
    public static formatSlides(slides: Slide[]): string {
        if (slides.length === 0) {
            throw new Error("Slide array cannot be empty.");
        }
        return slides.map(s => `[${s.slideId}] ${s.title}\n${s.content}`).join('\n\n');
    }

    public static exportToJSON(slides: Slide[]): string {
        return JSON.stringify({ version: "1.0", data: slides });
    }
}
