from http import HTTPStatus

from tests.e2e.conftest import TRANSACTIONS_URL


class TestGetTransactionListCornerCases:
    def test_list_is_never_null(self, client):
        # The list endpoint must always return a valid object even if the store is empty
        response = client.get(TRANSACTIONS_URL)

        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert "items" in body
        assert body["items"] is not None
