import pandas as pd
import openai
import sqlite3
import hashlib
from datetime import datetime, timedelta

# ============= CONFIGURATIONS =============
openai.api_key = "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"
CACHE_DB = "cache.db"  # SQLite Database for caching
CACHE_EXPIRY = timedelta(minutes=10)  # Cache expiry time

# ============= CACHE SETUP =============
# Initialize cache table
conn = sqlite3.connect(CACHE_DB)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cache (
        cache_key TEXT PRIMARY KEY,
        response TEXT,
        timestamp DATETIME
    )
''')
conn.commit()
conn.close()

# ============= CACHE FUNCTIONS =============
def get_cache_key(question, data_str):
    """Generate a unique cache key using a hash of the question and data."""
    cache_key = hashlib.md5((question + data_str).encode()).hexdigest()
    return cache_key


def get_from_cache(cache_key):
    """Retrieve the cached response if it exists and hasn't expired."""
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT response, timestamp FROM cache WHERE cache_key = ?
    ''', (cache_key,))
    row = cursor.fetchone()
    conn.close()

    if row:
        response, timestamp = row
        timestamp = datetime.fromisoformat(timestamp)
        if datetime.now() - timestamp < CACHE_EXPIRY:
            return response
    return None


def set_cache(cache_key, response):
    """Store the response in cache with the current timestamp."""
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO cache (cache_key, response, timestamp) VALUES (?, ?, ?)
    ''', (cache_key, response, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# ============= LLM INTERACTION =============
def ask_llm(question, context_df):
    """Sends a query to OpenAI's API with the entire raw employee data."""
    context_str = context_df.to_string(index=False)
    cache_key = get_cache_key(question, context_str)
    cached_response = get_from_cache(cache_key)
    if cached_response:
        print("⚡ Using cached response")
        return cached_response

    prompt = (
        f"### Question ###\n{question}\n\n"
        f"### Employee Data ###\n{context_str}\n\n"
        f"### Instructions ###\n"
        f"- Analyze the employee data to answer the question.\n"
        f"- Format the output in plain text without any special characters.\n"
        f"- Ensure the response is accurate and consistent."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant analyzing employee data."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        llm_response = response["choices"][0]["message"]["content"]

        print("\n### Answer ###")
        print(llm_response)

        # Ask for user confirmation before caching
        user_feedback = input("\nIs the above response correct? (yes/no): ").strip().lower()
        if user_feedback == "yes":
            set_cache(cache_key, llm_response)
            print("✅ Response cached.")
        else:
            print("❌ Response not cached. Please rephrase your question.")

        return llm_response

    except openai.error.OpenAIError as e:
        print(f"Error interacting with OpenAI API: {e}")
        return "An error occurred while processing your request."

# ============= MAIN FLOW =============
def main():
    df_employees = pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6],
        "name": ["Alice", "Bob", "Charlie", "Harry", "Sam", "David"],
        "department": ["HR", "Engineering", "Finance", "Finance", "Engineering", "HR"],
        "salary": [50000, 60000, 55000, 40000, 70000, 60000]
    })

    print("\nWelcome to Employee Data Analyzer!")
    print("Ask a question about the employee data or type 'exit' to quit.")

    while True:
        question = input("\nYour question: ").strip()
        if question.lower() == 'exit':
            print("Exiting... Have a great day!")
            break

        response = ask_llm(question, df_employees)

if __name__ == "__main__":
    main()
