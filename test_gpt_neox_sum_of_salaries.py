import pandas as pd
import openai
import sqlite3
from use_database_table import EmployeeTable
# Set your OpenAI API key (Replace 'your-api-key' with your actual key)
openai.api_key = "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"

def remove_duplicates():
    """Removes duplicate employee records while keeping the lowest ID."""
    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()

    query = """
    DELETE FROM employees
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM employees
        GROUP BY name, department, salary
    );
    """
    cursor.execute(query)
    conn.commit()
    
    # Fetch cleaned data
    df_cleaned = pd.read_sql("SELECT * FROM employees", conn)
    conn.close()
    
    return df_cleaned

def ask_llm(question, context_df):
    """Sends a query to OpenAI's API with the entire raw employee data."""

    # Convert DataFrame to string format (excluding index)
    context_str = context_df.to_string(index=False)

    # Improved structured prompt
    prompt = (
        f"### Question ###\nCalculate the total salary expenditure for each department based on the given employee data.\n\n"
        f"### Employee Data ###\n{context_str}\n\n"
        f"### Instructions ###\n"
        f"- Group employees by department.\n"
        f"- Sum the salaries of employees within each department.\n"
        f"- Output format should be strictly plain text without special characters like '**' or '-' or extra formatting.\n"
        f"- Each department should appear only once in the final output.\n"
    )


    # Call OpenAI API for response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant analyzing employee data."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.5
    )

    return response["choices"][0]["message"]["content"]

# Remove duplicates before querying
df_employees = remove_duplicates()

# Ensure the dataframe has required columns
required_columns = {'id', 'name', 'department', 'salary'}
assert required_columns.issubset(df_employees.columns), "Missing required columns in DataFrame"

# Ask GPT to determine the highest earners
question = "Calculate the total salary expenditure for each department based on the provided employee data."
response = ask_llm(question, df_employees)
print(response)