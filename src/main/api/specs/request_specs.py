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
        return RequestSpecs.base_headers()