export class TransformerSRLTextAnnotator {
    public annotate(textId: string, labels: string[]): void {
        console.log(`Annotating ${textId} with ${labels.length} labels`);
    }
}
