import html
import textwrap
from datetime import date

import streamlit as st
import streamlit.components.v1 as components

from db import fetch_one, test_connection
from ui import (
    apply_global_styles,
    content_card,
    metric_card,
    render_brand,
    render_hero,
    section_heading,
)
from auth_manager import render_auth_screen
from trip_manager import get_trips, render_trip_manager_page
from itinerary_manager import render_itinerary_page
from expense_manager import render_expenses_page
from bookings_manager import render_bookings_page
from members_manager import render_members_page
from reports_manager import render_reports_page


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="TravelMate | Trip Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Light"


def render_raw_html(markup):
    """Render HTML directly after normalizing its indentation."""
    cleaned_markup = textwrap.dedent(markup).strip()
    st.html(cleaned_markup)


apply_global_styles()


# --------------------------------------------------
# ADDITIONAL FORM STYLING

render_raw_html(
    """
    <style>
    [data-testid="stTextArea"] textarea,
    div[data-baseweb="textarea"] textarea,
    textarea,
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input,
    [data-testid="stTimeInput"] input {
        background-color: var(--tm-input) !important;
        color: var(--tm-text) !important;
        -webkit-text-fill-color: var(--tm-text) !important;
        caret-color: var(--tm-primary) !important;
        border-color: var(--tm-border) !important;
        opacity: 1 !important;
        font-size: 15px !important;
    }

    [data-testid="stTextArea"] textarea::placeholder,
    textarea::placeholder,
    input::placeholder {
        color: var(--tm-muted) !important;
        -webkit-text-fill-color: var(--tm-muted) !important;
        opacity: 0.85 !important;
    }

    [data-testid="stWidgetLabel"] p {
        color: var(--tm-text) !important;
    }
    </style>
    """
)


# TRIP CARD STYLING

render_raw_html(
    """
    <style>
    .tm-trip-card {
        background: var(--tm-surface);
        border: 1px solid var(--tm-border);
        border-radius: 19px;
        padding: 22px;
        margin-bottom: 10px;
        box-shadow: var(--tm-shadow);
        min-height: 275px;
        transition: transform 150ms ease, border-color 150ms ease;
    }

    .tm-trip-card:hover {
        transform: translateY(-2px);
        border-color: var(--tm-primary);
    }

    .tm-trip-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
        gap: 10px;
    }

    .tm-trip-symbol {
        width: 45px;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--tm-primary-soft);
        color: var(--tm-primary);
        border-radius: 13px;
        font-size: 23px;
    }

    .tm-trip-status {
        display: inline-block;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.7px;
        padding: 6px 10px;
        border-radius: 20px;
    }

    .tm-status-planned {
        background: var(--tm-primary-soft);
        color: var(--tm-primary);
    }

    .tm-status-ongoing {
        background: var(--tm-success-soft);
        color: var(--tm-success);
    }

    .tm-status-completed {
        background: var(--tm-surface-alt);
        color: var(--tm-muted);
    }

    .tm-status-cancelled {
        background: var(--tm-danger-soft);
        color: var(--tm-danger);
    }

    .tm-trip-title {
        font-size: 20px;
        font-weight: 800;
        letter-spacing: -0.5px;
        line-height: 1.4;
        color: var(--tm-text);
        margin-bottom: 7px;
        overflow-wrap: anywhere;
    }

    .tm-trip-description {
        font-size: 13px;
        color: var(--tm-muted);
        line-height: 1.6;
        min-height: 41px;
        margin-bottom: 15px;
        overflow-wrap: anywhere;
    }

    .tm-trip-meta {
        font-size: 12px;
        color: var(--tm-muted);
        margin-bottom: 17px;
        line-height: 1.7;
    }

    .tm-trip-stat-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 10px;
    }

    .tm-trip-stat-label {
        color: var(--tm-muted);
        font-size: 11px;
        margin-bottom: 4px;
    }

    .tm-trip-stat-value {
        color: var(--tm-text);
        font-size: 15px;
        font-weight: 750;
        overflow-wrap: anywhere;
    }

    .tm-progress-track {
        width: 100%;
        height: 6px;
        background: var(--tm-border);
        border-radius: 20px;
        overflow: hidden;
        margin-top: 13px;
    }

    .tm-progress-fill {
        height: 100%;
        background: var(--tm-primary);
        border-radius: 20px;
    }

    .tm-trip-progress-caption {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        margin-top: 8px;
        font-size: 11px;
        color: var(--tm-muted);
    }

    .tm-welcome-note {
        font-size: 14px;
        color: var(--tm-muted);
        line-height: 1.7;
        margin-top: 6px;
    }

    @media (max-width: 768px) {
        .tm-trip-card { padding: 16px; }
        .tm-trip-stat-row { flex-wrap: wrap; }
    }
    </style>
    """
)


