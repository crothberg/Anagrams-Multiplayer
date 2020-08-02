import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
db = psycopg2.connect(DATABASE_URL, sslmode='allow')
db.autocommit = True

def print_log_line(log_line):
    cur = db.cursor()
    cur.execute('INSERT INTO LOGS (LOG_LINE, TIME) VALUES (%s, NOW())', (log_line,))

