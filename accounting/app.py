from threading import Thread

from fastapi import FastAPI
from fastapi_utilities import repeat_at

import repositories as repo
from domain import Account, EmptyBalancePaymentError, Transaction
from jobs import sync_accounts
from jobs.task import sync_account_balance

sync_accounts_job = Thread(target=sync_accounts, name="sync_accounts_job")
sync_accounts_job.start()

sync_accounts_balance_job = Thread(target=sync_account_balance, name="sync_accounts_balance_job")
sync_accounts_balance_job.start()


def send_payment_msg(account: Account, transaction: Transaction) -> None:
    # function to sending mail about payment
    pass


@repeat_at(cron="0 1 * * *")
async def payments() -> None:
    accounts = repo.get_all_accounts()
    for account in accounts:
        try:
            transaction = account.payment()
        except EmptyBalancePaymentError:
            continue

        repo.create_transaction(account, transaction)
        repo.save_account(account)
        send_payment_msg(account, transaction)


app = FastAPI()
