"""
Google Vision API OCR Integration.
Provides high-accuracy text extraction from images using Google Cloud Vision.
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        creds_path = os.getenv('GOOGLE_VISION_CREDENTIALS_PATH')
        if creds_path:
            # Convert to absolute path
            if not os.path.isabs(creds_path):
                creds_path = os.path.abspath(creds_path)

            return os.path.exists(creds_path)
        return False
    except Exception:
        return False


def setup_vision_client():
    """Initialize Google Vision API client using environment variables."""
    if not VISION_AVAILABLE:
        st.error("Google Cloud Vision library not installed. Run: pip install google-cloud-vision")
        return None

    try:
        # Get credentials path from environment
        credentials_path = os.getenv('GOOGLE_VISION_CREDENTIALS_PATH')
        if not credentials_path:
            st.error("Google Vision not configured. Set GOOGLE_VISION_CREDENTIALS_PATH in .env")
            return None

        # Convert to absolute path if needed
        if not os.path.isabs(credentials_path):
            credentials_path = os.path.abspath(credentials_path)

        # Verify file exists
        if not os.path.exists(credentials_path):
            st.error(f"Credentials file not found at: {credentials_path}")
            return None

        # Set environment variable for Google Cloud
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

        # Create and return the client
        client = vision.ImageAnnotatorClient()
        return client

    except Exception as e:
        st.error(f"Failed to initialize Vision API: {str(e)}")
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
    Extract text with word-level confidence scores and language detection.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Tuple of (full_text, words_list, average_confidence, detected_language)
        words_list contains dicts with 'text' and 'confidence' keys
    """
    client = setup_vision_client()
    if not client:
        return None, [], 0, None

    try:
        image = vision.Image(content=image_bytes)
        response = client.document_text_detection(image=image)

        if response.error.message:
            raise Exception(f'Vision API error: {response.error.message}')

        # Get full text
        full_text = ""
        detected_language = None

        if response.full_text_annotation:
            full_text = response.full_text_annotation.text

            # Extract detected language from first page
            if response.full_text_annotation.pages:
                page = response.full_text_annotation.pages[0]
                if hasattr(page, 'property') and page.property:
                    if hasattr(page.property, 'detected_languages') and page.property.detected_languages:
                        # Get the most confident language
                        langs = page.property.detected_languages
                        if langs:
                            # Sort by confidence and get top language
                            top_lang = max(langs, key=lambda x: x.confidence if hasattr(x, 'confidence') else 0)
                            detected_language = top_lang.language_code if hasattr(top_lang, 'language_code') else None

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

        return full_text, words, avg_confidence, detected_language

    except Exception as e:
        st.error(f"OCR extraction failed: {e}")
        return None, [], 0, None


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


def display_confidence_result(text: str, words: list, avg_confidence: float, detected_language: str = None, key_suffix: str = "") -> str:
    """
    Display OCR result with confidence information and metrics.

    Args:
        text: Full extracted text
        words: Word-level confidence data
        avg_confidence: Average confidence score
        detected_language: Detected language code
        key_suffix: Unique suffix for widget keys (required for batch processing)

    Returns:
        The (potentially edited) extracted text
    """
    # Show 3 metrics in columns
    col1, col2, col3 = st.columns(3)

    confidence_pct = avg_confidence * 100
    word_count = len(words)

    # Language code to name mapping
    lang_names = {
        'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
        'it': 'Italian', 'pt': 'Portuguese', 'nl': 'Dutch', 'ru': 'Russian',
        'zh': 'Chinese', 'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic',
        'hi': 'Hindi', 'th': 'Thai', 'vi': 'Vietnamese', 'pl': 'Polish',
        'uk': 'Ukrainian', 'cs': 'Czech', 'sv': 'Swedish', 'da': 'Danish',
        'fi': 'Finnish', 'no': 'Norwegian', 'el': 'Greek', 'he': 'Hebrew',
        'tr': 'Turkish', 'id': 'Indonesian', 'ms': 'Malay', 'ro': 'Romanian',
        'hu': 'Hungarian', 'bg': 'Bulgarian', 'hr': 'Croatian', 'sk': 'Slovak',
        'sl': 'Slovenian', 'sr': 'Serbian', 'lt': 'Lithuanian', 'lv': 'Latvian',
        'et': 'Estonian', 'fa': 'Persian', 'bn': 'Bengali', 'ta': 'Tamil',
        'te': 'Telugu', 'mr': 'Marathi', 'gu': 'Gujarati', 'kn': 'Kannada',
        'ml': 'Malayalam', 'pa': 'Punjabi', 'ur': 'Urdu', 'af': 'Afrikaans'
    }
    lang_display = lang_names.get(detected_language, detected_language) if detected_language else 'Unknown'

    with col1:
        if confidence_pct >= 90:
            st.metric("Confidence", f"{confidence_pct:.0f}%", delta="High", delta_color="normal")
        elif confidence_pct >= 70:
            st.metric("Confidence", f"{confidence_pct:.0f}%", delta="Medium", delta_color="off")
        else:
            st.metric("Confidence", f"{confidence_pct:.0f}%", delta="Low", delta_color="inverse")

    with col2:
        st.metric("Word Count", f"{word_count:,}")

    with col3:
        st.metric("Language", lang_display)

    # Show low-confidence words if any
    low_conf_words = get_low_confidence_words(words)
    if low_conf_words:
        with st.expander(f"⚠️ {len(low_conf_words)} words with low confidence (<70%)"):
            for w in low_conf_words[:20]:  # Show first 20
                conf_pct = w['confidence'] * 100
                if conf_pct < 50:
                    st.markdown(f"🔴 `{w['text']}` - {conf_pct:.0f}%")
                else:
                    st.markdown(f"🟡 `{w['text']}` - {conf_pct:.0f}%")
            if len(low_conf_words) > 20:
                st.caption(f"... and {len(low_conf_words) - 20} more")

    # Show the extracted text (editable)
    text_key = f"ocr_text_{key_suffix}" if key_suffix else "ocr_extracted_text"
    edited_text = st.text_area("Extracted Text (editable)", text, height=300, key=text_key)

    return edited_text


