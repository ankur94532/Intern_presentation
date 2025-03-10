import pandas as pd
import openai
from use_database_table import EmployeeTable

# Set your OpenAI API key (Replace 'your-api-key' with your actual key)
openai.api_key = "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"

def preprocess_context(context_df):
    """Extracts unique department names from the DataFrame."""
    distinct_departments = context_df['department'].unique()
    return distinct_departments

def ask_llm(question, context_df):
    "Sends a query to OpenAI's API with structured context."

    # Preprocess context to ensure it's concise
    context_df = preprocess_context(context_df)
    context_df = pd.DataFrame(context_df)

    # Create a string representation of the context
    context_str = context_df.to_string(index=False)

    # Create a structured prompt
    prompt = (
        f"### Question ###\n{question}\n\n"
        f"### Employee Data ###\n{context_str}\n\n"
        f"### Instructions ###\n"
        f"- Provide a structured summary.\n"
        f"- Ensure accuracy in identifying department-specific details.\n"
        f"- If data is insufficient, state that explicitly.\n"
    )

    # Call OpenAI API for completion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use a better model if needed
        messages=[{"role": "system", "content": "You are an AI assistant analyzing employee data."},
                  {"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.5
    )

    return response["choices"][0]["message"]["content"]

# Fetch data from the employees table
connection_string = 'sqlite:///example.db'
employee_table = EmployeeTable(connection_string)
df_employees = employee_table.fetch_data()
# Ensure the dataframe has the required columns
assert 'id' in df_employees.columns, "Column 'id' not found in the DataFrame"
assert 'name' in df_employees.columns, "Column 'name' not found in the DataFrame"
assert 'department' in df_employees.columns, "Column 'department' not found in the DataFrame"
assert 'salary' in df_employees.columns, "Column 'salary' not found in the DataFrame"

# Ask LLM a question
question = "Find the distinct departments."
response = ask_llm(question, df_employees)
print(response)