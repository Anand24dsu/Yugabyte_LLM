import random
from datetime import datetime, timedelta
from faker import Faker
from pathlib import Path

# Setup
fake = Faker()
departments = ["Sales", "IT", "HR", "Finance", "Marketing", "Product Development", "Business Development"]
job_titles = {
    "Sales": ["Sales Manager", "Account Executive"],
    "IT": ["Software Engineer", "SysAdmin"],
    "HR": ["HR Specialist", "Recruiter"],
    "Finance": ["Financial Analyst", "Accountant"],
    "Marketing": ["Marketing Manager", "SEO Specialist"],
    "Product Development": ["Product Analyst", "UX Designer"],
    "Business Development": ["BD Manager", "Partnership Lead"]
}
activity_templates = [
    "Meeting with clients",
    "Team collaboration",
    "Customer retention strategy",
    "Product brainstorming session",
    "Financial forecasting and budgeting",
    "Internal review and documentation",
    "Data reporting and analysis"
]

# Generate 1000 rows
start_date = datetime(2020, 1, 1)
rows = []
for i in range(1000):
    dept = random.choice(departments)
    job = random.choice(job_titles[dept])
    name = fake.name()
    employee_id = f"E{1000 + i:04d}"
    week_number = random.randint(1, 52)
    num_meetings = random.randint(0, 10)
    sales = round(random.uniform(5000, 30000), 2)
    hours_worked = round(random.uniform(30, 60), 1)
    activity = random.choice(activity_templates)
    hire_date = start_date + timedelta(days=random.randint(0, 1500))
    email = fake.email()

    stmt = f"""INSERT INTO activities 
(employee_id, full_name, week_number, num_meetings, total_sales_rmb, hours_worked, activities, department, hire_date, email, job_title) 
VALUES 
('{employee_id}', '{name.replace("'", "''")}', {week_number}, {num_meetings}, {sales}, {hours_worked}, '{activity}', '{dept}', '{hire_date.date()}', '{email}', '{job}');"""
    rows.append(stmt)

# Save to sample_data.sql
output_path = Path("sample_data.sql")
output_path.write_text("\n".join(rows), encoding="utf-8")

"✅ Generated 1000 INSERT statements to sample_data.sql"
