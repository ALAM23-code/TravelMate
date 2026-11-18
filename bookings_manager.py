
from datetime import datetime, time
from decimal import Decimal

import streamlit as st

from db import fetch_all, fetch_one, transaction
from trip_manager import get_trips
from ui import metric_card, render_hero, section_heading


def money(amount, currency="INR"):
    amount = Decimal(str(amount or 0))
    formatted = f"{amount:,.2f}".rstrip("0").rstrip(".")

    if currency == "INR":
        return f"₹{formatted}"

    return f"{currency} {formatted}"


def render_bookings_page():
    render_hero(
        "TRAVEL LOGISTICS",
        "Every booking, in one place.",
        (
            "Organize your stays, manage transport schedules, "
            "and keep important booking references accessible."
        ),
    )

    trips = get_trips()

    if not trips:
        st.info("Create a trip in My Trips before adding bookings.")
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
            index
            for index, label in enumerate(labels)
            if trip_options[label] == previous_id
        ),
        0,
    )

    selected_label = st.selectbox(
        "Choose a trip",
        labels,
        index=default_index,
        key="bookings_trip_selector",
    )

    trip_id = trip_options[selected_label]
    st.session_state["selected_trip_id"] = trip_id

    trip = fetch_one(
        """
        SELECT trip_id, trip_name, start_date, end_date, currency
        FROM trips
        WHERE trip_id = %s
        """,
        (trip_id,),
    )

    if not trip:
        st.error("The selected trip could not be found.")
        return

    currency = trip["currency"]

    accommodations = fetch_all(
        """
        SELECT
            accommodation_id,
            name,
            address,
            check_in_date,
            check_out_date,
            booking_reference,
            cost,
            booking_status,
            notes
        FROM accommodation
        WHERE trip_id = %s
        ORDER BY check_in_date, accommodation_id
        """,
        (trip_id,),
    )

    transport_records = fetch_all(
        """
        SELECT
            transportation_id,
            type,
            provider,
            departure_date,
            arrival_date,
            from_location,
            to_location,
            cost,
            booking_reference,
            notes
        FROM transportation
        WHERE trip_id = %s
        ORDER BY departure_date, transportation_id
        """,
        (trip_id,),
    )

    accommodation_cost = sum(
        (Decimal(str(item["cost"] or 0)) for item in accommodations),
        Decimal("0.00"),
    )

    transport_cost = sum(
        (Decimal(str(item["cost"] or 0)) for item in transport_records),
        Decimal("0.00"),
    )

    section_heading(
        trip["trip_name"],
        "All booking information for your selected trip.",
        eyebrow="BOOKING OVERVIEW",
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            "Accommodation records",
            len(accommodations),
            icon="🏨",
        )

    with col2:
        metric_card(
            "Transport records",
            len(transport_records),
            icon="🚆",
        )

    with col3:
        metric_card(
            "Accommodation cost",
            money(accommodation_cost, currency),
            icon="🛏️",
        )

    with col4:
        metric_card(
            "Transport cost",
            money(transport_cost, currency),
            icon="🚗",
        )

    accommodation_tab, transport_tab = st.tabs(
        ["🏨 Accommodation", "🚆 Transportation"]
    )

    # --------------------------------------------------
    # ACCOMMODATION
    # --------------------------------------------------

    with accommodation_tab:
        section_heading(
            "Where the group stays",
            "Add accommodation details, dates and booking references.",
            eyebrow="ACCOMMODATION",
        )

        with st.expander("＋ Add accommodation", expanded=False):
            with st.form(
                "add_accommodation_form",
                clear_on_submit=True,
            ):
                name = st.text_input(
                    "Accommodation name *",
                    placeholder="e.g. Mountain View Hotel",
                )

                address = st.text_input(
                    "Address",
                    placeholder="City, area or full address",
                )

                col1, col2 = st.columns(2)

                with col1:
                    check_in = st.date_input(
                        "Check-in date",
                        value=trip["start_date"],
                    )

                with col2:
                    check_out = st.date_input(
                        "Check-out date",
                        value=trip["end_date"],
                    )

                col3, col4 = st.columns(2)

                with col3:
                    cost = st.number_input(
                        "Total accommodation cost",
                        min_value=0.0,
                        value=0.0,
                        step=500.0,
                        format="%.2f",
                    )

                with col4:
                    booking_status = st.selectbox(
                        "Booking status",
                        ["PLANNED", "BOOKED", "CANCELLED", "COMPLETED"],
                    )

                booking_reference = st.text_input(
                    "Booking reference",
                    placeholder="e.g. HOTEL-2026-001",
                )

                notes = st.text_area(
                    "Accommodation notes",
                    placeholder="Room details, check-in instructions...",
                    key=f"accommodation_notes_{trip_id}",
                )

                submitted = st.form_submit_button(
                    "Save accommodation",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if not name.strip():
                    st.error("Please enter an accommodation name.")

                elif check_out < check_in:
                    st.error(
                        "Check-out cannot be earlier than check-in."
                    )

                else:
                    try:
                        with transaction() as connection:
                            cursor = connection.cursor()

                            try:
                                cursor.execute(
                                    """
                                    INSERT INTO accommodation (
                                        trip_id,
                                        name,
                                        address,
                                        check_in_date,
                                        check_out_date,
                                        booking_reference,
                                        cost,
                                        booking_status,
                                        notes
                                    )
                                    VALUES (
                                        %s, %s, %s, %s, %s,
                                        %s, %s, %s, %s
                                    )
                                    """,
                                    (
                                        trip_id,
                                        name.strip(),
                                        address.strip() or None,
                                        check_in,
                                        check_out,
                                        booking_reference.strip() or None,
                                        cost,
                                        booking_status,
                                        notes.strip() or None,
                                    ),
                                )
                            finally:
                                cursor.close()

                    except Exception as exc:
                        st.error("Unable to save accommodation.")
                        st.code(str(exc))

                    else:
                        st.success("Accommodation saved successfully!")
                        st.rerun()

        section_heading(
            "Accommodation records",
            "Review the stays planned or booked for this trip.",
        )

        if not accommodations:
            st.info(
                "No accommodation records yet. "
                "Use the form above to add the first stay."
            )

        else:
            for item in accommodations:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f'### 🏨 {item["name"]}')

                        if item["address"]:
                            st.caption(item["address"])

                        st.write(
                            f'**Check-in:** {item["check_in_date"]}'
                        )
                        st.write(
                            f'**Check-out:** {item["check_out_date"]}'
                        )

                        if item["booking_reference"]:
                            st.write(
                                "**Booking reference:** "
                                f'{item["booking_reference"]}'
                            )

                        if item["notes"]:
                            st.write(item["notes"])

                    with col2:
                        st.markdown(
                            f'**{money(item["cost"], currency)}**'
                        )
                        st.caption(item["booking_status"])

    # --------------------------------------------------
    # TRANSPORTATION
    # --------------------------------------------------

    with transport_tab:
        section_heading(
            "Getting around",
            "Record flights, trains, buses, transfers and other transport.",
            eyebrow="TRANSPORTATION",
        )

        with st.expander("＋ Add transportation", expanded=False):
            with st.form(
                "add_transportation_form",
                clear_on_submit=True,
            ):
                transport_type = st.selectbox(
                    "Transportation type",
                    [
                        "Flight",
                        "Train",
                        "Bus / Coach",
                        "Car / SUV",
                        "Taxi",
                        "Ferry",
                        "Other",
                    ],
                )

                provider = st.text_input(
                    "Provider or operator",
                    placeholder="e.g. Indian Railways",
                )

                col1, col2 = st.columns(2)

                with col1:
                    departure_date = st.date_input(
                        "Departure date",
                        value=trip["start_date"],
                    )

                    departure_time = st.time_input(
                        "Departure time",
                        value=time(9, 0),
                    )

                    from_location = st.text_input(
                        "From",
                        placeholder="Starting location",
                    )

                with col2:
                    arrival_date = st.date_input(
                        "Arrival date",
                        value=trip["end_date"],
                    )

                    arrival_time = st.time_input(
                        "Arrival time",
                        value=time(10, 0),
                    )

                    to_location = st.text_input(
                        "To",
                        placeholder="Destination",
                    )

                col3, col4 = st.columns(2)

                with col3:
                    cost = st.number_input(
                        "Recorded transportation cost",
                        min_value=0.0,
                        value=0.0,
                        step=500.0,
                        format="%.2f",
                    )

                with col4:
                    booking_reference = st.text_input(
                        "Booking reference",
                        placeholder="Ticket or booking number",
                    )

                notes = st.text_area(
                    "Transportation notes",
                    placeholder="Platform, departure terminal, reminders...",
                    key=f"transport_notes_{trip_id}",
                )

                submitted = st.form_submit_button(
                    "Save transportation",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                departure = datetime.combine(
                    departure_date,
                    departure_time,
                )

                arrival = datetime.combine(
                    arrival_date,
                    arrival_time,
                )

                if arrival < departure:
                    st.error(
                        "Arrival cannot be earlier than departure."
                    )

                else:
                    try:
                        with transaction() as connection:
                            cursor = connection.cursor()

                            try:
                                cursor.execute(
                                    """
                                    INSERT INTO transportation (
                                        trip_id,
                                        type,
                                        provider,
                                        departure_date,
                                        arrival_date,
                                        from_location,
                                        to_location,
                                        cost,
                                        booking_reference,
                                        notes
                                    )
                                    VALUES (
                                        %s, %s, %s, %s, %s,
                                        %s, %s, %s, %s, %s
                                    )
                                    """,
                                    (
                                        trip_id,
                                        transport_type,
                                        provider.strip() or None,
                                        departure,
                                        arrival,
                                        from_location.strip() or None,
                                        to_location.strip() or None,
                                        cost,
                                        booking_reference.strip() or None,
                                        notes.strip() or None,
                                    ),
                                )
                            finally:
                                cursor.close()

                    except Exception as exc:
                        st.error("Unable to save transportation.")
                        st.code(str(exc))

                    else:
                        st.success("Transportation saved successfully!")
                        st.rerun()

        section_heading(
            "Transportation records",
            "Review departure times, arrival times and ticket details.",
        )

        if not transport_records:
            st.info(
                "No transportation records yet. "
                "Add your first journey using the form above."
            )

        else:
            for item in transport_records:
                with st.container(border=True):
                    st.markdown(f'### 🚆 {item["type"]}')

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**DEPARTURE**")
                        st.write(
                            item["from_location"] or "Not specified"
                        )
                        st.write(
                            str(item["departure_date"] or "Not scheduled")
                        )

                    with col2:
                        st.markdown("**ARRIVAL**")
                        st.write(
                            item["to_location"] or "Not specified"
                        )
                        st.write(
                            str(item["arrival_date"] or "Not scheduled")
                        )

                    if item["provider"]:
                        st.caption(f'Provider: {item["provider"]}')

                    col3, col4 = st.columns(2)

                    with col3:
                        st.write(
                            f'**Cost:** {money(item["cost"], currency)}'
                        )

                    with col4:
                        if item["booking_reference"]:
                            st.write(
                                "**Reference:** "
                                f'{item["booking_reference"]}'
                            )

                    if item["notes"]:
                        st.info(item["notes"])
