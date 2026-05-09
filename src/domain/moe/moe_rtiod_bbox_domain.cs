// moe_rtiod_bbox_domain.cs — Domain Layer: RTIOD BBox Domain
// C# geometric validation logic for multi-modal Object Detection bounding boxes.

using System;

namespace Omni.Domain.MoE.RTIOD
{
    public struct BoundingBox
    {
        public float XMin;
        public float YMin;
        public float XMax;
        public float YMax;
        public float Confidence;

        public bool IsValid()
        {
            return XMax > XMin && YMax > YMin && Confidence >= 0.0f && Confidence <= 1.0f;
        }

        public float Area()
        {
            return (XMax - XMin) * (YMax - YMin);
        }
    }

    public class BBoxValidator
    {
        public bool ValidateIntersection(BoundingBox a, BoundingBox b, out float iou)
        {
            iou = 0f;
            if (!a.IsValid() || !b.IsValid()) return false;

            float intersectXMin = Math.Max(a.XMin, b.XMin);
            float intersectYMin = Math.Max(a.YMin, b.YMin);
            float intersectXMax = Math.Min(a.XMax, b.XMax);
            float intersectYMax = Math.Min(a.YMax, b.YMax);

            if (intersectXMax < intersectXMin || intersectYMax < intersectYMin)
                return true; // No intersection, but geometrically valid

            float intersectArea = (intersectXMax - intersectXMin) * (intersectYMax - intersectYMin);
            float unionArea = a.Area() + b.Area() - intersectArea;

            iou = intersectArea / unionArea;
            return true;
        }
    }
}
