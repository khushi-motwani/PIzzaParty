"""Database configuration module."""
import mysql.connector


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="n3u3da!",
        database="Portfolio",
        autocommit=True
    )
