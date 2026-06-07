### ./main/api/config/config.py
from pathlib import Path
from typing import Any

class Config:
    _isinstance = None
    _dictionary = {}

    def __new__(cls):
        if cls._isinstance is None:
            cls._isinstance = super(Config, cls).__new__(cls)

            config_path = Path(__file__).parents[4] / 'resources' / 'urls.properties'

            if not config_path.exists():
                raise FileNotFoundError(f"Config path not found: {config_path}")

            with open(config_path, "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.split("=")
                        cls._dictionary[key] = value.strip()

        return cls._isinstance

    @staticmethod
    def fetch(key: str, default_value: Any = None) -> Any:
        return Config()._dictionary.get(key, default_value)### ./main/api/classes/api_manager.py
from typing import List, Any

from src.main.api.steps.admin_steps import AdminSteps
from src.main.api.steps.user_steps import UserSteps


class ApiManger:
    def __init__(self, created_obj: List[Any]):
        self.admin_steps = AdminSteps(created_obj)
        self.user_steps = UserSteps(created_obj)
### ./main/api/specs/response_specs.py
from requests import Response
from http import HTTPStatus

class ResponseSpecs:
    @staticmethod
    def request_ok():
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.OK, response.text
        return confirm

    @staticmethod
    def request_created():
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.CREATED, response.text
        return confirm

    @staticmethod
    def request_bad():
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, response.text
        return confirm

    @staticmethod
    def request_unprocessable():
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, response.text
        return confirm

    @staticmethod
    def request_forbidden():
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.FORBIDDEN, response.text
        return confirm

    @staticmethod
    def request_unauthorized():
        def confirm(response: Response):
            assert response.status_code == HTTPStatus.UNAUTHORIZED, response.text
        return confirm### ./main/api/specs/request_specs.py
from urllib3.util import url

from src.main.api.config.config import Config
from src.main.api.models.login_user_response import LoginUserResponse
from src.main.api.models.user_login_request import LoginUserRequest
import requests


class RequestSpecs:
    @staticmethod
    def base_headers():
        return {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

    @staticmethod
    def auth_headers(username: str, password: str):
        request = LoginUserRequest(username=username, password=password)
        response = requests.post(
            url='http://localhost:4111/api/auth/token/login',
            json=request.model_dump(),
            headers=RequestSpecs.base_headers()
        )
        if response.status_code == 200:
            response_data = LoginUserResponse(**response.json())
            token = response_data.token
            headers = RequestSpecs.base_headers()
            headers["Authorization"] = f"Bearer {token}"
            return headers
        raise Exception("Failed to login")

    @staticmethod
    def unauth_headers():
        return RequestSpecs.base_headers()### ./main/api/tests/create_user_test.py
import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManger
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.db.crud.user_crud import UserCrudDb as User


@pytest.mark.api
class TestCreateUser:
    @pytest.mark.parametrize(
        "create_user_request",
        [RandomModelGenerator.generate(CreateUserRequest)]
    )
    def test_create_user_valid(self, api_manager: ApiManger, create_user_request: CreateUserRequest, db_session: Session):
        response = api_manager.admin_steps.create_user(create_user_request)

        assert create_user_request.username == response.username
        assert create_user_request.role == response.role

        user_from_db = User.get_user_by_username(db_session, create_user_request.username)
        assert user_from_db.username == create_user_request.username, "Созданного пользователя нет в БД"

    @pytest.mark.parametrize(
        "username, password", [
            ("абв", "Pas!sw0rd"),
            ("ab", "Pas!sw0rd"),
            ("abv!", "Pas!sw0rd"),
            ("Maxx1", "Pas!sw0rд"),
            ("Maxx2", "Pas!sw0"),
            ("Maxx3", "pas!sw0rd"),
            ("Maxx4", "PAS!SW0RD"),
            ("Maxx5", "PASSW0RD"),
            ("Maxx6", "Pas!swOrd"),
        ]
    )
    def test_create_user_invalid(self, db_session: Session, username: str, password: str , api_manager: ApiManger):

        create_user_request = CreateUserRequest(username=username, password=password, role="ROLE_USER")
        api_manager.admin_steps.create_invalid_user(create_user_request)

        user_from_db = User.get_user_by_username(db_session, create_user_request.username)

        assert user_from_db is None, "Пользователь создан, ошибка"

### ./main/api/tests/credit_repay_test.py
import pytest
from src.main.api.models.credit_request import CreditRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest


@pytest.mark.api
class TestCreditRequest:
    def test_credit_repay(self, api_manager, create_credit_user_request):
        credit_amount = 5000
        term_months = 12

        create_account_response = api_manager.user_steps.create_account(create_credit_user_request)
        account_id = create_account_response.id
        credit_request = CreditRequest(accountId=account_id, amount=credit_amount, termMonths=term_months)
        credit_request_response = api_manager.user_steps.credit_request(credit_request, create_credit_user_request)
        credit_id = credit_request_response.creditId
        credit_repay_request = CreditRepayRequest(creditId=credit_id, accountId=account_id, amount=credit_amount)
        credit_repay_response = api_manager.user_steps.credit_repay_request(credit_repay_request, create_credit_user_request)

        assert credit_repay_response.creditId == credit_id
        assert credit_repay_response.amountDeposited == credit_amount


    def test_credit_repay_unsufficient_amount(self, api_manager, create_credit_user_request):
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

        assert credit_repay_response.json().get("error") == f"The amount is not enough. Credit balance: -{credit_amount}"### ./main/api/tests/transfer_account_test.py
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

        assert transfer_account_response.fromAccountIdBalance == leftover

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

        assert transfer_account_response.json().get('error') == f"Insufficient funds. Current balance: {deposit_amount}.00, required: {transfer_amount}.00"### ./main/api/tests/create_account_test.py
import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManger
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.api
class TestCreateAccount:
    def test_create_account(self, db_session: Session, api_manager: ApiManger, create_user_request: CreateUserRequest):
        response = api_manager.user_steps.create_account(create_user_request)

        assert response.balance == 0

        account_from_db = Account.get_account_by_id(db_session, response.id)
        assert account_from_db.id == response.id, "Счёт не создан, id аккаунта нет в БД"
        assert account_from_db.balance is not None, "Поле баланса для созданного счёта отсутствует в БД"### ./main/api/tests/login_user_test.py
import pytest
from src.main.api.fixtures.api_fixture import api_manager
from src.main.api.models.user_login_request import LoginUserRequest


@pytest.mark.api
class TestUserLogin:
    def test_login_admin(self, api_manager):
        login_user_request = LoginUserRequest(username="admin", password="123456")
        response = api_manager.admin_steps.login_user(login_user_request)

        assert login_user_request.username == response.user.username
        assert response.user.role == "ROLE_ADMIN"

    def test_login_user(self, api_manager, create_user_request):
        response = api_manager.admin_steps.login_user(create_user_request)

        assert create_user_request.username == response.user.username
        assert response.user.role == "ROLE_USER"### ./main/api/tests/credit_request_test.py
import pytest
from requests import Session

from src.main.api.classes.api_manager import ApiManger
from src.main.api.fixtures.db_fixture import db_session
from src.main.api.models.create_user_request import CreateCreditUserRequest, CreateUserRequest
from src.main.api.models.credit_request import CreditRequest
from src.main.api.db.crud.credit_crud import CreditCrudDb as Credit

@pytest.mark.api
class TestCreditRequest:
    def test_credit_request_valid_user(self, api_manager: ApiManger, create_credit_user_request: CreateCreditUserRequest, db_session: Session):
        create_account_response = api_manager.user_steps.create_account(create_credit_user_request)
        account_id = create_account_response.id
        credit_request = CreditRequest(accountId=account_id, amount=5000, termMonths=12)
        credit_request_response = api_manager.user_steps.credit_request(credit_request, create_credit_user_request)
        assert credit_request_response.id == account_id

        credit_id = credit_request_response.id
        credit_from_db = Credit.get_credit_by_id(db_session, credit_id)
        assert credit_from_db.account_id == account_id, "Кредит не создан в БД, или принядлежит другому счёту"

    def test_credit_request_invalid_user(self, api_manager: ApiManger, create_user_request: CreateUserRequest):
        create_account_response = api_manager.user_steps.create_account(create_user_request)
        account_id = create_account_response.id
        credit_request = CreditRequest(accountId=account_id, amount=5000, termMonths=12)
        credit_request_response = api_manager.user_steps.credit_invalid_request_(credit_request, create_user_request)
        assert credit_request_response.json().get("detail") == "Forbidden: ROLE_CREDIT access required"

### ./main/api/tests/deposit_account_test.py
import pytest
from sqlalchemy.orm import Session

from src.main.api.classes.api_manager import ApiManger
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest


@pytest.mark.api
class TestDepositAccount:
    def test_deposit_account(self, api_manager: ApiManger, create_user_request: CreateUserRequest, db_session: Session):
        deposit_amount = 1000

        account_response = api_manager.user_steps.create_account(create_user_request)
        account_id = account_response.id
        deposit_account_request = DepositAccountRequest(accountId=account_id, amount=deposit_amount)
        deposit_response = api_manager.user_steps.deposit_account(deposit_account_request, create_user_request)

        assert deposit_response.balance == deposit_amount

        account_from_db = Account.get_account_by_id(db_session, deposit_response.id)
        assert account_from_db.balance == deposit_amount, "В БД не сохранилась запись о балансе аккаунта"




    def test_deposit_account_without_token(self, api_manager, create_user_request):
        deposit_amount = 1000

        account_response = api_manager.user_steps.create_account(create_user_request)
        account_id = account_response.id
        deposit_account_request = DepositAccountRequest(accountId=account_id, amount=deposit_amount)
        deposit_response = api_manager.user_steps.deposit_account_without_token(deposit_account_request)

        assert deposit_response.json().get("message") == "JWT Token not found"### ./main/api/foundation/requesters/validated_crud_requester.py
from typing import Optional

from src.main.api.config.config import Config
from src.main.api.foundation.http_requester import HttpRequester
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.models.base_model import BaseModel
from http import HTTPStatus
import allure

class ValidateCrudRequester(HttpRequester):
    def __init__(self, request_spec, endpoint, response_spec):
        super().__init__(request_spec, endpoint, response_spec)
        self.crud_requester = CrudRequester(
            request_spec=request_spec,
            response_spec=response_spec,
            endpoint=endpoint
        )

    def post(self, model: Optional[BaseModel] = None):
        response = self.crud_requester.post(model)
        with allure.step(f"POST {Config.fetch("backendUrl")}{self.endpoint.value.url} and Validated Model"):
            allure.attach(f"Validated Model response: {self.endpoint.value.response_model.__name__}")

        self.response_spec(response)
        if response.status_code in [HTTPStatus.OK, HTTPStatus.CREATED]:
            return self.endpoint.value.response_model.model_validate(response.json())
        return response

    def delete(self, user_id: int):
        response = self.crud_requester.delete(user_id)
        self.response_spec(response)
        return self.endpoint.value.response_model.model_validate(response.json())### ./main/api/foundation/requesters/crud_requester.py
from typing import Optional
import requests
from requests import Response
from src.main.api.config.config import Config
from src.main.api.foundation.http_requester import HttpRequester
from src.main.api.models.base_model import BaseModel
import allure


class CrudRequester(HttpRequester):
    def post(self, model: Optional[BaseModel]) -> BaseModel | Response:
        body = model.model_dump() if model is not None else ""

        with allure.step(f"POST {Config.fetch("backendUrl")}{self.endpoint.value.url}"):
            allure.attach(str(body), "Request body", allure.attachment_type.JSON)

        response = requests.post(
            url=f"{Config.fetch("backendUrl")}{self.endpoint.value.url}",
            headers=self.request_spec,
            json=body
        )
        allure.attach(
            response.text,
            "Response body",
            allure.attachment_type.JSON
        )
        self.response_spec(response)
        return response

    def delete(self, user_id: int) -> BaseModel | Response:
        response = requests.delete(
            url=f"{Config.fetch("backendUrl")}{self.endpoint.value.url}/{user_id}",
            headers=self.request_spec
        )
        self.response_spec(response)
        return response### ./main/api/foundation/endpoint.py
from dataclasses import dataclass
from enum import Enum
from src.main.api.models.base_model import BaseModel
from typing import Optional, Type
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.credit_repay_response import CreditRepayResponse
from src.main.api.models.credit_request import CreditRequest
from src.main.api.models.credit_request_response import CreditRequestResponse
from src.main.api.models.deposit_account_request import DepositAccountRequest
from src.main.api.models.deposit_account_response import DepositAccountResponse
from src.main.api.models.login_user_response import LoginUserResponse
from src.main.api.models.transfer_accounts_request import TransferAccountRequest
from src.main.api.models.transfer_accounts_response import TransferAccountResponse
from src.main.api.models.user_login_request import LoginUserRequest


@dataclass
class EndpointConfiguration:
    url: str
    request_model: Optional[Type[BaseModel]]
    response_model: Optional[Type[BaseModel]]


class Endpoint(Enum):
    ADMIN_CREATE_USER = EndpointConfiguration(
        request_model = CreateUserRequest,
        url = "/admin/create",
        response_model = CreateUserResponse
    )

    ADMIN_DELETE_USER = EndpointConfiguration(
        request_model = None,
        url = "/admin/users",
        response_model = None
    )

    LOGIN_USER = EndpointConfiguration(
        request_model = LoginUserRequest,
        url= "/auth/token/login",
        response_model = LoginUserResponse
    )

    CREATE_ACCOUNT = EndpointConfiguration(
        request_model = None,
        url = "/account/create",
        response_model = CreateAccountResponse
    )

    DEPOSIT_ACCOUNT = EndpointConfiguration(
        request_model= DepositAccountRequest,
        url = "/account/deposit",
        response_model = DepositAccountResponse
    )

    TRANSFER_ACCOUNT = EndpointConfiguration(
        request_model = TransferAccountRequest,
        url = "/account/transfer",
        response_model = TransferAccountResponse
    )

    CREDIT_REQUEST = EndpointConfiguration(
        request_model = CreditRequest,
        url = "/credit/request",
        response_model= CreditRequestResponse
    )

    CREDIT_REPAY = EndpointConfiguration(
        request_model= CreditRepayRequest,
        url = "/credit/repay",
        response_model= CreditRepayResponse
    )### ./main/api/foundation/crud_endpoint.py
from typing import Protocol, Optional

from requests import Response

from src.main.api.models.base_model import BaseModel


class CrudEndpoint(Protocol):
    def post(self, model: Optional[BaseModel]) -> BaseModel | Response:...
    def get(self, user_id: int) -> BaseModel | Response:...
    def delete(self, user_id: int) -> BaseModel | Response:...### ./main/api/foundation/http_requester.py
from typing import Dict, Callable
from src.main.api.foundation.endpoint import Endpoint


class HttpRequester:
    def __init__(self, request_spec: Dict, endpoint: Endpoint, response_spec: Callable):
        self.request_spec = request_spec
        self.endpoint = endpoint
        self.response_spec = response_spec
### ./main/api/models/credit_request.py
from src.main.api.models.base_model import BaseModel

class CreditRequest(BaseModel):
    accountId: int
    amount: float
    termMonths: int
### ./main/api/models/create_user_response.py
from src.main.api.models.base_model import BaseModel

class CreateUserResponse(BaseModel):
    id: int
    username: str
    password: str
    role: str### ./main/api/models/create_user_request.py
from src.main.api.generators.creation_rule import CreationRule
from src.main.api.models.base_model import BaseModel
from typing import Annotated

class CreateUserRequest(BaseModel):
    username: Annotated[str, CreationRule(regex=r'^[A-Za-z0-9]{3,15}$')]
    password: Annotated[str, CreationRule(regex=r'^[A-Z]{3}[a-z]{1}[0-9]{2}[!$_]{4}$')]
    role: Annotated[str, CreationRule(regex=r'^ROLE_USER')]

class CreateCreditUserRequest(BaseModel):
    username: Annotated[str, CreationRule(regex=r'^[A-Za-z0-9]{3,15}$')]
    password: Annotated[str, CreationRule(regex=r'^[A-Z]{3}[a-z]{1}[0-9]{2}[!$_]{4}$')]
    role: Annotated[str, CreationRule(regex=r'^ROLE_CREDIT_SECRET')]### ./main/api/models/transfer_accounts_response.py
from src.main.api.models.base_model import BaseModel


class TransferAccountResponse(BaseModel):
    fromAccountId: int
    toAccountId: int
    fromAccountIdBalance: float### ./main/api/models/transfer_accounts_request.py
from src.main.api.models.base_model import BaseModel


class TransferAccountRequest(BaseModel):
    fromAccountId: int
    toAccountId: int
    amount: float### ./main/api/models/credit_request_response.py
from src.main.api.models.base_model import BaseModel

class CreditRequestResponse(BaseModel):
    id: int
    amount: float
    termMonths: int
    balance: float
    creditId: int
### ./main/api/models/base_model.py
from pydantic import BaseModel as BM


class BaseModel(BM):...### ./main/api/models/credit_repay_request.py
from src.main.api.models.base_model import BaseModel

class CreditRepayRequest(BaseModel):
    creditId: int
    accountId: int
    amount: float### ./main/api/models/login_user_response.py
from src.main.api.models.base_model import BaseModel

class User(BaseModel):
    username: str
    role: str

class LoginUserResponse(BaseModel):
    token: str
    user: User### ./main/api/models/credit_repay_response.py
from src.main.api.models.base_model import BaseModel

class CreditRepayResponse(BaseModel):
    creditId: int
    amountDeposited: float### ./main/api/models/user_login_request.py
from src.main.api.models.base_model import BaseModel

class LoginUserRequest(BaseModel):
    username: str
    password: str### ./main/api/models/deposit_account_response.py
from src.main.api.models.base_model import BaseModel


class DepositAccountResponse(BaseModel):
    id: int
    balance: float
### ./main/api/models/create_account_response.py
from src.main.api.models.base_model import BaseModel


class CreateAccountResponse(BaseModel):
    id: int
    number: str
    balance: float
### ./main/api/models/deposit_account_request.py
from src.main.api.models.base_model import BaseModel


class DepositAccountRequest(BaseModel):
    accountId: int
    amount: float
### ./main/api/steps/admin_steps.py
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.validated_crud_requester import ValidateCrudRequester
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.models.create_user_request import CreateUserRequest, CreateCreditUserRequest
from src.main.api.models.user_login_request import LoginUserRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class AdminSteps(BaseSteps):
    def create_user(self, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username="admin", password="123456"),
            Endpoint.ADMIN_CREATE_USER,
            ResponseSpecs.request_ok()
        ).post(create_user_request)

        self.created_obj.append(response)
        return response

    def create_credit_user(self, create_credit_user_request: CreateCreditUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username="admin", password="123456"),
            Endpoint.ADMIN_CREATE_USER,
            ResponseSpecs.request_ok()
        ).post(create_credit_user_request)

        self.created_obj.append(response)
        return response

    def delete_user(self, user_id: int):
        CrudRequester(
            RequestSpecs.auth_headers(username="admin", password="123456"),
            Endpoint.ADMIN_DELETE_USER,
            ResponseSpecs.request_ok()
        ).delete(user_id)

    def create_invalid_user(self, create_user_request: CreateUserRequest):
        CrudRequester(
            RequestSpecs.auth_headers(username="admin", password="123456"),
            Endpoint.ADMIN_CREATE_USER,
            ResponseSpecs.request_bad()
        ).post(create_user_request)

    def login_user(self, login_user_request: LoginUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.unauth_headers(),
            Endpoint.LOGIN_USER,
            ResponseSpecs.request_ok()
        ).post(login_user_request)
        return response### ./main/api/steps/user_steps.py

