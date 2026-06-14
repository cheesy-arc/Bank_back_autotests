from src.main.api.generators.creation_rule import CreationRule
from src.main.api.models.base_model import BaseModel
from typing import Annotated

class CreditRequest(BaseModel):
    accountId: int
    amount: Annotated[float, CreationRule(regex=r'^([5-9][0-9]{3}|1[0-4][0-9]{3})\.[0-9]{2}$')]
    termMonths: Annotated[int, CreationRule(regex=r'^(3|6|12|24)$')]
