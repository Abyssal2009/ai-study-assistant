"""
Study Assistant - Settings Page
Application settings and configuration.
"""

import streamlit as st
import database as db


def render():
    """Render the Settings page."""
    st.title("⚙️ Settings")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔑 API Keys", "📧 Email Reminders", "🃏 SRS Settings", "🗄️ Data", "☁️ Backup & Sync", "🔍 Search"
    ])

    # TAB 1: API Keys
    with tab1:
        st.markdown("### Claude API Key")
        st.markdown("""
        The AI features (Bubble Ace, AI Tools) require a Claude API key from Anthropic.

        **How to get a key:**
        1. Go to [console.anthropic.com](https://console.anthropic.com)
        2. Create an account or sign in
        3. Generate an API key
        4. Paste it below
        """)

        if 'bubble_ace_api_key' not in st.session_state:
            st.session_state.bubble_ace_api_key = ""

        api_key = st.text_input(
            "API Key",
            value=st.session_state.bubble_ace_api_key,
            type="password",
            placeholder="sk-ant-..."
        )

        if api_key != st.session_state.bubble_ace_api_key:
            st.session_state.bubble_ace_api_key = api_key
            st.success("API key saved for this session!")

        st.info("Note: API keys are only stored for the current session and are not saved to disk.")

    # TAB 2: Email Reminders
    with tab2:
        st.markdown("### Email Reminder Settings")
        st.markdown("""
        Get daily email reminders about your homework, exams, and flashcards.

        **Setup requires:**
        1. A Gmail account (or other email provider)
        2. An app password (not your regular password)

        See the `email_reminder.py` file for configuration.
        """)

        st.warning("Email reminders require manual setup. Check the documentation for details.")

        # Show current config status
        try:
            import config
            if hasattr(config, 'EMAIL_ADDRESS') and config.EMAIL_ADDRESS:
                st.success(f"Email configured: {config.EMAIL_ADDRESS}")
            else:
                st.info("Email not configured yet.")
        except ImportError:
            st.info("Config file not found. Copy config.example.py to config.py")

    # TAB 3: SRS Settings
    with tab3:
        st.markdown("### Spaced Repetition Settings")
        st.markdown("Configure how the SRS (Spaced Repetition System) works for your flashcards and topics.")

        st.markdown("#### Notification Settings")

        # Get current settings
        streak_setting = db.get_notification_setting('srs_include_streak', 'true')
        overdue_setting = db.get_notification_setting('srs_highlight_overdue', 'true')

        include_streak = st.checkbox(
            "Include streak status in email reminders",
            value=streak_setting[0] == 'true' if streak_setting[0] else True,
            help="Show your current review streak in daily email reminders"
        )

        highlight_overdue = st.checkbox(
            "Highlight overdue cards in notifications",
            value=overdue_setting[0] == 'true' if overdue_setting[0] else True,
            help="Show warnings when you have overdue flashcards"
        )

        if st.button("Save SRS Settings", key="save_srs_settings"):
            db.set_notification_setting('srs_include_streak', str(include_streak).lower(), include_streak)
            db.set_notification_setting('srs_highlight_overdue', str(highlight_overdue).lower(), highlight_overdue)
            st.success("SRS settings saved!")

        st.markdown("---")
        st.markdown("#### Topic Sync")
        st.markdown("Sync topics from flashcards to enable topic-level spaced repetition tracking.")

        if st.button("Sync Topics from Flashcards"):
            count = db.sync_topics_from_flashcards()
            if count > 0:
                st.success(f"Synced {count} new topics for review tracking!")
            else:
                st.info("All flashcard topics are already synced.")

        # Show topic stats
        topics_due = db.get_topics_due_count()
        st.metric("Topics Due for Review", topics_due)

        st.markdown("---")
        st.markdown("#### SRS Statistics")

        streak = db.get_review_streak()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Streak", f"{streak['current_streak']} days")
        with col2:
            st.metric("Longest Streak", f"{streak['longest_streak']} days")

    # TAB 4: Data Management
    with tab4:
        st.markdown("### Data Management")

        # Database stats
        st.markdown("#### Database Statistics")

        col1, col2 = st.columns(2)

        with col1:
            subjects = db.get_all_subjects()
            st.metric("Subjects", len(subjects))

            all_homework = db.get_all_homework(include_completed=True)
            st.metric("Homework Items", len(all_homework) if all_homework else 0)

            notes_count = db.get_notes_count()
            st.metric("Notes", notes_count)

        with col2:
            fc_stats = db.get_flashcard_stats()
            st.metric("Flashcards", fc_stats['total'])

            paper_count = db.get_paper_count()
            st.metric("Past Papers", paper_count)

            exams = db.get_all_exams()
            st.metric("Exams", len(exams) if exams else 0)

        st.markdown("---")
        st.markdown("#### Danger Zone")

        st.warning("These actions cannot be undone!")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑️ Clear Completed Homework"):
                if st.session_state.get('confirm_clear_hw'):
                    db.clear_completed_homework()
                    st.session_state.confirm_clear_hw = False
                    st.success("Cleared completed homework!")
                    st.rerun()
                else:
                    st.session_state.confirm_clear_hw = True
                    st.warning("Click again to confirm")

        with col2:
            if st.button("🗑️ Clear All Flashcard Reviews"):
                if st.session_state.get('confirm_clear_reviews'):
                    db.reset_flashcard_reviews()
                    st.session_state.confirm_clear_reviews = False
                    st.success("Reset all flashcard reviews!")
                    st.rerun()
                else:
                    st.session_state.confirm_clear_reviews = True
                    st.warning("Click again to confirm")

        st.markdown("---")
        st.markdown("#### About")
        st.markdown("""
        **Study Assistant v1.9**

        A personal study tool built for GCSE students.

        Features:
        - Homework tracking
        - Exam calendar
        - Flashcards with spaced repetition (SM-2)
        - Focus timer
        - Notes with OCR import + image storage
        - Past paper analysis
        - AI study tools powered by Claude
        - Semantic search (RAG)
        - Cloud backup (OneDrive / Google Drive)

        Built with Streamlit + Python + SQLite
        """)

    # TAB 5: Backup & Sync
    with tab5:
        st.markdown("### Backup & Sync")

        import backup
        from cloud import CloudService, get_available_services

        # Cloud service selection
        st.markdown("#### Cloud Service")

        if 'cloud_service' not in st.session_state:
            st.session_state.cloud_service = CloudService.NONE.value

        services = get_available_services()
        selected_service = st.selectbox(
            "Select cloud backup service:",
            options=[s['id'] for s in services],
            format_func=lambda x: next((s['name'] for s in services if s['id'] == x), x),
            key="cloud_service_select"
        )

        if selected_service != st.session_state.cloud_service:
            st.session_state.cloud_service = selected_service

        # Cloud connection status and auth
        if selected_service == CloudService.GOOGLE_DRIVE.value:
            st.markdown("---")
            st.markdown("#### Google Drive Connection")
            _render_google_drive_section()

        # Google Calendar section
        st.markdown("---")
        st.markdown("#### Google Calendar Sync")
        _render_google_calendar_section()

        # Local backup section
        st.markdown("---")
        st.markdown("#### Local Backups")

        col1, col2 = st.columns(2)
        with col1:
            backup_name = st.text_input("Backup name (optional):", placeholder="my_backup")
        with col2:
            st.write("")  # Spacer
            st.write("")
            if st.button("📦 Create Backup Now", type="primary"):
                with st.spinner("Creating backup..."):
                    success, msg, path = backup.create_backup(backup_name if backup_name else None)
                    if success:
                        st.success(msg)
                        # Upload to cloud if connected
                        if selected_service != CloudService.NONE.value and path:
                            _upload_to_cloud(selected_service, path)
                    else:
                        st.error(msg)

        # List local backups
        local_backups = backup.list_local_backups()
        if local_backups:
            st.markdown("##### Available Local Backups")
            for bkp in local_backups[:5]:  # Show last 5
                with st.expander(f"📁 {bkp['filename']} ({bkp['size_mb']:.2f} MB)"):
                    st.caption(f"Created: {bkp.get('created_at', 'Unknown')}")
                    if bkp.get('counts'):
                        counts = bkp['counts']
                        st.caption(
                            f"Contains: {counts.get('notes', 0)} notes, "
                            f"{counts.get('flashcards', 0)} flashcards, "
                            f"{counts.get('note_images', 0)} images"
                        )

                    bcol1, bcol2, bcol3 = st.columns(3)
                    with bcol1:
                        if st.button("🔄 Restore", key=f"restore_{bkp['filename']}"):
                            st.session_state.pending_restore = bkp['path']
                    with bcol2:
                        if st.button("☁️ Upload", key=f"upload_{bkp['filename']}"):
                            if selected_service != CloudService.NONE.value:
                                _upload_to_cloud(selected_service, bkp['path'])
                            else:
                                st.warning("Select a cloud service first")
                    with bcol3:
                        if st.button("🗑️ Delete", key=f"delete_{bkp['filename']}"):
                            success, msg = backup.delete_backup(bkp['path'])
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

            # Cleanup old backups
            if len(local_backups) > 5:
                if st.button("🧹 Cleanup Old Backups (keep 5)"):
                    deleted, msg = backup.cleanup_old_backups(5)
                    st.info(msg)
                    st.rerun()
        else:
            st.info("No local backups yet. Create one using the button above.")

        # Restore confirmation
        if 'pending_restore' in st.session_state:
            st.markdown("---")
            st.warning("⚠️ Restore will replace all current data. A safety backup will be created first.")
            rcol1, rcol2 = st.columns(2)
            with rcol1:
                if st.button("✅ Confirm Restore", type="primary"):
                    with st.spinner("Restoring backup..."):
                        success, msg = backup.restore_backup(st.session_state.pending_restore)
                        if success:
                            st.success(msg)
                            del st.session_state.pending_restore
                            st.rerun()
                        else:
                            st.error(msg)
            with rcol2:
                if st.button("❌ Cancel"):
                    del st.session_state.pending_restore
                    st.rerun()

    # TAB 6: Search (RAG Status)
    with tab6:
        st.markdown("### Search & Indexing")

        try:
            import rag
            stats = rag.get_index_stats()

            st.markdown("#### Semantic Search Status")

            semantic = stats.get('semantic_status', {})
            if semantic.get('available'):
                st.success("✅ Semantic search is available")
                st.caption(f"Model: {semantic.get('model_name', 'Unknown')}")
                st.caption(f"Model loaded: {'Yes' if semantic.get('model_loaded') else 'Not yet'}")
            else:
                st.warning("⚠️ Semantic search unavailable (keyword search only)")
                if semantic.get('error'):
                    st.caption(f"Error: {semantic['error']}")
                st.info("Install sentence-transformers for semantic search: `pip install sentence-transformers`")

            st.markdown("#### Index Statistics")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Indexed Documents", stats.get('total_documents', 0))
                st.metric("Notes", stats.get('notes_count', 0))
            with col2:
                st.metric("Flashcards", stats.get('flashcards_count', 0))
                st.metric("Note Images", stats.get('note_images_count', 0))

            st.markdown("---")

            if st.button("🔄 Rebuild Search Index", type="primary"):
                with st.spinner("Rebuilding index... This may take a moment."):
                    rag.index_all_content()
                    st.success("Search index rebuilt!")
                    st.rerun()

        except ImportError:
            st.error("RAG module not available")
        except Exception as e:
            st.error(f"Error loading search status: {e}")


