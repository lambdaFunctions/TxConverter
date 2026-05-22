from http import HTTPStatus

from tests.e2e.conftest import (
    TRANSACTIONS_URL,
    VALID_DATE,
    VALID_DESCRIPTION,
    HUGE_INTEGER_AMOUNT,
    HUGE_DECIMAL_AMOUNT,
    NEGATIVE_AMOUNT,
    FUTURE_DATE,
    LARGE_DECIMAL_VALUE,
)


class TestCreateTransactionCornerCases:
    def test_amount_with_huge_integer_part(self, client):
        # A ridiculously large integer part should be rejected by schema validation
        body = {
            "amount": HUGE_INTEGER_AMOUNT,
            "date": VALID_DATE,
            "description": VALID_DESCRIPTION,
        }
        response = client.post(TRANSACTIONS_URL, json=body)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_amount_with_huge_decimal_part(self, client):
        # A ridiculously long decimal part should be rejected or safely rounded
        body = {
            "amount": HUGE_DECIMAL_AMOUNT,
            "date": VALID_DATE,
            "description": VALID_DESCRIPTION,
        }
        response = client.post(TRANSACTIONS_URL, json=body)

        assert response.status_code in (HTTPStatus.OK, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_negative_amount(self, client):
        body = {
            "amount": NEGATIVE_AMOUNT,
            "date": VALID_DATE,
            "description": VALID_DESCRIPTION,
        }
        response = client.post(TRANSACTIONS_URL, json=body)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_future_date(self, client):
        # A date in the future must be rejected
        body = {
            "amount": "10.00",
            "date": FUTURE_DATE,
            "description": VALID_DESCRIPTION,
        }
        response = client.post(TRANSACTIONS_URL, json=body)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_amount_with_large_decimal_value(self, client):
        # A decimal value whose integer part exceeds MAX_AMOUNT must be rejected
        body = {
            "amount": LARGE_DECIMAL_VALUE,
            "date": VALID_DATE,
            "description": VALID_DESCRIPTION,
        }
        response = client.post(TRANSACTIONS_URL, json=body)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
