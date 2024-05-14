import pyodbc
import os

driver= '{ODBC Driver 17 for SQL Server}'
server = os.getenv('SQL_SERVER')
database = os.getenv('SQL_DATABASE')
username = os.getenv('SQL_USER')
password = os.getenv('SQL_PASSWORD')

conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

try:
    connection = pyodbc.connect(conn_str)
    print("Connection successful!")
    connection.close()
except Exception as e:
    print(f"Error connecting: {str(e)}")