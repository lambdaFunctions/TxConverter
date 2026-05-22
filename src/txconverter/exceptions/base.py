from http import HTTPStatus

from fastapi.responses import JSONResponse

from src.txconverter.constants.base import INTERNAL_ERROR_MESSAGE
from src.txconverter.constants.base_codes import INTERNAL_ERROR_CODE


class TxConverterBaseException(Exception):
    message: str = INTERNAL_ERROR_MESSAGE
    http_status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    code: str = INTERNAL_ERROR_CODE

    def __init__(
        self,
        message: str | None = None,
        http_status: HTTPStatus | None = None,
        code: str | None = None,
    ) -> None:
        self.message = message or self.__class__.message
        self.http_status = http_status or self.__class__.http_status
        self.code = code or self.__class__.code
        super().__init__(self.message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"code={self.code!r}, "
            f"http_status={self.http_status}, "
            f"message={self.message!r})"
        )

    @staticmethod
    def to_json_response() -> JSONResponse:
        return JSONResponse(
            status_code=TxConverterBaseException.http_status,
            content={
                "error": {
                    "code": TxConverterBaseException.code,
                    "message": TxConverterBaseException.message,
                }
            },
        )


def is_custom_exception(exc: Exception) -> bool:
    return isinstance(exc, TxConverterBaseException)
