from src.txconverter.models.currencies_model import CurrenciesModel
from src.txconverter.api.internal.schemas.currencies import (
    PostCreateCurrencyRegisterResponse,
)


def map_create_currency(
    currency: CurrenciesModel,
) -> PostCreateCurrencyRegisterResponse:
    return PostCreateCurrencyRegisterResponse(
        country_currency_desc=currency.country_currency_desc,
        date=currency.record_date,
        exchange_rate=currency.exchange_rate,
    )
