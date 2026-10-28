import streamlit as st
import pandas as pd
from analyzer import (
    load_outlook_csv,
    generate_summary,
    generate_charts,
    generate_report,
    load_calendar
)

# ==========================
# SIDEBAR
# ==========================

with st.sidebar:

    st.title("📅 Calendar Analyzer")

    st.markdown("""
    Upload an Outlook or Google Calendar export
    and generate meeting analytics.

    Version 1.3.1
    """)

    st.divider()

    with st.expander("📖 How do I export my calendar?"):

        provider = st.selectbox(
            "Calendar Provider",
            [
                "Google Calendar",
                "Outlook Desktop",
                "Outlook Web",
                "Apple Calendar"
            ]
        )

        if provider == "Google Calendar":

            st.markdown("""
            ### Google Calendar

            1. Open Google Calendar
            2. Click ⚙️ Settings
            3. Select **Import & Export**
            4. Click **Export**
            5. Google downloads a ZIP file
            6. Extract the ZIP
            7. Upload the `.ics` file(s) here
            """)

        elif provider == "Outlook Desktop":

            st.markdown("""
            ### Outlook Desktop

            1. Open Outlook
            2. File → Open & Export
            3. Import/Export
            4. Export to a File
            5. Comma Separated Values (CSV)
            6. Select Calendar
            7. Save and upload the CSV
            """)

        elif provider == "Outlook Web":

            st.markdown("""
            ### Outlook Web

            1. Open Outlook on the Web
            2. Open Calendar
            3. Settings → Calendar
            4. Shared Calendars
            5. Publish Calendar
            6. Download the ICS file
            7. Upload the ICS file here
            """)

        elif provider == "Apple Calendar":

            st.markdown("""
            ### Apple Calendar

            1. Open Calendar
            2. Right-click your calendar
            3. Share Calendar
            4. Enable Public Calendar
            5. Copy/download the ICS file
            6. Upload the ICS file here
            """)

    st.divider()

    PRO_MODE = st.toggle(
        "Pro Mode (Development)",
        value=False
    )



# ==========================
# MAIN PAGE
# ==========================

st.title("📅 Calendar Analyzer")

uploaded_files = st.file_uploader(
    "Upload Calendar File",
    type=["csv", "ics"],
    accept_multiple_files=True
)

if uploaded_files:

    if not PRO_MODE and len(uploaded_files) > 1:

        st.error(
            "Free users may upload one calendar at a time."
        )

        st.stop()

    results = []

    for uploaded_file in uploaded_files:

        result = load_calendar(uploaded_file)

        results.append(result)

    # -----------------------------
    # Upload Information
    # -----------------------------

    st.subheader("Uploaded Calendars")

    for result in results:

        st.success(
            f"{result['calendar_type']} | "
            f"Loaded: {result['events_loaded']} | "
            f"Skipped: {result['events_skipped']}"
        )

    # -----------------------------
    # Analysis Mode
    # -----------------------------

    if PRO_MODE and len(results) > 1:

        analysis_mode = st.radio(
            "Analysis Mode",
            [
                "Combined",
                "Separate"
            ]
        )

    else:

        analysis_mode = "Combined"

    # -----------------------------
    # SEPARATE MODE
    # -----------------------------

    if analysis_mode == "Separate":

        for result in results:

            df = result["data"]

            calendar_type = result["calendar_type"]

            st.header(calendar_type)

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

            st.subheader("Analysis Report")

            st.text(report_text)

            fig = generate_charts(df)

            st.pyplot(fig)

    # -----------------------------
    # COMBINED MODE
    # -----------------------------

    else:

        combined_df = pd.concat(
            [
                result["data"]
                for result in results
            ],
            ignore_index=True
        )

        summary = generate_summary(
            combined_df
        )

        report_text = generate_report(
            summary
        )

        st.success(
            f"Combined Analysis ({len(results)} calendar(s))"
        )

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

        st.text(report_text)

        st.download_button(
            "Download Report",
            report_text,
            file_name="calendar_report.txt"
        )

        fig = generate_charts(
            combined_df
        )

        st.pyplot(fig)