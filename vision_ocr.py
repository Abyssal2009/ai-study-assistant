"""
Google Vision API OCR Integration.
Provides high-accuracy text extraction from images using Google Cloud Vision.
"""

import streamlit as st
import os
from pathlib import Path

# Track if Vision API is available
VISION_AVAILABLE = False

try:
    from google.cloud import vision
    VISION_AVAILABLE = True
except ImportError:
    vision = None


def is_vision_available() -> bool:
    """Check if Google Vision API is available and configured."""
    if not VISION_AVAILABLE:
        return False

    # Check if credentials are configured
    try:
        if 'google_vision' in st.secrets:
            creds_path = st.secrets['google_vision']['credentials_path']
            return Path(creds_path).exists()
    except Exception:
        pass

    # Check environment variable
    return 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ


def setup_vision_client():
    """Initialize Google Vision API client using secrets.toml."""
    if not VISION_AVAILABLE:
        st.error("Google Cloud Vision library not installed. Run: pip install google-cloud-vision")
        return None

    try:
        # Set credentials from secrets if available
        if 'google_vision' in st.secrets:
            credentials_path = st.secrets['google_vision']['credentials_path']
            if Path(credentials_path).exists():
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            else:
                st.error(f"Credentials file not found: {credentials_path}")
                return None

        client = vision.ImageAnnotatorClient()
        return client
    except Exception as e:
        st.error(f"Failed to initialize Vision API: {e}")
        return None


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from image file using Vision API.

    Args:
        image_path: Path to the image file

    Returns:
        Extracted text string
    """
    client = setup_vision_client()
    if not client:
        return None

    try:
        with open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)

        if response.error.message:
            raise Exception(f'Vision API error: {response.error.message}')

        texts = response.text_annotations
        if texts:
            return texts[0].description
        return ""

    except Exception as e:
        st.error(f"OCR extraction failed: {e}")
        return None


def extract_text_from_bytes(image_bytes: bytes) -> str:
    """
    Extract text from uploaded file bytes.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Extracted text string
    """
    client = setup_vision_client()
    if not client:
        return None

    try:
        image = vision.Image(content=image_bytes)
        response = client.text_detection(image=image)

        if response.error.message:
            raise Exception(f'Vision API error: {response.error.message}')

        texts = response.text_annotations
        if texts:
            return texts[0].description
        return ""

    except Exception as e:
        st.error(f"OCR extraction failed: {e}")
        return None


def extract_text_with_confidence(image_bytes: bytes) -> tuple:
    """
    Extract text with word-level confidence scores.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Tuple of (full_text, words_list, average_confidence)
        words_list contains dicts with 'text' and 'confidence' keys
    """
    client = setup_vision_client()
    if not client:
        return None, [], 0

    try:
        image = vision.Image(content=image_bytes)
        response = client.document_text_detection(image=image)

        if response.error.message:
            raise Exception(f'Vision API error: {response.error.message}')

        # Get full text
        full_text = ""
        if response.full_text_annotation:
            full_text = response.full_text_annotation.text

        # Get word-level confidence
        words = []
        if response.full_text_annotation:
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            word_text = ''.join([symbol.text for symbol in word.symbols])
                            confidence = word.confidence if hasattr(word, 'confidence') else 1.0
                            words.append({
                                'text': word_text,
                                'confidence': confidence
                            })

        # Calculate average confidence
        avg_confidence = sum(w['confidence'] for w in words) / len(words) if words else 0

        return full_text, words, avg_confidence

    except Exception as e:
        st.error(f"OCR extraction failed: {e}")
        return None, [], 0


def get_low_confidence_words(words: list, threshold: float = 0.7) -> list:
    """
    Get words with confidence below threshold.

    Args:
        words: List of word dicts with 'text' and 'confidence'
        threshold: Confidence threshold (0-1)

    Returns:
        List of low-confidence word dicts
    """
    return [w for w in words if w['confidence'] < threshold]


def display_confidence_result(text: str, words: list, avg_confidence: float):
    """
    Display OCR result with confidence information.

    Args:
        text: Full extracted text
        words: Word-level confidence data
        avg_confidence: Average confidence score
    """
    # Show confidence score
    confidence_pct = avg_confidence * 100

    if confidence_pct >= 90:
        st.success(f"✓ Extracted with {confidence_pct:.0f}% confidence")
    elif confidence_pct >= 80:
        st.info(f"✓ Extracted with {confidence_pct:.0f}% confidence")
    else:
        st.warning(f"⚠️ Low confidence ({confidence_pct:.0f}%) - please review extracted text")

    # Show low-confidence words if any
    low_conf_words = get_low_confidence_words(words)
    if low_conf_words:
        with st.expander(f"⚠️ {len(low_conf_words)} words with low confidence"):
            for w in low_conf_words[:20]:  # Show first 20
                st.caption(f"'{w['text']}' - {w['confidence']*100:.0f}%")
            if len(low_conf_words) > 20:
                st.caption(f"... and {len(low_conf_words) - 20} more")

    # Show the extracted text
    st.text_area("Extracted Text", text, height=300)


def show_api_cost_warning():
    """Display Vision API pricing information."""
    st.caption("💰 Vision API: Free for first 1,000 requests/month, then $1.50 per 1,000")
