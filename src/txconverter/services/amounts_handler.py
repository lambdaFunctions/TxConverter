from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class DecimalsHandler:
    @staticmethod
    def round_to_two(value: Decimal) -> Decimal:
        return value.quantize(AmountHandler.TWO_PLACES, rounding=ROUND_HALF_UP)


class AmountHandler:
    """Gathers the necessary logic to handle amounts in the way the
    system is expected to behavior.

    **Rounding**

    Rounding logic implemented is the standard for accounting:
        2.845 -> 2.85

    This means a "round half up" strategy is used. The rationale is
    to have a standard behafior expected for what more criterious audit
    process would expected.
    """

    decimals = DecimalsHandler

    TWO_PLACES = Decimal("0.01")

    @staticmethod
    def str_to_decimal(value: str) -> Decimal | InvalidOperation:
        """Note: Opting to convert the `str` into `Decimal` using two
        decimal places as the default behavior/convention given the system's
        context of two decimal places for the fraction part.
        """
        if not isinstance(value, str):
            raise InvalidOperation()

        amount: Decimal = Decimal(value)
        return AmountHandler.decimals.round_to_two(amount)

    @staticmethod
    def decimal_to_str(value: Decimal) -> str:
        return str(AmountHandler.decimals.round_to_two(value))

    @staticmethod
    def is_negative(value: Decimal) -> bool:
        return value < AmountHandler.decimals.round_to_two(Decimal("0"))