from src.main.api.fixtures.user_fixture import create_user_request
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.foundation.requesters.validated_crud_requester import ValidateCrudRequester
from src.main.api.models.create_user_request import CreateUserRequest, CreateCreditUserRequest
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.credit_request import CreditRequest
from src.main.api.models.deposit_account_request import DepositAccountRequest
from src.main.api.models.transfer_accounts_request import TransferAccountRequest
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps



class UserSteps(BaseSteps):
    def create_account(self, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREATE_ACCOUNT,
            ResponseSpecs.request_created()
        ).post()
        return response

    def deposit_account(self, deposit_account_request: DepositAccountRequest, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.DEPOSIT_ACCOUNT,
            ResponseSpecs.request_ok()
        ).post(deposit_account_request)
        return response

    def deposit_account_without_token(self, deposit_account_request: DepositAccountRequest):
        response = ValidateCrudRequester(
            RequestSpecs.unauth_headers(),
            Endpoint.DEPOSIT_ACCOUNT,
            ResponseSpecs.request_unauthorized()
        ).post(deposit_account_request)
        return response

    def transfer_account(self, transfer_account_request: TransferAccountRequest, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.TRANSFER_ACCOUNT,
            ResponseSpecs.request_ok()
        ).post(transfer_account_request)
        return response

    def transfer_account_insufficient_funds(self, transfer_account_request: TransferAccountRequest, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.TRANSFER_ACCOUNT,
            ResponseSpecs.request_unprocessable()
        ).post(transfer_account_request)
        return response

    def credit_request(self, credit_request: CreditRequest, create_credit_user_request: CreateCreditUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_credit_user_request.username, password=create_credit_user_request.password),
            Endpoint.CREDIT_REQUEST,
            ResponseSpecs.request_created()
        ).post(credit_request)
        return response

    def credit_invalid_request_(self, credit_request: CreditRequest, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_REQUEST,
            ResponseSpecs.request_forbidden()
        ).post(credit_request)
        return response

    def credit_repay_request(self, credit_repay_request: CreditRepayRequest, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_ok()
        ).post(credit_repay_request)
        return response

    def credit_repay_insufficient_request(self, credit_repay_request: CreditRepayRequest, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_unprocessable()
        ).post(credit_repay_request)
        return response### ./main/api/steps/base_steps.py
