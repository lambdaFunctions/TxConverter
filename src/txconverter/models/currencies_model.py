from pydantic import BaseModel, ConfigDict


class CurrenciesModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    country_currency_desc: str
    record_date: str
    exchange_rate: str
