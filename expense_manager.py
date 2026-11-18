from decimal import Decimal, ROUND_HALF_UP

import plotly.express as px
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


def split_amount_equally(amount, member_ids):
    """Split an amount to the cent; allocate any remainder fairly."""
    amount = Decimal(str(amount)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    if not member_ids:
        raise ValueError("The trip has no members to split the expense.")

    total_cents = int(amount * 100)
    base_cents, remainder = divmod(total_cents, len(member_ids))

    allocations = []
    for index, member_id in enumerate(member_ids):
        cents = base_cents + (1 if index < remainder else 0)
        allocations.append((int(member_id), Decimal(cents) / Decimal("100")))

    return allocations


def _chart_template():
    """Return a Plotly template matching the selected app appearance."""
    return "plotly_dark" if st.session_state.get("theme_mode") == "Dark" else "plotly_white"


def _style_chart(fig):
    """Use a transparent chart background with readable theme-aware text."""
    dark_mode = st.session_state.get("theme_mode") == "Dark"
    text_color = "#E5E7EB" if dark_mode else "#172B4D"

    fig.update_layout(
        template=_chart_template(),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=text_color,
        margin=dict(t=24, b=20, l=10, r=10),
        legend_title_text="Category",
    )
    return fig


def render_expenses_page():
    render_hero(
        "GROUP FINANCES",
        "Every rupee, accounted for.",
        (
            "Record group expenses, share costs fairly, "
            "track individual spending and stay within your trip budget."
        ),
    )

    trips = get_trips()
    if not trips:
        st.info("Create a trip in My Trips before recording expenses.")
        return

    trip_options = {
        f'{trip["trip_name"]} · Trip #{trip["trip_id"]}': int(trip["trip_id"])
        for trip in trips
    }
    labels = list(trip_options.keys())
    previous_id = st.session_state.get("selected_trip_id")

    default_index = next(
        (index for index, label in enumerate(labels) if trip_options[label] == previous_id),
        0,
    )

    selected_label = st.selectbox(
        "Choose a trip",
        labels,
        index=default_index,
        key="expense_trip_selector",
    )

    trip_id = trip_options[selected_label]
    st.session_state["selected_trip_id"] = trip_id

    trip = fetch_one(
        """
        SELECT trip_id, trip_name, planned_budget, currency, status
        FROM trips
        WHERE trip_id = %s
        """,
        (trip_id,),
    )

    if not trip:
        st.error("The selected trip could not be found.")
        return

    members = fetch_all(
        """
        SELECT u.user_id, u.full_name, u.email
        FROM trip_member tm
        INNER JOIN users u ON u.user_id = tm.user_id
        WHERE tm.trip_id = %s
        ORDER BY u.full_name
        """,
        (trip_id,),
    )

    categories = fetch_all(
        """
        SELECT category_id, category_name
        FROM expense_category
        ORDER BY category_name
        """
    )

    expenses = fetch_all(
        """
        SELECT
            e.expense_id,
            e.expense_date,
            e.description,
            e.amount,
            e.expense_type,
            e.receipt_path,
            u.full_name AS paid_by,
            ec.category_name
        FROM expense e
        INNER JOIN users u ON u.user_id = e.paid_by
        INNER JOIN expense_category ec ON ec.category_id = e.category_id
        WHERE e.trip_id = %s
        ORDER BY e.expense_date DESC, e.expense_id DESC
        """,
        (trip_id,),
    )

    total_spent = sum(
        (Decimal(str(item["amount"])) for item in expenses),
        Decimal("0.00"),
    )
    shared_spending = sum(
        (
            Decimal(str(item["amount"]))
            for item in expenses
            if item["expense_type"] == "SHARED"
        ),
        Decimal("0.00"),
    )
    personal_spending = sum(
        (
            Decimal(str(item["amount"]))
            for item in expenses
            if item["expense_type"] == "PERSONAL"
        ),
        Decimal("0.00"),
    )

    budget = Decimal(str(trip["planned_budget"] or 0))
    remaining = budget - total_spent
    currency = trip["currency"]

    section_heading(
        trip["trip_name"],
        "Review spending and manage the group's shared costs.",
        eyebrow="EXPENSE OVERVIEW",
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card(
            "Total spending",
            money(total_spent, currency),
            icon="💳",
            note=f"{len(expenses)} recorded expenses",
        )
    with col2:
        metric_card(
            "Shared expenses",
            money(shared_spending, currency),
            icon="👥",
            note="Costs allocated across members",
        )
    with col3:
        metric_card(
            "Personal expenses",
            money(personal_spending, currency),
            icon="👤",
            note="Individual spending records",
        )
    with col4:
        metric_card(
            "Budget remaining",
            money(remaining, currency),
            icon="💰",
            note="May be negative if over budget",
        )

    if budget > 0:
        percentage = float(total_spent / budget * 100)
        st.markdown("#### Budget progress")
        st.progress(min(max(percentage / 100, 0.0), 1.0))
        left, right = st.columns(2)
        with left:
            st.caption(f"{percentage:.1f}% of planned budget recorded")
        with right:
            st.caption(f"Budget: {money(budget, currency)}")
        if percentage > 100:
            st.warning("Recorded expenses exceed the planned budget.")
    else:
        st.info(
            "This trip has a zero budget. Set a positive budget "
            "to calculate budget utilization."
        )

    st.markdown("---")
    section_heading(
        "Record an expense",
        (
            "Select who paid and whether the cost is shared or personal. "
            "Shared costs are currently divided equally among trip members."
        ),
        eyebrow="ADD EXPENSE",
    )

    if not members:
        st.warning("Add at least one member to the trip before recording expenses.")
        return
    if not categories:
        st.error("No expense categories were found. Check the expense_category table.")
        return

    member_options = {
        f'{member["full_name"]} ({member["email"]})': int(member["user_id"])
        for member in members
    }
    category_options = {
        category["category_name"]: int(category["category_id"])
        for category in categories
    }

    with st.expander("＋ Add a new expense", expanded=False):
        with st.form("new_expense_form", clear_on_submit=True):
            description = st.text_input(
                "Expense description *",
                placeholder="e.g. Dinner for the group",
            )
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input(
                    "Amount *",
                    min_value=0.01,
                    value=100.00,
                    step=100.00,
                    format="%.2f",
                )
            with col2:
                expense_date = st.date_input("Expense date")

            col3, col4 = st.columns(2)
            with col3:
                category_label = st.selectbox(
                    "Category",
                    list(category_options.keys()),
                )
            with col4:
                payer_label = st.selectbox(
                    "Who paid?",
                    list(member_options.keys()),
                )

            expense_type = st.radio(
                "Expense type",
                ["SHARED", "PERSONAL"],
                horizontal=True,
                format_func=lambda value: (
                    "Shared — divide among the group"
                    if value == "SHARED"
                    else "Personal — assign to the payer"
                ),
            )
            receipt_path = st.text_input(
                "Receipt path (optional)",
                placeholder="e.g. receipts/dinner.pdf",
                help=(
                    "For now, enter a file path only if the file already exists. "
                    "Actual uploads can be added separately."
                ),
            )
            submitted = st.form_submit_button(
                "Save expense",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not description.strip():
                st.error("Please enter an expense description.")
            else:
                payer_id = member_options[payer_label]
                amount_decimal = Decimal(str(amount)).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
                cursor = None
                try:
                    with transaction() as connection:
                        cursor = connection.cursor()
                        cursor.execute(
                            """
                            INSERT INTO expense (
                                trip_id, paid_by, category_id, amount,
                                expense_date, description, expense_type, receipt_path
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                trip_id,
                                payer_id,
                                category_options[category_label],
                                amount_decimal,
                                expense_date,
                                description.strip(),
                                expense_type,
                                receipt_path.strip() or None,
                            ),
                        )
                        expense_id = cursor.lastrowid

                        if expense_type == "SHARED":
                            allocations = split_amount_equally(
                                amount_decimal,
                                [member["user_id"] for member in members],
                            )
                            split_rows = [
                                (
                                    expense_id,
                                    member_id,
                                    allocated_amount,
                                    "SETTLED" if member_id == payer_id else "PENDING",
                                )
                                for member_id, allocated_amount in allocations
                            ]
                        else:
                            split_rows = [
                                (expense_id, payer_id, amount_decimal, "SETTLED")
                            ]

                        cursor.executemany(
                            """
                            INSERT INTO expense_split (
                                expense_id, user_id, allocated_amount, settlement_status
                            )
                            VALUES (%s, %s, %s, %s)
                            """,
                            split_rows,
                        )
                except Exception as exc:
                    st.error("The expense could not be saved.")
                    with st.expander("Technical error details"):
                        st.code(str(exc))
                else:
                    st.success("Expense and allocations saved successfully.")
                    st.rerun()
                finally:
                    if cursor is not None:
                        cursor.close()

    st.markdown("---")
    section_heading(
        "Expense history",
        "All recorded expenses for the selected trip.",
        eyebrow="TRANSACTIONS",
    )

    if not expenses:
        st.info("No expenses have been recorded for this trip yet.")
    else:
        expense_table = [
            {
                "Date": str(item["expense_date"]),
                "Description": item["description"],
                "Category": item["category_name"],
                "Paid by": item["paid_by"],
                "Type": item["expense_type"],
                "Amount": money(item["amount"], currency),
            }
            for item in expenses
        ]
        # Do not pass a 'theme' argument to st.dataframe(); it is unsupported.
        st.dataframe(
            expense_table,
            use_container_width=True,
            hide_index=True,
        )

        category_totals = fetch_all(
            """
            SELECT
                ec.category_name,
                SUM(e.amount) AS total_amount
            FROM expense e
            INNER JOIN expense_category ec
                ON ec.category_id = e.category_id
            WHERE e.trip_id = %s
            GROUP BY ec.category_id, ec.category_name
            ORDER BY total_amount DESC
            """,
            (trip_id,),
        )

        if category_totals:
            section_heading(
                "Where the money goes",
                "Recorded spending by expense category.",
            )
            chart_data = [
                {
                    "Category": item["category_name"],
                    "Amount": float(item["total_amount"] or 0),
                }
                for item in category_totals
            ]
            fig = px.pie(
                chart_data,
                names="Category",
                values="Amount",
                hole=0.62,
                color_discrete_sequence=[
                    "#2563EB", "#0F766E", "#F59E0B", "#8B5CF6",
                    "#EC4899", "#64748B", "#14B8A6", "#EA580C",
                ],
                template=_chart_template(),
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(
                _style_chart(fig),
                use_container_width=True,
            )

    st.markdown("---")
    section_heading(
        "Group balances",
        "Compare what each member paid toward shared expenses with their allocated share.",
        eyebrow="SETTLEMENT SUMMARY",
    )

    balances = fetch_all(
        """
        SELECT
            u.user_id,
            u.full_name,
            COALESCE((
                SELECT SUM(e.amount)
                FROM expense e
                WHERE e.trip_id = tm.trip_id
                  AND e.paid_by = tm.user_id
                  AND e.expense_type = 'SHARED'
            ), 0) AS shared_paid,
            COALESCE((
                SELECT SUM(es.allocated_amount)
                FROM expense_split es
                INNER JOIN expense e2 ON e2.expense_id = es.expense_id
                WHERE e2.trip_id = tm.trip_id
                  AND es.user_id = tm.user_id
                  AND e2.expense_type = 'SHARED'
            ), 0) AS shared_share,
            COALESCE((
                SELECT SUM(es.allocated_amount)
                FROM expense_split es
                INNER JOIN expense e3 ON e3.expense_id = es.expense_id
                WHERE e3.trip_id = tm.trip_id
                  AND es.user_id = tm.user_id
                  AND e3.expense_type = 'SHARED'
                  AND e3.paid_by <> es.user_id
                  AND es.settlement_status = 'PENDING'
            ), 0) AS pending_share
        FROM trip_member tm
        INNER JOIN users u ON u.user_id = tm.user_id
        WHERE tm.trip_id = %s
        ORDER BY u.full_name
        """,
        (trip_id,),
    )

    if balances:
        balance_rows = []
        for member in balances:
            shared_paid = Decimal(str(member["shared_paid"] or 0))
            shared_share = Decimal(str(member["shared_share"] or 0))
            net_balance = shared_paid - shared_share

            if net_balance > 0:
                position = "Net payer — others may owe them"
            elif net_balance < 0:
                position = "Allocated share exceeds paid amount"
            else:
                position = "Even so far"

            balance_rows.append(
                {
                    "Member": member["full_name"],
                    "Shared paid": money(shared_paid, currency),
                    "Allocated share": money(shared_share, currency),
                    "Net position": money(net_balance, currency),
                    "Pending share": money(member["pending_share"], currency),
                    "Summary": position,
                }
            )

        st.dataframe(
            balance_rows,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")
    section_heading(
        "Update settlement status",
        "Mark an individual allocation as pending or settled.",
    )

    if not expenses:
        st.info("Record an expense first to manage settlement statuses.")
        return

    expense_options = {
        f'#{item["expense_id"]} — {item["description"]} ({money(item["amount"], currency)})':
        int(item["expense_id"])
        for item in expenses
    }
    chosen_expense_label = st.selectbox(
        "Choose an expense",
        list(expense_options.keys()),
        key="settlement_expense_selector",
    )
    chosen_expense_id = expense_options[chosen_expense_label]

    allocations = fetch_all(
        """
        SELECT
            es.expense_split_id,
            es.user_id,
            u.full_name,
            es.allocated_amount,
            es.settlement_status
        FROM expense_split es
        INNER JOIN users u ON u.user_id = es.user_id
        INNER JOIN expense e ON e.expense_id = es.expense_id
        WHERE es.expense_id = %s
          AND e.trip_id = %s
        ORDER BY u.full_name
        """,
        (chosen_expense_id, trip_id),
    )

    if allocations:
        st.dataframe(
            [
                {
                    "Member": item["full_name"],
                    "Allocated amount": money(item["allocated_amount"], currency),
                    "Status": item["settlement_status"],
                }
                for item in allocations
            ],
            use_container_width=True,
            hide_index=True,
        )

        allocation_options = {
            f'{item["full_name"]} — {money(item["allocated_amount"], currency)}':
            int(item["expense_split_id"])
            for item in allocations
        }

        with st.form("settlement_status_form"):
            allocation_label = st.selectbox(
                "Choose a member's allocation",
                list(allocation_options.keys()),
            )
            selected_allocation_id = allocation_options[allocation_label]
            current_allocation = next(
                item for item in allocations
                if int(item["expense_split_id"]) == selected_allocation_id
            )
            new_status = st.selectbox(
                "Settlement status",
                ["PENDING", "SETTLED"],
                index=(
                    1 if current_allocation["settlement_status"] == "SETTLED" else 0
                ),
            )
            update_submitted = st.form_submit_button(
                "Update settlement",
                type="primary",
                use_container_width=True,
            )

        if update_submitted:
            cursor = None
            try:
                with transaction() as connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        """
                        UPDATE expense_split es
                        INNER JOIN expense e ON e.expense_id = es.expense_id
                        SET es.settlement_status = %s
                        WHERE es.expense_split_id = %s
                          AND e.trip_id = %s
                          AND e.expense_id = %s
                        """,
                        (
                            new_status,
                            selected_allocation_id,
                            trip_id,
                            chosen_expense_id,
                        ),
                    )
            except Exception as exc:
                st.error("Unable to update the settlement status.")
                with st.expander("Technical error details"):
                    st.code(str(exc))
            else:
                st.success("Settlement status updated.")
                st.rerun()
            finally:
                if cursor is not None:
                    cursor.close()
