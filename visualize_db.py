import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import psycopg2
from dotenv import load_dotenv
import openai

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Database connection (YugabyteDB via psycopg2)
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", 5433)),
    user=os.getenv("DB_USER", "yugabyte"),
    password=os.getenv("DB_PASSWORD", "yugabyte"),
    dbname=os.getenv("DB_NAME", "employee_tracking"),
)

# Load data
query = "SELECT * FROM activities"
df = pd.read_sql(query, conn)
conn.close()

# Output directory
output_dir = Path("./visualizations")
output_dir.mkdir(exist_ok=True)

# OpenAI summary function
def get_ai_summary(df: pd.DataFrame, chart_title: str) -> str:
    csv_data = df.to_csv(index=False)
    prompt = f"""You are a data analyst. Here's a dataset (in CSV format) used to create the chart titled: \"{chart_title}\". 
Analyze the data and summarize the key insights in a short paragraph.

CSV Data:
{csv_data}

Summary:"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful data analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI summary unavailable: {str(e)}"

# 1. Department Distribution
dept_counts = df["department"].value_counts().reset_index()
dept_counts.columns = ["department", "count"]
fig1 = px.bar(
    dept_counts,
    x="department",
    y="count",
    color="department",
    title="Employee Distribution by Department",
    labels={"count": "Number of Records"},
)
summary1 = get_ai_summary(dept_counts, "Employee Distribution by Department")
fig1.write_html(str(output_dir / "1_department_distribution.html"))
with open(output_dir / "1_department_distribution_summary.txt", "w") as f:
    f.write(summary1)
print("✅ Saved 1_department_distribution.html and summary")

# 2. Average Hours Worked by Employee
hours_by_emp = df.groupby("full_name")["hours_worked"].mean().reset_index()
fig2 = px.bar(
    hours_by_emp.sort_values("hours_worked", ascending=False),
    x="full_name",
    y="hours_worked",
    title="Average Hours Worked by Employee",
    labels={"hours_worked": "Average Hours"},
    color="hours_worked",
    color_continuous_scale="Magma",
)
fig2.add_hline(y=40, line_dash="dash", line_color="red", annotation_text="40h/week")
fig2.update_layout(xaxis_tickangle=45)
summary2 = get_ai_summary(hours_by_emp, "Average Hours Worked by Employee")
fig2.write_html(str(output_dir / "2_hours_by_employee.html"))
with open(output_dir / "2_hours_by_employee_summary.txt", "w") as f:
    f.write(summary2)
print("✅ Saved 2_hours_by_employee.html and summary")

# 3. Weekly Sales Performance (Sales Only)
sales_df = df[df["department"] == "Sales"]
if not sales_df.empty:
    pivot = sales_df.pivot_table(
        index="week_number", columns="full_name", values="total_sales_rmb", aggfunc="sum"
    )
    fig3 = go.Figure()
    for name in pivot.columns:
        fig3.add_trace(
            go.Scatter(
                x=pivot.index,
                y=pivot[name],
                mode="lines+markers",
                name=name
            )
        )
    fig3.update_layout(
        title="Weekly Sales Performance by Employee",
        xaxis_title="Week Number",
        yaxis_title="Total Sales (RMB)",
        template="plotly_white"
    )
    summary3 = get_ai_summary(sales_df, "Weekly Sales Performance by Employee")
    fig3.write_html(str(output_dir / "3_sales_performance.html"))
    with open(output_dir / "3_sales_performance_summary.txt", "w") as f:
        f.write(summary3)
    print("✅ Saved 3_sales_performance.html and summary")

# 4. Total Meetings by Employee and Department
meetings_df = df.groupby(["full_name", "department"])["num_meetings"].sum().reset_index()
fig4 = px.bar(
    meetings_df,
    x="full_name",
    y="num_meetings",
    color="department",
    title="Total Meetings by Employee and Department",
    labels={"num_meetings": "Total Meetings"},
)
fig4.update_layout(xaxis_tickangle=45)
summary4 = get_ai_summary(meetings_df, "Total Meetings by Employee and Department")
fig4.write_html(str(output_dir / "4_meetings_distribution.html"))
with open(output_dir / "4_meetings_distribution_summary.txt", "w") as f:
    f.write(summary4)
print("✅ Saved 4_meetings_distribution.html and summary")

# 5. Correlation Heatmap
numeric_df = df.select_dtypes(include="number")
if not numeric_df.empty:
    corr_matrix = numeric_df.corr().round(2)
    fig5 = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        title="Correlation Between Numeric Variables",
        aspect="auto"
    )
    summary5 = get_ai_summary(corr_matrix.reset_index(), "Correlation Between Numeric Variables")
    fig5.write_html(str(output_dir / "5_correlation_heatmap.html"))
    with open(output_dir / "5_correlation_heatmap_summary.txt", "w") as f:
        f.write(summary5)
    print("✅ Saved 5_correlation_heatmap.html and summary")

print("\n🎉 All visualizations and summaries saved to ./visualizations")
