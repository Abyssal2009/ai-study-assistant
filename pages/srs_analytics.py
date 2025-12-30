"""
Study Assistant - SRS Analytics Page
Comprehensive analytics for spaced repetition flashcard learning.
"""

import streamlit as st
import database as db
from datetime import date, timedelta
import pandas as pd


def render():
    """Render the SRS Analytics page."""
    st.title("📊 SRS Analytics")
    st.markdown("**Track your flashcard learning progress and memory retention.**")

    # Check for flashcards
    fc_stats = db.get_flashcard_stats()
    if fc_stats['total'] == 0:
        st.warning("No flashcards yet. Add some in the Flashcards page to see analytics!")
        st.stop()

    # Top metrics row
    _render_top_metrics()

    st.markdown("---")

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Progress",
        "📅 Forecast",
        "🔥 Streak & Activity",
        "📊 Detailed Stats"
    ])

    with tab1:
        _render_progress_tab()

    with tab2:
        _render_forecast_tab()

    with tab3:
        _render_streak_activity_tab()

    with tab4:
        _render_detailed_stats_tab()


def _render_top_metrics():
    """Render the top metrics row."""
    col1, col2, col3, col4 = st.columns(4)

    due_count = db.get_due_flashcards_count()
    overdue_count = db.get_overdue_flashcards_count()
    streak = db.get_review_streak()
    weekly = db.get_weekly_srs_summary()

    with col1:
        # Due today card
        if due_count > 0:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #3498db22, #3498db11);
                        border-left: 4px solid #3498db;
                        padding: 15px; border-radius: 0 8px 8px 0;">
                <h2 style="margin: 0; color: #3498db;">{due_count}</h2>
                <p style="margin: 5px 0 0 0; color: #666;">Cards Due Today</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #2ecc7122, #2ecc7111);
                        border-left: 4px solid #2ecc71;
                        padding: 15px; border-radius: 0 8px 8px 0;">
                <h2 style="margin: 0; color: #2ecc71;">0</h2>
                <p style="margin: 5px 0 0 0; color: #666;">All Caught Up!</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        # Overdue card
        if overdue_count > 0:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e74c3c22, #e74c3c11);
                        border-left: 4px solid #e74c3c;
                        padding: 15px; border-radius: 0 8px 8px 0;">
                <h2 style="margin: 0; color: #e74c3c;">{overdue_count}</h2>
                <p style="margin: 5px 0 0 0; color: #666;">Overdue Cards</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #2ecc7122, #2ecc7111);
                        border-left: 4px solid #2ecc71;
                        padding: 15px; border-radius: 0 8px 8px 0;">
                <h2 style="margin: 0; color: #2ecc71;">0</h2>
                <p style="margin: 5px 0 0 0; color: #666;">No Overdue</p>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        # Streak card
        streak_val = streak['current_streak']
        streak_color = "#e67e22" if streak_val > 0 else "#95a5a6"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {streak_color}22, {streak_color}11);
                    border-left: 4px solid {streak_color};
                    padding: 15px; border-radius: 0 8px 8px 0;">
            <h2 style="margin: 0; color: {streak_color};">{streak_val} 🔥</h2>
            <p style="margin: 5px 0 0 0; color: #666;">Day Streak</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        # Weekly accuracy
        accuracy = weekly['accuracy']
        acc_color = "#2ecc71" if accuracy >= 80 else "#f39c12" if accuracy >= 60 else "#e74c3c"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {acc_color}22, {acc_color}11);
                    border-left: 4px solid {acc_color};
                    padding: 15px; border-radius: 0 8px 8px 0;">
            <h2 style="margin: 0; color: {acc_color};">{accuracy:.0f}%</h2>
            <p style="margin: 5px 0 0 0; color: #666;">Weekly Accuracy</p>
        </div>
        """, unsafe_allow_html=True)


def _render_progress_tab():
    """Render the Progress tab with retention charts."""
    st.markdown("### 📈 Learning Progress")

    # Retention rate over time
    st.markdown("#### Retention Rate (Last 30 Days)")
    retention_data = db.get_retention_rate_over_time(30)

    if retention_data:
        df = pd.DataFrame(retention_data)
        df['review_date'] = pd.to_datetime(df['review_date'])
        st.line_chart(df.set_index('review_date')['retention_rate'], use_container_width=True)

        # Summary stats
        avg_retention = sum(d['retention_rate'] for d in retention_data) / len(retention_data)
        st.caption(f"Average retention: **{avg_retention:.1f}%** over {len(retention_data)} review days")
    else:
        st.info("No review data yet. Start reviewing flashcards to see your progress!")

    st.markdown("---")

    # Forgetting curve
    st.markdown("#### Forgetting Curve")
    st.caption("Success rate at different review intervals")

    curve_data = db.get_forgetting_curve_data()
    if curve_data:
        df = pd.DataFrame(curve_data)
        st.bar_chart(df.set_index('interval_bucket')['success_rate'], use_container_width=True)

        # Interpretation
        if len(curve_data) >= 3:
            short_term = next((d['success_rate'] for d in curve_data if d['bucket_order'] <= 2), 0)
            long_term = next((d['success_rate'] for d in curve_data if d['bucket_order'] >= 5), 0)

            if long_term >= 80:
                st.success("Excellent long-term retention! Your learning is sticking.")
            elif long_term >= 60:
                st.info("Good retention. Regular reviews are helping.")
            else:
                st.warning("Long-term retention could improve. Try reviewing more frequently.")
    else:
        st.info("Not enough review data for forgetting curve analysis.")

    st.markdown("---")

    # Performance by subject
    st.markdown("#### Performance by Subject")
    subject_data = db.get_srs_performance_by_subject()

    if subject_data:
        for subj in subject_data:
            accuracy = subj['accuracy'] or 0
            colour = subj['subject_colour']

            st.markdown(f"""
            <div style="background: {colour}11; border-left: 4px solid {colour};
                        padding: 10px 15px; margin-bottom: 8px; border-radius: 0 8px 8px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="color: {colour};">{subj['subject_name']}</strong>
                    <span>{subj['total_cards']} cards | {accuracy:.0f}% accuracy</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No subject data available.")