# FORMATTING HELPERS
# --------------------------------------------------

def format_money(amount, currency="INR"):
    amount = float(amount or 0)
    formatted = f"{amount:,.2f}".rstrip("0").rstrip(".")

    if currency == "INR":
        return f"₹{formatted}"

    return f"{currency} {formatted}"


def format_date(value):
    if not value:
        return "Date not set"

    if isinstance(value, date):
        return value.strftime("%d %b %Y")

    return str(value)


# --------------------------------------------------
# TRIP CARD NAVIGATION CALLBACK
# --------------------------------------------------

def open_trip_details(trip_id):
    """Select a trip and navigate before Streamlit recreates widgets."""
    st.session_state["selected_trip_id"] = int(trip_id)
    st.session_state["page_nav"] = "My Trips"


# TRIP CARD
# --------------------------------------------------

def render_trip_card(trip):
    trip_id = int(trip["trip_id"])
    name = html.escape(str(trip["trip_name"]))
    description = html.escape(
        str(trip.get("description") or "No trip description added yet.")
    )

    status = str(trip["status"]).upper()
    status_class = {
        "PLANNED": "tm-status-planned",
        "ONGOING": "tm-status-ongoing",
        "COMPLETED": "tm-status-completed",
        "CANCELLED": "tm-status-cancelled",
    }.get(status, "tm-status-planned")

    start_date = html.escape(format_date(trip.get("start_date")))
    end_date = html.escape(format_date(trip.get("end_date")))
    members = int(trip.get("member_count") or 0)
    budget = float(trip.get("planned_budget") or 0)
    expenses = float(trip.get("actual_expenses") or 0)
    currency = str(trip.get("currency") or "INR")

    percentage = expenses / budget * 100 if budget > 0 else 0
    bar_width = min(max(percentage, 0), 100)
    amount_display = html.escape(format_money(budget, currency))
    spent_display = html.escape(format_money(expenses, currency))

    render_raw_html(
        f"""
        <div class="tm-trip-card">
            <div class="tm-trip-card-header">
                <div class="tm-trip-symbol">✈️</div>
                <span class="tm-trip-status {status_class}">
                    {html.escape(status)}
                </span>
            </div>

            <div class="tm-trip-title">{name}</div>
            <div class="tm-trip-description">{description}</div>

            <div class="tm-trip-meta">
                📅 {start_date} – {end_date}
                &nbsp; · &nbsp; 👥 {members} members
            </div>

            <div class="tm-trip-stat-row">
                <div>
                    <div class="tm-trip-stat-label">PLANNED BUDGET</div>
                    <div class="tm-trip-stat-value">{amount_display}</div>
                </div>
                <div style="text-align: right;">
                    <div class="tm-trip-stat-label">RECORDED SPENDING</div>
                    <div class="tm-trip-stat-value">{spent_display}</div>
                </div>
            </div>

            <div class="tm-progress-track">
                <div class="tm-progress-fill" style="width: {bar_width:.2f}%;"></div>
            </div>

            <div class="tm-trip-progress-caption">
                <span>Budget utilized</span>
                <span>{percentage:.1f}%</span>
            </div>
        </div>
        """
    )

    st.button(
        "View trip details →",
        key=f"view_trip_{trip_id}",
        use_container_width=True,
        on_click=open_trip_details,
        args=(trip_id,),
    )


# --------------------------------------------------
# DASHBOARD DATA
# --------------------------------------------------

def load_dashboard_data():
    stats = fetch_one(
        """
        SELECT
            (SELECT COUNT(*) FROM trips) AS total_trips,
            (
                SELECT COUNT(*)
                FROM trips
                WHERE status IN ('PLANNED', 'ONGOING')
            ) AS active_trips,
            (
                SELECT COUNT(DISTINCT user_id)
                FROM trip_member
            ) AS total_travelers,
            (
                SELECT COALESCE(SUM(amount), 0)
                FROM expense
            ) AS total_expenses
        """
    )

    trips = get_trips()
    return stats, trips


# --------------------------------------------------
# SIDEBAR AND LOGOUT
# --------------------------------------------------

