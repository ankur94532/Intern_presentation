import pandas as pd
import openai
import sqlite3
import hashlib
from datetime import datetime, timedelta

# ============= CONFIGURATIONS =============
# Securely load your OpenAI API key from environment variable
openai.api_key = "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"

CACHE_DB = "cache.db"  # SQLite database for caching
CACHE_EXPIRY = timedelta(minutes=10)  # Cache expiry time

# ============= CACHE SETUP =============
def init_cache_db():
    """Initialize the SQLite cache table if it doesn't exist."""
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            cache_key TEXT PRIMARY KEY,
            response TEXT,
            expiry TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def get_cache_key(question, data_str):
    """Generate a unique cache key using a hash of the question and data."""
    cache_key = hashlib.md5((question + data_str).encode()).hexdigest()
    return cache_key

def get_from_cache(cache_key):
    """Retrieve the cached response if it exists and hasn't expired."""
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT response, expiry FROM cache WHERE cache_key = ?;
    """, (cache_key,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        response, expiry = result
        if datetime.now() < datetime.fromisoformat(expiry):
            return response
        else:
            delete_cache(cache_key)  # Expire old cache
    return None

def set_cache(cache_key, response):
    """Store the response in cache with an expiry time."""
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    
    expiry_time = (datetime.now() + CACHE_EXPIRY).isoformat()
    cursor.execute("""
        INSERT OR REPLACE INTO cache (cache_key, response, expiry)
        VALUES (?, ?, ?);
    """, (cache_key, response, expiry_time))
    
    conn.commit()
    conn.close()

def delete_cache(cache_key):
    """Delete expired cache entries."""
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cache WHERE cache_key = ?;", (cache_key,))
    conn.commit()
    conn.close()

# ============= DATA CLEANING =============
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

# ============= LLM INTERACTION =============
def ask_llm(question, context_df):
    """Sends a query to OpenAI's API with the entire raw employee data."""

    # Convert DataFrame to string format (excluding index)
    context_str = context_df.to_string(index=False)
    
    # Check if response is already cached
    cache_key = get_cache_key(question, context_str)
    cached_response = get_from_cache(cache_key)
    if cached_response:
        print("⚡ Using cached response")
        return cached_response

    # Improved structured prompt
    prompt = (
        f"### Question ###\n{question}\n\n"
        f"### Employee Data ###\n{context_str}\n\n"
        f"### Instructions ###\n"
        f"- Analyze the employee data to answer the question.\n"
        f"- Format the output in plain text without any special characters.\n"
        f"- Ensure the response is accurate and consistent."
    )

    try:
        # Call OpenAI API for response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant analyzing employee data."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3  # Lowered for more consistent responses
        )

        # Extract the content from the response
        llm_response = response["choices"][0]["message"]["content"]
        
        # Store in cache
        set_cache(cache_key, llm_response)
        
        return llm_response
    
    except openai.error.OpenAIError as e:
        print(f"Error interacting with OpenAI API: {e}")
        return "An error occurred while processing your request. Please try again later."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "An unexpected error occurred."

# ============= MAIN FLOW =============
def main():
    # Initialize SQLite cache
    init_cache_db()

    # Remove duplicates before querying
    df_employees = remove_duplicates()

    # Ensure the dataframe has required columns
    required_columns = {'id', 'name', 'department', 'salary'}
    assert required_columns.issubset(df_employees.columns), "Missing required columns in DataFrame"

    # Dynamic query input
    print("\nWelcome to Employee Data Analyzer!")
    print("Ask a question about the employee data or type 'exit' to quit.")
    
    while True:
        question = input("\nYour question: ")
        if question.lower() == 'exit':
            print("Exiting... Have a great day!")
            break
        
        # Get response from LLM
        response = ask_llm(question, df_employees)
        print("\n### Answer ###")
        print(response)

# ============= ENTRY POINT =============
if __name__ == "__main__":
    main()
