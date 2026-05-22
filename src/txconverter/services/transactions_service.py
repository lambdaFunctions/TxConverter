from datetime import datetime, timezone

from src.txconverter.api.common.pagination import PageParams, PaginatedResult
from src.txconverter.api.public.schemas.transactions import GetTransactionListRequest
from src.txconverter.models.transactions_model import TransactionsModel
from src.txconverter.repository.transactions_repository import TxRepository
from src.txconverter.services.conversions_handler import ConversionHandler
from src.txconverter.infra.id_generator import sf


class PurchaseTxService:
    def __init__(self):
        self.repo = TxRepository()
        self.conversions = ConversionHandler()

    def _generate_id(self) -> int:
        return sf.next_id()

    async def create(self, raw_tx: dict) -> TransactionsModel:
        tx = TransactionsModel(
            id=self._generate_id(),
            created_at=datetime.now(timezone.utc).isoformat(),
            **raw_tx,
        )
        return await self.repo.create(tx)

    async def get_by_id(self, id: int) -> TransactionsModel | None:
        return await self.repo.get_by_id(id)

    async def get_list(
        self, filters: GetTransactionListRequest, params: PageParams
    ) -> PaginatedResult[TransactionsModel]:
        return await self.repo.get_list(filters, params)
