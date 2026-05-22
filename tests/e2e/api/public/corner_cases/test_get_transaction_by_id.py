from http import HTTPStatus

from tests.e2e.conftest import TRANSACTIONS_URL


class TestGetTransactionByIdCornerCases:
    def test_id_is_zero(self, client):
        response = client.get(f"{TRANSACTIONS_URL}/0")

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_id_is_negative(self, client):
        response = client.get(f"{TRANSACTIONS_URL}/-1")

        assert response.status_code == HTTPStatus.NOT_FOUND