from typing import List

class BaseSteps:
    def __init__(self, created_obj: List[Any]):
        self.created_obj = created_obj### ./main/api/db/models/account_table.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from src.main.api.db.base import Base

class Account(Base):
    __tablename__ = "account"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_id'), nullable=False)
    number = Column(String, unique=True, nullable=False)
    balance = Column(Float, nullable=False)

    def __repr__(self):
        return f'<Account(id={self.id}, user_id={self.user_id}, number={self.number}, balance={self.balance}>'### ./main/api/db/models/transaction_table.py
from src.main.api.db.base import Base
from sqlalchemy import Integer, Float, String, Column, DateTime


class Transaction(Base):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True, autoincrement=True)
    to_account_id = Column(Integer, nullable=True)
    from_account_id = Column(Integer, nullable=True)
    credit_id = Column(Integer, nullable=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f'<Transaction(id={self.id}, to_account_id={self.to_account_id}, from_account_id={self.from_account_id}, credit_id={self.credit_id}, transaction_type={self.transaction_type}, credit_id={self.credit_id}, created_at={self.created_at}>'### ./main/api/db/models/user_table.py
from sqlalchemy import Column, Integer, String, DateTime
from src.main.api.db.base import Base

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    deleted_at = Column(DateTime, nullable=False)


    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}>, role={self.role}, deleted_at={self.deleted_at})>"### ./main/api/db/models/credit_table.py
