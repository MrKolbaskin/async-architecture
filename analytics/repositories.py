from typing import Tuple

import psycopg2


def get_db_conn():
    return psycopg2.connect("host=localhost dbname=task-tracker user=postgres password=postgres")


def get_analytics() -> list[dict]:
    conn = get_db_conn()

    with conn.cursor() as cursor:
        cursor.execute("select day, cost from analytics_data")

        rows: list[Tuple[str, float]] = cursor.fetchall()  # type: ignore

        res = [{"day": row[0], "cost": row[1]} for row in rows]

    conn.close()

    return res


def get_cost_by_day(day: str) -> float:
    conn = get_db_conn()

    with conn.cursor() as cursor:
        cursor.execute("select cost from analytics_data where day=%s", (day,))
        raw_res: Tuple[float] = cursor.fetchone()  # type: ignore
        res: float = raw_res[0] if raw_res else 0

    conn.close()

    return res


def insert_cost_by_day(day: str, cost: float) -> None:
    conn = get_db_conn()
    cursor = conn.cursor()

    if get_cost_by_day(day) > 0:
        cursor.execute("update analytics_data set cost=%s where day=%s", (cost, day))
    else:
        cursor.execute(
            "insert into analytics_data (day, cost) values (%s, %s)",
            (day, cost),
        )

    conn.commit()


def insert_data() -> list[dict]:
    conn = get_db_conn()

    with conn.cursor() as cursor:
        cursor.execute("select day, cost from analytics_data")

        rows: list[Tuple[str, float]] = cursor.fetchall()  # type: ignore

        res = [{"day": row[0], "cost": row[1]} for row in rows]

    conn.close()

    return res
