import os
import time
import random
import openai
import pyttsx3
import psycopg2
import psycopg2.extras
from pathlib import Path
from typing import Optional, Any, List, Dict
from dotenv import load_dotenv
import re

# === Load .env ===
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

openai.api_key = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "yugabyte"),
    "password": os.getenv("DB_PASSWORD", "yugabyte"),
    "dbname": os.getenv("DB_NAME", "employee_tracking"),
    "port": int(os.getenv("DB_PORT", "5433")),
}

# === Initialize TTS ===
engine = pyttsx3.init()
def speak(text: str):
    engine.say(text)
    engine.runAndWait()

# === Retry-safe OpenAI call ===
def call_openai_with_retry(prompt: str, model: str = DEFAULT_MODEL, max_retries: int = 6):
    base_wait = 5
    for i in range(max_retries):
        try:
            return openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt.strip()}],
                temperature=0.45,
                max_tokens=1000,
                top_p=1.0,
                timeout=60,
            )
        except openai.error.RateLimitError:
            wait = base_wait * (2 ** i) + random.uniform(0, 5)
            print(f"⏳ Retry {i+1}: Rate limit hit. Waiting {int(wait)}s...")
            time.sleep(wait)
        except Exception as e:
            print(f"❌ OpenAI error: {e}")
            break
    return None

def get_db_connection():
    try:
        return psycopg2.connect(**DB_CONFIG, cursor_factory=psycopg2.extras.DictCursor)
    except Exception as e:
        print(f"⚠️ DB connection failed: {e}")
        return None

# === SQL prompt formatting ===
def get_sql_prompt(nl_query: str, schema: str) -> str:
    return f"""
You are a PostgreSQL expert.

Convert the following question into a safe SQL query using this schema:
{schema}

Question:
{nl_query}

Rules:
- Output only a valid SQL query that starts with SELECT or WITH
- Do NOT use INSERT, UPDATE, DELETE, DROP, ALTER, or comments
- Use PostgreSQL syntax only
- Do NOT explain or describe the query
"""

# === Validate and clean SQL ===
def _validate_sql(sql: str) -> bool:
    allowed_prefixes = ("SELECT", "WITH")
    forbidden = ("DROP", "DELETE", "UPDATE", "INSERT", "ALTER")
    return sql.upper().startswith(allowed_prefixes) and not any(f in sql.upper() for f in forbidden)

def clean_sql_output(sql: str) -> str:
    # Remove ```sql or ``` blocks
    return re.sub(r"```(?:sql)?\s*([\s\S]+?)\s*```", r"\1", sql).strip()

def query_to_sql(nl_query: str, schema: str) -> Optional[str]:
    prompt = get_sql_prompt(nl_query, schema)
    response = call_openai_with_retry(prompt)
    if not response:
        return None

    sql = response.choices[0].message.content.strip()
    sql = clean_sql_output(sql)
    print("📄 SQL:", sql)

    if not _validate_sql(sql):
        print("⚠️ SQL validation failed.")
        return None
    return sql

# === Summary prompt ===
def get_summary_prompt(query: str, results: List[Dict[str, Any]]) -> str:
    return f"""
You are a business analyst.

# Question:
{query}

# Query Results:
{results}

Summarize the results in clear professional English. Focus on trends, comparisons, and key takeaways.
"""

def summarize_results(query: str, results: List[Dict[str, Any]]) -> str:
    if not results:
        return "ℹ️ No results found."

    prompt = get_summary_prompt(query, results)
    response = call_openai_with_retry(prompt)
    if not response:
        return "❌ Summary failed."
    return response.choices[0].message.content.strip()

def query_to_summary(nl_query: str, schema: str) -> str:
    sql = query_to_sql(nl_query, schema)
    if not sql:
        return "❌ SQL generation failed."

    conn = get_db_connection()
    if not conn:
        return "❌ Database connection failed."

    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            result_data = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        return f"❌ Query error: {e}"
    finally:
        conn.close()

    summary = summarize_results(nl_query, result_data)
    return summary

# === App Runner ===
def main():
    schema = """
activities(
    id INT,
    employee_id VARCHAR(20),
    full_name VARCHAR(100),
    week_number INT,
    num_meetings INT,
    total_sales_rmb DECIMAL(10, 2),
    hours_worked DECIMAL(5, 1),
    activities TEXT,
    department VARCHAR(50),
    hire_date DATE,
    email VARCHAR(100),
    job_title VARCHAR(100)
)
"""
    print("💬 Ask a question about employee activity data (type 'exit' to quit):")
    while True:
        user_query = input("💬 > ").strip()
        if user_query.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break
        answer = query_to_summary(user_query, schema)
        print("📝 Answer:\n", answer)
        speak(answer)

if __name__ == "__main__":
    main()
