import psycopg2
import os
from pathlib import Path

# Load SQL init script
sql_file_path = Path(__file__).parent / "init_db.sql"
with open(sql_file_path, "r") as f:
    sql = f.read()

# YugabyteDB connection config
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    user=os.getenv("DB_USER", "yugabyte"),
    password=os.getenv("DB_PASSWORD", "yugabyte"),
    dbname=os.getenv("DB_NAME", "yugabyte"),
    port=os.getenv("DB_PORT", "5433")
)

# Execute SQL statements
with conn.cursor() as cursor:
    statements = sql.split(";")
    for stmt in statements:
        stmt = stmt.strip()
        if stmt:
            try:
                cursor.execute(stmt)
            except Exception as e:
                print(f"⚠️ Error executing statement:\n{stmt}\n{e}")

conn.commit()
conn.close()

print("✅ Database initialized successfully.")
