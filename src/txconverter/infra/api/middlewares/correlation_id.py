from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.txconverter.infra.id_generator import sf
from src.txconverter.infra.logging import correlation_id_var


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        cid = str(sf.next_id())
        request.state.correlation_id = cid
        correlation_id_var.set(cid)
        return await call_next(request)
