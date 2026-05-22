from http import HTTPStatus

from src.txconverter.exceptions.base import TxConverterBaseException
from src.txconverter.constants.currencies import CURRENCY_NOT_FOUND, CURRENCY_AMBIGUOUS, CURRENCY_TOO_OLD


class CurrencyNotFoundError(TxConverterBaseException):
    message = "Currency not found"
    http_status = HTTPStatus.NOT_FOUND
    code = CURRENCY_NOT_FOUND


class AmbiguousCurrencyError(TxConverterBaseException):
    http_status = HTTPStatus.UNPROCESSABLE_ENTITY
    code = CURRENCY_AMBIGUOUS

    def __init__(self, name: str, matches: list[str]) -> None:
        descriptors = ", ".join(sorted(matches))
        super().__init__(
            message=f"Ambiguous currency '{name}'. Specify one of: {descriptors}"
        )


class CurrencyOlderThanAvailableDataRequestError(TxConverterBaseException):
    message = "Conversion request older than available data"
    http_status = HTTPStatus.BAD_REQUEST
    code = CURRENCY_TOO_OLD


class CurrencyTooOldRequestError(TxConverterBaseException):
    message = "Conversion request older than threshold"
    http_status = HTTPStatus.BAD_REQUEST
    code = CURRENCY_TOO_OLD

