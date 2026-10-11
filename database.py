
import os
import psycopg2
from dotenv import load_dotenv

# Load settings from the .env file
load_dotenv()

def get_db_connection():
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "floodlens"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5
    )
    return connection


if __name__ == "__main__":
    try:
        connection = get_db_connection()
        print("PostgreSQL connected successfully!")

        connection.close()
        print("Connection closed.")

    except Exception as error:
        print("Database connection failed.")
        print(error)
