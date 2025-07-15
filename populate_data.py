import psycopg2
from psycopg2.extras import RealDictCursor
import random
from faker import Faker
from datetime import datetime, timedelta
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Initialize Faker
fake = Faker("en_US")
fake.seed_instance(42)  # For reproducibility

# YugabyteDB (YSQL) configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5433)),
    "user": os.getenv("DB_USER", "yugabyte"),
    "password": os.getenv("DB_PASSWORD", "yugabyte"),
    "dbname": os.getenv("DB_NAME", "employee_tracking"),
}
# Fixed employee data to match the queries
employees = [
    {
        "id": 1,
        "name": "Wei Zhang",
        "email": "w.zhang@company.com",
        "dept": "Sales",
        "job": "Sales Manager",
        "hire_date": "2024-06-15",  # Normal period
        "activities": {
            1: [
                "Met with 5 clients; Closed 3 deals worth $45,000",
                42.5,
                4,
                35000.00,
            ],  # Week 1 (hours, meetings, sales)
            7: [
                "Prepared Q3 sales report; Customer retention strategy planning",
                39.5,
                3,
                28000.00,
            ],  # Week 7 (Aug 28)
        },
    },
    {
        "id": 2,
        "name": "Na Li",
        "email": "n.li@company.com",
        "dept": "Marketing",
        "job": "Marketing Manager",
        "hire_date": "2024-08-10",  # Normal period
        "activities": {
            1: [
                "Content calendar planning; Social media strategy meeting",
                38.0,
                6,
                0.00,
            ],  # Week 1
            2: [
                "SEO optimization project; Brand positioning workshop",
                39.5,
                8,
                0.00,
            ],  # Week 2
        },
    },
    {
        "id": 3,
        "name": "Tao Huang",
        "email": "t.huang@company.com",
        "dept": "Product Development",
        "job": "Product Manager",
        "hire_date": "2024-05-20",
        "activities": {
            1: [
                "Product roadmap review; User research planning",
                41.0,
                5,
                0.00,
            ],  # Week 1
            2: ["Feature prioritization; Sprint planning", 40.5, 4, 0.00],  # Week 2
        },
    },
    {
        "id": 4,
        "name": "Min Chen",
        "email": "m.chen@company.com",
        "dept": "Finance",
        "job": "Financial Analyst",
        "hire_date": "2020-03-15",  # During recession (for query 13)
        "activities": {
            1: ["Budget review; Financial forecasting", 43.0, 3, 0.00],  # Week 1
            2: [
                "Expense reports analysis; Quarterly closing preparation",
                42.5,
                4,
                0.00,
            ],  # Week 2
        },
    },
    {
        "id": 5,
        "name": "Qiang Wang",
        "email": "q.wang@company.com",
        "dept": "IT",
        "job": "Data Engineer",  # Role requiring data analysis skills
        "hire_date": "2021-11-10",  # During recession (for query 13)
        "activities": {
            1: [
                "Database optimization; Data pipeline maintenance",
                44.5,
                2,
                0.00,
            ],  # Week 1
            2: [
                "Data quality assessment; ETL process improvement",
                43.0,
                3,
                0.00,
            ],  # Week 2
        },
    },
    {
        "id": 6,
        "name": "Yue Lin",
        "email": "y.lin@company.com",
        "dept": "Sales",
        "job": "Account Manager",
        "hire_date": "2023-01-20",  # Normal period
        "activities": {
            1: [
                "Client relationship management; Sales territory planning",
                39.0,
                5,
                28000.00,
            ],  # Week 1
            2: [
                "Proposal development; Sales pipeline review",
                41.5,
                6,
                32000.00,
            ],  # Week 2
            7: [
                "Customer retention issues identified; Implemented discount strategy for at-risk accounts",
                43.0,
                4,
                38000.00,
            ],  # Week 7 (customer retention challenges)
        },
    },
    {
        "id": 7,
        "name": "Yang Zhao",
        "email": "y.zhao@company.com",
        "dept": "IT",
        "job": "SysAdmin",
        "hire_date": "2022-09-05",  # Normal period
        "activities": {
            1: ["Server maintenance; Network security review", 40.0, 2, 0.00],  # Week 1
            2: [
                "Cloud infrastructure setup; Backup system verification",
                38.5,
                3,
                0.00,
            ],  # Week 2
        },
    },
    {
        "id": 8,
        "name": "Xue Wu",
        "email": "x.wu@company.com",
        "dept": "Finance",
        "job": "CFO",
        "hire_date": "2020-05-18",  # During recession (for query 13)
        "activities": {
            1: [
                "Executive budget meeting; Financial strategy planning",
                46.0,
                7,
                0.00,
            ],  # Week 1
            2: [
                "Investor relations preparation; Financial review",
                44.5,
                5,
                0.00,
            ],  # Week 2
        },
    },
    {
        "id": 9,
        "name": "Jie Zhou",
        "email": "j.zhou@company.com",
        "dept": "Marketing",
        "job": "SEO Analyst",  # Role requiring data analysis skills
        "hire_date": "2021-08-15",  # During recession (for query 13)
        "activities": {
            1: [
                "Keyword performance analysis; Competitor benchmarking",
                38.5,
                3,
                0.00,
            ],  # Week 1
            2: [
                "SEO strategy development; Analytics dashboard creation",
                40.0,
                4,
                0.00,
            ],  # Week 2
            5: [
                "Customer retention issues analysis; Implemented targeted email campaign to re-engage dormant customers",
                42.5,
                5,
                0.00,
            ],  # Week 5 (customer retention challenges)
        },
    },
    {
        "id": 10,
        "name": "Fang Xu",
        "email": "f.xu@company.com",
        "dept": "Sales",
        "job": "Sales Director",
        "hire_date": "2024-02-10",  # Normal period
        "activities": {
            1: [
                "Sales team coaching; Revenue forecast review",
                45.0,
                6,
                30000.00,
            ],  # Week 1
            2: [
                "Sales incentive planning; Customer segmentation analysis",
                47.5,
                5,
                32000.00,
            ],  # Week 2
            7: [
                "High-value prospect meetings; Closed major deal",
                48.0,
                4,
                52000.00,
            ],  # Week 7 (highest revenue in a single week)
        },
    },
]

