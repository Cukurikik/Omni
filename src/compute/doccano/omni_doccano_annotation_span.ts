// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Doccano Annotation Span (OMNI Zero-Mock Implementation)
// Implements mathematical disjoint interval overlap checking.

export type Result<T> = 
  | { value: T; isOk: true; error: null }
  | { value: null; isOk: false; error: string };

export type AnnotationSpan = {
    start: number;
    end: number;
    label: string;
};

export class DoccanoSpanValidator {
   public validateSpans(spans: AnnotationSpan[]): Result<boolean> {
       if (!spans || spans.length === 0) {
            return { value: true, isOk: true, error: null }; // Void is valid
       }
       
       for (const span of spans) {
           if (span.start >= span.end || span.start < 0) {
               return { value: null, isOk: false, error: "Invalid span parameters: start must be < end." };
           }
       }
       
       // Sort spans mathematically by start parameter
       const sorted = [...spans].sort((a, b) => a.start - b.start);
       
       // Detect Overlaps
       for (let i = 0; i < sorted.length - 1; i++) {
           const current = sorted[i];
           const next = sorted[i + 1];
           
           if (current.end > next.start) {
               return { value: null, isOk: false, error: `Overlap detected between offsets ${current.start}-${current.end} and ${next.start}-${next.end}.` };
           }
       }
       
       return { value: true, isOk: true, error: null };
   }
}
