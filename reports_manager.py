import pandas as pd
import plotly.express as px
import streamlit as st

from db import fetch_all, fetch_one
from trip_manager import get_trips
from ui import metric_card, render_hero, section_heading


def money(amount, currency="INR"):
    amount = float(amount or 0)
    formatted = f"{amount:,.2f}".rstrip("0").rstrip(".")
    return f"₹{formatted}" if currency == "INR" else f"{currency} {formatted}"


def chart_colors():
    """Return chart colors based on the selected TravelMate appearance."""
    is_dark = st.session_state.get("theme_mode", "Light") == "Dark"
    if is_dark:
        return {
            "font": "#E5E7EB",
            "grid": "#334155",
            "paper": "rgba(0,0,0,0)",
            "plot": "rgba(0,0,0,0)",
            "blue": "#60A5FA",
            "teal": "#2DD4BF",
            "amber": "#FBBF24",
            "muted": "#94A3B8",
        }
    return {
        "font": "#172B4D",
        "grid": "#E2E8F0",
        "paper": "rgba(0,0,0,0)",
        "plot": "rgba(0,0,0,0)",
        "blue": "#2563EB",
        "teal": "#0F766E",
        "amber": "#F59E0B",
        "muted": "#64748B",
    }


def show_chart(fig):
    colors = chart_colors()
    fig.update_layout(
        paper_bgcolor=colors["paper"],
        plot_bgcolor=colors["plot"],
        font_color=colors["font"],
        margin=dict(t=35, b=24, l=10, r=10),
        legend_title_text="",
    )
    fig.update_xaxes(gridcolor=colors["grid"], zerolinecolor=colors["grid"])
    fig.update_yaxes(gridcolor=colors["grid"], zerolinecolor=colors["grid"])
    st.plotly_chart(fig, use_container_width=True)


def show_table(data, *, hide_index=True):
    """Render a Streamlit dataframe with arguments supported by older versions too."""
    st.dataframe(data, use_container_width=True, hide_index=hide_index)


