import streamlit as st

from analyzer import (
    load_calendar,
    generate_summary,
    generate_charts,
    generate_report
)

# ==========================
# SIDEBAR
# ==========================

with st.sidebar:
    st.title("📅 Calendar Analyzer")

    st.markdown("""
    Upload an Outlook or Google Calendar export
    and generate meeting analytics.

    Version 1.0
    """)

    uploaded_file = st.file_uploader(
        "Upload Calendar CSV",
        type=["csv"]
    )

# ==========================
# MAIN PAGE
# ==========================

st.title("📅 Calendar Analyzer")

if uploaded_file:

    df = load_calendar(uploaded_file)

    summary = generate_summary(df)

    report_text = generate_report(summary)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Meetings",
            summary["total_meetings"]
        )

    with col2:
        st.metric(
            "Hours",
            summary["total_hours"]
        )

    with col3:
        st.metric(
            "Avg Length",
            f"{summary['average_meeting_length_hours']:.2f}"
        )

    with col4:
        st.metric(
            "Avg Hours/Week",
            summary["average_hours_per_week"]
        )

    st.header("Report")
    st.subheader("Analysis Report")
    st.text(report_text)
    st.download_button(
        "Download Report",
        report_text,
        file_name="calendar_report.txt"
    )

    fig = generate_charts(df)

    st.pyplot(fig)