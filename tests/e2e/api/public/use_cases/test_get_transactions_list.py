from http import HTTPStatus
from unittest.mock import patch

from tests.e2e.conftest import TRANSACTIONS_URL, VALID_DATE

_TX_REPO_MODULE = "src.txconverter.repository.transactions_repository"
_BUILTINS_MODULE = "builtins"

_UNIQUE_DESC = "UniquePaginationTestDesc_7g3k"


def _create_unique(client):
    resp = client.post(
        TRANSACTIONS_URL,
        json={"amount": "10.00", "date": VALID_DATE, "description": _UNIQUE_DESC},
    )
    assert resp.status_code == HTTPStatus.OK
    return resp.json()


class TestGetTransactionList:
    def test_success(self, client):
        response = client.get(TRANSACTIONS_URL)

        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert "items" in body
        assert isinstance(body["items"], list)
        assert "total" in body
        assert "page" in body
        assert "page_size" in body
        assert "pages" in body

    def test_router_wrong_method(self, client):
        response = client.delete(TRANSACTIONS_URL)

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_success_returns_created_transaction(self, client):
        tx = _create_unique(client)

        response = client.get(
            TRANSACTIONS_URL,
            params={"description": _UNIQUE_DESC, "page_size": 100},
        )

        assert response.status_code == HTTPStatus.OK
        ids = [item["id"] for item in response.json()["items"]]
        assert tx["id"] in ids

    def test_repository_read_failure(self, client):
        with patch(
            _TX_REPO_MODULE + ".TxRepository.get_list",
            side_effect=IOError("disk error"),
        ):
            response = client.get(TRANSACTIONS_URL)

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_file_handling_failure(self, client):
        with patch(
            _BUILTINS_MODULE + ".open",
            side_effect=PermissionError("permission denied"),
        ):
            response = client.get(TRANSACTIONS_URL)

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_repository_corrupted_file(self, client):
        with patch(
            _TX_REPO_MODULE + ".ijson.kvitems",
            side_effect=Exception("corrupted JSON stream"),
        ):
            response = client.get(TRANSACTIONS_URL)

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_pagination_defaults(self, client):
        response = client.get(TRANSACTIONS_URL)

        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert body["page"] == 1
        assert body["page_size"] == 10

    def test_pagination_custom_page_size(self, client):
        response = client.get(TRANSACTIONS_URL, params={"page": 1, "page_size": 1})

        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert len(body["items"]) <= 1
        assert body["page_size"] == 1

    def test_filter_by_description(self, client):
        _create_unique(client)

        response = client.get(
            TRANSACTIONS_URL,
            params={"description": _UNIQUE_DESC, "page_size": 100},
        )

        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert body["total"] >= 1
        assert all(_UNIQUE_DESC in item["description"] for item in body["items"])

    def test_filter_by_description_no_match(self, client):
        response = client.get(
            TRANSACTIONS_URL,
            params={"description": "zzz_no_match_zzz"},
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json()["total"] == 0

    def test_filter_by_date_range(self, client):
        tx = _create_unique(client)

        response = client.get(
            TRANSACTIONS_URL,
            params={
                "description": _UNIQUE_DESC,
                "date_from": tx["date"],
                "date_to": tx["date"],
                "page_size": 100,
            },
        )

        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert body["total"] >= 1
        assert all(item["date"] == tx["date"] for item in body["items"])
