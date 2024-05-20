from urllib.parse import quote_plus
import os 
import pyodbc
import warnings

warnings.filterwarnings("ignore")
def get_db_connection():
    driver= '{ODBC Driver 17 for SQL Server}'
    server = os.getenv('SQL_SERVER')
    database = os.getenv('SQL_DATABASE')
    username = os.getenv('SQL_USER')
    password = os.getenv('SQL_PASSWORD')

    conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    return pyodbc.connect(conn_str)