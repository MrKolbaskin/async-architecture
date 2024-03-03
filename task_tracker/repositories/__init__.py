import psycopg2


def get_db_conn():
    return psycopg2.connect("host=localhost dbname=task-tracker user=postgres password=postgres")
