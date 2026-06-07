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
        return f'<Transaction(id={self.id}, to_account_id={self.to_account_id}, from_account_id={self.from_account_id}, credit_id={self.credit_id}, transaction_type={self.transaction_type}, credit_id={self.credit_id}, created_at={self.created_at}>'