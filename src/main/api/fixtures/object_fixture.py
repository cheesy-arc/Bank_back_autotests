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
            logging.warning(f"Error in delete user_id: {u.id}")