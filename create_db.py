import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

try:
    # Connect to YugabyteDB default database to create new one
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5433),
        user=os.getenv("DB_USER", "yugabyte"),
        password=os.getenv("DB_PASSWORD", "yugabyte"),
        dbname="yugabyte"
    )
    conn.autocommit = True
    with conn.cursor() as cursor:
        cursor.execute("CREATE DATABASE employee_tracking;")
        print("✅ Database 'employee_tracking' created.")
except psycopg2.errors.DuplicateDatabase:
    print("ℹ️ Database already exists.")
except Exception as e:
    print(f"❌ Failed to create database: {e}")
finally:
    if conn:
        conn.close()

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5433)),
    "user": os.getenv("DB_USER", "yugabyte"),
    "password": os.getenv("DB_PASSWORD", "yugabyte"),
    "dbname": os.getenv("DB_NAME", "employee_tracking"),
}
        

SCHEMA_PATH = Path(__file__).parent / "init_db.sql"

try:
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            with open(SCHEMA_PATH, "r") as f:
                sql = f.read()
                cursor.execute(sql)
                conn.commit()
                print("✅ Schema initialized successfully.")
except Exception as e:
    print(f"❌ Failed to initialize schema: {e}")