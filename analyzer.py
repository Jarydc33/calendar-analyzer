import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# =====================================
# SUMMARY FUNCTION
# =====================================

def load_calendar(path):
    df = pd.read_csv(path)

    df["Start"] = pd.to_datetime(
        df["Start Date"] + " " + df["Start Time"]
    )

    df["End"] = pd.to_datetime(
        df["End Date"] + " " + df["End Time"]
    )

    df["DurationHours"] = (
        df["End"] - df["Start"]
    ).dt.total_seconds() / 3600

    return df

def generate_summary(df):

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    total_meetings = len(df)
    total_hours = round(df["DurationHours"].sum(), 2)
    avg_length = round(df["DurationHours"].mean(), 2)

    date_range_days = (
        df["Start"].max() -
        df["Start"].min()
    ).days

    weeks_covered = max(
        date_range_days / 7,
        1
    )

    avg_hours_per_week = round(
        total_hours / weeks_covered,
        2
    )

    weekday_hours = (
        df.groupby(
            df["Start"].dt.day_name()
        )["DurationHours"]
        .sum()
        .reindex(
            weekday_order,
            fill_value=0
        )
        .round(2)
        .to_dict()
    )

    monthly_hours = (
        df.groupby(
            df["Start"].dt.to_period("M")
        )["DurationHours"]
        .sum()
        .round(2)
        .to_dict()
    )

    most_frequent_meetings = (
        df["Subject"]
        .value_counts()
        .head(10)
        .to_dict()
    )

    longest_meetings = (
        df.sort_values(
            "DurationHours",
            ascending=False
        )
        [["Subject", "DurationHours", "Start"]]
        .head(10)
        .to_dict("records")
    )

    return {
        "total_meetings": total_meetings,
        "total_hours": total_hours,
        "average_meeting_length_hours": avg_length,
        "average_hours_per_week": avg_hours_per_week,
        "hours_by_weekday": weekday_hours,
        "hours_by_month": monthly_hours,
        "most_frequent_meetings": most_frequent_meetings,
        "longest_meetings": longest_meetings,
    }


# =====================================
# DASHBOARD FUNCTION
# =====================================

def generate_charts(df):

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    # -------------------------
    # Aggregations
    # -------------------------

    weekday_hours = (
        df.groupby(
            df["Start"].dt.day_name()
        )["DurationHours"]
        .sum()
        .reindex(
            weekday_order,
            fill_value=0
        )
    )

    weekly_hours = (
        df.groupby(
            df["Start"].dt.to_period("W")
        )["DurationHours"]
        .sum()
    )

    top_meetings = (
        df["Subject"]
        .value_counts()
        .head(10)
    )

    # -------------------------
    # Heatmap Data
    # -------------------------

    heatmap_df = df.copy()

    heatmap_df["Weekday"] = (
        heatmap_df["Start"]
        .dt.day_name()
    )

    heatmap_df["Hour"] = (
        heatmap_df["Start"]
        .dt.hour
    )

    heatmap = (
        heatmap_df.pivot_table(
            index="Hour",
            columns="Weekday",
            values="DurationHours",
            aggfunc="sum",
            fill_value=0
        )
        .reindex(
            columns=weekday_order,
            fill_value=0
        )
    )

    heatmap = heatmap.reindex(
        range(24),
        fill_value=0
    )

    # -------------------------
    # Summary Metrics
    # -------------------------

    total_meetings = len(df)
    total_hours = df["DurationHours"].sum()
    avg_length = df["DurationHours"].mean()
    longest_meeting = df["DurationHours"].max()

    # -------------------------
    # Dashboard
    # -------------------------

    fig, axes = plt.subplots(
        2,
        3,
        figsize=(20, 10)
    )

    fig.suptitle(
        "Calendar Analyzer Dashboard",
        fontsize=20,
        fontweight="bold"
    )

    # ======================
    # Hours by Weekday
    # ======================

    ax = axes[0, 0]

    ax.bar(
        weekday_hours.index,
        weekday_hours.values
    )

    ax.set_title(
        "Meeting Hours by Day"
    )

    ax.set_ylabel("Hours")

    ax.tick_params(
        axis="x",
        rotation=45
    )

    # ======================
    # Heatmap
    # ======================

    ax = axes[0, 1]

    im = ax.imshow(
        heatmap.values,
        aspect="auto",
        cmap="YlOrRd",
        origin="lower"
    )

    ax.set_title(
        "Meeting Heatmap"
    )

    ax.set_xticks(
        np.arange(len(weekday_order))
    )

    ax.set_xticklabels(
        weekday_order,
        rotation=45
    )

    ax.set_yticks(
        np.arange(0, 24, 2)
    )

    ax.set_yticklabels(
        np.arange(0, 24, 2)
    )

    ax.set_xlabel("Day")
    ax.set_ylabel("Hour")

    fig.colorbar(
        im,
        ax=ax,
        label="Hours"
    )

    # ======================
    # Weekly Trend
    # ======================

    ax = axes[0, 2]

    ax.plot(
        weekly_hours.index.astype(str),
        weekly_hours.values,
        marker="o"
    )

    ax.set_title(
        "Meeting Hours by Week"
    )

    ax.set_ylabel("Hours")

    ax.tick_params(
        axis="x",
        rotation=45
    )

    # ======================
    # Top Meetings
    # ======================

    ax = axes[1, 0]

    ax.barh(
        top_meetings.index[::-1],
        top_meetings.values[::-1]
    )

    ax.set_title(
        "Top 10 Meeting Subjects"
    )

    ax.set_xlabel(
        "Occurrences"
    )

    # ======================
    # Duration Histogram
    # ======================

    ax = axes[1, 1]

    ax.hist(
        df["DurationHours"],
        bins=15
    )

    ax.set_title(
        "Meeting Length Distribution"
    )

    ax.set_xlabel("Hours")
    ax.set_ylabel("Count")

    # ======================
    # KPI Summary
    # ======================

    ax = axes[1, 2]

    ax.axis("off")

    summary_text = (
        f"Total Meetings: {total_meetings}\n\n"
        f"Total Hours: {total_hours:.1f}\n\n"
        f"Average Length: {avg_length:.2f} hrs\n\n"
        f"Longest Meeting: {longest_meeting:.2f} hrs"
    )

    ax.text(
        0.05,
        0.95,
        summary_text,
        fontsize=13,
        verticalalignment="top",
        bbox=dict(
            boxstyle="round",
            facecolor="#F0F0F0"
        )
    )

    plt.tight_layout()
    plt.show()

    return fig
