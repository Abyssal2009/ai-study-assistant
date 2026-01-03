"""
Study Assistant - OCR Utilities
Image quality assessment for OCR.
"""

import numpy as np
from PIL import Image
from typing import Tuple

# Try to import OpenCV
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def assess_image_quality(image: Image.Image) -> Tuple[int, str]:
    """
    Assess image quality for OCR.

    Args:
        image: PIL Image to assess

    Returns:
        Tuple of (score 0-100, user-friendly message)
    """
    if not CV2_AVAILABLE:
        return 50, "Quality check unavailable (OpenCV not installed)"

    try:
        # Convert PIL to OpenCV format
        rgb = np.array(image.convert('RGB'))
        cv_img = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

        # 1. Sharpness (Laplacian variance) - 0-40 points
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var > 500:
            sharpness_score = 40
        elif laplacian_var > 100:
            sharpness_score = 30
        elif laplacian_var > 50:
            sharpness_score = 20
        elif laplacian_var > 20:
            sharpness_score = 10
        else:
            sharpness_score = 0

        # 2. Contrast (standard deviation) - 0-30 points
        contrast = gray.std()
        if contrast > 60:
            contrast_score = 30
        elif contrast > 40:
            contrast_score = 20
        elif contrast > 25:
            contrast_score = 10
        else:
            contrast_score = 0

        # 3. Text presence (edge detection) - 0-30 points
        edges = cv2.Canny(gray, 100, 200)
        edge_ratio = np.count_nonzero(edges) / edges.size
        if edge_ratio > 0.05:
            text_score = 30
        elif edge_ratio > 0.02:
            text_score = 20
        elif edge_ratio > 0.01:
            text_score = 10
        else:
            text_score = 0

        total_score = sharpness_score + contrast_score + text_score

        # Generate message
        if total_score >= 80:
            message = "Excellent - Ready to extract text"
        elif total_score >= 60:
            message = "Good - Should work well"
        elif total_score >= 40:
            message = "Fair - Results may have some errors"
        elif total_score >= 20:
            message = "Poor - Please retake with better lighting"
        else:
            message = "Too low quality - Cannot process reliably"

        return total_score, message

    except Exception as e:
        return 50, f"Quality check error: {str(e)}"


def is_opencv_available() -> bool:
    """Check if OpenCV is available."""
    return CV2_AVAILABLE
