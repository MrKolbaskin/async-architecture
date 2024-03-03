from typing import List, Tuple

from domain.task import Task, TaskStatus, User

from . import get_db_conn
from .user import get_user_by_id


def get_all_uncompleted_tasks() -> List[Task]:
    conn = get_db_conn()

    with conn.cursor() as cursor:
        cursor.execute("select id, status, assignee, description from tasks where status=%s", (TaskStatus.TODO,))

        rows: List[Tuple[int, str, int, str]] = cursor.fetchall()  # type: ignore

        tasks = [
            Task(id=row[0], status=TaskStatus(row[1]), assignee=get_user_by_id(row[2]), description=row[3])
            for row in rows
        ]

    conn.close()

    return tasks


def get_task_by_id(task_id: int) -> Task:
    conn = get_db_conn()

    with conn.cursor() as cursor:
        cursor.execute("select id, status, assignee, description from tasks where id=%s", (task_id,))

        row: Tuple[int, str, int, str] = cursor.fetchone()  # type: ignore

        task = Task(id=row[0], status=TaskStatus(row[1]), assignee=get_user_by_id(row[2]), description=row[3])

    conn.close()

    return task


def save(task: Task) -> None:
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("update tasks set status=%s, assignee=%s where id=%s", (task.status, task.assignee.id, task.id))

    conn.commit()


def create_task(description: str, assignee: User) -> None:
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute(
        "insert into tasks (status, assignee, description) values (%s, %s, %s)",
        (TaskStatus.TODO, assignee.id, description),
    )

    conn.commit()
