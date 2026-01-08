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
                        # Check if we're editing this note
                        if st.session_state.get('editing_note') and st.session_state.editing_note['id'] == note['id']:
                            st.markdown("### ✏️ Edit Note")

                            # Find current subject index for selectbox
                            current_subject_idx = 0
                            for i, s in enumerate(subjects):
                                if s['id'] == note['subject_id']:
                                    current_subject_idx = i
                                    break

                            with st.form("edit_note_form"):
                                edit_title = st.text_input("Title *", value=note['title'])
                                edit_subject = st.selectbox(
                                    "Subject *",
                                    options=subjects,
                                    index=current_subject_idx,
                                    format_func=lambda x: x['name']
                                )
                                edit_topic = st.text_input("Topic (optional)", value=note.get('topic', '') or '')
                                edit_content = st.text_area("Content *", value=note['content'], height=300)

                                col_save, col_cancel = st.columns(2)
                                with col_save:
                                    save_clicked = st.form_submit_button("💾 Save Changes", type="primary")
                                with col_cancel:
                                    cancel_clicked = st.form_submit_button("Cancel")

                                if save_clicked:
                                    if edit_title and edit_content:
                                        db.update_note(
                                            note_id=note['id'],
                                            title=edit_title,
                                            content=edit_content,
                                            topic=edit_topic if edit_topic else None,
                                            subject_id=edit_subject['id']
                                        )
                                        del st.session_state.editing_note
                                        st.success("Note updated!")
                                        st.rerun()
                                    else:
                                        st.error("Title and content are required.")

                                if cancel_clicked:
                                    del st.session_state.editing_note
                                    st.rerun()
                        else:
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
                                    st.rerun()
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

        # Check Vision API availability
        try:
            import vision_ocr
            vision_available = vision_ocr.is_vision_available()
        except ImportError:
            vision_available = False

        if not vision_available:
            st.error("Google Vision API is not configured. Please set up credentials.")
            st.stop()

        # Info banner about the OCR engine
        vision_ocr.show_ocr_info_banner()

        # Usage tracker
        vision_ocr.show_usage_tracker()

        # Quality tips
        vision_ocr.show_quality_tips()

        st.markdown("---")

        # Image preprocessing option
        auto_enhance = st.checkbox(
            "Auto-enhance image quality",
            value=False,
            help="Enhance contrast (1.5x) and sharpness (1.3x) before OCR for better results"
        )

        # Batch file upload
        uploaded_files = st.file_uploader(
            "Upload images",
            type=['png', 'jpg', 'jpeg'],
            help="Supported formats: PNG, JPG, JPEG. Select multiple files for batch processing.",
            accept_multiple_files=True
        )

        if uploaded_files:
            # Initialize batch results storage
            if 'ocr_batch_results' not in st.session_state:
                st.session_state.ocr_batch_results = []

            # Show uploaded images
            st.markdown(f"**{len(uploaded_files)} image(s) uploaded**")

            # Extract All button for batch
            if st.button("🔍 Extract Text from All", type="primary"):
                st.session_state.ocr_batch_results = []

                progress_bar = st.progress(0)
                for i, uploaded_file in enumerate(uploaded_files):
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        try:
                            uploaded_file.seek(0)
                            image_bytes = uploaded_file.read()

                            # Apply preprocessing if enabled
                            if auto_enhance:
                                image_bytes = vision_ocr.preprocess_image(image_bytes)

                            text, words, avg_confidence, detected_language = vision_ocr.extract_text_with_confidence(image_bytes)

                            # Increment usage tracker
                            vision_ocr.increment_usage()

                            st.session_state.ocr_batch_results.append({
                                'filename': uploaded_file.name,
                                'text': text if text else "",
                                'words': words,
                                'confidence': avg_confidence,
                                'language': detected_language,
                                'uploaded_file': uploaded_file
                            })
                        except Exception as e:
                            st.session_state.ocr_batch_results.append({
                                'filename': uploaded_file.name,
                                'text': "",
                                'words': [],
                                'confidence': 0,
                                'language': None,
                                'error': str(e)
                            })

                    progress_bar.progress((i + 1) / len(uploaded_files))

                st.success(f"Processed {len(uploaded_files)} image(s)!")
                st.rerun()

            # Display batch results
            if st.session_state.get('ocr_batch_results'):
                st.markdown("---")
                st.markdown("### Extraction Results")

                all_texts = []

                for i, result in enumerate(st.session_state.ocr_batch_results):
                    with st.expander(f"📄 {result['filename']}", expanded=(len(st.session_state.ocr_batch_results) == 1)):
                        if result.get('error'):
                            st.error(f"Error: {result['error']}")
                        elif result['text']:
                            # Display metrics and editable text
                            edited_text = vision_ocr.display_confidence_result(
                                result['text'],
                                result['words'],
                                result['confidence'],
                                result['language'],
                                key_suffix=f"batch_{i}"
                            )
                            # Update result with edited text
                            result['text'] = edited_text
                            all_texts.append(edited_text)

                            st.markdown("---")

                            # Save options for this image
                            st.markdown("**Save Options:**")
                            save_cols = st.columns(3)

                            with save_cols[0]:
                                if st.button("💾 Save as Note", key=f"save_note_{i}"):
                                    st.session_state.ocr_text = result['text']
                                    st.session_state.ocr_uploaded_file = result.get('uploaded_file')
                                    st.session_state.save_single_ocr = True
                                    st.rerun()

                            with save_cols[1]:
                                if st.button("🃏 Convert to Flashcards", key=f"flashcards_{i}"):
                                    st.session_state.ocr_for_flashcards = result['text']
                                    st.session_state.flashcard_source_file = result['filename']
                                    st.rerun()

                            with save_cols[2]:
                                st.download_button(
                                    "📥 Download TXT",
                                    data=result['text'],
                                    file_name=f"{Path(result['filename']).stem}_extracted.txt",
                                    mime="text/plain",
                                    key=f"download_{i}"
                                )
                        else:
                            st.warning("No text could be extracted from this image.")

                # Combined download for batch
                if len(all_texts) > 1:
                    st.markdown("---")
                    separator = "\n\n" + "="*50 + "\n\n"
                    combined_text = separator.join([
                        f"--- {result['filename']} ---\n{result['text']}"
                        for result in st.session_state.ocr_batch_results
                        if result['text']
                    ])
                    st.download_button(
                        "📥 Download All Combined",
                        data=combined_text,
                        file_name="all_extracted_text.txt",
                        mime="text/plain",
                        type="primary"
                    )

            # Convert to Flashcards section
            if 'ocr_for_flashcards' in st.session_state and st.session_state.ocr_for_flashcards:
                st.markdown("---")
                st.markdown("### 🃏 Convert to Flashcards")
                st.caption(f"Source: {st.session_state.get('flashcard_source_file', 'Unknown')}")

                api_key = st.session_state.get('bubble_ace_api_key', '')
                if not api_key:
                    st.warning("Please set your Claude API key in Settings or Bubble Ace to generate flashcards.")
                else:
                    if st.button("Generate Flashcards", type="primary"):
                        with st.spinner("AI is creating flashcards..."):
                            try:
                                import utils

                                flashcard_prompt = f"""Create study flashcards from these notes. Extract key concepts, definitions, and important facts.

Notes:
{st.session_state.ocr_for_flashcards}

Return flashcards in this exact format (one per line):
Q: [question]
A: [answer]

Q: [question]
A: [answer]

Create 5-10 high-quality flashcards focusing on the most important concepts."""

                                response = utils.call_claude(api_key, flashcard_prompt, model="sonnet")

                                if response and not response.startswith("Error:"):
                                    st.session_state.generated_flashcards = response
                                    st.success("Flashcards generated!")
                                else:
                                    st.error(f"Generation failed: {response}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

                    if 'generated_flashcards' in st.session_state:
                        st.text_area("Generated Flashcards", st.session_state.generated_flashcards, height=300)

                        # Parse and save flashcards
                        if st.button("Save Flashcards to Database"):
                            try:
                                # Parse Q: A: format
                                lines = st.session_state.generated_flashcards.split('\n')
                                current_q = None
                                saved_count = 0

                                for line in lines:
                                    line = line.strip()
                                    if line.startswith('Q:'):
                                        current_q = line[2:].strip()
                                    elif line.startswith('A:') and current_q:
                                        answer = line[2:].strip()
                                        # Save to database
                                        db.add_flashcard(
                                            subject_id=subjects[0]['id'],  # Default to first subject
                                            question=current_q,
                                            answer=answer
                                        )
                                        saved_count += 1
                                        current_q = None

                                if saved_count > 0:
                                    st.success(f"Saved {saved_count} flashcards!")
                                    del st.session_state.generated_flashcards
                                    del st.session_state.ocr_for_flashcards
                                else:
                                    st.warning("No flashcards found to save.")
                            except Exception as e:
                                st.error(f"Failed to save: {e}")

                    if st.button("Cancel", key="cancel_flashcards"):
                        del st.session_state.ocr_for_flashcards
                        if 'generated_flashcards' in st.session_state:
                            del st.session_state.generated_flashcards
                        st.rerun()

            # Single note save form (triggered from batch results)
            if st.session_state.get('save_single_ocr') and 'ocr_text' in st.session_state:
                st.markdown("---")
                st.markdown("### Save as Note")

                # AI Enhancement Section
                st.markdown("#### Enhance with AI (optional)")
                st.caption("Let AI recognize the subject and create clear, structured study notes.")

                api_key = st.session_state.get('bubble_ace_api_key', '')
                if not api_key:
                    st.warning("Please set your Claude API key in Settings or Bubble Ace to use AI enhancement.")

                if st.button("✨ Enhance Notes with AI", type="secondary", disabled=not api_key):
                    with st.spinner("AI is enhancing your notes..."):
                        try:
                            import utils

                            enhance_prompt = f"""You are an expert study note creator. A student has scanned handwritten/printed notes using OCR.

TASK:
1. Identify the subject and specific topic
2. Fix any OCR errors or garbled text
3. Reorganize into clear, structured study notes:
   - Add clear headings
   - Use bullet points for lists
   - Highlight key terms with **bold**
   - Remove redundancy
   - Add brief clarifications where helpful
4. Make the notes optimized for learning and revision

Original scanned text:
{st.session_state.ocr_text}

Respond in this exact format:
**Subject:** [detected subject, e.g., Biology, Maths, History]
**Topic:** [specific topic covered]

---

[Your enhanced, well-structured notes here]"""

                            response = utils.call_claude(api_key, enhance_prompt, model="sonnet")

                            if response and not response.startswith("Error:"):
                                st.session_state.ocr_enhanced = response
                                st.session_state.use_enhanced = True

                                # Try to extract subject and topic from response
                                lines = response.split('\n')
                                for line in lines:
                                    if line.startswith('**Subject:**'):
                                        st.session_state.detected_subject = line.replace('**Subject:**', '').strip()
                                    elif line.startswith('**Topic:**'):
                                        st.session_state.detected_topic = line.replace('**Topic:**', '').strip()

                                st.success("Notes enhanced!")
                                st.rerun()
                            else:
                                st.error(f"Enhancement failed: {response}")
                        except Exception as e:
                            error_msg = str(e)
                            if "authentication_error" in error_msg or "invalid" in error_msg.lower() and "api" in error_msg.lower():
                                st.error("Invalid API key. Please check your Claude API key.")
                            else:
                                st.error(f"Enhancement error: {error_msg}")

                # Show comparison if enhanced version exists
                if 'ocr_enhanced' in st.session_state and st.session_state.ocr_enhanced:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Original (OCR)**")
                        st.text_area("", value=st.session_state.ocr_text, height=250, key="orig_preview", disabled=True)
                    with col2:
                        st.markdown("**Enhanced (AI)**")
                        st.markdown(st.session_state.ocr_enhanced[:1500] + "..." if len(st.session_state.ocr_enhanced) > 1500 else st.session_state.ocr_enhanced)

                    use_enhanced = st.checkbox("Use AI-enhanced version", value=st.session_state.get('use_enhanced', True))
                    st.session_state.use_enhanced = use_enhanced

                # Determine which content to use
                if st.session_state.get('use_enhanced') and 'ocr_enhanced' in st.session_state:
                    enhanced = st.session_state.ocr_enhanced
                    if '---' in enhanced:
                        content_to_save = enhanced.split('---', 1)[1].strip()
                    else:
                        content_to_save = enhanced
                    default_topic = st.session_state.get('detected_topic', '')
                else:
                    content_to_save = st.session_state.ocr_text
                    default_topic = ''

                with st.form("save_ocr"):
                    ocr_title = st.text_input("Note Title *")
                    ocr_subject = st.selectbox(
                        "Subject *",
                        options=subjects,
                        format_func=lambda x: x['name'],
                        key="ocr_subject"
                    )
                    ocr_topic = st.text_input("Topic (optional)", value=default_topic)
                    ocr_content = st.text_area("Content", value=content_to_save, height=200)
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
                            for key in ['ocr_text', 'ocr_uploaded_file', 'ocr_enhanced', 'use_enhanced',
                                       'detected_subject', 'detected_topic', 'save_single_ocr', 'ocr_batch_results']:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.rerun()

                # Cancel button
                if st.button("Cancel", key="cancel_save"):
                    for key in ['ocr_text', 'ocr_uploaded_file', 'ocr_enhanced', 'use_enhanced',
                               'detected_subject', 'detected_topic', 'save_single_ocr']:
                        if key in st.session_state:
                            del st.session_state[key]
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
