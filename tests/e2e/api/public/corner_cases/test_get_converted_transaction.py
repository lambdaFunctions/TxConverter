from http import HTTPStatus

from tests.e2e.conftest import (
    TRANSACTIONS_URL,
    VERY_LONG_CURRENCY_NAME,
)


class TestGetConvertedTransactionCornerCases:
    def test_currency_name_too_long(self, client, created_transaction_id):
        # A 200-char currency name won't match any Treasury record
        response = client.get(
            f"{TRANSACTIONS_URL}/{created_transaction_id}",
            params={"currency": VERY_LONG_CURRENCY_NAME},
        )

        assert response.status_code in (HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND)
