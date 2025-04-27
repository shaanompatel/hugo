from django.db import connection
import numpy as np # Import numpy to handle NaN values
import pandas as pd # Import pandas
import os
from google import genai
from google.genai import types
from django.db import connection



def execute_sql_query(query: str):
    """Execute an SQL query against the company database and return results.

    Args:
        query: A valid SQL query

    Returns:
        The query results as a list of dictionaries
    """
    try:
        with connection.cursor() as cursor:
            # Execute the query
            cursor.execute(query)

            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            # Fetch results
            rows = cursor.fetchall()

            # Convert to list of dictionaries
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))

            return results
    except Exception as e:
        return [{"error": f"SQL Error: {str(e)}"}]

# 2. Get database schema function
def get_database_schema(table_name: str):
    """Retrieve the schema of the company database.

    Args:
        table_name: Table name to get specific schema, or empty string for all tables

    Returns:
        Database schema information
    """
    # Get schema based on table name parameter
    schema = {"tables": []}

    with connection.cursor() as cursor:
        if table_name == "":
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table[0]

                # Get column information for this table
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                table_schema = {
                    "name": table_name,
                    "columns": []
                }

                for col in columns:
                    table_schema["columns"].append({
                        "name": col[1],
                        "type": col[2],
                        "primary_key": bool(col[5])
                    })

                schema["tables"].append(table_schema)
        else:
            # Get specific table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            if columns:  # Make sure the table exists
                table_schema = {
                    "name": table_name,
                    "columns": []
                }

                for col in columns:
                    table_schema["columns"].append({
                        "name": col[1],
                        "type": col[2],
                        "primary_key": bool(col[5])
                    })

                schema["tables"].append(table_schema)

    return schema






