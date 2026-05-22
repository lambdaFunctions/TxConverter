from fastapi.responses import JSONResponse

from src.txconverter.exceptions.base import TxConverterBaseException


def build_error_response(exc: TxConverterBaseException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_status.value,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


def build_fallback_response() -> JSONResponse:
    """This fallback exists to ensure that if the exception raised by the API is not
    one of the ones we know (one that was created, has specific message, status code,
    code, etc.), we can still return a response in the API's due format. Therefore,
    this function's result is a JSON response with the same properties the
    `TxConverterBaseException` class has.
    """
    return TxConverterBaseException.to_json_response()
