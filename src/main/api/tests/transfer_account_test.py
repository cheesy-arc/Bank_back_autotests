import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManger
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.transfer_accounts_request import TransferAccountRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction

@pytest.mark.api
class TestTransferAccount:
    def test_transfer_valid_amount(self, api_manager: ApiManger, create_user_request: CreateUserRequest, db_session: Session):
        deposit_amount = 1000
        transfer_amount = 500.75

        account_response_1 = api_manager.user_steps.create_account(create_user_request)
        account_id_1 = account_response_1.id
        account_response_2 = api_manager.user_steps.create_account(create_user_request)
        account_id_2 = account_response_2.id
        deposit_account_request = DepositAccountRequest(accountId=account_id_1, amount=deposit_amount)
        api_manager.user_steps.deposit_account(deposit_account_request, create_user_request)
        transfer_account_request = TransferAccountRequest(fromAccountId=account_id_1, toAccountId=account_id_2, amount=transfer_amount)
        transfer_account_response = api_manager.user_steps.transfer_account(transfer_account_request, create_user_request)
        leftover = deposit_amount - transfer_amount

        assert transfer_account_response.fromAccountIdBalance == leftover, "Неверный остаток после перевода"

        transaction_from_db = Transaction.get_transaction_by_amount(db_session, amount=transfer_amount)
        assert transaction_from_db.from_account_id == account_id_1, "Транзакция отсутсвует в БД или не принадлежит счёту"
        assert transaction_from_db.to_account_id == account_id_2, "Транзакция отсутсвует в БД или не принадлежит счёту"



    def test_transfer_invalid_amount(self, api_manager: ApiManger, create_user_request: CreateUserRequest, db_session: Session):
        deposit_amount = 1000
        transfer_amount = 2000

        account_response_1 = api_manager.user_steps.create_account(create_user_request)
        account_id_1 = account_response_1.id
        account_response_2 = api_manager.user_steps.create_account(create_user_request)
        account_id_2 = account_response_2.id
        deposit_account_request = DepositAccountRequest(accountId=account_id_1, amount=deposit_amount)
        api_manager.user_steps.deposit_account(deposit_account_request, create_user_request)
        transfer_account_request = TransferAccountRequest(fromAccountId=account_id_1, toAccountId=account_id_2, amount=transfer_amount)
        transfer_account_response = api_manager.user_steps.transfer_account_insufficient_funds(transfer_account_request, create_user_request)

        assert transfer_account_response.json().get('error') == f"Insufficient funds. Current balance: {deposit_amount}.00, required: {transfer_amount}.00"

        transaction_from_db = Transaction.get_transaction_by_amount(db_session, amount=transfer_amount)
        assert transaction_from_db is None, "Транзакция совершилась, ошибка"