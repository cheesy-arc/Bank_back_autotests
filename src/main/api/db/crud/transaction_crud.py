from sqlalchemy.orm import Session
from src.main.api.db.models.transaction_table import Transaction

class TransactionCrudDb:
    @staticmethod
    def get_transaction_by_amount(db: Session, amount: float) -> Transaction | None:
        return db.query(Transaction).order_by(Transaction.id.desc()).filter_by(amount=amount).first()