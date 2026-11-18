from datetime import date

import streamlit as st

from db import fetch_all, transaction
from ui import metric_card, render_hero, section_heading


# --------------------------------------------------
# FORMATTING HELPERS
# --------------------------------------------------

def money(amount, currency="INR"):
    amount = float(amount or 0)
    formatted = f"{amount:,.2f}".rstrip("0").rstrip(".")
    return f"₹{formatted}" if currency == "INR" else f"{currency} {formatted}"


def format_date(value):
    if not value:
        return "Not set"
    if isinstance(value, date):
        return value.strftime("%d %b %Y")
    return str(value)


# --------------------------------------------------
# DATA ACCESS
# --------------------------------------------------

def get_trips():
    """Return trips with member counts and recorded expense totals."""
    return fetch_all(
        """
        SELECT
            t.trip_id,
            t.trip_name,
            t.description,
            t.start_date,
            t.end_date,
            t.planned_budget,
            t.currency,
            t.status,
            u.full_name AS organizer_name,
            (
                SELECT COUNT(*)
                FROM trip_member tm
                WHERE tm.trip_id = t.trip_id
            ) AS member_count,
            (
                SELECT COALESCE(SUM(e.amount), 0)
                FROM expense e
                WHERE e.trip_id = t.trip_id
            ) AS actual_expenses
        FROM trips t
        INNER JOIN users u ON u.user_id = t.organizer_id
        ORDER BY
            CASE t.status
                WHEN 'ONGOING' THEN 1
                WHEN 'PLANNED' THEN 2
                WHEN 'COMPLETED' THEN 3
                WHEN 'CANCELLED' THEN 4
                ELSE 5
            END,
            t.start_date ASC
        """
    )


def get_users():
    """Return registered users that can be assigned to trips."""
    return fetch_all(
        """
        SELECT user_id, full_name, email, phone
        FROM users
        ORDER BY full_name
        """
    )


# --------------------------------------------------
# CREATE TRIP
# --------------------------------------------------

def create_trip_form(users):
    with st.expander("＋ Create a new trip", expanded=False):
        if not users:
            st.warning(
                "No registered users exist yet. Create a user record before creating a trip."
            )
            return

        user_options = {
            f'{user["full_name"]} ({user["email"]})': int(user["user_id"])
            for user in users
        }

        with st.form("create_trip_form", clear_on_submit=True):
            st.markdown("### Trip information")
            st.caption("Enter the details of your group's journey.")

            trip_name = st.text_input(
                "Trip name *",
                placeholder="e.g. Manali Adventure",
            )
            description = st.text_area(
                "Description",
                placeholder="Tell your group about this trip...",
                key="create_trip_description",
            )

            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start date", value=date.today())
            with col2:
                end_date = st.date_input("End date", value=date.today())

            col3, col4 = st.columns(2)
            with col3:
                budget = st.number_input(
                    "Planned budget",
                    min_value=0.0,
                    value=50000.0,
                    step=1000.0,
                    format="%.2f",
                )
            with col4:
                currency = st.selectbox("Currency", ["INR", "USD", "EUR", "GBP"])

            organizer_label = st.selectbox(
                "Trip organizer",
                options=list(user_options.keys()),
            )

            submitted = st.form_submit_button(
                "Create trip",
                type="primary",
                use_container_width=True,
            )

        if not submitted:
            return
        if not trip_name.strip():
            st.error("Please enter a trip name.")
            return
        if end_date < start_date:
            st.error("The end date cannot be earlier than the start date.")
            return

        cursor = None
        try:
            with transaction() as connection:
                cursor = connection.cursor()
                organizer_id = user_options[organizer_label]

                cursor.execute(
                    """
                    INSERT INTO trips (
                        trip_name, description, start_date, end_date,
                        planned_budget, currency, status, organizer_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, 'PLANNED', %s)
                    """,
                    (
                        trip_name.strip(),
                        description.strip() or None,
                        start_date,
                        end_date,
                        budget,
                        currency,
                        organizer_id,
                    ),
                )
                new_trip_id = cursor.lastrowid

                cursor.execute(
                    """
                    INSERT INTO trip_member (trip_id, user_id, role)
                    VALUES (%s, %s, 'ORGANIZER')
                    """,
                    (new_trip_id, organizer_id),
                )

        except Exception as exc:
            st.error("The trip could not be created.")
            with st.expander("Technical error details"):
                st.code(str(exc))
        else:
            st.session_state["selected_trip_id"] = int(new_trip_id)
            st.session_state["trip_created_notice"] = trip_name.strip()
            st.rerun()
        finally:
            if cursor is not None:
                cursor.close()


# --------------------------------------------------
# TRIP MANAGEMENT PAGE
# --------------------------------------------------