def _render_google_drive_section():
    """Render Google Drive connection UI."""
    from cloud.google_drive import get_client

    client = get_client()

    if client.is_authenticated():
        success, msg, user_info = client.get_user_info()
        if success and user_info:
            st.success(f"✅ Connected as {user_info.get('name', 'Unknown')} ({user_info.get('email', '')})")

        if st.button("Disconnect Google Drive"):
            client.disconnect()
            st.rerun()

        # List cloud backups
        success, msg, cloud_backups = client.list_backups()
        if success and cloud_backups:
            st.markdown("##### Cloud Backups")
            for cb in cloud_backups[:5]:
                st.caption(f"☁️ {cb['name']} ({cb['size_mb']:.2f} MB)")

        # Google Calendar status
        st.markdown("---")
        st.markdown("##### Google Calendar Sync")
        try:
            from cloud.google_calendar import get_client as get_calendar_client
            cal_client = get_calendar_client()
            if cal_client.is_authenticated():
                st.success("📅 Calendar sync enabled")
                st.caption("Exams will sync to 'Study Assistant Exams' calendar")
            else:
                st.info("📅 Calendar sync available - reconnect to enable")
                st.caption("Calendar scope may need re-authorization")
        except Exception as e:
            st.caption(f"Calendar status: {e}")
    else:
        st.info("Not connected to Google Drive")

        if not client.has_credentials_file():
            st.warning("""
            **Google credentials file not found.**

            To set up Google Drive & Calendar:
            1. Go to [Google Cloud Console](https://console.cloud.google.com)
            2. Create a project and enable **Drive API** and **Calendar API**
            3. Create OAuth 2.0 credentials (Desktop app)
            4. Download the credentials JSON file
            5. Save it as `google_credentials.json` in the app folder
            """)
        else:
            if st.button("🔗 Connect Google Drive"):
                success, msg, _ = client.start_auth_flow()
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


