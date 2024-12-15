import streamlit as st
import altair as alt
import pandas as pd
from datetime import datetime


def format_date(ts):
    return datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")


def create_conversation_chart(conversations, on_select):
    """Create an interactive bar chart of conversations"""
    if not conversations:
        return

    # Convert conversations to DataFrame
    data = []
    for phone, stats in conversations.items():
        data.append(
            {
                "contact": f"{stats['contact_name']} ({phone})",
                "messages": stats["count"],
                "date_range": f"{format_date(stats['first_date'])} to {format_date(stats['last_date'])}",
                "phone": phone,
            }
        )

    df = pd.DataFrame(data)
    df = df.sort_values("messages", ascending=True).tail(20)  # Show top 20

    # Create interactive chart
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("messages:Q", title="Number of Messages"),
            y=alt.Y("contact:N", title=None, sort="-x"),
            tooltip=["contact", "messages", "date_range"],
            color=alt.value("#1f77b4"),
        )
        .properties(
            height=min(
                len(df) * 25, 500
            )  # Dynamic height based on number of bars
        )
        .interactive()
    )

    # Use streamlit's chart click events
    selected_point = alt.selection_single(
        encodings=["y"], bind="legend"  # Allow selection by clicking bars
    )

    chart = chart.add_selection(selected_point)

    # Display chart
    st.altair_chart(chart, use_container_width=True)

    # Return the data for selection handling
    return df
