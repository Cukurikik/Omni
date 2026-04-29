class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class BBoxGeometry:
    def __init__(self):
        pass

    def compute_intersection_over_union(self, box_a: list, box_b: list) -> OmniResult:
        if len(box_a) != 4 or len(box_b) != 4:
            return OmniResult(error="Bounding boxes must be [x1, y1, x2, y2]")

        # Deterministic simulation of Document Layout Analysis IoU calculation
        # Used to group text blocks in complex PDF RAG ingestion
        try:
            x_left = max(box_a[0], box_b[0])
            y_top = max(box_a[1], box_b[1])
            x_right = min(box_a[2], box_b[2])
            y_bottom = min(box_a[3], box_b[3])

            if x_right < x_left or y_bottom < y_top:
                return OmniResult(value=0.0)

            intersection_area = (x_right - x_left) * (y_bottom - y_top)
            
            box_a_area = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
            box_b_area = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
            
            iou = intersection_area / float(box_a_area + box_b_area - intersection_area)
            return OmniResult(value=iou)
        except Exception as e:
            return OmniResult(error=str(e))
