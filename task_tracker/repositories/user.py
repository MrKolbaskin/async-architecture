from typing import List, Tuple

from domain.user import User

from . import get_db_conn


def get_all_users() -> List[User]:
    conn = get_db_conn()

    with conn.cursor() as cursor:
        cursor.execute("select id, username from users")

        rows: List[Tuple[int, str]] = cursor.fetchall()  # type: ignore

        users = [User(id=row[0], username=row[1]) for row in rows]

    conn.close()

    return users


def get_user_by_id(id: int) -> User:
    conn = get_db_conn()

    with conn.cursor() as cursor:
        cursor.execute("select id, username from users where id=%s", (id,))

        res: Tuple[int, str] = cursor.fetchone()  # type: ignore

        user = User(id=res[0], username=res[1])

    conn.close()

    return user


def get_user_by_username(username: str) -> User:
    conn = get_db_conn()

    with conn.cursor() as cursor:
        cursor.execute("select id, username from users where username=%s", (username,))

        res: Tuple[int, str] = cursor.fetchone()  # type: ignore

        user = User(id=res[0], username=res[1])

    conn.close()

    return user


def create_user(username: str) -> None:
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("insert into users (username) values (%s)", (username,))

    conn.commit()