def _render_forecast_tab():
    """Render the Forecast tab."""
    st.markdown("### 📅 Review Forecast")
    st.caption("Predicted cards due for the upcoming period")

    # Time period selector
    period = st.radio("Forecast period:", [7, 14, 30], format_func=lambda x: f"{x} days", horizontal=True)

    forecast_data = db.get_review_forecast(period)

    if forecast_data:
        # Build complete date range with zeros for missing days
        start_date = date.today()
        date_counts = {d['due_date']: d['cards_due'] for d in forecast_data}

        full_data = []
        for i in range(period):
            d = start_date + timedelta(days=i)
            d_str = d.isoformat()
            full_data.append({
                'date': d_str,
                'cards_due': date_counts.get(d_str, 0)
            })

        df = pd.DataFrame(full_data)
        df['date'] = pd.to_datetime(df['date'])
        st.bar_chart(df.set_index('date')['cards_due'], use_container_width=True)

        # Summary
        total_due = sum(d['cards_due'] for d in full_data)
        peak_day = max(full_data, key=lambda x: x['cards_due'])
        avg_daily = total_due / period

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cards Due", total_due)
        with col2:
            st.metric("Daily Average", f"{avg_daily:.1f}")
        with col3:
            st.metric("Peak Day", f"{peak_day['cards_due']} cards")

        # Workload assessment
        st.markdown("---")
        st.markdown("#### Workload Assessment")

        if avg_daily > 50:
            st.warning(f"Heavy workload ahead! Consider spacing out new cards.")
        elif avg_daily > 20:
            st.info(f"Moderate workload. Plan for ~{int(avg_daily * 0.5)} minutes daily.")
        else:
            st.success(f"Light workload. You're on track!")
    else:
        st.success("No cards scheduled for the next {period} days. Great job staying ahead!")