from sqlalchemy import Column, Integer, Float, DateTime
from src.main.api.db.base import Base

class Credit(Base):
    __tablename__ = "credit"
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    term_months = Column(Integer, nullable=False)
    balance = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f'<Credit(id={self.id}, account_id={self.account_id}, amount={self.amount}, term_months={self.term_months}, balance={self.balance}, created_at={self.created_at}>'### ./main/api/db/engine.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main.api.config.config import Config

engine = create_engine(Config.fetch('dataBaseUrl'), echo=False)
SessionLocal = sessionmaker(bind=engine)### ./main/api/db/crud/credit_crud.py
from sqlalchemy.orm import Session
from src.main.api.db.models.credit_table import Credit

class CreditCrudDb:
    @staticmethod
    def get_credit_by_id(db: Session, credit_id: int) -> Credit | None:
        return db.query(Credit).filter_by(id=credit_id).first()### ./main/api/db/crud/account_crud.py
from sqlalchemy.orm import Session
from src.main.api.db.models.account_table import Account


class AccountCrudDb:
    @staticmethod
    def get_account_by_id(db: Session, account_id: int) -> Account | None:
        return db.query(Account).filter_by(id=account_id).first()### ./main/api/db/crud/user_crud.py
from sqlalchemy.orm import Session
from src.main.api.db.models.user_table import User

