from database_table import DatabaseTable

# Define the table name and connection string
table_name = "employees"
connection_string = "sqlite:///example.db"  # SQLite connection string

# Create an instance of the DatabaseTable class
db_table = DatabaseTable(table_name, connection_string)

# Fetch data from the table
data = db_table.fetch_data()

# Display the data
print(data)
class EmployeeTable(DatabaseTable):
    def __init__(self, connection_string):
        super().__init__('employees', connection_string)
        self.metadata = {
            'table_name': 'employees',
            'description': 'Employee details and payroll information',
            'columns': {
                'id': 'Employee ID',
                'name': 'Employee Name',
                'department': 'Department Name',
                'salary': 'Salary of the Employee'
            }
        }
