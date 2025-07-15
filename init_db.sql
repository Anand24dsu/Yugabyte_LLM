-- Drop table if exists
DROP TABLE IF EXISTS activities;

-- Create main employee activity tracking table
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(20) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    week_number INT NOT NULL,
    num_meetings INT DEFAULT 0,
    total_sales_rmb DECIMAL(10, 2) DEFAULT 0.00,
    hours_worked DECIMAL(5, 1) DEFAULT 0.0,
    activities TEXT,
    department VARCHAR(50),
    hire_date DATE,
    email VARCHAR(100),
    job_title VARCHAR(100)
);

-- Optional indexes for performance
CREATE INDEX idx_employee_id ON activities(employee_id);
CREATE INDEX idx_department ON activities(department);
CREATE INDEX idx_week_number ON activities(week_number);
CREATE INDEX idx_hire_date ON activities(hire_date);
