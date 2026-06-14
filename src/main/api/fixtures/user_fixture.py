import pytest

from src.main.api.fixtures.api_fixture import api_manager
from src.main.api.models.create_user_request import CreateUserRequest, CreateCreditUserRequest
from src.main.api.models.credit_request import CreditRequest
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.deposit_account_request import DepositAccountRequest


@pytest.fixture
def create_user_request(api_manager):
    user_request = RandomModelGenerator.generate(CreateUserRequest)
    api_manager.admin_steps.create_user(user_request)
    return user_request

@pytest.fixture
def create_credit_user_request(api_manager):
    user_request = RandomModelGenerator.generate(CreateCreditUserRequest)
    api_manager.admin_steps.create_credit_user(user_request)
    return user_request

@pytest.fixture
def create_account(api_manager, create_user_request):
    response = api_manager.user_steps.create_account(create_user_request)
    return response

@pytest.fixture
def create_second_account(api_manager, create_user_request):
    response = api_manager.user_steps.create_account(create_user_request)
    return response

@pytest.fixture
def create_account_credit_user(api_manager, create_credit_user_request):
    response = api_manager.user_steps.create_account(create_credit_user_request)
    return response

@pytest.fixture
def credit_create(api_manager, create_account_credit_user, create_credit_user_request):
    # credit_request = CreditRequest(accountId=create_account_credit_user.id, amount=5000, termMonths=12)
    credit_request = RandomModelGenerator.generate(CreditRequest, accountId=create_account_credit_user.id)
    response = api_manager.user_steps.credit_request(credit_request, create_credit_user_request)
    return response

@pytest.fixture
def deposit_account(api_manager, create_account, create_user_request):
    deposit_account_request = RandomModelGenerator.generate(DepositAccountRequest, accountId=create_account.id)
    response = api_manager.user_steps.deposit_account(deposit_account_request, create_user_request)
    return response