# Add activities data for weeks 7-10 for top hours worked (for query 18)
for emp_id in [5, 8, 10]:  # Qiang Wang, Xue Wu, Fang Xu - for top 3 hours
    emp = next(e for e in employees if e["id"] == emp_id)
    for week in range(7, 11):
        if week not in emp["activities"]:
            emp["activities"][week] = [
                "Strategic planning; Team coordination",
                47.0 + (emp_id % 3),  # High hours for these employees
                4 + (week % 3),
                30000.00 if emp["dept"] == "Sales" else 0.00,
            ]

try:
    # Establish connection
    conn = psycopg2.connect(**DB_CONFIG)

    with conn.cursor() as cursor:
        # Reset data
        if "--reset" in sys.argv:
            print("Resetting existing data...")
            cursor.execute("TRUNCATE TABLE activities")
            conn.commit()

        # Generate data for all employees and weeks
        print("Generating sample data...")

        # First ensure we have complete data for all employees for all weeks
        for emp in employees:
            emp_id = emp["id"]
            name = emp["name"]
            email = emp["email"]
            dept = emp["dept"]
            job = emp["job"]
            hire_date = emp["hire_date"]

            # For each week 1-10
            for week in range(1, 11):
                # Use predefined activities if available, otherwise generate random ones
                if week in emp["activities"]:
                    activities_str = emp["activities"][week][0]
                    hours_worked = emp["activities"][week][1]
                    num_meetings = emp["activities"][week][2]
                    total_sales = emp["activities"][week][3]
                else:
                    hours_worked = round(random.uniform(35, 40), 1)
                    num_meetings = random.randint(2, 5)
                    total_sales = (
                        round(random.uniform(25000, 30000), 2)
                        if dept == "Sales"
                        else 0.00
                    )
                    activities_str = "Regular weekly activities; Standard meetings"

                # Special case for week 7 - aligns with "2024-08-28" for query 3
                week_start_date = None
                if week == 7:
                    week_start_date = "2024-08-28"

                # Insert data
                cursor.execute(
                    """
                    INSERT INTO activities 
                    (employee_id, full_name, week_number, 
                     num_meetings, total_sales_rmb, hours_worked, 
                     activities, department, hire_date, email, job_title)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        f"EMP{emp_id:03d}",
                        name,
                        week,
                        num_meetings,
                        total_sales,
                        hours_worked,
                        activities_str,
                        dept,
                        hire_date,
                        email,
                        job,
                    ),
                )

        conn.commit()
        print(f"Successfully generated data for 10 employees × 10 weeks = 100 records")

except psycopg2.Error as e:
    print(f"Database error: {e}")
    if "conn" in locals():
        conn.rollback()
    sys.exit(1)

except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)

finally:
    try:
        if "conn" in locals():
            conn.close()
    except:
        pass

