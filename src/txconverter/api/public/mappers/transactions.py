from src.txconverter.models.transactions_model import TransactionsModel
from src.txconverter.models.conversions_model import ConversionsModel
from src.txconverter.api.public.schemas.transactions import (
    PostPurchaseTransactionResponse,
    GetTransactionResponse,
    GetTxConversionResponse,
)


def map_create_transaction(tx: TransactionsModel) -> PostPurchaseTransactionResponse:
    return PostPurchaseTransactionResponse(
        id=tx.get_id(),
        description=tx.description,
        date=tx.date,
        amount=tx.amount,
    )


def map_raw_transaction(tx: TransactionsModel) -> GetTransactionResponse:
    return GetTransactionResponse(
        id=tx.get_id(),
        description=tx.description,
        date=tx.date,
        amount=tx.amount,
    )


def map_converted_transaction(
    tx: TransactionsModel, converted: ConversionsModel
) -> GetTxConversionResponse:
    return GetTxConversionResponse(
        id=tx.get_id(),
        description=tx.description,
        original_amount=tx.amount,
        transaction_date=tx.date,
        record_date=converted.record_date,
        exchange_currency=converted.exchange_currency,
        exchange_rate=converted.exchange_rate,
        converted_amount=converted.converted_amount,
    )
