import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

def cursor():
    db_conn = psycopg2.connect(DATABASE_URL, sslmode='allow')
    db_conn.autocommit = True
    return db_conn.cursor()

def print_log_line(log_line):
    cur = cursor()
    cur.execute('INSERT INTO LOGS (LOG_LINE, TIME) VALUES (%s, NOW())', (log_line,))