def render_sidebar():
    """Render compact workspace navigation and the appearance selector."""
    st.sidebar.selectbox(
        "Appearance",
        options=["Light", "Dark"],
        key="theme_mode",
        format_func=lambda mode: "☀️  Light mode" if mode == "Light" else "🌙  Dark mode",
    )

    st.sidebar.markdown(
        '<div style="height: 16px;"></div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<div class="tm-eyebrow" style="margin-bottom: 8px;">WORKSPACE</div>',
        unsafe_allow_html=True,
    )

    pages = [
        "Overview",
        "My Trips",
        "Itinerary",
        "Expenses",
        "Bookings",
        "Members",
        "Reports",
    ]

    if "page_nav" not in st.session_state:
        st.session_state["page_nav"] = "Overview"

    st.sidebar.radio(
        "Navigate",
        pages,
        key="page_nav",
        label_visibility="collapsed",
        format_func=lambda page: {
            "Overview": "🏠  Overview",
            "My Trips": "🧭  My Trips",
            "Itinerary": "📅  Itinerary",
            "Expenses": "💳  Expenses",
            "Bookings": "🏨  Bookings",
            "Members": "👥  Members",
            "Reports": "📊  Reports",
        }.get(page, page),
    )


def handle_logout():
    """Clear the authenticated session before the next script run."""
    st.session_state.pop("current_user", None)
    st.session_state.pop("selected_trip_id", None)
    st.session_state["page_nav"] = "Overview"


def render_topbar():
    """Render the complete branded header inside one theme-matched panel."""
    user = st.session_state.get("current_user", {})
    full_name = html.escape(str(user.get("full_name") or "Traveler"))
    email = html.escape(str(user.get("email") or ""))

    # A single Streamlit container gives the brand, account details and
    # logout control one continuous background without changing their logic.
    with st.container(key="tm-header-panel"):
        brand_col, account_col, action_col = st.columns(
            [1.25, 1.35, 0.72],
            vertical_alignment="center",
            gap="medium",
        )

        with brand_col:
            st.html(
                """
                <div class="tm-topbar-brand">
                    <div class="tm-topbar-mark">✈</div>
                    <div>
                        <div class="tm-topbar-name">TravelMate</div>
                        <div class="tm-topbar-tagline">Plan together. Spend smarter.</div>
                    </div>
                </div>
                """
            )

        with account_col:
            st.html(
                f"""
                <div class="tm-account-summary">
                    <div class="tm-account-label">SIGNED IN AS</div>
                    <div class="tm-account-name">{full_name}</div>
                    <div class="tm-account-email">{email}</div>
                </div>
                """
            )

        with action_col:
            st.button(
                "Log out",
                key="topbar_logout_button",
                use_container_width=True,
                on_click=handle_logout,
            )

    st.markdown('<div class="tm-topbar-divider"></div>', unsafe_allow_html=True)


# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

def render_overview(stats, trips):
    render_hero(
        "YOUR TRAVEL WORKSPACE",
        "Every trip, beautifully organized.",
        (
            "Plan your itinerary, coordinate with your group, "
            "manage bookings and keep every travel expense in view."
        ),
    )

    render_raw_html(
        """
        <div class="tm-welcome-note">
            Here is an overview of your travel workspace.
        </div>
        """
    )

    st.markdown("")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            "Total trips",
            stats["total_trips"],
            icon="🧭",
            note="All trips in the database",
        )

    with col2:
        metric_card(
            "Active trips",
            stats["active_trips"],
            icon="✈️",
            note="Planned or ongoing",
        )

    with col3:
        metric_card(
            "Unique travelers",
            stats["total_travelers"],
            icon="👥",
            note="People in trip memberships",
        )

    with col4:
        metric_card(
            "Recorded expenses",
            format_money(stats["total_expenses"]),
            icon="💳",
            note="Across all recorded trips",
        )

    st.markdown("")
    section_heading(
        "Your trips",
        "Explore your trips and see their latest budget information.",
        eyebrow="TRIP MANAGEMENT",
    )

    if not trips:
        st.info(
            "No trips exist in the database yet. "
            "Open My Trips to create your first trip."
        )
        return

    columns = st.columns(2, gap="medium")

    for index, trip in enumerate(trips):
        with columns[index % 2]:
            render_trip_card(trip)


# --------------------------------------------------
# FALLBACK PAGE
# --------------------------------------------------

def render_placeholder_page(page):
    page_details = {
        "Itinerary": (
            "Your itinerary, day by day.",
            "Destinations, activity schedules, completion tracking and notes.",
            "The itinerary module is connected to your database.",
        ),
        "Expenses": (
            "Know where every rupee goes.",
            "Record shared and personal expenses, view allocations and monitor settlements.",
            "The expense module is connected to your database.",
        ),
        "Bookings": (
            "Keep your travel arrangements together.",
            "Manage accommodation, booking references and transportation schedules.",
            "The bookings module is connected to your database.",
        ),
        "Members": (
            "Your travel group, organized.",
            "Review trip members, roles and individual contributions.",
            "The members module is connected to your database.",
        ),
        "Reports": (
            "Understand every trip at a glance.",
            "Review budgets, expense breakdowns, member spending and activity progress.",
            "The reports module is connected to your database.",
        ),
    }

    title, description, information = page_details.get(
        page,
        (
            page,
            "Explore your travel workspace.",
            "Select a page from the sidebar.",
        ),
    )

    render_hero(page.upper(), title, description)
    content_card(
        f"{page} workspace",
        information,
        badge="TRAVELMATE",
    )


