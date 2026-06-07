import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManger
from src.main.api.models.create_user_request import CreateCreditUserRequest
from src.main.api.models.credit_request import CreditRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction


@pytest.mark.api
class TestCreditRequest:
    def test_credit_repay(self, api_manager: ApiManger, create_credit_user_request: CreateCreditUserRequest, db_session: Session):
        credit_amount = 5000
        term_months = 12

        create_account_response = api_manager.user_steps.create_account(create_credit_user_request)
        account_id = create_account_response.id
        credit_request = CreditRequest(accountId=account_id, amount=credit_amount, termMonths=term_months)
        credit_request_response = api_manager.user_steps.credit_request(credit_request, create_credit_user_request)
        credit_id = credit_request_response.creditId
        credit_repay_request = CreditRepayRequest(creditId=credit_id, accountId=account_id, amount=credit_amount)
        credit_repay_response = api_manager.user_steps.credit_repay_request(credit_repay_request, create_credit_user_request)

        assert credit_repay_response.creditId == credit_id, "Кредит не погашен или погашение для другого кредита"
        assert credit_repay_response.amountDeposited == credit_amount, "Сумма погашения не соответствует размеру кредита"

        transaction_from_db = Transaction.get_transaction_by_amount(db_session, credit_amount)
        assert transaction_from_db.credit_id == credit_id, "Транзакция не относится к погашаемому кредиту"


    def test_credit_repay_unsufficient_amount(self, api_manager: ApiManger, create_credit_user_request: CreateCreditUserRequest, db_session):
        credit_amount = 5000
        term_months = 12
        credit_repay_unsufficient_amount = 1000

        create_account_response = api_manager.user_steps.create_account(create_credit_user_request)
        account_id = create_account_response.id
        credit_request = CreditRequest(accountId=account_id, amount=credit_amount, termMonths=term_months)
        credit_request_response = api_manager.user_steps.credit_request(credit_request, create_credit_user_request)
        credit_id = credit_request_response.creditId
        credit_repay_request = CreditRepayRequest(creditId=credit_id, accountId=account_id, amount=credit_repay_unsufficient_amount)
        credit_repay_response = api_manager.user_steps.credit_repay_insufficient_request(credit_repay_request, create_credit_user_request)

        assert credit_repay_response.json().get("error") == f"The amount is not enough. Credit balance: -{credit_amount}", "Кредит погашен или текст ошибки не соответсвует ожиданиям"

        transaction_from_db = Transaction.get_transaction_by_amount(db_session, credit_amount)
        assert transaction_from_db.credit_id is None, "Транзакция погасила кредит, ошибка"