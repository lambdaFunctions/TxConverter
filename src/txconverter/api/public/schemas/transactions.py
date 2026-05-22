from typing import Any, Optional
from datetime import date
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, field_validator

from src.txconverter.api.common.pagination import PaginatedResult
from src.txconverter.constants.purchase_transactions.base import (
    DESCRIPTION_LEN,
    MAX_AMOUNT,
)
from src.txconverter.exceptions.transactions import (
    TxInvalidDescriptionLengthError,
    TxNegativeAmountError,
)
from src.txconverter.services.amounts_handler import AmountHandler


class PostPurchaseTransactionRequest(BaseModel):
    """
    The `datetime` property is `AwareDatetime` to keep track of the caller's
    current timezone just for future reference. This info should be normalized
    to UTC later, which will be the use system will use as reference.

    Example of datetime awared data:
    - Brazil: "2026-05-22T07:00:00-03:00"
    - India: "2026-05-22T15:30:00+05:30"

    Example of the same datetime, but normalized:
    - UTC Normalized: "2026-05-22T10:00:00Z"

    Important: Naive datetimes (without timezone spec) will be reject, such as:
    - `"2026-05-22T10:00:00"`
    """

    amount: str
    date: date
    description: str

    @field_validator("date")
    @classmethod
    def ensure_not_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Transaction date cannot be in the future")
        return value

    @field_validator("description")
    @classmethod
    def ensure_length(cls, value: Any) -> str | TxInvalidDescriptionLengthError:
        if len(value) > DESCRIPTION_LEN:
            message = f"Description length greater than {DESCRIPTION_LEN}"
            raise TxInvalidDescriptionLengthError(message=message)

        return value

    @field_validator("amount")
    @classmethod
    def check_amount(cls, value: str) -> str | TxNegativeAmountError:
        try:
            amount: Decimal = AmountHandler.str_to_decimal(value)
        except InvalidOperation:
            raise ValueError(f"Invalid amount: '{value}' is not a valid number")

        if AmountHandler.is_negative(amount):
            raise TxNegativeAmountError()

        if amount > MAX_AMOUNT:
            raise ValueError(
                f"Amount exceeds the maximum allowed value of {MAX_AMOUNT}"
            )

        amount = AmountHandler.decimals.round_to_two(amount)
        return str(amount)


class PostPurchaseTransactionResponse(BaseModel):
    id: str
    description: str
    date: str
    amount: str


class GetTransactionResponse(BaseModel):
    id: str
    description: str
    amount: str
    date: str


class GetTransactionListRequest(BaseModel):
    description: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    amount_min: Decimal | None = None
    amount_max: Decimal | None = None


class GetTransactionListResponse(PaginatedResult[GetTransactionResponse]):
    pass


class GetTxConversionRequest(BaseModel):
    currency: Optional[str] = None


class GetTxConversionResponse(BaseModel):
    id: str
    description: str
    transaction_date: str
    original_amount: str
    exchange_currency: str
    exchange_rate: str
    converted_amount: str
    record_date: str
