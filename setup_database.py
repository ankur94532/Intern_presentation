import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Create the employees table
cursor.execute('''
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    salary REAL NOT NULL
)
''')

# Insert sample employee data
employee_data = [
    ('Alice', 'HR', 50000),
    ('Bob', 'Engineering', 60000),
    ('Charlie', 'Finance', 55000),
    ('Harry','Finance',40000),
    ('Sam','Engineering',70000),
    ('David','HR',60000)
]

cursor.executemany('''
INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)
''', employee_data)

# Commit changes and close the connection
conn.commit()
conn.close()
