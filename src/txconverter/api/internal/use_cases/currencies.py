from loguru import logger

from src.txconverter.services.currencies_service import CurrencyService
from src.txconverter.services.conversions_handler import ConversionHandler
from src.txconverter.models.currencies_model import CurrenciesModel
from src.txconverter.api.internal.mappers.currencies import map_create_currency
from src.txconverter.api.internal.schemas.currencies import (
    PostCreateCurrencyRegisterRequest,
    PostCreateCurrencyRegisterResponse,
)
from src.txconverter.infra.clients.treasury_errors import InfraFetchCurrencyError
from src.txconverter.exceptions.currencies import AmbiguousCurrencyError, CurrencyNotFoundError, CurrencyOlderThanAvailableDataRequestError, CurrencyTooOldRequestError

currency_service = CurrencyService()


async def create_currency(
    body: PostCreateCurrencyRegisterRequest,
) -> PostCreateCurrencyRegisterResponse:

    possible_dates = ConversionHandler.get_possible_dates(body.date, True)

    logger.info("Possible dates: {}", possible_dates)

    # Choosing to use a currency not found given the endpoints domain

    for _date in possible_dates:
        if ConversionHandler.is_older_than_available_data(_date):
            raise CurrencyOlderThanAvailableDataRequestError()

    if ConversionHandler.is_older_than_threshold(body.date):
        raise CurrencyTooOldRequestError()

    target_currency_name = body.country_currency_desc

    currencies: (
        list[CurrenciesModel] | AmbiguousCurrencyError | InfraFetchCurrencyError
    ) = []
    currencies = await currency_service.get_curency_for_quarters(
        target_currency_name, possible_dates
    )

    if len(currencies) == 0:
        raise CurrencyNotFoundError(body.country_currency_desc)

    return map_create_currency(currencies[0])
