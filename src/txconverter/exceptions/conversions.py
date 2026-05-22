from http import HTTPStatus

from src.txconverter.exceptions.base import TxConverterBaseException
from src.txconverter.constants.conversions import CV_TOO_OLD, CV_NOT_AVAILABLE


class CvTooOldRequestError(TxConverterBaseException):
    message = "Conversion request older than threshold"
    http_status = HTTPStatus.BAD_REQUEST
    code = CV_TOO_OLD


class CvOlderThanAvailableDataRequestError(TxConverterBaseException):
    message = "Conversion request older than available data"
    http_status = HTTPStatus.BAD_REQUEST
    code = CV_TOO_OLD


class CvNotAvailableError(TxConverterBaseException):
    message = "Conversion not available for given params"
    http_status = HTTPStatus.BAD_REQUEST
    code = CV_NOT_AVAILABLE
