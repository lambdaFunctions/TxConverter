from http import HTTPStatus

from src.txconverter.exceptions.base import TxConverterBaseException
from src.txconverter.constants.currencies import CURRENCY_FETCHING_ERROR


class InfraFetchCurrencyError(TxConverterBaseException):
    message = "Internal Error while fetching currency"
    http_status = HTTPStatus.INTERNAL_SERVER_ERROR
    code = CURRENCY_FETCHING_ERROR