# =====================================
# PRETTY TEXT REPORT
# =====================================
def print_report(summary):
    """
    Display Calendar Analyzer results in a
    human-readable format.
    """

    print("\n")
    print("=" * 60)
    print("📅 CALENDAR ANALYZER REPORT")
    print("=" * 60)

    print("\nOVERVIEW")
    print("-" * 60)

    print(
        f"Total Meetings: "
        f"{summary['total_meetings']}"
    )

    print(
        f"Total Meeting Hours: "
        f"{summary['total_hours']:.2f}"
    )

    print(
        f"Average Meeting Length: "
        f"{summary['average_meeting_length_hours']:.2f} hours"
    )

    print(
        f"Average Hours Per Week: "
        f"{summary['average_hours_per_week']:.2f}"
    )

    print("\nTIME BY WEEKDAY")
    print("-" * 60)

    for day, hours in summary["hours_by_weekday"].items():
        print(
            f"{day:<12} {hours:>6.2f} hrs"
        )

    print("\nMOST FREQUENT MEETINGS")
    print("-" * 60)

    for subject, count in summary[
        "most_frequent_meetings"
    ].items():

        print(
            f"{subject:<40} {count}"
        )

    print("\nLONGEST MEETINGS")
    print("-" * 60)

    for meeting in summary[
        "longest_meetings"
    ][:5]:

        print(
            f"{meeting['DurationHours']:>5.2f} hrs | "
            f"{meeting['Subject']}"
        )

    print("\n")
    
def print_insights(summary):

    busiest_day = max(
        summary["hours_by_weekday"],
        key=summary["hours_by_weekday"].get
    )

    busiest_hours = summary["hours_by_weekday"][busiest_day]

    most_common = next(
        iter(summary["most_frequent_meetings"].items())
    )

    print("\nKEY INSIGHTS")
    print("-" * 60)

    print(
        f"• Your busiest meeting day is "
        f"{busiest_day} ({busiest_hours:.1f} hrs)"
    )

    print(
        f"• Your most frequent meeting is "
        f"'{most_common[0]}' "
        f"({most_common[1]} occurrences)"
    )

    print(
        f"• You spent "
        f"{summary['total_hours']:.1f} hours "
        f"in meetings during this period."
    )


def generate_report(summary):
    report = f"""
CALENDAR ANALYZER REPORT
==================================================

OVERVIEW
--------------------------------------------------
Total Meetings: {summary['total_meetings']}
Total Meeting Hours: {summary['total_hours']:.2f}
Average Meeting Length: {summary['average_meeting_length_hours']:.2f} hours
Average Hours Per Week: {summary['average_hours_per_week']:.2f}

TIME BY WEEKDAY
--------------------------------------------------
"""

    for day, hours in summary["hours_by_weekday"].items():
        report += f"{day:<12} {hours:.2f} hrs\n"

    report += "\nMOST FREQUENT MEETINGS\n"
    report += "--------------------------------------------------\n"

    for subject, count in summary["most_frequent_meetings"].items():
        report += f"{subject}: {count}\n"

    return report