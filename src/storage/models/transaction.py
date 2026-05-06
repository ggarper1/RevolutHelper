from datetime import datetime


class Transaction:
    TYPE = "Type"
    PRODUCT = "Product"
    START_DATE = "Started Date"
    COMPLETED_DATE = "Completed Date"
    DESCRIPTION = "Description"
    AMOUNT = "Amount"
    FEE = "Fee"
    CURRENCY = "Currency"
    STATE = "State"
    BALANCE = "Balance"

    @classmethod
    def columns(cls):
        return [
            cls.TYPE,
            cls.PRODUCT,
            cls.START_DATE,
            cls.COMPLETED_DATE,
            cls.DESCRIPTION,
            cls.AMOUNT,
            cls.FEE,
            cls.CURRENCY,
            cls.STATE,
            cls.BALANCE,
        ]

    def __init__(
        self,
        type: str,
        product: str,
        start_date: datetime,
        completed_date: datetime,
        description: str,
        amount: float,
        fee: float,
        currency: str,
        state: str,
        balance: float,
    ):
        self.type = type
        self.product = product
        self.start_date = start_date
        self.completed_date = completed_date
        self.description = description
        self.amount = amount
        self.fee = fee
        self.currency = currency
        self.state = state
        self.balance = balance
