from http import HTTPStatus

from src.txconverter.exceptions.base import TxConverterBaseException
from src.txconverter.constants.purchase_transactions.codes import (
    INVALID_DESCRIPTION_LENGTH,
    DATETIME_IN_PAST,
    INVALID_AMOUNT,
    TX_NOT_FOUND,
    TX_STORAGE_CORRUPTED,
    TX_STORAGE_FULL,
)


class TxInvalidDescriptionLengthError(TxConverterBaseException):
    message = "Invalid description length"
    http_status = HTTPStatus.UNPROCESSABLE_ENTITY
    code = INVALID_DESCRIPTION_LENGTH


class TxDatetimeIsInThePastError(TxConverterBaseException):
    message = "Invalid datetime: transaction is in the past"
    http_status = HTTPStatus.UNPROCESSABLE_ENTITY
    code = DATETIME_IN_PAST


class TxNegativeAmountError(TxConverterBaseException):
    message = "Amount is negative"
    http_status = HTTPStatus.UNPROCESSABLE_ENTITY
    code = INVALID_AMOUNT


class TxNotFoundError(TxConverterBaseException):
    message = "Transaction not found"
    http_status = HTTPStatus.NOT_FOUND
    code = TX_NOT_FOUND


class TxStorageCorruptedError(TxConverterBaseException):
    message = "Transaction storage is corrupted"
    http_status = HTTPStatus.INTERNAL_SERVER_ERROR
    code = TX_STORAGE_CORRUPTED


class TxStorageFullError(TxConverterBaseException):
    message = "Transaction storage is full"
    http_status = HTTPStatus(507)
    code = TX_STORAGE_FULL
