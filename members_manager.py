from datetime import date
from decimal import Decimal

import pandas as pd
import streamlit as st

from db import fetch_all, transaction
from trip_manager import get_trips, get_users
from ui import metric_card, render_hero, section_heading


def money(amount, currency="INR"):
    amount = Decimal(str(amount or 0))
    formatted = f"{amount:,.2f}".rstrip("0").rstrip(".")

    if currency == "INR":
        return f"₹{formatted}"
    return f"{currency} {formatted}"


def render_members_page():
    render_hero(
        "YOUR TRAVEL GROUP",
        "Good trips are built together.",
        (
            "Manage your travel group, see who's contributing, "
            "and keep track of the money set aside for the journey."
        ),
    )

    trips = get_trips()
    if not trips:
        st.info("Create a trip in My Trips to manage its members.")
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
        "Choose a trip",
        labels,
        index=default_index,
        key="members_trip_selector",
    )
    trip_id = trip_options[selected_label]
    st.session_state["selected_trip_id"] = trip_id

    trip_rows = fetch_all(
        """
        SELECT trip_id, trip_name, planned_budget, currency, start_date, end_date
        FROM trips
        WHERE trip_id = %s
        """,
        (trip_id,),
    )
    if not trip_rows:
        st.error("The selected trip could not be found.")
        return
    trip = trip_rows[0]
    currency = trip["currency"] or "INR"

    members = fetch_all(
        """
        SELECT
            u.user_id,
            u.full_name,
            u.email,
            u.phone,
            tm.role,
            tm.joined_at,
            COALESCE(c.total_contributed, 0) AS total_contributed
        FROM trip_member tm
        INNER JOIN users u ON u.user_id = tm.user_id
        LEFT JOIN (
            SELECT trip_id, user_id, SUM(amount) AS total_contributed
            FROM contribution
            GROUP BY trip_id, user_id
        ) c ON c.trip_id = tm.trip_id AND c.user_id = tm.user_id
        WHERE tm.trip_id = %s
        ORDER BY CASE tm.role WHEN 'ORGANIZER' THEN 0 ELSE 1 END, u.full_name
        """,
        (trip_id,),
    )

    contributions = fetch_all(
        """
        SELECT
            c.contribution_id,
            c.contribution_date,
            c.amount,
            c.description,
            u.full_name AS contributor
        FROM contribution c
        INNER JOIN users u ON u.user_id = c.user_id
        WHERE c.trip_id = %s
        ORDER BY c.contribution_date DESC, c.contribution_id DESC
        """,
        (trip_id,),
    )

    total_contributed = sum(
        (Decimal(str(item["amount"] or 0)) for item in contributions),
        Decimal("0.00"),
    )
    contributors_count = sum(
        1 for member in members
        if Decimal(str(member["total_contributed"] or 0)) > 0
    )

    section_heading(
        trip["trip_name"],
        f'{trip["start_date"]} – {trip["end_date"]}',
        eyebrow="GROUP OVERVIEW",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("Group members", len(members), icon="👥", note="People registered for this trip")
    with col2:
        metric_card("Total contributions", money(total_contributed, currency), icon="💰", note="Money recorded as contributed")
    with col3:
        metric_card("Contributors", contributors_count, icon="🤝", note="Members with recorded contributions")

    st.markdown("---")
    section_heading(
        "Meet the group",
        "View member details, roles and individual contributions.",
        eyebrow="TRIP MEMBERS",
    )

    if members:
        member_rows = [
            {
                "Name": member["full_name"],
                "Email": member["email"],
                "Phone": member.get("phone") or "Not provided",
                "Role": member["role"],
                "Joined": str(member["joined_at"]),
                "Contributed": money(member["total_contributed"], currency),
            }
            for member in members
        ]
        # Do not pass `theme=` here: st.dataframe() does not accept that argument.
        st.dataframe(member_rows, use_container_width=True, hide_index=True)
    else:
        st.info("There are no members in this trip yet.")

    st.markdown("---")
    section_heading(
        "Grow your travel group",
        "Add an existing registered user to the selected trip.",
        eyebrow="ADD MEMBERS",
    )

    all_users = get_users()
    existing_ids = {int(member["user_id"]) for member in members}
    available_users = [user for user in all_users if int(user["user_id"]) not in existing_ids]

    with st.expander("＋ Add a member", expanded=False):
        if not available_users:
            st.info("All registered users are already members of this trip.")
        else:
            user_options = {
                f'{user["full_name"]} ({user["email"]})': int(user["user_id"])
                for user in available_users
            }
            with st.form("add_member_from_members_page"):
                chosen_user = st.selectbox("Select a registered user", list(user_options.keys()))
                submitted = st.form_submit_button(
                    "Add to trip", type="primary", use_container_width=True
                )

            if submitted:
                try:
                    with transaction() as connection:
                        cursor = connection.cursor()
                        try:
                            cursor.execute(
                                """
                                INSERT INTO trip_member (trip_id, user_id, role)
                                VALUES (%s, %s, 'MEMBER')
                                """,
                                (trip_id, user_options[chosen_user]),
                            )
                        finally:
                            cursor.close()
                except Exception as exc:
                    st.error("Unable to add this member.")
                    with st.expander("Technical error details"):
                        st.code(str(exc))
                else:
                    st.session_state["member_added_notice"] = chosen_user
                    st.rerun()

    added_member = st.session_state.pop("member_added_notice", None)
    if added_member:
        st.success(f"{added_member} has been added to the trip.")

    st.markdown("---")
    section_heading(
        "Record a contribution",
        "Record money a member has contributed toward the trip. This is separate from expenses they pay.",
        eyebrow="TRIP FUND",
    )

    if not members:
        st.info("Add a member before recording a contribution.")
    else:
        member_options = {
            f'{member["full_name"]} ({member["email"]})': int(member["user_id"])
            for member in members
        }
        with st.form("add_contribution_form", clear_on_submit=True):
            contributor_label = st.selectbox("Who contributed?", list(member_options.keys()))
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input(
                    "Contribution amount", min_value=0.01, value=1000.00,
                    step=500.00, format="%.2f",
                )
            with col2:
                contribution_date = st.date_input("Contribution date", value=date.today())
            description = st.text_input(
                "Description", placeholder="e.g. Initial trip fund contribution"
            )
            submitted = st.form_submit_button(
                "Save contribution", type="primary", use_container_width=True
            )

        if submitted:
            try:
                with transaction() as connection:
                    cursor = connection.cursor()
                    try:
                        cursor.execute(
                            """
                            INSERT INTO contribution (
                                trip_id, user_id, amount, contribution_date, description
                            )
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (
                                trip_id,
                                member_options[contributor_label],
                                Decimal(str(amount)).quantize(Decimal("0.01")),
                                contribution_date,
                                description.strip() or None,
                            ),
                        )
                    finally:
                        cursor.close()
            except Exception as exc:
                st.error("Unable to save the contribution.")
                with st.expander("Technical error details"):
                    st.code(str(exc))
            else:
                st.success("Contribution recorded successfully!")
                st.rerun()

    st.markdown("---")
    section_heading(
        "Contribution history",
        "See every recorded contribution for this trip.",
        eyebrow="FUND ACTIVITY",
    )

    if contributions:
        history_rows = [
            {
                "Date": str(item["contribution_date"]),
                "Contributor": item["contributor"],
                "Amount": money(item["amount"], currency),
                "Description": item["description"] or "—",
            }
            for item in contributions
        ]
        # Do not pass `theme=` here: st.dataframe() does not accept that argument.
        st.dataframe(history_rows, use_container_width=True, hide_index=True)

        csv_data = pd.DataFrame(history_rows).to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download contribution history (CSV)",
            data=csv_data,
            file_name=f"trip_{trip_id}_contributions.csv",
            mime="text/csv",
        )
    else:
        st.info("No contributions have been recorded for this trip yet.")
