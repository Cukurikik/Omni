// OMNI MMDETECTION: Non-Maximum Suppression (NMS)
// TypeScript logic to filter overlapping bounding boxes predicting the same object.
// Source: open-mmlab/mmdetection

export interface BBox {
    id: string;
    classId: number;
    score: number;
    x1: number;
    y1: number;
    x2: number;
    y2: number;
}

export class NMSFilter {
    /**
     * Calculates the Intersection over Union of two boxes.
     */
    private static calculateIoU(boxA: BBox, boxB: BBox): number {
        const x1 = Math.max(boxA.x1, boxB.x1);
        const y1 = Math.max(boxA.y1, boxB.y1);
        const x2 = Math.min(boxA.x2, boxB.x2);
        const y2 = Math.min(boxA.y2, boxB.y2);

        const width = Math.max(0, x2 - x1);
        const height = Math.max(0, y2 - y1);
        const interArea = width * height;

        const areaA = (boxA.x2 - boxA.x1) * (boxA.y2 - boxA.y1);
        const areaB = (boxB.x2 - boxB.x1) * (boxB.y2 - boxB.y1);

        const unionArea = areaA + areaB - interArea;

        return unionArea <= 0 ? 0 : interArea / unionArea;
    }

    /**
     * Applies Non-Maximum Suppression to remove redundant, overlapping bounding boxes.
     * @param boxes Array of detected bounding boxes
     * @param iouThreshold Overlap threshold above which lower-scoring boxes are removed
     */
    public static apply(boxes: BBox[], iouThreshold: number = 0.5): BBox[] {
        if (boxes.length === 0) return [];

        // 1. Sort boxes by confidence score descending
        const sortedBoxes = [...boxes].sort((a, b) => b.score - a.score);
        const selectedBoxes: BBox[] = [];

        while (sortedBoxes.length > 0) {
            // 2. Pick the box with the highest score
            const currentBox = sortedBoxes.shift()!;
            selectedBoxes.push(currentBox);

            // 3. Remove all remaining boxes that have an IoU > threshold with the current box
            // Note: NMS is typically done per-class. We assume this input is already grouped by class,
            // or we add a class check here.
            for (let i = sortedBoxes.length - 1; i >= 0; i--) {
                if (currentBox.classId === sortedBoxes[i].classId) {
                    const iou = this.calculateIoU(currentBox, sortedBoxes[i]);
                    if (iou > iouThreshold) {
                        sortedBoxes.splice(i, 1);
                    }
                }
            }
        }

        return selectedBoxes;
    }
}
