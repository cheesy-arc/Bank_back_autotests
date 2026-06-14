import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManger
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest


@pytest.mark.api
class TestDepositAccount:
    def test_deposit_account(self, api_manager: ApiManger, db_session: Session, create_user_request: CreateUserRequest, create_account):

        deposit_request = RandomModelGenerator.generate(DepositAccountRequest, accountId=create_account.id)
        deposit_response = api_manager.user_steps.deposit_account(deposit_request, create_user_request)

        assert deposit_response.balance == deposit_request.amount, "Баланс не соответствует изначальной сумме перевода"

        account_from_db = Account.get_account_by_id(db_session, deposit_response.id)
        assert account_from_db.balance == deposit_request.amount, "В БД не сохранилась запись о балансе аккаунта"


    def test_deposit_account_without_token(self, api_manager: ApiManger, db_session: Session, create_account):

        deposit_request = RandomModelGenerator.generate(DepositAccountRequest, accountId=create_account.id)
        deposit_response = api_manager.user_steps.deposit_account_without_token(deposit_request)

        assert deposit_response.json().get("message") == "JWT Token not found"

        account_from_db = Account.get_account_by_id(db_session, create_account.id)
        assert account_from_db.balance == 0, "Баланс пополнен, ошибка"