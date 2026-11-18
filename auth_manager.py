
import base64
import hashlib
import hmac
import re

import mysql.connector
import streamlit as st

from db import fetch_one, transaction
from ui import render_brand, render_hero


# --------------------------------------------------
# PASSWORD SECURITY
# --------------------------------------------------

HASH_ITERATIONS = 600_000


def hash_password(password):
    """Store a salted PBKDF2 password hash, never plain text."""
    salt = __import__("secrets").token_bytes(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        HASH_ITERATIONS,
    )

    salt_text = base64.b64encode(salt).decode("ascii")
    digest_text = base64.b64encode(digest).decode("ascii")

    return (
        f"pbkdf2_sha256${HASH_ITERATIONS}"
        f"${salt_text}${digest_text}"
    )


def verify_password(password, stored_hash):
    """Verify passwords created by this module."""
    if not stored_hash or not stored_hash.startswith("pbkdf2_sha256$"):
        return False

    try:
        algorithm, iterations_text, salt_text, digest_text = (
            stored_hash.split("$")
        )

        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations_text)

        if not 100_000 <= iterations <= 2_000_000:
            return False

        salt = base64.b64decode(salt_text, validate=True)
        expected_digest = base64.b64decode(
            digest_text,
            validate=True,
        )

        actual_digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )

        return hmac.compare_digest(
            actual_digest,
            expected_digest,
        )

    except (ValueError, TypeError):
        return False


# --------------------------------------------------
# REGISTER ACCOUNT
# --------------------------------------------------

def register_user(full_name, email, phone, password):
    full_name = full_name.strip()
    email = email.strip().lower()
    phone = phone.strip() or None

    if not full_name:
        return None, "Please enter your full name."

    if len(full_name) > 120:
        return None, "Your name must be at most 120 characters."

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return None, "Please enter a valid email address."

    if len(email) > 160:
        return None, "Your email address is too long."

    if phone and len(phone) > 25:
        return None, "Your phone number must be at most 25 characters."

    if len(password) < 8:
        return None, "Your password must contain at least 8 characters."

    if len(password) > 128:
        return None, "Your password must be at most 128 characters."

    password_hash = hash_password(password)

    try:
        with transaction() as connection:
            cursor = connection.cursor()

            try:
                cursor.execute(
                    """
                    INSERT INTO users (
                        full_name,
                        email,
                        password_hash,
                        phone
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        full_name,
                        email,
                        password_hash,
                        phone,
                    ),
                )

                user_id = cursor.lastrowid

            finally:
                cursor.close()

    except mysql.connector.IntegrityError as exc:
        if exc.errno == 1062:
            return None, (
                "An account with this email already exists. "
                "Please log in instead."
            )

        return None, "The account could not be created."

    except Exception:
        return None, (
            "Unable to create your account. "
            "Please check the database connection."
        )

    return {
        "user_id": int(user_id),
        "full_name": full_name,
        "email": email,
    }, None


# --------------------------------------------------
# LOG IN
# --------------------------------------------------

def authenticate_user(email, password):
    email = email.strip().lower()

    user = fetch_one(
        """
        SELECT
            user_id,
            full_name,
            email,
            password_hash
        FROM users
        WHERE LOWER(email) = %s
        LIMIT 1
        """,
        (email,),
    )

    if not user or not verify_password(
        password,
        user["password_hash"],
    ):
        return None, "Incorrect email address or password."

    return {
        "user_id": int(user["user_id"]),
        "full_name": user["full_name"],
        "email": user["email"],
    }, None


# --------------------------------------------------
# AUTHENTICATION PAGE
# --------------------------------------------------

def render_auth_screen():
    render_brand()

    render_hero(
        "WELCOME TO TRAVELMATE",
        "Your next adventure starts here.",
        (
            "Create an account to plan trips, coordinate with your "
            "travel group, manage expenses and organize bookings."
        ),
    )

    left, center, right = st.columns([1, 2, 1])

    with center:
        login_tab, register_tab = st.tabs(
            ["Log in", "Create account"]
        )

        with login_tab:
            st.markdown("### Welcome back")
            st.caption("Sign in to continue to your travel workspace.")

            with st.form("login_form"):
                email = st.text_input(
                    "Email address",
                    placeholder="you@example.com",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                )

                submitted = st.form_submit_button(
                    "Log in",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if not email.strip() or not password:
                    st.error(
                        "Please enter both your email and password."
                    )
                else:
                    try:
                        user, error = authenticate_user(
                            email,
                            password,
                        )
                    except Exception:
                        user, error = None, (
                            "Unable to access the account database. "
                            "Please try again."
                        )

                    if error:
                        st.error(error)
                    else:
                        st.session_state["current_user"] = user
                        st.rerun()

        with register_tab:
            st.markdown("### Create your account")
            st.caption(
                "Register once, then use your credentials to log in."
            )

            with st.form("registration_form"):
                full_name = st.text_input(
                    "Full name",
                    placeholder="Enter your full name",
                )

                email = st.text_input(
                    "Email address",
                    placeholder="you@example.com",
                )

                phone = st.text_input(
                    "Phone number (optional)",
                    placeholder="Enter your phone number",
                )

                password = st.text_input(
                    "Create password",
                    type="password",
                    help="Use at least 8 characters.",
                )

                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                )

                submitted = st.form_submit_button(
                    "Create account",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if password != confirm_password:
                    st.error("The passwords do not match.")

                else:
                    user, error = register_user(
                        full_name,
                        email,
                        phone,
                        password,
                    )

                    if error:
                        st.error(error)

                    else:
                        st.session_state["current_user"] = user
                        st.session_state["registration_notice"] = (
                            f'Welcome to TravelMate, {user["full_name"]}!'
                        )
                        st.rerun()
