import json
from http import HTTPStatus
from unittest.mock import patch

from tests.e2e.conftest import (
    TRANSACTIONS_URL,
    VALID_TRANSACTION_BODY,
    VALID_AMOUNT,
    VALID_DATE,
    VALID_DESCRIPTION,
    TOO_LONG_DESCRIPTION,
    NEGATIVE_AMOUNT,
)

_TX_REPO_MODULE = "src.txconverter.repository.transactions_repository"
_BUILTINS_MODULE = "builtins"


class TestCreateTransaction:
    def test_success(self, client):
        response = client.post(TRANSACTIONS_URL, json=VALID_TRANSACTION_BODY)

        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert body["description"] == VALID_DESCRIPTION
        assert body["amount"] == VALID_AMOUNT
        assert body["date"] == VALID_DATE
        assert "id" in body

    def test_router_wrong_method(self, client):
        # PUT to /transactions is not a defined route
        response = client.put(TRANSACTIONS_URL, json=VALID_TRANSACTION_BODY)

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_schema_invalid_description_too_long(self, client):
        body = {**VALID_TRANSACTION_BODY, "description": TOO_LONG_DESCRIPTION}
        response = client.post(TRANSACTIONS_URL, json=body)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_schema_invalid_amount_negative(self, client):
        body = {**VALID_TRANSACTION_BODY, "amount": NEGATIVE_AMOUNT}
        response = client.post(TRANSACTIONS_URL, json=body)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_schema_missing_required_field(self, client):
        body = {"amount": VALID_AMOUNT, "date": VALID_DATE}  # missing description
        response = client.post(TRANSACTIONS_URL, json=body)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_repository_write_failure(self, client):
        # Simulates the repository failing to write (e.g. I/O error)
        with patch(
            _TX_REPO_MODULE + ".TxRepository.create",
            side_effect=IOError("disk full"),
        ):
            response = client.post(TRANSACTIONS_URL, json=VALID_TRANSACTION_BODY)

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_file_handling_failure(self, client):
        # Simulates the underlying file open failing (e.g. permissions)
        with patch(
            _BUILTINS_MODULE + ".open",
            side_effect=PermissionError("permission denied"),
        ):
            response = client.post(TRANSACTIONS_URL, json=VALID_TRANSACTION_BODY)

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_repository_corrupted_file(self, client):
        with patch(
            _TX_REPO_MODULE + ".json.load",
            side_effect=json.JSONDecodeError("bad token", "", 0),
        ):
            response = client.post(TRANSACTIONS_URL, json=VALID_TRANSACTION_BODY)

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_schema_invalid_amount_not_a_number(self, client):
        body = {**VALID_TRANSACTION_BODY, "amount": "abc"}
        response = client.post(TRANSACTIONS_URL, json=body)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_schema_invalid_date_format(self, client):
        body = {**VALID_TRANSACTION_BODY, "date": "not-a-date"}
        response = client.post(TRANSACTIONS_URL, json=body)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_amount_is_rounded_to_two_decimal_places(self, client):
        body = {**VALID_TRANSACTION_BODY, "amount": "1.005"}
        response = client.post(TRANSACTIONS_URL, json=body)

        assert response.status_code == HTTPStatus.OK
        assert response.json()["amount"] == "1.01"

    def test_amount_zero_is_accepted(self, client):
        body = {**VALID_TRANSACTION_BODY, "amount": "0.00"}
        response = client.post(TRANSACTIONS_URL, json=body)

        assert response.status_code == HTTPStatus.OK

    def test_repository_rejects_write_when_at_size_limit(self, client):
        with patch(_TX_REPO_MODULE + ".TX_FILE_MAX_BYTES", 0):
            response = client.post(TRANSACTIONS_URL, json=VALID_TRANSACTION_BODY)

        assert response.status_code == HTTPStatus.INSUFFICIENT_STORAGE

    def test_repository_allows_write_when_below_limit(self, client):
        with patch(_TX_REPO_MODULE + ".TX_FILE_MAX_BYTES", 999_999_999):
            response = client.post(TRANSACTIONS_URL, json=VALID_TRANSACTION_BODY)

        assert response.status_code == HTTPStatus.OK
