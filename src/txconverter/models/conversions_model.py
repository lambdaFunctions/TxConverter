from pydantic import BaseModel, ConfigDict


class ConversionsModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    converted_amount: str
    exchange_rate: str
    exchange_currency: str
    record_date: str
