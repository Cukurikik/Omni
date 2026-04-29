import cv2
import numpy as np

def resize_and_normalize(image: np.ndarray, size: tuple) -> np.ndarray:
    resized = cv2.resize(image, size)
    normalized = resized.astype(np.float32) / 255.0
    return normalized
