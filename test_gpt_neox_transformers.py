import pandas as pd
from transformers import pipeline
from use_database_table import EmployeeTable

# Initialize the LLM using pipeline with a smaller model
pipe = pipeline("text-generation", model="gpt2-medium")

def preprocess_context(context_df):
    # Find the unique departments
    distinct_departments = context_df['department'].unique()
    return distinct_departments

def ask_llm(question, context_df):
    # Preprocess context to ensure it's concise
    context_df = preprocess_context(context_df)
    context_df = pd.DataFrame(context_df)
    # Create a string representation of the context
    context_str = context_df.to_string(index=False)
    
    # Create a prompt for the LLM
    prompt = f"{question}\n\n{context_str}\n\nPlease provide a summary based on the above information."
    
    # Generate a response using the LLM
    response = pipe(prompt, max_length=100, num_return_sequences=1, truncation=True)
    return response[0]['generated_text']

# Fetch data from the employees table
connection_string = 'sqlite:///example.db'
employee_table = EmployeeTable(connection_string)
df_employees = employee_table.fetch_data()

# Ensure the dataframe has the right columns
assert 'id' in df_employees.columns, "Column 'id' not found in the DataFrame"
assert 'name' in df_employees.columns, "Column 'name' not found in the DataFrame"
assert 'department' in df_employees.columns, "Column 'department' not found in the DataFrame"
assert 'salary' in df_employees.columns, "Column 'salary' not found in the DataFrame"

# Analyze data with the LLM
question = "find the distinct departments"
response = ask_llm(question, df_employees)
print(response)
import pandas as pd
from transformers import pipeline
from use_database_table import EmployeeTable

def fetch_data_from_table(table_name, connection_string):
    # Initialize the table object and fetch data
    table = EmployeeTable(connection_string)
    return table.fetch_data()

# Initialize the LLM using pipeline with a smaller model
pipe = pipeline("text-generation", model="gpt2-medium")

def ask_llm(question, context):
    # Convert context to string
    context_str = context.to_string(index=False)
    prompt = f"{question}\n\nContext:\n{context_str}"
    response = pipe(prompt, max_length=150, num_return_sequences=1, truncation=True)
    return response[0]['generated_text']

def main():
    connection_string = 'sqlite:///example.db'
    table_name = 'employees'
    
    # Fetch data from the employees table
    context_df = fetch_data_from_table(table_name, connection_string)
    
    # Ask the LLM a question directly
    question = "Find the highest paid employee with names for each department."
    response = ask_llm(question, context_df)
    print(response)

if __name__ == "__main__":
    main()