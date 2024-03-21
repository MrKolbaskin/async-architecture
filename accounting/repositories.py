from typing import Tuple
from uuid import UUID

import psycopg2

from domain import Account, Transaction


def get_db_conn():
    return psycopg2.connect("host=localhost dbname=accounting user=postgres password=postgres")


def create_transaction(account: Account, transaction: Transaction) -> None:
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute(
        "insert into transactions (id, cost, type, account) values (%s, %s, %s, %s)",
        (str(transaction.id), transaction.cost, transaction.type_, str(account.id)),
    )

    conn.commit()


def create_account(account: Account) -> None:
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute(
        "insert into accounts (id, username, balance) values (%s, %s, %s)",
        (str(account.id), account.username, account.balance),
    )

    conn.commit()


def save_account(account: Account) -> None:
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("update accounts set balance=%s where id=%s", (account.balance, str(account.id)))

    conn.commit()


def get_account_by_username(username: str) -> Account:
    conn = get_db_conn()

    with conn.cursor() as cursor:
        cursor.execute("select id, username, balance from accounts where username=%s", (username,))

        res: Tuple[str, str, float] = cursor.fetchone()  # type: ignore

        account = Account(id=UUID(res[0]), username=res[1], balance=res[2])

    conn.close()

    return account


def get_all_accounts() -> list[Account]:
    conn = get_db_conn()

    with conn.cursor() as cursor:
        cursor.execute("select id, username, balance from accounts")

        rows: list[Tuple[str, str, float]] = cursor.fetchall()  # type: ignore

        accounts = [Account(id=UUID(row[0]), username=row[1], balance=row[2]) for row in rows]

    conn.close()

    return accounts