def render_trip_manager_page():
    created_trip = st.session_state.pop("trip_created_notice", None)
    deleted_trip = st.session_state.pop("trip_deleted_notice", None)
    added_member = st.session_state.pop("member_added_notice", None)

    if created_trip:
        st.success(f'Trip "{created_trip}" created successfully.')
    if deleted_trip:
        st.success(f'Trip "{deleted_trip}" and its associated records were deleted.')
    if added_member:
        st.success(f"{added_member} has been added to the trip.")

    render_hero(
        "TRIP MANAGEMENT",
        "Every journey starts with a plan.",
        "Create trips, organize your travel group, and keep all important details together.",
    )

    users = get_users()
    create_trip_form(users)
    trips = get_trips()

    section_heading(
        "Your trips",
        "Select a trip to see its details and manage its members.",
        eyebrow="MY TRIPS",
    )

    if not trips:
        st.info("No trips are available. Use 'Create a new trip' above to get started.")
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
        key="trip_manager_selector",
    )
    trip_id = trip_options[selected_label]
    st.session_state["selected_trip_id"] = trip_id

    trip = next(
        (item for item in trips if int(item["trip_id"]) == trip_id),
        None,
    )
    if not trip:
        st.error("The selected trip could not be found.")
        return

    # Trip overview
    section_heading(
        trip["trip_name"],
        trip.get("description") or "No description has been added.",
        eyebrow="TRIP OVERVIEW",
    )

    budget = float(trip["planned_budget"] or 0)
    expenses = float(trip["actual_expenses"] or 0)
    currency = trip["currency"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Planned budget", money(budget, currency), icon="💰")
    with col2:
        metric_card("Recorded spending", money(expenses, currency), icon="💳")
    with col3:
        metric_card(
            "Budget remaining",
            money(budget - expenses, currency),
            icon="📊",
            note="May be negative if over budget",
        )
    with col4:
        metric_card(
            "Group size",
            int(trip["member_count"]),
            icon="👥",
            note="Registered trip members",
        )

    col5, col6 = st.columns(2)
    with col5:
        st.markdown("**Trip dates**")
        st.write(f'{format_date(trip["start_date"])} – {format_date(trip["end_date"])}')
    with col6:
        st.markdown("**Organizer**")
        st.write(trip["organizer_name"])

    st.markdown("**Current status:**")
    st.write(trip["status"])

    # Members
    st.markdown("---")
    section_heading(
        "Travel group",
        "See who is part of this trip and add other registered users.",
        eyebrow="GROUP MEMBERS",
    )

    members = fetch_all(
        """
        SELECT u.user_id, u.full_name, u.email, tm.role, tm.joined_at
        FROM trip_member tm
        INNER JOIN users u ON u.user_id = tm.user_id
        WHERE tm.trip_id = %s
        ORDER BY
            CASE tm.role WHEN 'ORGANIZER' THEN 0 ELSE 1 END,
            u.full_name
        """,
        (trip_id,),
    )

    if members:
        # Streamlit's st.dataframe() does not accept a `theme` keyword.
        # Keep the dataframe compatible with supported Streamlit versions.
        st.dataframe(
            [
                {
                    "Name": member["full_name"],
                    "Email": member["email"],
                    "Role": member["role"],
                    "Joined": str(member["joined_at"]),
                }
                for member in members
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No members have been added to this trip.")

    existing_ids = {int(member["user_id"]) for member in members}
    available_users = [
        user for user in users if int(user["user_id"]) not in existing_ids
    ]

    with st.expander("＋ Add a member to this trip"):
        if not available_users:
            st.info("All registered users are already members of this trip.")
        else:
            available_options = {
                f'{user["full_name"]} ({user["email"]})': int(user["user_id"])
                for user in available_users
            }
            with st.form("add_trip_member_form"):
                selected_user_label = st.selectbox(
                    "Choose a registered user",
                    options=list(available_options.keys()),
                )
                add_submitted = st.form_submit_button(
                    "Add member",
                    type="primary",
                    use_container_width=True,
                )

            if add_submitted:
                cursor = None
                try:
                    with transaction() as connection:
                        cursor = connection.cursor()
                        cursor.execute(
                            """
                            INSERT INTO trip_member (trip_id, user_id, role)
                            VALUES (%s, %s, 'MEMBER')
                            """,
                            (trip_id, available_options[selected_user_label]),
                        )
                except Exception as exc:
                    st.error("Unable to add the member.")
                    with st.expander("Technical error details"):
                        st.code(str(exc))
                else:
                    st.session_state["member_added_notice"] = selected_user_label
                    st.rerun()
                finally:
                    if cursor is not None:
                        cursor.close()

    # Danger zone: delete trip
    st.markdown("---")
    section_heading(
        "Danger zone",
        "Permanently remove a trip that was created by mistake. This action cannot be undone.",
        eyebrow="TRIP MANAGEMENT",
    )

    with st.expander("🗑️ Delete this trip", expanded=False):
        st.error(
            "Deleting this trip can permanently remove its related memberships, "
            "destinations, activities, expenses, expense splits, accommodation, "
            "transportation, contributions, and trip photo records."
        )
        st.markdown(f'**Selected trip:** {trip["trip_name"]} (Trip #{trip_id})')

        with st.form(f"delete_trip_form_{trip_id}"):
            confirmation_name = st.text_input(
                "Type the exact trip name to confirm deletion",
                placeholder=trip["trip_name"],
                key=f"delete_trip_name_{trip_id}",
            )
            acknowledge = st.checkbox(
                "I understand that this deletion cannot be undone.",
                key=f"delete_trip_ack_{trip_id}",
            )
            delete_submitted = st.form_submit_button(
                "Permanently delete trip",
                type="primary",
                use_container_width=True,
            )

        if delete_submitted:
            if confirmation_name != trip["trip_name"]:
                st.error("The trip name does not match exactly. Nothing has been deleted.")
            elif not acknowledge:
                st.error("Please confirm that you understand the consequences of deleting this trip.")
            else:
                cursor = None
                try:
                    with transaction() as connection:
                        cursor = connection.cursor()
                        cursor.execute(
                            "DELETE FROM trips WHERE trip_id = %s",
                            (trip_id,),
                        )
                        if cursor.rowcount != 1:
                            raise ValueError(
                                "The selected trip was not deleted. It may no longer exist."
                            )
                except Exception as exc:
                    st.error("The trip could not be deleted. The transaction was rolled back if supported.")
                    with st.expander("Technical error details"):
                        st.code(str(exc))
                else:
                    st.session_state["trip_deleted_notice"] = trip["trip_name"]
                    st.session_state.pop("selected_trip_id", None)
                    st.rerun()
                finally:
                    if cursor is not None:
                        cursor.close()
