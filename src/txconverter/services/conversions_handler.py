from decimal import Decimal, ROUND_DOWN
from datetime import date
from dateutil.relativedelta import relativedelta

from src.txconverter.models.transactions_model import TransactionsModel
from src.txconverter.models.currencies_model import CurrenciesModel
from src.txconverter.models.conversions_model import ConversionsModel
from src.txconverter.services.amounts_handler import AmountHandler


class ConversionHandler:
    THRESHOLD_MONTHS = 6
    THRESHOLD_YEAR = 2001

    @staticmethod
    def get_possible_dates(target_date: date, sanitize: bool = True) -> list[date]:
        """Returns the most valid target date and its fallbacks (up to the application's
        threshold) based on a requested target date.
        """
        target_year = target_date.year

        quarters = ConversionHandler.get_quarters_dates(
            target_year
        ) + ConversionHandler.get_quarters_dates(target_year - 1)

        result = sorted(
            (q for q in quarters if q <= target_date),
            reverse=True,
        )

        if sanitize:
            return ConversionHandler.sanitize_possible_dates(result)

        return result

    @staticmethod
    def get_quarters_dates(year: int) -> list[date]:
        return [
            date(year, 3, 31),
            date(year, 6, 30),
            date(year, 9, 30),
            date(year, 12, 31),
        ]

    @staticmethod
    def get_threshold_in_iteractions_len() -> int:

        result = Decimal(ConversionHandler.THRESHOLD_MONTHS) / Decimal("3")
        result = result.quantize(Decimal("1"), rounding=ROUND_DOWN)
        return int(result)

    @staticmethod
    def sanitize_possible_dates(dates: list[date]) -> list[date]:
        range_limit = ConversionHandler.get_threshold_in_iteractions_len()
        return dates[:range_limit]

    @staticmethod
    def is_older_than_threshold(target_date: date) -> bool:
        past_threshold = date.today() - relativedelta(
            months=ConversionHandler.THRESHOLD_MONTHS
        )
        return target_date < past_threshold

    @staticmethod
    def is_older_than_available_data(target_date: date) -> bool:
        return target_date.year < ConversionHandler.THRESHOLD_YEAR

    @staticmethod
    def convert_to(
        tx: TransactionsModel, currency: CurrenciesModel
    ) -> ConversionsModel:
        value = Decimal(tx.amount) * Decimal(currency.exchange_rate)
        return ConversionsModel(
            converted_amount=AmountHandler.decimal_to_str(value),
            exchange_rate=currency.exchange_rate,
            exchange_currency=currency.country_currency_desc,
            record_date=currency.record_date,
        )
