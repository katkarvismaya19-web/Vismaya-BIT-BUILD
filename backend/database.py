# app/database.py
import mysql.connector
from fastapi import HTTPException, status

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        # IMPORTANT: In a real app, load these from a config file or environment variables
        conn = mysql.connector.connect(
            host="localhost",
            user="root",      # <-- Replace with your MySQL username
            password="0809202327",  # <-- Replace with your MySQL password
            database="paisabuddy"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to the database."
        )