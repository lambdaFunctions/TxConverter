from fastapi import FastAPI

from src.txconverter.infra.logging import setup_logging
from src.txconverter.api.public.routers import transactions
from src.txconverter.api.internal.routers import currencies
from src.txconverter.infra.api.middlewares.correlation_id import CorrelationIdMiddleware
from src.txconverter.infra.api.middlewares.exceptions import ExceptionHandlerMiddleware
from src.txconverter.infra.api.middlewares.logging import LoggingMiddleware

setup_logging()

app = FastAPI(title="Tx Converter")

app.add_middleware(ExceptionHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(transactions.router)
app.include_router(currencies.router)
