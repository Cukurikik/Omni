// OMNI OpenCV Canny Edge Engine — Compute Layer (Python)
// Absorbing opencv/opencv image processing fundamentals
// Deterministic geometry gradient mapping without mocks

import math
from typing import List, Dict, Any, Tuple

class OpenCVError(Exception):
    pass

class OmniOpencvCannyEdge:
    def __init__(self, low_threshold: int, high_threshold: int):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.images_processed = 0

    def compute_sobel_gradients(self, img_2d: List[List[int]]) -> tuple:
        rows = len(img_2d)
        cols = len(img_2d[0])
        
        G = [[0.0] * cols for _ in range(rows)]
        theta = [[0.0] * cols for _ in range(rows)]

        # Sobel kernels
        Kx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        Ky = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]

        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                gx = 0.0
                gy = 0.0
                for u in range(-1, 2):
                    for v in range(-1, 2):
                        gx += img_2d[i + u][j + v] * Kx[u + 1][v + 1]
                        gy += img_2d[i + u][j + v] * Ky[u + 1][v + 1]

                G[i][j] = math.sqrt(gx*gx + gy*gy)
                theta[i][j] = math.atan2(gy, gx)

        return G, theta

    def non_max_suppression(self, G: List[List[float]], theta: List[List[float]]) -> List[List[float]]:
        rows = len(G)
        cols = len(G[0])
        Z = [[0.0] * cols for _ in range(rows)]
        
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                angle = theta[i][j] * 180.0 / math.pi
                if angle < 0:
                    angle += 180

                q = 255.0
                r = 255.0

                # Angle 0
                if (0 <= angle < 22.5) or (157.5 <= angle <= 180):
                    q = G[i][j+1]
                    r = G[i][j-1]
                # Angle 45
                elif (22.5 <= angle < 67.5):
                    q = G[i+1][j-1]
                    r = G[i-1][j+1]
                # Angle 90
                elif (67.5 <= angle < 112.5):
                    q = G[i+1][j]
                    r = G[i-1][j]
                # Angle 135
                elif (112.5 <= angle < 157.5):
                    q = G[i-1][j-1]
                    r = G[i+1][j+1]

                if (G[i][j] >= q) and (G[i][j] >= r):
                    Z[i][j] = G[i][j]
                else:
                    Z[i][j] = 0.0
                    
        return Z

    def hysteresis_thresholding(self, img: List[List[float]]) -> List[List[int]]:
        rows = len(img)
        cols = len(img[0])
        res = [[0] * cols for _ in range(rows)]
        
        strong = 255
        weak = 25 # Changed from 75 to keep values simple uint8 representation
        
        for i in range(rows):
            for j in range(cols):
                if img[i][j] >= self.high_threshold:
                    res[i][j] = strong
                elif (img[i][j] <= self.high_threshold) and (img[i][j] >= self.low_threshold):
                    res[i][j] = weak
                else:
                    res[i][j] = 0
                    
        # Hysteresis connect logic
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                if res[i][j] == weak:
                    # Check 8 surrounding pixels for strong edge
                    if (res[i+1][j-1] == strong or res[i+1][j] == strong or res[i+1][j+1] == strong
                        or res[i][j-1] == strong or res[i][j+1] == strong
                        or res[i-1][j-1] == strong or res[i-1][j] == strong or res[i-1][j+1] == strong):
                        res[i][j] = strong
                    else:
                        res[i][j] = 0
        return res

    def apply_canny_edge_detection(self, image_matrix: List[List[int]]) -> Tuple[bool, List[List[int]], str]:
        """
        Executes zero-mock Canny Edge detection process:
        1. Sobel Gradients
        2. Non-Maximum Suppression
        3. Double thresholding (Hysteresis)
        """
        try:
            if not image_matrix or not image_matrix[0]:
                raise OpenCVError("Empty image matrix.")

            self.images_processed += 1

            # Sequence execution bounded mathematically
            G, theta = self.compute_sobel_gradients(image_matrix)
            Z = self.non_max_suppression(G, theta)
            edges = self.hysteresis_thresholding(Z)

            return True, edges, ""

        except OpenCVError as e:
            return False, [], str(e)
        except Exception as e:
            return False, [], f"System panic: {e}"

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniOpencvCannyEdge",
            "evaluations_run": self.images_processed,
            "status": "Operational"
        }
