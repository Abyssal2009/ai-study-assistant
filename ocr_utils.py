"""
Study Assistant - OCR Utilities
Image quality assessment and preprocessing for improved OCR accuracy.
"""

import numpy as np
from PIL import Image, ImageFilter
from typing import Tuple

# Try to import OpenCV
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV format (BGR)."""
    rgb = np.array(pil_image.convert('RGB'))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
    """Convert OpenCV image (BGR or grayscale) to PIL Image."""
    if len(cv2_image.shape) == 2:
        # Grayscale
        return Image.fromarray(cv2_image)
    else:
        # BGR to RGB
        rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)


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
        cv_img = pil_to_cv2(image)
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


def preprocess_for_ocr(image: Image.Image) -> Image.Image:
    """
    Preprocess image to improve OCR accuracy.

    Pipeline:
    1. Convert to grayscale
    2. Denoise
    3. Enhance contrast (CLAHE)
    4. Adaptive thresholding
    5. Upscale if small

    Args:
        image: PIL Image to preprocess

    Returns:
        Preprocessed PIL Image
    """
    if not CV2_AVAILABLE:
        # Fallback to PIL-only preprocessing
        return _preprocess_pil_only(image)

    try:
        # Convert to OpenCV format
        cv_img = pil_to_cv2(image)

        # 1. Convert to grayscale
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

        # 2. Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)

        # 3. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # 4. Adaptive thresholding
        # Use Gaussian adaptive threshold for better handling of varying lighting
        thresh = cv2.adaptiveThreshold(
            enhanced, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,
            C=2
        )

        # 5. Upscale if image is small (Tesseract works better with larger images)
        height, width = thresh.shape
        if width < 1000 or height < 1000:
            scale = max(1000 / width, 1000 / height, 1.5)
            new_width = int(width * scale)
            new_height = int(height * scale)
            thresh = cv2.resize(thresh, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        return cv2_to_pil(thresh)

    except Exception as e:
        # Fallback to PIL-only preprocessing on error
        return _preprocess_pil_only(image)


def _preprocess_pil_only(image: Image.Image) -> Image.Image:
    """
    Fallback preprocessing using only PIL (when OpenCV unavailable).

    Args:
        image: PIL Image to preprocess

    Returns:
        Preprocessed PIL Image
    """
    # Convert to grayscale
    gray = image.convert('L')

    # Apply median filter to reduce noise
    denoised = gray.filter(ImageFilter.MedianFilter(size=3))

    # Enhance contrast
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Contrast(denoised)
    enhanced = enhancer.enhance(1.5)

    # Simple threshold (PIL doesn't have adaptive threshold)
    # Convert to black and white
    threshold = 128
    bw = enhanced.point(lambda x: 255 if x > threshold else 0, '1')

    # Convert back to grayscale for Tesseract
    result = bw.convert('L')

    # Upscale if small
    width, height = result.size
    if width < 1000 or height < 1000:
        scale = max(1000 / width, 1000 / height, 1.5)
        new_size = (int(width * scale), int(height * scale))
        result = result.resize(new_size, Image.LANCZOS)

    return result


def get_tesseract_config(for_handwriting: bool = True) -> str:
    """
    Get optimized Tesseract configuration string.

    Args:
        for_handwriting: If True, use settings optimized for handwriting

    Returns:
        Tesseract config string
    """
    if for_handwriting:
        # OEM 1: LSTM neural network (better for handwriting)
        # PSM 1: Auto with orientation detection
        return '--oem 1 --psm 1 -l eng'
    else:
        # OEM 3: Default (LSTM + legacy)
        # PSM 3: Fully automatic
        return '--oem 3 --psm 3 -l eng'


def extract_text_with_confidence(image: Image.Image) -> Tuple[str, float]:
    """
    Extract text from image and estimate confidence.

    Args:
        image: PIL Image to process

    Returns:
        Tuple of (extracted text, confidence 0-1)
    """
    import pytesseract
    import os

    # Find Tesseract on Windows
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

    # Preprocess image
    preprocessed = preprocess_for_ocr(image)

    # Get config
    config = get_tesseract_config(for_handwriting=True)

    # Extract text with detailed data
    try:
        data = pytesseract.image_to_data(preprocessed, config=config, output_type=pytesseract.Output.DICT)

        # Calculate average confidence
        confidences = [int(c) for c in data['conf'] if int(c) > 0]
        avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0

        # Extract text
        text = pytesseract.image_to_string(preprocessed, config=config)

        return text.strip(), avg_confidence

    except Exception as e:
        # Fallback to simple extraction
        text = pytesseract.image_to_string(preprocessed, config=config)
        return text.strip(), 0.5


def is_opencv_available() -> bool:
    """Check if OpenCV is available."""
    return CV2_AVAILABLE
