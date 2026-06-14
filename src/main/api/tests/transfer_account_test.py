import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManger
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.transfer_accounts_request import TransferAccountRequest
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction

@pytest.mark.api
class TestTransferAccount:
    def test_transfer_valid_amount(self, api_manager: ApiManger, create_user_request: CreateUserRequest, db_session: Session, create_account, create_second_account, deposit_account):
        deposit_amount = 1000
        transfer_amount = 500.75

        transfer_account_request = TransferAccountRequest(fromAccountId=create_account.id, toAccountId=create_second_account.id, amount=transfer_amount)
        transfer_account_response = api_manager.user_steps.transfer_account(transfer_account_request, create_user_request)
        leftover = deposit_amount - transfer_amount

        assert transfer_account_response.fromAccountIdBalance == leftover, "Неверный остаток после перевода"

        transaction_from_db = Transaction.get_transaction_by_amount(db_session, amount=transfer_amount)
        assert transaction_from_db.from_account_id == create_account.id, "Транзакция отсутсвует в БД или не принадлежит счёту"
        assert transaction_from_db.to_account_id == create_second_account.id, "Транзакция отсутсвует в БД или не принадлежит счёту"

    def test_transfer_invalid_amount(self, api_manager: ApiManger, create_user_request: CreateUserRequest, db_session: Session, create_account, create_second_account, deposit_account):
        deposit_amount = 1000
        transfer_amount = 2000

        transfer_account_request = TransferAccountRequest(fromAccountId=create_account.id, toAccountId=create_second_account.id, amount=transfer_amount)
        transfer_account_response = api_manager.user_steps.transfer_account_insufficient_funds(transfer_account_request, create_user_request)

        assert transfer_account_response.json().get('error') == f"Insufficient funds. Current balance: {deposit_amount}.00, required: {transfer_amount}.00"

        transaction_from_db = Transaction.get_transaction_by_amount(db_session, amount=transfer_amount)
        assert transaction_from_db is None, "Транзакция совершилась, ошибка"