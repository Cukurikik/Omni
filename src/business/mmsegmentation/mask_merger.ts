// OMNI MMSEGMENTATION: Semantic Mask Merger
// TypeScript logic to overlay and merge multiple probability masks into a single class map.
// Source: open-mmlab/mmsegmentation

export interface SemanticMask {
    classId: number;
    probabilities: Float32Array; // Flattened 2D array of [0.0 - 1.0]
    width: number;
    height: number;
}

export class MaskMerger {
    /**
     * Takes an array of masks (each representing a different class's probability at each pixel)
     * and returns a single array where each index contains the classId with the highest probability.
     */
    public static mergeArgmax(masks: SemanticMask[]): Int32Array {
        if (masks.length === 0) {
            throw new Error("No masks provided for merging.");
        }

        const width = masks[0].width;
        const height = masks[0].height;
        const totalPixels = width * height;

        // Validation
        for (const mask of masks) {
            if (mask.width !== width || mask.height !== height) {
                throw new Error("All masks must have the same dimensions.");
            }
            if (mask.probabilities.length !== totalPixels) {
                throw new Error("Probability array length mismatch.");
            }
        }

        const finalClassMap = new Int32Array(totalPixels);

        // For every pixel, find the class with the highest probability
        for (let i = 0; i < totalPixels; i++) {
            let maxProb = -1.0;
            let bestClass = -1;

            // Background class threshold (if all probs are very low)
            const BACKGROUND_THRESHOLD = 0.3;

            for (const mask of masks) {
                const p = mask.probabilities[i];
                if (p > maxProb) {
                    maxProb = p;
                    bestClass = mask.classId;
                }
            }

            if (maxProb < BACKGROUND_THRESHOLD) {
                finalClassMap[i] = 0; // Assuming 0 is background
            } else {
                finalClassMap[i] = bestClass;
            }
        }

        return finalClassMap;
    }
}
