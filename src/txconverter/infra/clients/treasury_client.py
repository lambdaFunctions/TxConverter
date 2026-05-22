import httpx
from httpx import Response
from loguru import logger

from src.txconverter.infra.clients.treasury_errors import InfraFetchCurrencyError
from infra import settings


class TreasuryClient:
    ENDPOINT = "/accounting/od/rates_of_exchange"

    def __init__(self):
        self._base_url: str = settings.TRRE_API_BASE_URL
        self.fields: str = "country_currency_desc,exchange_rate,record_date"

    def _get_url(self) -> str:
        return f"{self._base_url}{self.ENDPOINT}?fields={self.fields}"

    async def _fetch(self, url: str) -> Response:
        try:
            logger.info("Fetching for: {}", url)
            async with httpx.AsyncClient() as client:
                return await client.get(url)
        except Exception as error:
            logger.error("Internal error fetching currency: {}", error)
            raise InfraFetchCurrencyError()

    def get_currencies_or_none(self, response: Response) -> list[dict]:
        try:
            response.raise_for_status()
            return response.json()["data"]
        except Exception as error:
            logger.warning("Treasury API: error getting response: {}", error)
            return []

    async def fetch_currency_for_date(self, name: str, target_date: str) -> Response:
        filter = (
            f"&filter=country_currency_desc:eq:{name},record_date:lte:{target_date}"
        )
        url = f"{self._get_url()}{filter}"
        return await self._fetch(url)

    async def fetch_all_quartes_currency(
        self, name: str, past_limit: str, current_limit: str
    ) -> Response:
        filter = f"&filter=country_currency_desc:eq:{name},record_date:gte:{past_limit},record_date:lte:{current_limit}"
        url = f"{self._get_url()}{filter}"
        return await self._fetch(url)