def _upload_to_cloud(service: str, local_path: str):
    """Upload a backup to Google Drive."""
    from cloud import CloudService
    from cloud.google_drive import get_client

    if service != CloudService.GOOGLE_DRIVE.value:
        return

    with st.spinner("Uploading to Google Drive..."):
        client = get_client()
        if client.is_authenticated():
            success, msg = client.upload_backup(local_path)
            if success:
                st.success(f"☁️ {msg}")
            else:
                st.error(msg)
        else:
            st.warning("Connect to Google Drive first")


def _render_google_calendar_section():
    """Render Google Calendar sync UI."""
    import google_calendar as gcal

    # Check if credentials are configured
    if not gcal.is_configured():
        st.warning("""
        **Google Calendar not configured.**

        To enable exam sync to Google Calendar:
        1. Go to [Google Cloud Console](https://console.cloud.google.com)
        2. Create a project and enable **Google Calendar API**
        3. Create OAuth 2.0 credentials (Web application)
        4. Set redirect URI to `http://localhost:8501`
        5. Add credentials to `.streamlit/secrets.toml`:

        ```toml
        [google_calendar]
        client_id = "YOUR_CLIENT_ID"
        client_secret = "YOUR_CLIENT_SECRET"
        ```
        """)
        return

    # Check connection status
    is_connected = db.is_calendar_connected()

    if is_connected:
        tokens = db.get_calendar_tokens()
        st.success("📅 Google Calendar connected")

        if tokens and tokens.get('last_sync'):
            st.caption(f"Last sync: {tokens['last_sync']}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Sync All Exams", type="primary"):
                with st.spinner("Syncing exams to Google Calendar..."):
                    success, fail = gcal.sync_all_exams()
                    if success > 0:
                        st.success(f"Synced {success} exams to Google Calendar!")
                    if fail > 0:
                        st.warning(f"{fail} exams failed to sync")
                    if success == 0 and fail == 0:
                        st.info("All exams already synced!")

        with col2:
            if st.button("🔌 Disconnect Calendar"):
                gcal.disconnect_calendar()
                st.success("Disconnected from Google Calendar")
                st.rerun()

        # Show sync stats
        exams_without_cal = db.get_exams_without_calendar_id()
        all_exams = db.get_all_exams()

        synced = len(all_exams) - len(exams_without_cal) if all_exams else 0
        total = len(all_exams) if all_exams else 0

        st.caption(f"Synced: {synced}/{total} exams")

    else:
        st.info("Connect to Google Calendar to sync your exam dates automatically.")

        auth_url = gcal.get_calendar_auth_url()
        if auth_url:
            st.markdown(f"[🔗 Connect Google Calendar]({auth_url})")
            st.caption("After authorization, you'll be redirected back here.")
        else:
            st.error("Failed to generate authorization URL")
