"""
Study Assistant - What Next? Page
Study recommendations based on deadlines and priorities.
"""

import streamlit as st
import database as db
from utils import get_urgency_colour, get_urgency_icon, URGENCY_LABELS


def render():
    """Render the What Next? recommendations page."""
    st.title("🎯 What Should I Study Next?")
    st.markdown("**Personalised recommendations based on your deadlines, exams, and flashcards.**")

    subjects = db.get_all_subjects()
    if not subjects:
        st.warning("Please add subjects first in the Subjects page.")
        st.stop()

    # Get all recommendations
    recommendations = db.get_study_recommendations(limit=10)

    if not recommendations:
        st.success("""
        🎉 **Amazing! You're all caught up!**

        No urgent tasks right now. Here are some suggestions:
        - Add flashcards for topics you're learning
        - Start a focus session to review a subject
        - Check if you have any upcoming exams to prepare for
        """)
    else:
        # Top recommendation (highlighted)
        top_rec = recommendations[0]
        color = get_urgency_colour(top_rec['urgency'])
        icon = get_urgency_icon(top_rec['urgency'])
        label = URGENCY_LABELS.get(top_rec['urgency'], 'LOW')

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {color}33, {color}11);
                    border: 2px solid {color};
                    padding: 20px;
                    border-radius: 12px;
                    margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="background: {color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">{label}</span>
                <span style="color: #666; font-size: 14px;">{top_rec['subject_name']}</span>
            </div>
            <h2 style="margin: 15px 0 10px 0; color: {color};">{icon} {top_rec['title']}</h2>
            <p style="font-size: 1.1em; margin: 10px 0; color: #444;">{top_rec['reason']}</p>
            <p style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.5); border-radius: 8px;">
                <strong>Action:</strong> {top_rec['action']}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Other recommendations
        if len(recommendations) > 1:
            st.markdown("### Other Priorities")

            for rec in recommendations[1:]:
                color = get_urgency_colour(rec['urgency'])
                icon = get_urgency_icon(rec['urgency'])

                st.markdown(f"""
                <div style="background: white;
                            border-left: 4px solid {color};
                            padding: 15px;
                            margin: 10px 0;
                            border-radius: 0 8px 8px 0;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>{icon} {rec['title']}</strong>
                        <span style="color: #666; font-size: 14px;">{rec['subject_name']}</span>
                    </div>
                    <p style="margin: 5px 0; color: #666; font-size: 14px;">{rec['reason']}</p>
                </div>
                """, unsafe_allow_html=True)