def render_reports_page():
    render_hero(
        "TRIP ANALYTICS",
        "Understand every part of your journey.",
        "Explore budgets, spending patterns, itinerary progress and contributions through interactive reports.",
    )

    trips = get_trips()
    if not trips:
        st.info("Create a trip before viewing its reports.")
        return

    trip_options = {
        f'{trip["trip_name"]} · Trip #{trip["trip_id"]}': int(trip["trip_id"])
        for trip in trips
    }
    labels = list(trip_options.keys())
    previous_id = st.session_state.get("selected_trip_id")
    default_index = next(
        (i for i, label in enumerate(labels) if trip_options[label] == previous_id),
        0,
    )

    selected_label = st.selectbox(
        "Choose a trip to analyze",
        labels,
        index=default_index,
        key="reports_trip_selector",
    )
    trip_id = trip_options[selected_label]
    st.session_state["selected_trip_id"] = trip_id

    summary = fetch_one(
        """
        SELECT
            t.trip_id,
            t.trip_name,
            t.start_date,
            t.end_date,
            t.planned_budget,
            t.currency,
            t.status,
            u.full_name AS organizer_name,
            (SELECT COUNT(*) FROM trip_member tm WHERE tm.trip_id = t.trip_id) AS member_count,
            (SELECT COALESCE(SUM(e.amount), 0) FROM expense e WHERE e.trip_id = t.trip_id) AS actual_expenses,
            (SELECT COUNT(*) FROM destinations d WHERE d.trip_id = t.trip_id) AS destination_count,
            (SELECT COUNT(*) FROM activities a INNER JOIN destinations d ON d.destination_id = a.destination_id WHERE d.trip_id = t.trip_id) AS activity_count,
            (SELECT COUNT(*) FROM activities a INNER JOIN destinations d ON d.destination_id = a.destination_id WHERE d.trip_id = t.trip_id AND a.is_completed = 1) AS completed_count
        FROM trips t
        INNER JOIN users u ON u.user_id = t.organizer_id
        WHERE t.trip_id = %s
        """,
        (trip_id,),
    )

    if not summary:
        st.error("Unable to retrieve the selected trip.")
        return

    currency = summary["currency"]
    budget = float(summary["planned_budget"] or 0)
    spent = float(summary["actual_expenses"] or 0)
    remaining = budget - spent
    activity_count = int(summary["activity_count"] or 0)
    completed_count = int(summary["completed_count"] or 0)
    member_count = int(summary["member_count"] or 0)
    budget_used = spent / budget * 100 if budget > 0 else 0
    completion = completed_count / activity_count * 100 if activity_count else 0

    section_heading(
        summary["trip_name"],
        f'{summary["start_date"]} – {summary["end_date"]} · Organized by {summary["organizer_name"]}',
        eyebrow="TRIP REPORT",
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Planned budget", money(budget, currency), icon="💰")
    with col2:
        metric_card("Recorded spending", money(spent, currency), icon="💳")
    with col3:
        metric_card("Members", member_count, icon="👥")
    with col4:
        metric_card(
            "Activity completion",
            f"{completion:.1f}%",
            icon="✅",
            note=f"{completed_count} of {activity_count} activities",
        )

    if budget > 0:
        st.markdown("#### Budget utilization")
        st.progress(min(max(budget_used / 100, 0.0), 1.0))
        left, right = st.columns(2)
        with left:
            st.caption(f"{budget_used:.1f}% of planned budget recorded")
        with right:
            st.caption(f"Remaining: {money(remaining, currency)}")
        if spent > budget:
            st.warning("This trip is over its planned budget.")
        elif spent == budget:
            st.info("Recorded expenses equal the planned budget.")
    else:
        st.info("This trip has a zero budget. Set a positive budget to calculate utilization.")

    overview_tab, expense_tab, itinerary_tab, logistics_tab = st.tabs(
        ["📊 Overview", "💳 Expense analysis", "🗓️ Itinerary progress", "🏨 Bookings & contributions"]
    )

    # OVERVIEW
    with overview_tab:
        section_heading(
            "Budget versus recorded spending",
            "Booking costs and contributions are shown separately from expenses to avoid double-counting.",
        )
        budget_chart = pd.DataFrame(
            [
                {"Measure": "Planned budget", "Amount": budget},
                {"Measure": "Recorded expenses", "Amount": spent},
                {"Measure": "Budget remaining", "Amount": remaining},
            ]
        )
        colors = chart_colors()
        fig = px.bar(
            budget_chart,
            x="Measure",
            y="Amount",
            text="Amount",
            color="Measure",
            color_discrete_map={
                "Planned budget": colors["blue"],
                "Recorded expenses": colors["teal"],
                "Budget remaining": colors["amber"],
            },
        )
        fig.update_traces(texttemplate="%{text:,.2f}", textposition="outside")
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title=f"Amount ({currency})")
        show_chart(fig)

        section_heading(
            "Shared versus personal spending",
            "Compare the amount and number of expenses by type.",
        )
        expense_types = fetch_all(
            """
            SELECT expense_type, COUNT(*) AS expense_count,
                   COALESCE(SUM(amount), 0) AS total_amount,
                   COALESCE(AVG(amount), 0) AS average_amount
            FROM expense
            WHERE trip_id = %s
            GROUP BY expense_type
            ORDER BY total_amount DESC
            """,
            (trip_id,),
        )
        if expense_types:
            type_data = pd.DataFrame(
                [
                    {
                        "Type": row["expense_type"],
                        "Total amount": float(row["total_amount"] or 0),
                        "Number of expenses": int(row["expense_count"] or 0),
                    }
                    for row in expense_types
                ]
            )
            left, right = st.columns(2)
            with left:
                fig = px.pie(
                    type_data,
                    names="Type",
                    values="Total amount",
                    hole=0.60,
                    color_discrete_sequence=[colors["blue"], colors["teal"]],
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")
                show_chart(fig)
            with right:
                show_table(
                    [
                        {
                            "Expense type": row["expense_type"],
                            "Count": int(row["expense_count"] or 0),
                            "Total": money(row["total_amount"], currency),
                            "Average": money(row["average_amount"], currency),
                        }
                        for row in expense_types
                    ]
                )
        else:
            st.info("No expense records are available for this trip.")

    # EXPENSE ANALYSIS
    with expense_tab:
        section_heading(
            "Spending by category",
            "Find out which categories account for the recorded expenses.",
        )
        categories = fetch_all(
            """
            SELECT ec.category_name, COUNT(e.expense_id) AS expense_count,
                   COALESCE(SUM(e.amount), 0) AS total_amount,
                   COALESCE(AVG(e.amount), 0) AS average_amount
            FROM expense_category ec
            INNER JOIN expense e ON e.category_id = ec.category_id
            WHERE e.trip_id = %s
            GROUP BY ec.category_id, ec.category_name
            ORDER BY total_amount DESC
            """,
            (trip_id,),
        )
        if categories:
            category_data = pd.DataFrame(
                [
                    {
                        "Category": row["category_name"],
                        "Total amount": float(row["total_amount"] or 0),
                        "Expense count": int(row["expense_count"] or 0),
                    }
                    for row in categories
                ]
            )
            colors = chart_colors()
            fig = px.bar(
                category_data,
                x="Category",
                y="Total amount",
                text="Total amount",
                color="Total amount",
                color_continuous_scale=[colors["muted"], colors["blue"]],
            )
            fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig.update_layout(
                xaxis_title="",
                yaxis_title=f"Amount ({currency})",
                coloraxis_showscale=False,
            )
            show_chart(fig)
            show_table(
                [
                    {
                        "Category": row["category_name"],
                        "Expenses": int(row["expense_count"] or 0),
                        "Total": money(row["total_amount"], currency),
                        "Average": money(row["average_amount"], currency),
                    }
                    for row in categories
                ]
            )
        else:
            st.info("No expenses are recorded for this trip yet.")

        st.markdown("---")
        section_heading(
            "Spending by member",
            "See who paid for expenses and how payments are categorized.",
        )
        member_spending = fetch_all(
            """
            SELECT u.full_name AS member_name,
                   COUNT(e.expense_id) AS expenses_paid,
                   COALESCE(SUM(e.amount), 0) AS total_paid,
                   COALESCE(SUM(CASE WHEN e.expense_type = 'SHARED' THEN e.amount ELSE 0 END), 0) AS shared_paid,
                   COALESCE(SUM(CASE WHEN e.expense_type = 'PERSONAL' THEN e.amount ELSE 0 END), 0) AS personal_paid
            FROM expense e
            INNER JOIN users u ON u.user_id = e.paid_by
            WHERE e.trip_id = %s
            GROUP BY u.user_id, u.full_name
            ORDER BY total_paid DESC
            """,
            (trip_id,),
        )
        if member_spending:
            show_table(
                [
                    {
                        "Member": row["member_name"],
                        "Expenses paid": int(row["expenses_paid"] or 0),
                        "Total paid": money(row["total_paid"], currency),
                        "Shared paid": money(row["shared_paid"], currency),
                        "Personal paid": money(row["personal_paid"], currency),
                    }
                    for row in member_spending
                ]
            )
        else:
            st.info("No member spending records exist yet.")

        st.markdown("---")
        section_heading("Expense ledger", "Download all recorded expenses for this trip.")
        ledger = fetch_all(
            """
            SELECT e.expense_date, e.description, ec.category_name,
                   u.full_name AS paid_by, e.expense_type, e.amount, e.receipt_path
            FROM expense e
            INNER JOIN expense_category ec ON ec.category_id = e.category_id
            INNER JOIN users u ON u.user_id = e.paid_by
            WHERE e.trip_id = %s
            ORDER BY e.expense_date DESC, e.expense_id DESC
            """,
            (trip_id,),
        )
        if ledger:
            ledger_df = pd.DataFrame(
                [
                    {
                        "Date": str(row["expense_date"]),
                        "Description": row["description"],
                        "Category": row["category_name"],
                        "Paid by": row["paid_by"],
                        "Type": row["expense_type"],
                        "Amount": float(row["amount"] or 0),
                        "Receipt path": row["receipt_path"] or "",
                    }
                    for row in ledger
                ]
            )
            show_table(ledger_df)
            st.download_button(
                "Download expense ledger (CSV)",
                data=ledger_df.to_csv(index=False).encode("utf-8"),
                file_name=f"trip_{trip_id}_expense_ledger.csv",
                mime="text/csv",
            )
        else:
            st.info("There are no expenses to export.")

    # ITINERARY PROGRESS
    with itinerary_tab:
        section_heading(
            "Activity completion by destination",
            "Measure itinerary progress across the trip.",
        )
        destination_report = fetch_all(
            """
            SELECT d.destination_id, d.location_name, d.visit_date,
                   COUNT(a.activity_id) AS total_activities,
                   COALESCE(SUM(CASE WHEN a.is_completed = 1 THEN 1 ELSE 0 END), 0) AS completed_activities,
                   COALESCE(SUM(CASE WHEN a.activity_id IS NOT NULL AND a.is_completed = 0 THEN 1 ELSE 0 END), 0) AS pending_activities
            FROM destinations d
            LEFT JOIN activities a ON a.destination_id = d.destination_id
            WHERE d.trip_id = %s
            GROUP BY d.destination_id, d.location_name, d.visit_date
            ORDER BY d.visit_date, d.destination_id
            """,
            (trip_id,),
        )
        if destination_report:
            destination_data = pd.DataFrame(
                [
                    {
                        "Destination": row["location_name"],
                        "Completed": int(row["completed_activities"] or 0),
                        "Pending": int(row["pending_activities"] or 0),
                    }
                    for row in destination_report
                ]
            )
            colors = chart_colors()
            fig = px.bar(
                destination_data,
                x="Destination",
                y=["Completed", "Pending"],
                barmode="stack",
                color_discrete_map={
                    "Completed": colors["teal"],
                    "Pending": colors["muted"],
                },
            )
            fig.update_layout(xaxis_title="", yaxis_title="Number of activities")
            show_chart(fig)
            show_table(
                [
                    {
                        "Destination": row["location_name"],
                        "Visit date": str(row["visit_date"] or "Not set"),
                        "Total activities": int(row["total_activities"] or 0),
                        "Completed": int(row["completed_activities"] or 0),
                        "Pending": int(row["pending_activities"] or 0),
                    }
                    for row in destination_report
                ]
            )
        else:
            st.info("No destinations have been added to this trip.")

        st.markdown("---")
        section_heading(
            "Activities still pending",
            "Review activities that have not been marked complete.",
        )
        pending_activities = fetch_all(
            """
            SELECT d.location_name, a.activity_name, a.activity_date,
                   a.start_time, a.end_time, a.notes
            FROM activities a
            INNER JOIN destinations d ON d.destination_id = a.destination_id
            WHERE d.trip_id = %s AND a.is_completed = 0
            ORDER BY a.activity_date, a.start_time
            """,
            (trip_id,),
        )
        if pending_activities:
            show_table(
                [
                    {
                        "Destination": row["location_name"],
                        "Activity": row["activity_name"],
                        "Date": str(row["activity_date"] or "Not set"),
                        "Start": str(row["start_time"] or "Not set"),
                        "End": str(row["end_time"] or "Not set"),
                        "Notes": row["notes"] or "",
                    }
                    for row in pending_activities
                ]
            )
        else:
            st.success("There are no pending activities for this trip.")

    # BOOKINGS AND CONTRIBUTIONS
    with logistics_tab:
        section_heading(
            "Accommodation summary",
            "Review accommodation records and booking statuses.",
        )
        stays = fetch_all(
            """
            SELECT name, address, check_in_date, check_out_date,
                   booking_status, booking_reference, cost
            FROM accommodation
            WHERE trip_id = %s
            ORDER BY check_in_date, accommodation_id
            """,
            (trip_id,),
        )
        if stays:
            stays_df = pd.DataFrame(
                [
                    {
                        "Accommodation": row["name"],
                        "Address": row["address"] or "",
                        "Check-in": str(row["check_in_date"] or ""),
                        "Check-out": str(row["check_out_date"] or ""),
                        "Status": row["booking_status"],
                        "Reference": row["booking_reference"] or "",
                        "Cost": float(row["cost"] or 0),
                    }
                    for row in stays
                ]
            )
            show_table(stays_df)
            st.download_button(
                "Download accommodation report (CSV)",
                data=stays_df.to_csv(index=False).encode("utf-8"),
                file_name=f"trip_{trip_id}_accommodation.csv",
                mime="text/csv",
            )
        else:
            st.info("No accommodation records are available.")

        st.markdown("---")
        section_heading(
            "Transportation schedule",
            "Review the trip's recorded transport segments.",
        )
        transport = fetch_all(
            """
            SELECT type, provider, departure_date, arrival_date,
                   from_location, to_location, booking_reference, cost
            FROM transportation
            WHERE trip_id = %s
            ORDER BY departure_date, transportation_id
            """,
            (trip_id,),
        )
        if transport:
            transport_df = pd.DataFrame(
                [
                    {
                        "Type": row["type"],
                        "Provider": row["provider"] or "",
                        "From": row["from_location"] or "",
                        "To": row["to_location"] or "",
                        "Departure": str(row["departure_date"] or ""),
                        "Arrival": str(row["arrival_date"] or ""),
                        "Reference": row["booking_reference"] or "",
                        "Cost": float(row["cost"] or 0),
                    }
                    for row in transport
                ]
            )
            show_table(transport_df)
            st.download_button(
                "Download transportation report (CSV)",
                data=transport_df.to_csv(index=False).encode("utf-8"),
                file_name=f"trip_{trip_id}_transportation.csv",
                mime="text/csv",
            )
        else:
            st.info("No transportation records are available.")

        st.markdown("---")
        section_heading(
            "Member contributions",
            "Track money recorded as contributed toward the trip.",
        )
        contributions = fetch_all(
            """
            SELECT u.full_name AS contributor,
                   COUNT(c.contribution_id) AS contribution_count,
                   COALESCE(SUM(c.amount), 0) AS total_contributed
            FROM contribution c
            INNER JOIN users u ON u.user_id = c.user_id
            WHERE c.trip_id = %s
            GROUP BY u.user_id, u.full_name
            ORDER BY total_contributed DESC
            """,
            (trip_id,),
        )
        if contributions:
            contribution_df = pd.DataFrame(
                [
                    {
                        "Contributor": row["contributor"],
                        "Contribution records": int(row["contribution_count"] or 0),
                        "Total contributed": float(row["total_contributed"] or 0),
                    }
                    for row in contributions
                ]
            )
            show_table(contribution_df)
            st.download_button(
                "Download contributions report (CSV)",
                data=contribution_df.to_csv(index=False).encode("utf-8"),
                file_name=f"trip_{trip_id}_contributions.csv",
                mime="text/csv",
            )
            total_contributions = sum(
                float(row["total_contributed"] or 0)
                for row in contributions
            )
            st.metric(
                "Total recorded contributions",
                money(total_contributions, currency),
            )
        else:
            st.info("No contributions are recorded for this trip.")