# --------------------------------------------------
# MAIN APPLICATION
# --------------------------------------------------

def scroll_to_top_when_page_changes(page):
    """
    Reset the actual Streamlit main-content scroller after sidebar navigation.
    The reset is only triggered when the selected page changes, so normal
    scrolling and widget interactions on the current page are unaffected.
    """
    previous_page = st.session_state.get("_previous_page_nav")

    if previous_page == page:
        return

    st.session_state["_previous_page_nav"] = page

    components.html(
        """
        <script>
        (() => {
            const resetMainScroll = () => {
                try {
                    const win = window.parent;
                    const doc = win.document;

                    // Streamlit's main content region is the only region
                    // whose scroll position should be reset.
                    const main = doc.querySelector('[data-testid="stMain"]')
                        || doc.querySelector('section.main')
                        || doc.querySelector('main');

                    const resetElement = (element) => {
                        if (!element) return;
                        element.scrollTop = 0;
                        if (typeof element.scrollTo === "function") {
                            element.scrollTo(0, 0);
                        }
                    };

                    // Reset the main region and any nested element that
                    // actually owns vertical scrolling.
                    if (main) {
                        resetElement(main);
                        main.querySelectorAll("*").forEach((element) => {
                            const style = win.getComputedStyle(element);
                            const overflowY = style.overflowY;
                            const canScroll = (
                                (overflowY === "auto" || overflowY === "scroll")
                                && element.scrollHeight > element.clientHeight
                            );
                            if (canScroll) resetElement(element);
                        });
                    }

                    // Also reset the document-level scroller when the
                    // browser uses it for the Streamlit page.
                    resetElement(doc.scrollingElement);
                    resetElement(doc.documentElement);
                    resetElement(doc.body);
                    win.scrollTo(0, 0);
                } catch (error) {
                    console.warn("TravelMate navigation scroll reset:", error);
                }
            };

            // Streamlit can restore the previous scroll position after the
            // component mounts, so retry across several render frames.
            let frames = 0;
            const retryForFrames = () => {
                resetMainScroll();
                frames += 1;
                if (frames < 45) {
                    window.requestAnimationFrame(retryForFrames);
                }
            };

            window.requestAnimationFrame(retryForFrames);
            [100, 250, 500, 800, 1200, 1600, 2200].forEach((delay) => {
                window.setTimeout(resetMainScroll, delay);
            });
        })();
        </script>
        """,
        height=1,
        width=1,
    )


def main():
    # Require a logged-in user before displaying the workspace.
    if not st.session_state.get("current_user"):
        col_space, col_theme = st.columns([5, 1])
        with col_theme:
            st.selectbox(
                "Appearance",
                options=["Light", "Dark"],
                key="theme_mode",
                format_func=lambda mode: "☀️ Light" if mode == "Light" else "🌙 Dark",
            )
        render_auth_screen()
        st.stop()

    registration_notice = st.session_state.pop(
        "registration_notice",
        None,
    )

    render_sidebar()

    if registration_notice:
        st.success(registration_notice)

    try:
        connection_info = test_connection()
        stats, trips = load_dashboard_data()

    except Exception as exc:
        st.error("Unable to load the TravelMate dashboard.")
        st.markdown(
            """
            Please check the following:

            1. MySQL Server is running.
            2. `.streamlit/secrets.toml` contains the correct credentials.
            3. The `travel_itinerary_organizer` database and its tables exist.
            4. The Python dependencies are installed.
            """
        )

        with st.expander("Technical error details"):
            st.code(str(exc))

        st.stop()

    # Keep the connection check, but do not show technical database details in the UI.
    # Stable anchor at the very top of the main content area.
    st.markdown(
        '<div id="tm-page-top" style="height:1px; margin:0; padding:0;"></div>',
        unsafe_allow_html=True,
    )

    page = st.session_state["page_nav"]
    scroll_to_top_when_page_changes(page)
    render_topbar()

    if page == "Overview":
        render_overview(stats, trips)
    elif page == "My Trips":
        render_trip_manager_page()

    elif page == "Itinerary":
        render_itinerary_page()
    elif page == "Expenses":
        render_expenses_page()
    elif page == "Bookings":
        render_bookings_page()
    elif page == "Members":
        render_members_page()
    elif page == "Reports":
        render_reports_page()
    else:
        render_placeholder_page(page)


if __name__ == "__main__":
    main()
