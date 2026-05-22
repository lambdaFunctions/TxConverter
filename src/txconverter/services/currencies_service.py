from datetime import date

from loguru import logger
from httpx import Response

from src.txconverter.cache import rates as rates_cache
from src.txconverter.infra.clients.treasury_client import TreasuryClient
from src.txconverter.infra.clients.treasury_errors import InfraFetchCurrencyError
from src.txconverter.models.currencies_model import CurrenciesModel
from src.txconverter.exceptions.currencies import (
    AmbiguousCurrencyError,
    CurrencyNotFoundError,
)
from src.txconverter.services.conversions_handler import ConversionHandler

treasury_client = TreasuryClient()


class CurrencyService:
    async def get_currency_for_date(
        self, name: str, target_date: str
    ) -> CurrenciesModel | None | AmbiguousCurrencyError:
        response: Response = await treasury_client.fetch_currency_for_date(
            name, target_date
        )
        currencies: list[dict] = treasury_client.get_currencies_or_none(response)

        if len(currencies) == 0:
            return None

        if len(currencies) > 1:
            raise AmbiguousCurrencyError(
                name, [i["country_currency_desc"] for i in currencies]
            )

        return CurrenciesModel(**currencies[0])

    async def get_curency_for_quarters(
        self, name: str, quarters: list[date]
    ) -> list[CurrenciesModel] | AmbiguousCurrencyError | InfraFetchCurrencyError:

        possible_dates = [str(q) for q in quarters]
        record = await rates_cache.find(name, possible_dates)
        if record is not None:
            logger.debug("Cache hit for {} on dates {}", name, possible_dates)
            return [CurrenciesModel(**record)]

        past_limit = str(quarters[-1])
        current_limit = str(quarters[0])
        response: Response = await treasury_client.fetch_all_quartes_currency(
            name, past_limit, current_limit
        )
        raw_currencies: list[dict] = treasury_client.get_currencies_or_none(response)

        logger.info("Fetched currencies: {}", raw_currencies)

        if not raw_currencies:
            return []

        if self.has_different_country_currency(name, raw_currencies):
            raise AmbiguousCurrencyError(
                name, [i["country_currency_desc"] for i in raw_currencies]
            )

        blocks: dict[str, dict] = {}
        for r in raw_currencies:
            record_date = r.get("record_date", current_limit)
            blocks.setdefault(record_date, {})[r["country_currency_desc"]] = r

        for record_date, block in blocks.items():
            await rates_cache.store(record_date, block)

        result = [CurrenciesModel(**r) for r in raw_currencies]
        result.sort(key=lambda x: x.record_date, reverse=True)
        return result

    def has_different_country_currency(self, name: str, data: list[dict]) -> bool:
        return any(item.get("country_currency_desc") != name for item in data)

    async def get_by_name(self, name: str, tx_date: str) -> CurrenciesModel:
        quarters = ConversionHandler.get_possible_dates(date.fromisoformat(tx_date))
        possible_dates = [str(q) for q in quarters]

        record = await rates_cache.find(name, possible_dates)
        if record is not None:
            return CurrenciesModel(**record)

        logger.info(
            "Cache miss for {} on dates {}, querying Treasury API", name, possible_dates
        )
        currencies = await self.get_curency_for_quarters(name, quarters)

        if not currencies:
            raise CurrencyNotFoundError(name)

        return currencies[0]
