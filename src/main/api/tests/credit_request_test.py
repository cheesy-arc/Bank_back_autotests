import pytest
from requests import Session

from src.main.api.classes.api_manager import ApiManger
from src.main.api.models.create_user_request import CreateCreditUserRequest, CreateUserRequest
from src.main.api.models.credit_request import CreditRequest
from src.main.api.db.crud.credit_crud import CreditCrudDb as Credit
from src.main.api.generators.model_generator import RandomModelGenerator


@pytest.mark.api
class TestCreditRequest:
    def test_credit_request_valid_user(self, api_manager: ApiManger, create_credit_user_request: CreateCreditUserRequest, db_session: Session, create_account_credit_user):

        credit_request = RandomModelGenerator.generate(CreditRequest, accountId=create_account_credit_user.id,)
        credit_request_response = api_manager.user_steps.credit_request(credit_request, create_credit_user_request)
        assert credit_request_response.id == create_account_credit_user.id, "Кредит создан не на тот счёт"

        credit_from_db = Credit.get_credit_by_id(db_session, credit_request_response.creditId)
        assert credit_from_db.account_id == create_account_credit_user.id, "Кредит не создан в БД, или принядлежит другому счёту"

    def test_credit_request_invalid_user(self, api_manager: ApiManger, create_user_request: CreateUserRequest, create_account):

        credit_request = RandomModelGenerator.generate(CreditRequest, accountId=create_account.id)
        credit_request_response = api_manager.user_steps.credit_invalid_request_(credit_request, create_user_request)
        assert credit_request_response.json().get("detail") == "Forbidden: ROLE_CREDIT access required", "Кредит был создан или текст ошибки не соответствует ожиданиям"

