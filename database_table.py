import pandas as pd
from sqlalchemy import create_engine

class DatabaseTable:
    def __init__(self, table_name, connection_string):
        self.table_name = table_name
        self.engine = create_engine(connection_string)

    def fetch_data(self):
        query = f"SELECT * FROM {self.table_name}"
        return pd.read_sql(query, self.engine)