class UserCrudDb:
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter_by(username=username).first()### ./main/api/db/crud/transaction_crud.py
from sqlalchemy.orm import Session
from src.main.api.db.models.transaction_table import Transaction

class TransactionCrudDb:
    @staticmethod
    def get_transaction_by_amount(db: Session, amount: float) -> Transaction | None:
        return db.query(Transaction).order_by(Transaction.id.desc()).filter_by(amount=amount).first()### ./main/api/db/base.py
from sqlalchemy.orm import declarative_base

Base = declarative_base()### ./main/api/fixtures/api_fixture.py
import pytest

from src.main.api.classes.api_manager import ApiManger


@pytest.fixture
def api_manager(created_obj):
    return ApiManger(created_obj)### ./main/api/fixtures/object_fixture.py
import logging
from typing import List, Any
import pytest
from src.main.api.classes.api_manager import ApiManger
from src.main.api.models.create_user_response import CreateUserResponse


@pytest.fixture
def created_obj():
    object: List[Any] = []
    yield object
    clean_user(object)

def clean_user(objects: List[Any]):
    api_manager = ApiManger(objects)
    for u in objects:
        if isinstance(u, CreateUserResponse):
            api_manager.admin_steps.delete_user(u.id)
        else:
            logging.warning(f"Error in delete user_id: {u.id}")### ./main/api/fixtures/user_fixture.py
