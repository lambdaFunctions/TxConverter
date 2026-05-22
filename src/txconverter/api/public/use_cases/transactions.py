from typing import Union

from datetime import datetime

from loguru import logger

from src.txconverter.services.transactions_service import PurchaseTxService
from src.txconverter.services.currencies_service import CurrencyService
from src.txconverter.services.conversions_handler import ConversionHandler
from src.txconverter.exceptions.transactions import TxNotFoundError
from src.txconverter.models.currencies_model import CurrenciesModel
from src.txconverter.exceptions.currencies import AmbiguousCurrencyError
from src.txconverter.exceptions.conversions import (
    CvTooOldRequestError,
    CvOlderThanAvailableDataRequestError,
    CvNotAvailableError,
)
from src.txconverter.infra.clients.treasury_errors import InfraFetchCurrencyError
from src.txconverter.api.common.pagination import PageParams
from src.txconverter.api.public.mappers.transactions import (
    map_create_transaction,
    map_raw_transaction,
    map_converted_transaction,
)
from src.txconverter.api.public.schemas.transactions import (
    PostPurchaseTransactionRequest,
    PostPurchaseTransactionResponse,
    GetTransactionListRequest,
    GetTransactionListResponse,
    GetTransactionResponse,
    GetTxConversionRequest,
    GetTxConversionResponse,
)

purchase_tx_service = PurchaseTxService()
currency_service = CurrencyService()


async def create_transaction(
    body: PostPurchaseTransactionRequest,
) -> PostPurchaseTransactionResponse:
    tx = await purchase_tx_service.create(body.model_dump(mode="json"))
    return map_create_transaction(tx)


async def get_transaction_list(
    filters: GetTransactionListRequest, params: PageParams
) -> GetTransactionListResponse:
    result = await purchase_tx_service.get_list(filters, params)
    return GetTransactionListResponse(
        items=[map_raw_transaction(tx) for tx in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


async def get_raw_or_converted_transaction(
    id: str, params: GetTxConversionRequest
) -> Union[
    GetTransactionResponse,
    GetTxConversionResponse,
    TxNotFoundError,
    CvOlderThanAvailableDataRequestError,
    CvTooOldRequestError,
    CvNotAvailableError,
    AmbiguousCurrencyError,
    InfraFetchCurrencyError,
]:
    tx = await purchase_tx_service.get_by_id(int(id))

    if not tx:
        raise TxNotFoundError()

    target_currency_name = params.currency
    if not target_currency_name:
        return map_raw_transaction(tx)

    target_date = datetime.strptime(tx.date, "%Y-%m-%d")
    target_date = target_date.date()

    possible_dates = ConversionHandler.get_possible_dates(target_date, True)

    logger.info("Possible dates: {}", possible_dates)

    for _date in possible_dates:
        if ConversionHandler.is_older_than_available_data(_date):
            raise CvOlderThanAvailableDataRequestError()

    if ConversionHandler.is_older_than_threshold(target_date):
        raise CvTooOldRequestError()

    currencies: (
        list[CurrenciesModel] | AmbiguousCurrencyError | InfraFetchCurrencyError
    ) = []
    currencies = await currency_service.get_curency_for_quarters(
        target_currency_name, possible_dates
    )

    if len(currencies) == 0:
        raise CvNotAvailableError()

    converted = purchase_tx_service.conversions.convert_to(tx, currencies[0])

    return map_converted_transaction(tx, converted)
