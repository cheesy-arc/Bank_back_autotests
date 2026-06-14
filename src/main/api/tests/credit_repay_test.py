import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManger
from src.main.api.models.create_user_request import CreateCreditUserRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction


@pytest.mark.api
class TestCreditRequest:
    def test_credit_repay(self, api_manager: ApiManger, create_credit_user_request: CreateCreditUserRequest, db_session: Session, create_account_credit_user, credit_create):

        credit_repay_request = CreditRepayRequest(creditId=credit_create.creditId, accountId=create_account_credit_user.id, amount=credit_create.amount)
        credit_repay_response = api_manager.user_steps.credit_repay_request(credit_repay_request, create_credit_user_request)

        assert credit_repay_response.creditId == credit_create.creditId, "Кредит не погашен или погашение для другого кредита"
        assert credit_repay_response.amountDeposited == credit_create.amount, "Сумма погашения не соответствует размеру кредита"

        transaction_from_db = Transaction.get_transaction_by_amount(db_session, credit_create.amount)
        assert transaction_from_db.credit_id == credit_create.creditId, "Транзакция не относится к погашаемому кредиту"

    def test_credit_repay_unsufficient_amount(self, api_manager: ApiManger, create_credit_user_request: CreateCreditUserRequest, db_session: Session, create_account_credit_user, credit_create):
        credit_repay_unsufficient_amount = 1000

        credit_repay_request = CreditRepayRequest(creditId=credit_create.creditId, accountId=create_account_credit_user.id, amount=credit_repay_unsufficient_amount)
        credit_repay_response = api_manager.user_steps.credit_repay_insufficient_request(credit_repay_request, create_credit_user_request)

        assert credit_repay_response.json().get("error") == f"The amount is not enough. Credit balance: -{int(credit_create.amount)}", "Кредит погашен или текст ошибки не соответсвует ожиданиям"

        transaction_from_db = Transaction.get_transaction_by_amount(db_session, credit_create.amount)
        assert transaction_from_db.credit_id is None, "Транзакция погасила кредит, ошибка"