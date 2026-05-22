import json

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

_BODY_SNIPPET_LIMIT = 500


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        cid = getattr(request.state, "correlation_id", "-")

        request_data = await self._build_request_data(request)
        response = await call_next(request)
        response, response_data = await self._build_response_data(response)

        try:
            logger.info(
                "{}",
                json.dumps(
                    {"CID": cid, "request": request_data, "response": response_data}
                ),
            )
        except Exception:
            pass

        return response

    @staticmethod
    async def _build_request_data(request: Request) -> dict:
        try:
            raw = await request.body()
            body = raw.decode("utf-8", errors="replace")[:_BODY_SNIPPET_LIMIT] or None
            return {"method": request.method, "url": str(request.url), "body": body}
        except Exception:
            return {}

    @staticmethod
    async def _build_response_data(response: Response) -> tuple[Response, dict]:
        try:
            chunks = []
            async for chunk in response.body_iterator:
                chunks.append(chunk)
            body_bytes = b"".join(chunks)

            snippet = (
                body_bytes.decode("utf-8", errors="replace")[:_BODY_SNIPPET_LIMIT]
                or None
            )

            reconstructed = Response(
                content=body_bytes,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
            return reconstructed, {"status_code": response.status_code, "body": snippet}
        except Exception:
            return response, {"status_code": getattr(response, "status_code", None)}
