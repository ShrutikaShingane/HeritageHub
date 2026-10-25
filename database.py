import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

# Function to get database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""), # Agar password hai toh .env se aayega
            database=os.getenv("DB_NAME", "heritage_hub")
        )
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

