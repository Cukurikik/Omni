export interface BBox { x1: number; y1: number; x2: number; y2: number; }

export class OmniAnyLabelingAPI {
    /** OMNI Interface: AnyLabeling Segmentation API */
    public static computeIoU(a: BBox, b: BBox): number {
        const ix1 = Math.max(a.x1, b.x1), iy1 = Math.max(a.y1, b.y1);
        const ix2 = Math.min(a.x2, b.x2), iy2 = Math.min(a.y2, b.y2);
        const iw = Math.max(0, ix2 - ix1), ih = Math.max(0, iy2 - iy1);
        const inter = iw * ih;
        const areaA = (a.x2 - a.x1) * (a.y2 - a.y1);
        const areaB = (b.x2 - b.x1) * (b.y2 - b.y1);
        const union = areaA + areaB - inter;
        return union > 0 ? inter / union : 0;
    }
}