def show_ocr_info_banner():
    """Display info banner about the OCR engine."""
    st.info("""
**OCR Engine: Google Cloud Vision API**

**Features:**
- High accuracy text recognition
- Handwriting support
- Word-level confidence scores
- Multi-language detection

**Pricing:** 1,000 free requests/month, then $1.50 per 1,000
    """)


def show_api_cost_warning():
    """Display Vision API pricing information."""
    st.caption("💰 Vision API: Free for first 1,000 requests/month, then $1.50 per 1,000")


def show_quality_tips():
    """Display quality tips for better OCR results."""
    with st.expander("📋 Tips for best OCR results"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
**Good practices:**
- Good, even lighting
- Steady camera / scanner
- Capture straight-on (not angled)
- High contrast (dark text, light background)
- High resolution image
            """)
        with col2:
            st.markdown("""
**Avoid:**
- Blurry images
- Angled captures
- Poor or uneven lighting
- Shadows on text
- Low resolution
- Crumpled or folded paper
            """)


def preprocess_image(image_bytes: bytes, enhance_contrast: float = 1.5, enhance_sharpness: float = 1.3) -> bytes:
    """
    Preprocess image to improve OCR quality.

    Args:
        image_bytes: Raw image bytes
        enhance_contrast: Contrast enhancement factor (1.0 = no change)
        enhance_sharpness: Sharpness enhancement factor (1.0 = no change)

    Returns:
        Processed image bytes
    """
    from PIL import Image, ImageEnhance
    import io

    # Load image
    img = Image.open(io.BytesIO(image_bytes))

    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Enhance contrast
    if enhance_contrast != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(enhance_contrast)

    # Enhance sharpness
    if enhance_sharpness != 1.0:
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(enhance_sharpness)

    # Save to bytes
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=95)
    output.seek(0)

    return output.read()


def get_usage_this_month() -> int:
    """Get the OCR usage count for the current month."""
    from datetime import datetime

    current_month = datetime.now().strftime("%Y-%m")

    if 'ocr_usage' not in st.session_state:
        st.session_state.ocr_usage = {}

    return st.session_state.ocr_usage.get(current_month, 0)


def increment_usage():
    """Increment the OCR usage counter for the current month."""
    from datetime import datetime

    current_month = datetime.now().strftime("%Y-%m")

    if 'ocr_usage' not in st.session_state:
        st.session_state.ocr_usage = {}

    current = st.session_state.ocr_usage.get(current_month, 0)
    st.session_state.ocr_usage[current_month] = current + 1


def show_usage_tracker():
    """Display OCR usage tracker."""
    usage = get_usage_this_month()

    if usage > 900:
        st.warning(f"⚠️ OCR usage this month: {usage}/1,000 - Approaching free tier limit!")
    elif usage > 0:
        st.caption(f"📊 OCR usage this month: {usage}/1,000")
    else:
        st.caption("📊 OCR usage this month: 0/1,000")
