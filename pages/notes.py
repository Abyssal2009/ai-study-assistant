"""
Study Assistant - Notes Page
Note storage and OCR import with image storage.
"""

import streamlit as st
import database as db
import os
from pathlib import Path
from datetime import datetime

# Image storage path
IMAGES_PATH = Path(__file__).parent.parent / "data" / "images" / "notes"


def save_uploaded_image(uploaded_file, note_id: int) -> dict:
    """Save an uploaded image to disk and return file info."""
    # Ensure directory exists
    IMAGES_PATH.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = Path(uploaded_file.name).suffix.lower()
    filename = f"note_{note_id}_{timestamp}{ext}"
    file_path = IMAGES_PATH / filename

    # Save the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Get image dimensions
    try:
        from PIL import Image
        img = Image.open(file_path)
        width, height = img.size
    except (IOError, OSError):
        width, height = None, None  # Could not read image dimensions

    return {
        'filename': filename,
        'original_filename': uploaded_file.name,
        'file_path': str(file_path),
        'file_size': file_path.stat().st_size,
        'width': width,
        'height': height
    }


def render():
    """Render the Notes page."""
    st.title("📝 Notes")

    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("Please add subjects first in the Subjects page.")
        st.stop()

    tab1, tab2, tab3, tab4 = st.tabs(["📚 All Notes", "➕ Add Note", "📷 Import (OCR)", "⭐ Favourites"])

    # TAB 1: All Notes
    with tab1:
        notes = db.get_all_notes()

        # Search
        search_query = st.text_input("🔍 Search notes...", placeholder="Search by title or content")

        if search_query:
            notes = db.search_notes(search_query)
            st.caption(f"Found {len(notes)} results")

        # Filter
        filter_subject = st.selectbox(
            "Filter by subject:",
            options=[None] + subjects,
            format_func=lambda x: "All Subjects" if x is None else x['name'],
            key="filter_notes"
        )

        if filter_subject and notes:
            notes = [n for n in notes if n['subject_id'] == filter_subject['id']]

        if notes:
            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("### Note List")
                for i, note in enumerate(notes):
                    fav_icon = "⭐" if note.get('is_favourite') else ""
                    if st.button(f"{fav_icon} {note['title'][:30]}...", key=f"select_{note['id']}"):
                        st.session_state.selected_note_id = note['id']

            with col2:
                if 'selected_note_id' in st.session_state:
                    note = db.get_note_by_id(st.session_state.selected_note_id)
                    if note:
                        st.markdown(f"### {note['title']}")
                        st.caption(f"{note['subject_name']} | {note.get('topic', 'No topic')}")
                        st.markdown("---")
                        st.markdown(note['content'])

                        # Display associated images if any
                        note_images = db.get_note_images(note['id'])
                        if note_images:
                            st.markdown("---")
                            st.markdown("#### 📷 Source Images")
                            img_cols = st.columns(min(len(note_images), 3))
                            for i, img in enumerate(note_images):
                                with img_cols[i % 3]:
                                    if os.path.exists(img['file_path']):
                                        st.image(img['file_path'], caption=img['original_filename'],
                                                use_container_width=True)
                                        st.caption(f"Size: {img['file_size'] // 1024}KB")
                                    else:
                                        st.warning(f"Image not found: {img['original_filename']}")

                        st.markdown("---")

                        action_col1, action_col2, action_col3 = st.columns(3)
                        with action_col1:
                            fav_text = "Remove ⭐" if note.get('is_favourite') else "Add ⭐"
                            if st.button(fav_text):
                                db.toggle_note_favourite(note['id'])
                                st.rerun()
                        with action_col2:
                            if st.button("✏️ Edit"):
                                st.session_state.editing_note = note
                        with action_col3:
                            if st.button("🗑️ Delete"):
                                # Delete associated images from disk
                                for img in note_images:
                                    try:
                                        if os.path.exists(img['file_path']):
                                            os.remove(img['file_path'])
                                    except OSError:
                                        pass  # File deletion failed, continue anyway
                                db.delete_note(note['id'])
                                del st.session_state.selected_note_id
                                st.rerun()
                else:
                    st.info("Select a note from the list to view it")
        else:
            st.info("No notes yet. Create some using the 'Add Note' tab!")

    # TAB 2: Add Note
    with tab2:
        st.markdown("### Add New Note")

        with st.form("add_note"):
            title = st.text_input("Title *", placeholder="e.g., Cell Biology - Key Terms")
            subject = st.selectbox(
                "Subject *",
                options=subjects,
                format_func=lambda x: x['name']
            )
            topic = st.text_input("Topic (optional)", placeholder="e.g., Mitosis")
            content = st.text_area("Content *", height=300, placeholder="Your notes here...")

            if st.form_submit_button("Save Note", type="primary"):
                if title and content:
                    db.add_note(
                        subject_id=subject['id'],
                        title=title,
                        content=content,
                        topic=topic
                    )
                    st.success(f"Note saved: {title}")
                    st.rerun()
                else:
                    st.error("Please fill in title and content")

    # TAB 3: OCR Import
    with tab3:
        st.markdown("### 📷 Import from Image (OCR)")
        st.markdown("Upload a photo of handwritten or printed notes to convert to text.")

        uploaded_file = st.file_uploader(
            "Upload an image",
            type=['png', 'jpg', 'jpeg'],
            help="Supported formats: PNG, JPG, JPEG"
        )

        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

            # Import OCR utilities
            try:
                import ocr_utils
                from PIL import Image

                # Assess image quality
                image = Image.open(uploaded_file)
                quality_score, quality_msg = ocr_utils.assess_image_quality(image)

                # Show quality indicator
                if quality_score >= 60:
                    st.success(f"Image Quality: {quality_msg}")
                elif quality_score >= 40:
                    st.warning(f"Image Quality: {quality_msg}")
                else:
                    st.error(f"Image Quality: {quality_msg}")

                # Show OpenCV status
                if not ocr_utils.is_opencv_available():
                    st.caption("Note: Install opencv-python for better preprocessing")

            except ImportError:
                quality_score = 50  # Default if utils not available

            if st.button("🔍 Extract Text", type="primary"):
                with st.spinner("Processing image..."):
                    try:
                        from PIL import Image
                        import ocr_utils

                        # Reset file pointer and open image
                        uploaded_file.seek(0)
                        image = Image.open(uploaded_file)

                        # Use improved OCR with preprocessing
                        text, confidence = ocr_utils.extract_text_with_confidence(image)

                        if text.strip():
                            st.success("Text extracted!")

                            # Show confidence indicator
                            if confidence >= 0.7:
                                st.caption(f"Confidence: High ({confidence:.0%})")
                            elif confidence >= 0.5:
                                st.caption(f"Confidence: Medium ({confidence:.0%}) - Review for errors")
                            else:
                                st.caption(f"Confidence: Low ({confidence:.0%}) - May contain errors")

                            st.session_state.ocr_text = text
                            st.session_state.ocr_uploaded_file = uploaded_file
                            st.text_area("Extracted Text:", value=text, height=200)
                        else:
                            st.warning("No text could be extracted. Try a clearer image with better lighting.")
                            st.info("Tips: Use good lighting, hold camera straight, ensure text is dark and readable.")
                    except Exception as e:
                        st.error(f"OCR Error: {str(e)}")
                        st.info("Make sure Tesseract OCR is installed.")

            if 'ocr_text' in st.session_state and st.session_state.ocr_text:
                st.markdown("---")
                st.markdown("### Save as Note")

                with st.form("save_ocr"):
                    ocr_title = st.text_input("Note Title *")
                    ocr_subject = st.selectbox(
                        "Subject *",
                        options=subjects,
                        format_func=lambda x: x['name'],
                        key="ocr_subject"
                    )
                    ocr_topic = st.text_input("Topic (optional)")
                    ocr_content = st.text_area("Content", value=st.session_state.ocr_text, height=200)
                    save_image = st.checkbox("Save original image", value=True,
                                            help="Store the source image alongside the extracted text")

                    if st.form_submit_button("Save Note"):
                        if ocr_title and ocr_content:
                            # Save the note
                            note_id = db.add_note(
                                subject_id=ocr_subject['id'],
                                title=ocr_title,
                                content=ocr_content,
                                topic=ocr_topic
                            )

                            # Save the image if requested and available
                            if save_image and 'ocr_uploaded_file' in st.session_state:
                                try:
                                    # Reset file pointer
                                    st.session_state.ocr_uploaded_file.seek(0)
                                    image_info = save_uploaded_image(
                                        st.session_state.ocr_uploaded_file,
                                        note_id
                                    )
                                    # Save image record to database
                                    image_id = db.add_note_image(
                                        note_id=note_id,
                                        filename=image_info['filename'],
                                        original_filename=image_info['original_filename'],
                                        file_path=image_info['file_path'],
                                        file_size=image_info['file_size'],
                                        width=image_info['width'],
                                        height=image_info['height'],
                                        extracted_text=ocr_content
                                    )
                                    # Index image for RAG search
                                    try:
                                        import rag
                                        rag.index_note_image(image_id)
                                    except Exception:
                                        pass  # RAG indexing optional
                                    st.success("Note and image saved!")
                                except Exception as e:
                                    st.warning(f"Note saved, but image storage failed: {e}")
                            else:
                                st.success("Note saved!")

                            # Clean up session state
                            if 'ocr_text' in st.session_state:
                                del st.session_state.ocr_text
                            if 'ocr_uploaded_file' in st.session_state:
                                del st.session_state.ocr_uploaded_file
                            st.rerun()

    # TAB 4: Favourites
    with tab4:
        favourites = db.get_favourite_notes()
        if favourites:
            st.markdown(f"### ⭐ Favourite Notes ({len(favourites)})")
            for note in favourites:
                with st.expander(f"⭐ {note['title']}"):
                    st.caption(f"{note['subject_name']} | {note.get('topic', 'No topic')}")
                    st.markdown(note['content'][:500] + "..." if len(note['content']) > 500 else note['content'])
                    if st.button("View Full", key=f"view_fav_{note['id']}"):
                        st.session_state.selected_note_id = note['id']
                        st.rerun()
        else:
            st.info("No favourite notes yet. Star some notes to see them here!")
