"""Module for handling Snowflake connections."""

import os
from typing import Dict, Optional

import snowflake.connector


def create_connection(
    user: Optional[str] = None,
    password: Optional[str] = None,
    account: Optional[str] = None,
    warehouse: Optional[str] = None,
    database: Optional[str] = None,
    schema: Optional[str] = None,
    role: Optional[str] = None,
) -> snowflake.connector.SnowflakeConnection:
    """
    Create a connection to Snowflake.

    Parameters
    ----------
    user : str, optional
        Snowflake user name
    password : str, optional
        Password for the user
    account : str, optional
        Snowflake account identifier
    warehouse : str, optional
        Warehouse to use
    database : str, optional
        Database to use
    schema : str, optional
        Schema to use
    role : str, optional
        Role to use

    Returns
    -------
    snowflake.connector.SnowflakeConnection
        A connection to Snowflake
    """
    # Use environment variables if parameters not provided
    conn_params = {
        "user": user or os.environ.get("SNOWFLAKE_USER"),
        "password": password or os.environ.get("SNOWFLAKE_PASSWORD"),
        "account": account or os.environ.get("SNOWFLAKE_ACCOUNT"),
        "warehouse": warehouse or os.environ.get("SNOWFLAKE_WAREHOUSE"),
        "database": database or os.environ.get("SNOWFLAKE_DATABASE"),
        "schema": schema or os.environ.get("SNOWFLAKE_SCHEMA"),
        "role": role or os.environ.get("SNOWFLAKE_ROLE"),
    }

    # Remove None values
    conn_params = {k: v for k, v in conn_params.items() if v is not None}

    # Create and return connection
    return snowflake.connector.connect(**conn_params)


def execute_query(
    conn: snowflake.connector.SnowflakeConnection, query: str
) -> Dict:
    """
    Execute a query against Snowflake.

    Parameters
    ----------
    conn : snowflake.connector.SnowflakeConnection
        Connection to Snowflake
    query : str
        SQL query to execute

    Returns
    -------
    Dict
        Query results
    """
    cursor = conn.cursor(snowflake.connector.DictCursor)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results
