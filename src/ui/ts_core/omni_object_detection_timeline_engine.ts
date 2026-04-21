// ===========================================================================
// OMNI OBJECT DETECTION TIMELINE ENGINE (SEMESTER 5 — BATCH 17)
// ===========================================================================
// Absorbed From  : hoya012/deep_learning_object_detection
// Logic Inherited: Interface Layer (Object Detection Architecture History)
// ===========================================================================
//
// KNOWLEDGE ABSORBED:
//   deep_learning_object_detection catalogs the evolution of detection:
//     Two-stage: R-CNN → Fast R-CNN → Faster R-CNN → Cascade R-CNN
//     One-stage: YOLO → SSD → RetinaNet → FCOS
//     Anchor-free: CornerNet, CenterNet, FCOS
//     Transformer: DETR, Deformable DETR
//

export type DetectorFamily = "two_stage" | "one_stage" | "anchor_free" | "transformer";

export interface DetectorEntry {
    name: string;
    year: number;
    family: DetectorFamily;
    paper: string;
    cocoAP: number;        // COCO benchmark mAP
    fps: number;           // Frames per second (approximate)
    innovation: string;
    backbone: string;
}

const DETECTION_TIMELINE: DetectorEntry[] = [
    // Two-stage detectors
    { name: "R-CNN", year: 2014, family: "two_stage", paper: "Girshick et al.", cocoAP: 31.4, fps: 0.05, innovation: "Region proposals + CNN features + SVM classifier", backbone: "AlexNet" },
    { name: "Fast R-CNN", year: 2015, family: "two_stage", paper: "Girshick", cocoAP: 35.9, fps: 0.5, innovation: "RoI pooling: single CNN forward pass for all proposals", backbone: "VGG-16" },
    { name: "Faster R-CNN", year: 2015, family: "two_stage", paper: "Ren et al.", cocoAP: 42.1, fps: 5, innovation: "Region Proposal Network (RPN): end-to-end trainable", backbone: "ResNet-101" },
    { name: "FPN", year: 2017, family: "two_stage", paper: "Lin et al.", cocoAP: 44.3, fps: 6, innovation: "Feature Pyramid Network: multi-scale feature maps", backbone: "ResNet-101" },
    { name: "Cascade R-CNN", year: 2018, family: "two_stage", paper: "Cai & Vasconcelos", cocoAP: 46.3, fps: 4, innovation: "Multi-stage detection with increasing IoU thresholds", backbone: "ResNet-101" },

    // One-stage detectors
    { name: "YOLOv1", year: 2016, family: "one_stage", paper: "Redmon et al.", cocoAP: 23.0, fps: 45, innovation: "Single-shot: divide image into grid, predict boxes+classes", backbone: "Darknet" },
    { name: "SSD", year: 2016, family: "one_stage", paper: "Liu et al.", cocoAP: 31.2, fps: 46, innovation: "Multi-scale feature maps with default boxes at each level", backbone: "VGG-16" },
    { name: "YOLOv3", year: 2018, family: "one_stage", paper: "Redmon & Farhadi", cocoAP: 33.0, fps: 30, innovation: "Multi-scale predictions (3 scales), Darknet-53 backbone", backbone: "Darknet-53" },
    { name: "RetinaNet", year: 2017, family: "one_stage", paper: "Lin et al.", cocoAP: 40.8, fps: 5, innovation: "Focal Loss: solves class imbalance (easy vs hard examples)", backbone: "ResNet-101-FPN" },
    { name: "YOLOv8", year: 2023, family: "one_stage", paper: "Ultralytics", cocoAP: 53.9, fps: 100, innovation: "Anchor-free head + decoupled detect + C2f module", backbone: "CSPDarknet" },

    // Anchor-free
    { name: "CornerNet", year: 2018, family: "anchor_free", paper: "Law & Deng", cocoAP: 40.5, fps: 4, innovation: "Detect objects as corner pairs (top-left + bottom-right)", backbone: "Hourglass" },
    { name: "CenterNet", year: 2019, family: "anchor_free", paper: "Zhou et al.", cocoAP: 42.1, fps: 22, innovation: "Object = single center point + regression for size", backbone: "DLA-34" },
    { name: "FCOS", year: 2019, family: "anchor_free", paper: "Tian et al.", cocoAP: 44.7, fps: 12, innovation: "Per-pixel prediction: no anchors, fully convolutional", backbone: "ResNet-101-FPN" },

    // Transformer-based
    { name: "DETR", year: 2020, family: "transformer", paper: "Carion et al.", cocoAP: 43.3, fps: 3, innovation: "Set prediction: bipartite matching loss, no NMS needed", backbone: "ResNet-50 + Transformer" },
    { name: "Deformable DETR", year: 2021, family: "transformer", paper: "Zhu et al.", cocoAP: 46.2, fps: 5, innovation: "Deformable attention: attend to sparse set of key points", backbone: "ResNet-50 + DeformAttn" },
    { name: "DINO", year: 2022, family: "transformer", paper: "Zhang et al.", cocoAP: 63.3, fps: 4, innovation: "Contrastive denoising + mixed query selection + look-ahead", backbone: "Swin-L + Transformer" },
];


export class OmniObjectDetectionTimelineEngine {
    private timeline: DetectorEntry[];

    constructor() {
        this.timeline = [...DETECTION_TIMELINE];
    }

    public getByFamily(family: DetectorFamily): { success: boolean; value: DetectorEntry[] } {
        return { success: true, value: this.timeline.filter((d) => d.family === family) };
    }

    public getTimeline(): { success: boolean; value: DetectorEntry[] } {
        return { success: true, value: [...this.timeline].sort((a, b) => a.year - b.year) };
    }

    public compareAccuracyVsSpeed(): { success: boolean; value: Array<{ name: string; ap: number; fps: number; family: string }> } {
        return {
            success: true,
            value: this.timeline.map((d) => ({ name: d.name, ap: d.cocoAP, fps: d.fps, family: d.family }))
        };
    }

    public getBest(metric: "accuracy" | "speed"): { success: boolean; value: DetectorEntry } {
        const sorted = [...this.timeline].sort((a, b) =>
            metric === "accuracy" ? b.cocoAP - a.cocoAP : b.fps - a.fps
        );
        return { success: true, value: sorted[0] };
    }

    public getStats(): Record<string, any> {
        const byFamily: Record<string, number> = {};
        for (const d of this.timeline) byFamily[d.family] = (byFamily[d.family] || 0) + 1;
        return { totalDetectors: this.timeline.length, byFamily, yearRange: "2014-2023" };
    }

    public evaluateHealth(): Record<string, any> {
        return {
            engine: "OmniObjectDetectionTimelineEngine", layer: "Interface", status: "healthy",
            detectors: this.timeline.length,
            families: [...new Set(this.timeline.map((d) => d.family))],
            learned_from: "hoya012/deep_learning_object_detection",
        };
    }
}
