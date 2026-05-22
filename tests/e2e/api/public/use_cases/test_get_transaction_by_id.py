import json
from http import HTTPStatus
from unittest.mock import patch

from tests.e2e.conftest import TRANSACTIONS_URL

_TX_REPO_MODULE = "src.txconverter.repository.transactions_repository"
_BUILTINS_MODULE = "builtins"


class TestGetTransactionById:
    def test_success(self, client, created_transaction_id):
        response = client.get(f"{TRANSACTIONS_URL}/{created_transaction_id}")

        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert body["id"] == created_transaction_id
        assert "amount" in body
        assert "description" in body
        assert "date" in body

    def test_router_non_existing_route(self, client):
        # PATCH to /transactions/{id} is not a defined route
        response = client.patch(f"{TRANSACTIONS_URL}/1")

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_schema_invalid_id_not_integer(self, client):
        # The use case casts id to int; non-numeric value triggers a 500
        # because it propagates as ValueError before any explicit validation
        response = client.get(f"{TRANSACTIONS_URL}/not-a-number")

        assert response.status_code in (
            HTTPStatus.UNPROCESSABLE_ENTITY,
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    def test_service_tx_not_found(self, client):
        response = client.get(f"{TRANSACTIONS_URL}/999999999")

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_repository_read_failure(self, client, created_transaction_id):
        with patch(
            _TX_REPO_MODULE + ".TxRepository.get_by_id",
            side_effect=IOError("disk error"),
        ):
            response = client.get(f"{TRANSACTIONS_URL}/{created_transaction_id}")

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_file_handling_failure(self, client, created_transaction_id):
        with patch(
            _BUILTINS_MODULE + ".open",
            side_effect=PermissionError("permission denied"),
        ):
            response = client.get(f"{TRANSACTIONS_URL}/{created_transaction_id}")

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_repository_corrupted_file(self, client, created_transaction_id):
        with patch(
            _TX_REPO_MODULE + ".json.load",
            side_effect=json.JSONDecodeError("bad token", "", 0),
        ):
            response = client.get(f"{TRANSACTIONS_URL}/{created_transaction_id}")

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
