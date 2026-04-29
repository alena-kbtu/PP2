import psycopg2
from config import load_config

def connect():
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

if __name__ == '__main__':
    connection = connect()
    if connection:
        print('Connection established.')
        connection.close()