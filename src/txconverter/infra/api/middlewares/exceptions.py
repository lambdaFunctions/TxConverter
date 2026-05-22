from http import HTTPStatus

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from src.txconverter.constants.base import INTERNAL_ERROR_MESSAGE
from src.txconverter.constants.base_codes import INTERNAL_ERROR_CODE
from src.txconverter.exceptions.base import is_custom_exception
from src.txconverter.infra.api.response_builder import (
    build_error_response,
    build_fallback_response,
)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            try:
                if is_custom_exception(exc):
                    logger.warning(
                        "{} {} raised {}: {}",
                        request.method,
                        request.url.path,
                        type(exc).__name__,
                        exc,
                    )
                    return build_error_response(exc)
                logger.opt(exception=exc).error(
                    "Unhandled exception on {} {}", request.method, request.url.path
                )
                return build_fallback_response()
            except Exception as exc:
                return self._handle_unexpected_exception(request, exc)

    def _handle_unexpected_exception(self, request: Request, exc: Exception) -> JSONResponse:
        logger.opt(exception=exc).critical(
            "Exception handler itself failed on {} {}", request.method, request.url.path
        )
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            content={
                "error": {
                    "code": INTERNAL_ERROR_CODE,
                    "message": INTERNAL_ERROR_MESSAGE,
                }
            },
        )
