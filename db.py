
import mysql.connector
import pandas as pd
import streamlit as st

from contextlib import contextmanager


def get_connection():
    """
    Connect to the existing MySQL database using Streamlit secrets.
    """
    if "mysql" not in st.secrets:
        raise RuntimeError(
            "MySQL configuration is missing. "
            "Create .streamlit/secrets.toml first."
        )

    config = st.secrets["mysql"]

    required_fields = ["host", "user", "password", "database"]

    for field in required_fields:
        if field not in config:
            raise RuntimeError(
                f"Missing '{field}' in .streamlit/secrets.toml."
            )

    connection = mysql.connector.connect(
        host=config["host"],
        port=int(config.get("port", 3306)),
        user=config["user"],
        password=config["password"],
        database=config["database"],
        connection_timeout=10,
        autocommit=False,
    )

    return connection


@contextmanager
def transaction():
    """
    Execute multiple database operations as one transaction.
    Commit everything if successful; otherwise roll back.
    """
    connection = get_connection()

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def fetch_all(sql, params=None):
    """
    Execute a SELECT query and return all rows as dictionaries.
    """
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        return cursor.fetchall()

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


def fetch_one(sql, params=None):
    """
    Execute a SELECT query and return one row, or None.
    """
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        return cursor.fetchone()

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


def fetch_df(sql, params=None):
    """
    Execute a SELECT query and return a Pandas DataFrame.
    """
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params or ())

        rows = cursor.fetchall()

        columns = [
            column[0]
            for column in cursor.description
        ] if cursor.description else []

        return pd.DataFrame(rows, columns=columns)

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


def execute_query(sql, params=None):
    """
    Execute one INSERT, UPDATE, or DELETE statement.
    Return the affected row count and generated ID.
    """
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute(sql, params or ())
        connection.commit()

        return {
            "rowcount": cursor.rowcount,
            "lastrowid": cursor.lastrowid,
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


def execute_many(sql, data):
    """
    Execute the same INSERT or UPDATE statement for multiple records.
    """
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        cursor.executemany(sql, data)
        connection.commit()

        return cursor.rowcount

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


def test_connection():
    """
    Verify the MySQL connection and report the selected database.
    """
    return fetch_one(
        """
        SELECT
            DATABASE() AS database_name,
            VERSION() AS mysql_version
        """
    )
