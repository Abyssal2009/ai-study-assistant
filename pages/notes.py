"""
Study Assistant - Notes Page
Note storage and OCR import.
"""

import streamlit as st
import database as db


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
                        st.markdown("---")

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            fav_text = "Remove ⭐" if note.get('is_favourite') else "Add ⭐"
                            if st.button(fav_text):
                                db.toggle_note_favourite(note['id'])
                                st.rerun()
                        with col2:
                            if st.button("✏️ Edit"):
                                st.session_state.editing_note = note
                        with col3:
                            if st.button("🗑️ Delete"):
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

            if st.button("🔍 Extract Text", type="primary"):
                with st.spinner("Processing image..."):
                    try:
                        from PIL import Image
                        import pytesseract

                        # Try to find Tesseract on Windows
                        import os
                        tesseract_paths = [
                            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                        ]
                        for path in tesseract_paths:
                            if os.path.exists(path):
                                pytesseract.pytesseract.tesseract_cmd = path
                                break

                        image = Image.open(uploaded_file)
                        text = pytesseract.image_to_string(image)

                        if text.strip():
                            st.success("Text extracted!")
                            st.session_state.ocr_text = text
                            st.text_area("Extracted Text:", value=text, height=200)
                        else:
                            st.warning("No text could be extracted. Try a clearer image.")
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

                    if st.form_submit_button("Save Note"):
                        if ocr_title and ocr_content:
                            db.add_note(
                                subject_id=ocr_subject['id'],
                                title=ocr_title,
                                content=ocr_content,
                                topic=ocr_topic
                            )
                            st.success("Note saved!")
                            del st.session_state.ocr_text
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
