# -*- coding: utf-8 -*-
"""
OMNI Engine for OpenMMLab MMOCR.

Wraps the mmocr toolbox to provide end-to-end OCR pipelines including
text detection (DBNet, PANet, etc.), text recognition (CRNN, ABINet, etc.),
and key information extraction (SDMG-R). Inspired by the architecture at:
    https://github.com/open-mmlab/mmocr

@engine  OmniMMOCREngine
@domain  compute
@since   7.0.0 (Semester 7 — Batch 1)
"""
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class OmniMMOCREngine:
    """
    Production-grade OMNI wrapper for OpenMMLab MMOCR.

    Capabilities:
      - initialize_inferencer  : Set up the MMOCR inference pipeline.
      - detect_text           : Run text detection on an image.
      - recognize_text        : Run text recognition on an image.
      - run_end_to_end_ocr    : Full pipeline: detect + recognize + extract.
      - list_available_models : Enumerate supported model configurations.

    All methods return monadic Dict[str, Any] with 'status' field.
    """

    def __init__(self, model_dir: str = "/tmp/mmocr_models") -> None:
        """Initialize MMOCR engine with default configuration."""
        self.model_dir = model_dir
        self._inferencer = None
        self._det_model: Optional[str] = None
        self._rec_model: Optional[str] = None

    # ------------------------------------------------------------------
    # Core Methods
    # ------------------------------------------------------------------

    def initialize_inferencer(
        self,
        det_model: str = "DBNet",
        rec_model: str = "CRNN",
        device: str = "cpu",
    ) -> Dict[str, Any]:
        """
        Initializes the MMOCR TextDetInferencer and TextRecInferencer.

        @param det_model: Text detection model name (DBNet, PANet, PSENet, etc.).
        @param rec_model: Text recognition model name (CRNN, ABINet, ASTER, etc.).
        @param device: Compute device ('cpu' or 'cuda:0').
        @returns Dict with 'status' and loaded model names.
        """
        if not det_model or not rec_model:
            return {"status": "error", "message": "Both det_model and rec_model are required"}

        try:
            from mmocr.apis import TextDetInferencer, TextRecInferencer

            self._det_model = det_model
            self._rec_model = rec_model
            self._inferencer = {
                "det": TextDetInferencer(model=det_model, device=device),
                "rec": TextRecInferencer(model=rec_model, device=device),
            }
            return {
                "status": "success",
                "det_model": det_model,
                "rec_model": rec_model,
                "device": device,
            }
        except ImportError as e:
            return {"status": "error", "message": f"mmocr not installed: {e}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def detect_text(self, image_path: str) -> Dict[str, Any]:
        """
        Runs text detection on a single image.

        @param image_path: Absolute path to the input image.
        @returns Dict with 'status', detected bounding boxes, and scores.
        """
        if not image_path:
            return {"status": "error", "message": "image_path is required"}

        if not os.path.isfile(image_path):
            return {"status": "error", "message": f"Image not found: {image_path}"}

        if self._inferencer is None:
            return {"status": "error", "message": "Inferencer not initialized. Call initialize_inferencer first."}

        try:
            det = self._inferencer["det"]
            result = det(image_path, return_vis=False)

            predictions = result.get("predictions", [{}])
            det_polygons = predictions[0].get("det_polygons", []) if predictions else []
            det_scores = predictions[0].get("det_scores", []) if predictions else []

            return {
                "status": "success",
                "image": image_path,
                "num_detections": len(det_polygons),
                "polygons": det_polygons[:5],
                "scores": det_scores[:5],
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def recognize_text(self, image_path: str) -> Dict[str, Any]:
        """
        Runs text recognition on a cropped text-region image.

        @param image_path: Path to a cropped text region image.
        @returns Dict with 'status' and recognized text strings.
        """
        if not image_path:
            return {"status": "error", "message": "image_path is required"}

        if not os.path.isfile(image_path):
            return {"status": "error", "message": f"Image not found: {image_path}"}

        if self._inferencer is None:
            return {"status": "error", "message": "Inferencer not initialized. Call initialize_inferencer first."}

        try:
            rec = self._inferencer["rec"]
            result = rec(image_path, return_vis=False)

            predictions = result.get("predictions", [{}])
            rec_texts = predictions[0].get("rec_texts", []) if predictions else []
            rec_scores = predictions[0].get("rec_scores", []) if predictions else []

            return {
                "status": "success",
                "image": image_path,
                "texts": rec_texts,
                "scores": rec_scores,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def run_end_to_end_ocr(self, image_path: str) -> Dict[str, Any]:
        """
        Runs the full OCR pipeline: text detection → recognition → structured output.

        @param image_path: Path to the input image.
        @returns Dict with 'status', detected text blocks with bounding boxes and text.
        """
        if not image_path:
            return {"status": "error", "message": "image_path is required"}

        if not os.path.isfile(image_path):
            return {"status": "error", "message": f"Image not found: {image_path}"}

        if self._inferencer is None:
            return {"status": "error", "message": "Inferencer not initialized. Call initialize_inferencer first."}

        try:
            from mmocr.apis import MMOCRInferencer

            ocr = MMOCRInferencer(
                det=self._det_model,
                rec=self._rec_model,
                device="cpu",
            )
            result = ocr(image_path, return_vis=False)

            predictions = result.get("predictions", [{}])
            return {
                "status": "success",
                "image": image_path,
                "predictions": predictions[0] if predictions else {},
            }
        except ImportError:
            det_result = self.detect_text(image_path)
            if det_result["status"] != "success":
                return det_result
            return {
                "status": "success",
                "image": image_path,
                "detections": det_result.get("num_detections", 0),
                "note": "Recognition skipped — MMOCRInferencer unavailable",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_available_models(self) -> Dict[str, Any]:
        """
        Lists supported text detection and recognition model names.

        @returns Dict with 'status' and model lists.
        """
        return {
            "status": "success",
            "text_detection": [
                "DBNet", "DBNet++", "PANet", "PSENet",
                "TextSnake", "DRRG", "FCENet", "MaskRCNN",
            ],
            "text_recognition": [
                "CRNN", "ABINet", "ASTER", "MASTER",
                "NRTR", "SAR", "SATRN", "SVTR", "RobustScanner",
            ],
            "key_information_extraction": ["SDMG-R"],
        }

    # ------------------------------------------------------------------
    # Registry Interface
    # ------------------------------------------------------------------

    def diagnostics(self) -> Dict[str, Any]:
        """Returns engine health status for the OmniEngineRegistry."""
        return {
            "engine": "OmniMMOCREngine",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": [
                "initialize_inferencer",
                "detect_text",
                "recognize_text",
                "run_end_to_end_ocr",
                "list_available_models",
            ],
            "model_dir": self.model_dir,
            "inferencer_active": self._inferencer is not None,
        }
