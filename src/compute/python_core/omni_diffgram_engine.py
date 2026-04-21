import uuid
import datetime
import json
from typing import Dict, Any, List, Optional

class OmniDiffgramEngine:
    """
    OMNI Framework Diffgram Engine
    Domain: Training Data Platform
    Role: Parsing, validating, and formatting complex annotation models (bounding boxes, polygons).
    
    Adheres to OMNI Zero-Mock and Monadic Error Handling Standards.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.engine_id = str(uuid.uuid4())
        self.is_active = True

    def diagnostics(self) -> Dict[str, Any]:
        """Returns the operational status of the Diffgram Engine."""
        return {
            "engine": "OmniDiffgramEngine",
            "status": "operational" if self.is_active else "inactive",
            "engine_id": self.engine_id,
            "version": "1.0.0",
            "domain": "Training Data Platform"
        }

    def validate_annotation(self, annotation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monadic validation of a single Diffgram-style annotation instance.
        """
        if not self.is_active:
            return {"status": "error", "message": "Engine is inactive"}
            
        try:
            anno_type = annotation.get("type")
            if not anno_type:
                return {"status": "error", "message": "Annotation missing 'type'"}
                
            if anno_type == "box":
                if "x_min" not in annotation or "y_min" not in annotation or "x_max" not in annotation or "y_max" not in annotation:
                    return {"status": "error", "message": "Box annotation missing required coordinates"}
                is_valid = True
                
            elif anno_type == "polygon":
                points = annotation.get("points")
                if not isinstance(points, list) or len(points) < 3:
                     return {"status": "error", "message": "Polygon annotation requires at least 3 points"}
                is_valid = True
            else:
                return {"status": "error", "message": f"Unsupported annotation type: {anno_type}"}
                
            return {
                "status": "success", 
                "is_valid": is_valid,
                "type": anno_type,
                "label": annotation.get("label", "unlabeled")
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Exception during annotation validation: {str(e)}"}

    def export_to_coco_format(self, annotations: List[Dict[str, Any]], image_id: int) -> Dict[str, Any]:
        """
        Monadic function to export a list of valid annotations to COCO format.
        """
        if not self.is_active:
            return {"status": "error", "message": "Engine is inactive"}
            
        try:
            coco_annotations = []
            for idx, anno in enumerate(annotations):
                val_result = self.validate_annotation(anno)
                if val_result.get("status") == "success" and val_result.get("is_valid"):
                    if anno.get("type") == "box":
                        width = anno["x_max"] - anno["x_min"]
                        height = anno["y_max"] - anno["y_min"]
                        coco_anno = {
                            "id": idx + 1,
                            "image_id": image_id,
                            "category_id": anno.get("category_id", 1),
                            "bbox": [anno["x_min"], anno["y_min"], width, height],
                            "area": width * height,
                            "iscrowd": 0
                        }
                        coco_annotations.append(coco_anno)
            
            return {
                "status": "success",
                "coco_format": coco_annotations,
                "processed": len(coco_annotations),
                "total": len(annotations)
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Export format failed: {str(e)}"}