def _render_streak_activity_tab():
    """Render the Streak & Activity tab."""
    st.markdown("### 🔥 Streak & Activity")

    # Streak display
    streak = db.get_review_streak()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Current Streak")
        streak_val = streak['current_streak']

        # Large streak display
        if streak_val > 0:
            flame_size = min(streak_val, 10)  # Cap visual size
            flames = "🔥" * flame_size
            st.markdown(f"""
            <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #e67e2222, #e67e2211);
                        border-radius: 12px; margin-bottom: 20px;">
                <h1 style="font-size: 4rem; margin: 0; color: #e67e22;">{streak_val}</h1>
                <p style="font-size: 1.5rem; margin: 10px 0 0 0;">{flames}</p>
                <p style="color: #666; margin-top: 10px;">consecutive days</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align: center; padding: 30px; background: #f8f9fa;
                        border-radius: 12px; margin-bottom: 20px;">
                <h1 style="font-size: 4rem; margin: 0; color: #95a5a6;">0</h1>
                <p style="color: #666; margin-top: 10px;">Start reviewing to begin a streak!</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### Streak Records")
        st.metric("Longest Streak", f"{streak['longest_streak']} days")
        st.metric("Last Review", streak['last_review_date'] or "Never")

        if streak['current_streak'] > 0 and streak['current_streak'] >= streak['longest_streak']:
            st.success("You're at your longest streak! Keep going!")

    st.markdown("---")

    # Review heatmap
    st.markdown("#### Review Activity (Last 12 Weeks)")
    st.caption("Darker = more reviews")

    heatmap_data = db.get_review_heatmap_data(12)

    if heatmap_data:
        # Build visual heatmap using HTML/CSS
        _render_heatmap(heatmap_data)

        # Activity summary
        total_reviews = sum(d['count'] for d in heatmap_data)
        active_days = sum(1 for d in heatmap_data if d['count'] > 0)
        total_days = len(heatmap_data)

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Reviews", total_reviews)
        with col2:
            st.metric("Active Days", f"{active_days}/{total_days}")
        with col3:
            consistency = (active_days / total_days * 100) if total_days > 0 else 0
            st.metric("Consistency", f"{consistency:.0f}%")
    else:
        st.info("No activity data yet.")

    # Average review time trend
    st.markdown("---")
    st.markdown("#### Average Time per Card (Last 14 Days)")

    time_data = db.get_average_review_time_trend(14)
    if time_data:
        df = pd.DataFrame(time_data)
        df['review_date'] = pd.to_datetime(df['review_date'])
        st.line_chart(df.set_index('review_date')['avg_time_seconds'], use_container_width=True)
        st.caption("Lower times can indicate better recall speed")
    else:
        st.info("No timing data available.")


def _render_heatmap(heatmap_data: list):
    """Render a GitHub-style activity heatmap."""
    # Intensity colors
    colors = ['#ebedf0', '#c6e48b', '#7bc96f', '#239a3b', '#196127']

    # Group by week
    weeks = {}
    for d in heatmap_data:
        week_num = date.fromisoformat(d['date']).isocalendar()[1]
        if week_num not in weeks:
            weeks[week_num] = []
        weeks[week_num].append(d)

    # Build HTML grid
    html = '<div style="display: flex; gap: 3px; overflow-x: auto; padding: 10px 0;">'

    for week_num in sorted(weeks.keys()):
        week_data = weeks[week_num]
        html += '<div style="display: flex; flex-direction: column; gap: 3px;">'
        for day in sorted(week_data, key=lambda x: x['weekday']):
            color = colors[day['level']]
            title = f"{day['date']}: {day['count']} reviews"
            html += f'<div style="width: 12px; height: 12px; background: {color}; border-radius: 2px;" title="{title}"></div>'
        html += '</div>'

    html += '</div>'
    html += '<p style="font-size: 12px; color: #666; margin-top: 5px;">Less <span style="display: inline-flex; gap: 2px;">'
    for color in colors:
        html += f'<span style="width: 10px; height: 10px; background: {color}; display: inline-block; border-radius: 2px;"></span>'
    html += '</span> More</p>'

    st.markdown(html, unsafe_allow_html=True)


def _render_detailed_stats_tab():
    """Render the Detailed Stats tab."""
    st.markdown("### 📊 Detailed Statistics")

    # Card maturity distribution
    st.markdown("#### Card Maturity Distribution")
    maturity = db.get_card_maturity_distribution()

    if maturity['total'] > 0:
        col1, col2 = st.columns([2, 1])

        with col1:
            # Create pie chart data
            labels = ['New', 'Learning', 'Young', 'Mature']
            values = [maturity['new_cards'], maturity['learning'], maturity['young'], maturity['mature']]
            colors = ['#3498db', '#f39c12', '#2ecc71', '#27ae60']

            # Display as horizontal bars (more compatible)
            for label, value, color in zip(labels, values, colors):
                pct = (value / maturity['total'] * 100) if maturity['total'] > 0 else 0
                st.markdown(f"""
                <div style="margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                        <span>{label}</span>
                        <span><strong>{value}</strong> ({pct:.0f}%)</span>
                    </div>
                    <div style="background: #eee; height: 20px; border-radius: 4px; overflow: hidden;">
                        <div style="background: {color}; width: {pct}%; height: 100%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("**Legend:**")
            st.markdown("- **New**: Never reviewed")
            st.markdown("- **Learning**: < 7 day interval")
            st.markdown("- **Young**: 7-21 day interval")
            st.markdown("- **Mature**: > 21 day interval")

    st.markdown("---")

    # Subject breakdown table
    st.markdown("#### Subject Breakdown")
    subject_data = db.get_srs_performance_by_subject()

    if subject_data:
        # Create table data
        table_data = []
        for subj in subject_data:
            table_data.append({
                'Subject': subj['subject_name'],
                'Cards': subj['total_cards'],
                'Due': subj['due_cards'],
                'Avg Ease': f"{subj['avg_ease']:.2f}",
                'Accuracy': f"{subj['accuracy']:.0f}%",
                'Reviews': subj['total_reviews']
            })

        st.dataframe(table_data, use_container_width=True)

    st.markdown("---")

    # Weekly summary
    st.markdown("#### This Week's Summary")
    weekly = db.get_weekly_srs_summary()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Cards Reviewed", weekly['cards_reviewed'])
    with col2:
        st.metric("Correct", weekly['correct'])
    with col3:
        st.metric("Accuracy", f"{weekly['accuracy']}%")
    with col4:
        st.metric("Time Spent", f"{weekly['time_spent_mins']:.0f} min")

    st.markdown("---")

    # Export section
    st.markdown("#### Export Data")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Export Review History (CSV)"):
            history = db.get_review_history(90)
            if history:
                df = pd.DataFrame(history)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="flashcard_review_history.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No review history to export")

    with col2:
        if st.button("📊 Export Subject Stats (CSV)"):
            stats = db.get_srs_performance_by_subject()
            if stats:
                df = pd.DataFrame(stats)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="srs_subject_stats.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No subject stats to export")