import pytest
from src.main.api.models.create_user_request import CreateUserRequest, CreateCreditUserRequest
from src.main.api.generators.model_generator import RandomModelGenerator

@pytest.fixture
def create_user_request(api_manager):
    user_request = RandomModelGenerator.generate(CreateUserRequest)
    api_manager.admin_steps.create_user(user_request)
    return user_request

@pytest.fixture
def create_credit_user_request(api_manager):
    user_request = RandomModelGenerator.generate(CreateCreditUserRequest)
    api_manager.admin_steps.create_credit_user(user_request)
    return user_request### ./main/api/fixtures/db_fixture.py
import pytest
from src.main.api.db.engine import SessionLocal, engine

@pytest.fixture(scope='function')
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()### ./main/api/generators/creation_rule.py
from dataclasses import dataclass


@dataclass
class CreationRule:
    regex: str### ./main/api/generators/model_generator.py
import random
import uuid
from typing import Any, get_type_hints, get_origin, Annotated, get_args
import rstr
from src.main.api.generators.creation_rule import CreationRule


class RandomModelGenerator:
    @staticmethod
    def generate(cls: type) -> Any:
        type_hints = get_type_hints(cls, include_extras=True)
        init_data = {}

        for field_name, annotated_type in type_hints.items():
            rule = None
            actual_type = annotated_type()

            if get_origin(annotated_type) is Annotated:
                actual_type, *annotations = get_args(annotated_type)
                for ann in annotations:
                    if isinstance(ann, CreationRule):
                        rule = ann
            if rule:
                value = RandomModelGenerator._generate_from_regex(rule.regex, actual_type)
            else:
                value = RandomModelGenerator._generate_value(actual_type)

            init_data[field_name] = value

        return cls(**init_data)

    @staticmethod
    def _generate_from_regex(regex: str, field_type):
        generated = rstr.xeger(regex)
        if field_type is int:
            return int(generated)
        if field_type is float:
            return float(generated)
        return generated

    @staticmethod
    def _generate_value(field_type: type) -> Any:
        if field_type is str:
            return str(uuid.uuid4())[:8]
        elif field_type is int:
            return random.randint(1, 9999)
        elif field_type is float:
            return round(random.uniform(0, 100.), 2)
        elif field_type is bool:
            return random.choice([True, False])
        elif field_type is list:
            return [str(uuid.uuid4())[:5]]
        elif isinstance(field_type, type):
            return RandomModelGenerator.generate(field_type)
        return None