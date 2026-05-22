from datetime import date

from pydantic import BaseModel, field_validator


class PostCreateCurrencyRegisterRequest(BaseModel):
    country_currency_desc: str
    date: date

    @field_validator("date")
    @classmethod
    def ensure_not_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Transaction date cannot be in the future")
        return value


class PostCreateCurrencyRegisterResponse(BaseModel):
    country_currency_desc: str
    date: str
    exchange_rate: str
