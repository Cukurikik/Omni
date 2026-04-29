#include <math.h>

// OMNI MMDETECTION: Intersection over Union (IoU)
// C implementation for high-speed bounding box overlap calculations.
// Source: open-mmlab/mmdetection

typedef enum {
    IOU_SUCCESS = 0,
    IOU_ERR_INVALID_BOX = 1,
    IOU_ERR_NULL_PTR = 2
} iou_err_t;

typedef struct {
    float x1; // Left
    float y1; // Top
    float x2; // Right
    float y2; // Bottom
} BBox;

// Computes the area of a bounding box
float bbox_area(const BBox* box) {
    if (!box) return 0.0f;
    float width = box->x2 - box->x1;
    float height = box->y2 - box->y1;
    if (width <= 0 || height <= 0) return 0.0f;
    return width * height;
}

#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define MIN(a, b) ((a) < (b) ? (a) : (b))

// Calculates the IoU (Intersection over Union) of two bounding boxes
iou_err_t calculate_iou(const BBox* box_a, const BBox* box_b, float* out_iou) {
    if (!box_a || !box_b || !out_iou) {
        return IOU_ERR_NULL_PTR;
    }

    // Validate boxes
    if (box_a->x2 <= box_a->x1 || box_a->y2 <= box_a->y1 ||
        box_b->x2 <= box_b->x1 || box_b->y2 <= box_b->y1) {
        *out_iou = 0.0f;
        return IOU_ERR_INVALID_BOX;
    }

    // Coordinates of intersection rectangle
    float inter_x1 = MAX(box_a->x1, box_b->x1);
    float inter_y1 = MAX(box_a->y1, box_b->y1);
    float inter_x2 = MIN(box_a->x2, box_b->x2);
    float inter_y2 = MIN(box_a->y2, box_b->y2);

    float inter_width = inter_x2 - inter_x1;
    float inter_height = inter_y2 - inter_y1;

    // If no intersection
    if (inter_width <= 0 || inter_height <= 0) {
        *out_iou = 0.0f;
        return IOU_SUCCESS;
    }

    float inter_area = inter_width * inter_height;
    float area_a = bbox_area(box_a);
    float area_b = bbox_area(box_b);

    float union_area = area_a + area_b - inter_area;

    if (union_area <= 0) {
        *out_iou = 0.0f;
        return IOU_SUCCESS;
    }

    *out_iou = inter_area / union_area;
    return IOU_SUCCESS;
}
