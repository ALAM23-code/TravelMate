
from datetime import date, time

import streamlit as st

from db import fetch_all, fetch_one, transaction
from trip_manager import get_trips
from ui import metric_card, render_hero, section_heading


def format_date(value):
    if not value:
        return "Not scheduled"

    if isinstance(value, date):
        return value.strftime("%d %b %Y")

    return str(value)


def render_itinerary_page():
    render_hero(
        "PLAN YOUR JOURNEY",
        "Every day deserves a plan.",
        "Organize destinations, schedule activities, "
        "and keep your entire group on the same page.",
    )

    trips = get_trips()

    if not trips:
        st.info("Create a trip in My Trips before planning an itinerary.")
        return

    trip_options = {
        f'{trip["trip_name"]} · Trip #{trip["trip_id"]}':
        int(trip["trip_id"])
        for trip in trips
    }

    labels = list(trip_options.keys())
    previous_id = st.session_state.get("selected_trip_id")

    default_index = next(
        (
            i for i, label in enumerate(labels)
            if trip_options[label] == previous_id
        ),
        0,
    )

    selected_label = st.selectbox(
        "Choose a trip to plan",
        labels,
        index=default_index,
        key="itinerary_trip_selector",
    )

    trip_id = trip_options[selected_label]
    st.session_state["selected_trip_id"] = trip_id

    trip = fetch_one(
        """
        SELECT trip_id, trip_name, start_date, end_date, status
        FROM trips
        WHERE trip_id = %s
        """,
        (trip_id,),
    )

    if not trip:
        st.error("The selected trip could not be found.")
        return

    destinations = fetch_all(
        """
        SELECT
            destination_id,
            location_name,
            location_detail,
            visit_date,
            description,
            notes
        FROM destinations
        WHERE trip_id = %s
        ORDER BY visit_date, destination_id
        """,
        (trip_id,),
    )

    activities = fetch_all(
        """
        SELECT
            a.activity_id,
            a.activity_name,
            a.description,
            a.activity_date,
            a.start_time,
            a.end_time,
            a.is_completed,
            a.notes,
            d.destination_id,
            d.location_name
        FROM activities a
        INNER JOIN destinations d
            ON a.destination_id = d.destination_id
        WHERE d.trip_id = %s
        ORDER BY a.activity_date, a.start_time, a.activity_id
        """,
        (trip_id,),
    )

    completed_count = sum(
        bool(activity["is_completed"])
        for activity in activities
    )

    st.markdown("")
    section_heading(
        trip["trip_name"],
        (
            f'{format_date(trip["start_date"])} – '
            f'{format_date(trip["end_date"])}'
        ),
        eyebrow="YOUR SELECTED TRIP",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card(
            "Destinations",
            len(destinations),
            icon="📍",
            note="Places on your itinerary",
        )

    with col2:
        metric_card(
            "Activities",
            len(activities),
            icon="🗓️",
            note="Scheduled experiences",
        )

    with col3:
        metric_card(
            "Completed",
            f"{completed_count}/{len(activities)}",
            icon="✅",
            note="Activities marked complete",
        )

    st.markdown("---")

    section_heading(
        "Build your itinerary",
        "Add the places you'll visit and then schedule activities at each place.",
        eyebrow="ITINERARY PLANNER",
    )

    destination_tab, activity_tab = st.tabs(
        ["📍 Destinations", "🗓️ Activities"]
    )

    with destination_tab:
        with st.expander(
            "＋ Add a destination",
            expanded=not destinations,
        ):
            with st.form("add_destination_form", clear_on_submit=True):
                location_name = st.text_input(
                    "Destination name *",
                    placeholder="e.g. Solang Valley",
                )

                location_detail = st.text_input(
                    "Address, city or region",
                    placeholder="e.g. Manali, Himachal Pradesh",
                )

                visit_date = st.date_input(
                    "Planned visit date",
                    value=trip["start_date"],
                    min_value=trip["start_date"],
                    max_value=trip["end_date"],
                )

                description = st.text_area(
                    "Description",
                    placeholder="What do you want to see here?",
                    key=f"destination_description_{trip_id}",
                )

                notes = st.text_area(
                    "Travel notes",
                    placeholder="Transport tips, entry requirements, reminders...",
                )

                submitted = st.form_submit_button(
                    "Save destination",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if not location_name.strip():
                    st.error("Enter a destination name.")

                elif not (
                    trip["start_date"]
                    <= visit_date
                    <= trip["end_date"]
                ):
                    st.error(
                        "The visit date must fall within the trip dates."
                    )

                else:
                    cursor = None

                    try:
                        with transaction() as connection:
                            cursor = connection.cursor()

                            cursor.execute(
                                """
                                INSERT INTO destinations (
                                    trip_id,
                                    location_name,
                                    location_detail,
                                    visit_date,
                                    description,
                                    notes
                                )
                                VALUES (%s, %s, %s, %s, %s, %s)
                                """,
                                (
                                    trip_id,
                                    location_name.strip(),
                                    location_detail.strip() or None,
                                    visit_date,
                                    description.strip() or None,
                                    notes.strip() or None,
                                ),
                            )

                    except Exception as exc:
                        st.error("Unable to save the destination.")
                        st.code(str(exc))

                    else:
                        st.success("Destination added successfully!")
                        st.rerun()

                    finally:
                        if cursor is not None:
                            cursor.close()

        section_heading(
            "Your destinations",
            "Places are arranged by their planned visit date.",
        )

        if not destinations:
            st.info(
                "No destinations yet. Add the first place for your trip."
            )

        else:
            for destination in destinations:
                visit_day = format_date(destination["visit_date"])

                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(
                            f'### 📍 {destination["location_name"]}'
                        )

                        if destination["location_detail"]:
                            st.caption(
                                destination["location_detail"]
                            )

                    with col2:
                        st.markdown(f"**{visit_day}**")

                    if destination["description"]:
                        st.write(destination["description"])

                    if destination["notes"]:
                        st.info(destination["notes"])

    with activity_tab:
        if not destinations:
            st.info(
                "Add a destination first. Activities must be "
                "associated with a destination."
            )

        else:
            destination_options = {
                (
                    f'{destination["location_name"]} '
                    f'(ID {destination["destination_id"]})'
                ): int(destination["destination_id"])
                for destination in destinations
            }

            with st.expander(
                "＋ Schedule an activity",
                expanded=not activities,
            ):
                with st.form(
                    "add_activity_form",
                    clear_on_submit=True,
                ):
                    chosen_destination = st.selectbox(
                        "Destination *",
                        list(destination_options.keys()),
                    )

                    activity_name = st.text_input(
                        "Activity name *",
                        placeholder="e.g. Visit Hadimba Temple",
                    )

                    activity_description = st.text_area(
                        "Activity description",
                        placeholder="What will the group do?",
                        key=f"activity_description_{trip_id}",
                    )

                    activity_date = st.date_input(
                        "Activity date",
                        value=trip["start_date"],
                        min_value=trip["start_date"],
                        max_value=trip["end_date"],
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        start_time = st.time_input(
                            "Start time",
                            value=time(9, 0),
                        )

                    with col2:
                        end_time = st.time_input(
                            "End time",
                            value=time(10, 0),
                        )

                    activity_notes = st.text_area(
                        "Notes",
                        placeholder="Tickets, reminders or other details...",
                    )

                    activity_submitted = st.form_submit_button(
                        "Save activity",
                        type="primary",
                        use_container_width=True,
                    )

                if activity_submitted:
                    if not activity_name.strip():
                        st.error("Enter an activity name.")

                    elif end_time < start_time:
                        st.error(
                            "The activity end time must not be "
                            "earlier than its start time."
                        )

                    else:
                        cursor = None

                        try:
                            with transaction() as connection:
                                cursor = connection.cursor()

                                cursor.execute(
                                    """
                                    INSERT INTO activities (
                                        destination_id,
                                        activity_name,
                                        description,
                                        activity_date,
                                        start_time,
                                        end_time,
                                        notes
                                    )
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    """,
                                    (
                                        destination_options[
                                            chosen_destination
                                        ],
                                        activity_name.strip(),
                                        activity_description.strip() or None,
                                        activity_date,
                                        start_time,
                                        end_time,
                                        activity_notes.strip() or None,
                                    ),
                                )

                        except Exception as exc:
                            st.error("Unable to save the activity.")
                            st.code(str(exc))

                        else:
                            st.success("Activity scheduled successfully!")
                            st.rerun()

                        finally:
                            if cursor is not None:
                                cursor.close()

            st.markdown("---")

            section_heading(
                "Activity schedule",
                "Review what is planned and track completion.",
            )

            if not activities:
                st.info("No activities scheduled yet.")

            else:
                for activity in activities:
                    is_completed = bool(activity["is_completed"])

                    with st.container(border=True):
                        col1, col2 = st.columns([4, 1])

                        with col1:
                            st.markdown(
                                f'### {"✅" if is_completed else "🕒"} '
                                f'{activity["activity_name"]}'
                            )

                            st.caption(
                                f'{activity["location_name"]} · '
                                f'{format_date(activity["activity_date"])}'
                            )

                            start = activity["start_time"]
                            end = activity["end_time"]

                            if start and end:
                                st.write(
                                    f"**Time:** {start} – {end}"
                                )

                            if activity["description"]:
                                st.write(activity["description"])

                            if activity["notes"]:
                                st.caption(
                                    f'Note: {activity["notes"]}'
                                )

                        with col2:
                            st.markdown(
                                "**Completed**"
                                if is_completed
                                else "**Planned**"
                            )

                st.markdown("---")

                section_heading(
                    "Update activity status",
                    "Mark an activity complete when the group finishes it.",
                )

                activity_options = {
                    (
                        f'{activity["activity_name"]} — '
                        f'{activity["location_name"]} '
                        f'(ID {activity["activity_id"]})'
                    ): activity
                    for activity in activities
                }

                chosen_activity_label = st.selectbox(
                    "Choose an activity",
                    list(activity_options.keys()),
                    key="status_activity_selector",
                )

                chosen_activity = activity_options[
                    chosen_activity_label
                ]

                new_status = st.radio(
                    "New status",
                    ["Planned", "Completed"],
                    index=(
                        1 if bool(chosen_activity["is_completed"]) else 0
                    ),
                    horizontal=True,
                    key="activity_new_status",
                )

                if st.button(
                    "Update activity status",
                    type="primary",
                    use_container_width=True,
                ):
                    completed_value = (
                        1 if new_status == "Completed" else 0
                    )

                    try:
                        with transaction() as connection:
                            cursor = connection.cursor()

                            try:
                                cursor.execute(
                                    """
                                    UPDATE activities AS a
                                    INNER JOIN destinations AS d
                                        ON d.destination_id = a.destination_id
                                    SET
                                        a.is_completed = %s,
                                        a.completed_at = CASE
                                            WHEN %s = 1
                                            THEN CURRENT_TIMESTAMP
                                            ELSE NULL
                                        END
                                    WHERE
                                        a.activity_id = %s
                                        AND d.trip_id = %s
                                    """,
                                    (
                                        completed_value,
                                        completed_value,
                                        int(chosen_activity["activity_id"]),
                                        trip_id,
                                    ),
                                )

                                if cursor.rowcount == 0:
                                    current_record = fetch_one(
                                        """
                                        SELECT is_completed
                                        FROM activities
                                        WHERE activity_id = %s
                                        """,
                                        (
                                            int(
                                                chosen_activity["activity_id"]
                                            ),
                                        ),
                                    )

                                    if not current_record:
                                        raise ValueError(
                                            "The selected activity "
                                            "no longer exists."
                                        )

                            finally:
                                cursor.close()

                    except Exception as exc:
                        st.error("Unable to update activity status.")
                        st.code(str(exc))

                    else:
                        st.success("Activity status updated.")
                        st.rerun()
