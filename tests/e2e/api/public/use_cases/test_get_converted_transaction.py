from http import HTTPStatus
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

import httpx
import pytest

from tests.e2e.conftest import (
    TRANSACTIONS_URL,
    VALID_AMOUNT,
    VALID_DESCRIPTION,
    VALID_CURRENCY,
    LEGACY_CURRENCY,
)

_TREASURY_CLIENT_MODULE = "src.txconverter.infra.clients.treasury_client"
_CACHE_MODULE = "src.txconverter.cache.rates"
_CURRENCIES_SERVICE_MODULE = "src.txconverter.services.currencies_service"

_KNOWN_EXCHANGE_RATE = "5.00"
_KNOWN_RECORD_DATE = "2026-03-31"
_EXPECTED_CONVERTED_AMOUNT = str(
    (Decimal(VALID_AMOUNT) * Decimal(_KNOWN_EXCHANGE_RATE)).quantize(Decimal("0.01"))
)


@pytest.fixture
def known_currency_record():
    record = {
        "country_currency_desc": VALID_CURRENCY,
        "exchange_rate": _KNOWN_EXCHANGE_RATE,
        "record_date": _KNOWN_RECORD_DATE,
    }
    with patch(_CACHE_MODULE + ".find", return_value=record):
        yield record


class TestGetConvertedTransaction:
    def test_success(self, client, created_transaction_id, known_currency_record):
        response = client.get(
            f"{TRANSACTIONS_URL}/{created_transaction_id}",
            params={"currency": VALID_CURRENCY},
        )

        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert body["exchange_currency"] == VALID_CURRENCY
        assert body["exchange_rate"] == known_currency_record["exchange_rate"]
        assert body["record_date"] == known_currency_record["record_date"]
        assert body["converted_amount"] == _EXPECTED_CONVERTED_AMOUNT

    def test_router_wrong_method(self, client, created_transaction_id):
        response = client.put(
            f"{TRANSACTIONS_URL}/{created_transaction_id}",
            params={"currency": VALID_CURRENCY},
        )

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_schema_invalid_params_very_long_currency(
        self, client, created_transaction_id
    ):
        # A 200-char currency string won't match any Treasury record → 400 not available
        very_long = "A" * 200
        response = client.get(
            f"{TRANSACTIONS_URL}/{created_transaction_id}",
            params={"currency": very_long},
        )

        assert response.status_code in (HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND)

    def test_use_case_tx_not_found(self, client):
        response = client.get(
            f"{TRANSACTIONS_URL}/999999999",
            params={"currency": VALID_CURRENCY},
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_service_currency_not_available_for_date(self, client):
        # Ireland-Pound data is only available up to 2008-01-31.
        # Create a transaction older than that cutoff to trigger CvOlderThanAvailableDataRequestError
        old_tx_body = {
            "amount": VALID_AMOUNT,
            "date": "2001-01-01",
            "description": VALID_DESCRIPTION,
        }
        create_resp = client.post(TRANSACTIONS_URL, json=old_tx_body)
        assert create_resp.status_code == HTTPStatus.OK
        old_tx_id = create_resp.json()["id"]

        response = client.get(
            f"{TRANSACTIONS_URL}/{old_tx_id}",
            params={"currency": LEGACY_CURRENCY},
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_service_conversion_too_old(self, client):
        # A transaction from more than THRESHOLD_MONTHS (6) months ago triggers CvTooOldRequestError
        old_date = str(date.today() - timedelta(days=200))
        old_tx_body = {
            "amount": "10.00",
            "date": old_date,
            "description": "Old tx",
        }
        create_resp = client.post(TRANSACTIONS_URL, json=old_tx_body)
        assert create_resp.status_code == HTTPStatus.OK
        old_tx_id = create_resp.json()["id"]

        response = client.get(
            f"{TRANSACTIONS_URL}/{old_tx_id}",
            params={"currency": VALID_CURRENCY},
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_external_api_wrong_base_url(self, client, created_transaction_id):
        with (
            patch(_CACHE_MODULE + ".find", return_value=None),
            patch(
                _TREASURY_CLIENT_MODULE + ".TreasuryClient._fetch",
                side_effect=httpx.ConnectError("unreachable"),
            ),
        ):
            response = client.get(
                f"{TRANSACTIONS_URL}/{created_transaction_id}",
                params={"currency": VALID_CURRENCY},
            )

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_external_api_gateway_timeout(self, client, created_transaction_id):
        with (
            patch(_CACHE_MODULE + ".find", return_value=None),
            patch(
                _TREASURY_CLIENT_MODULE + ".TreasuryClient.fetch_all_quartes_currency",
                side_effect=httpx.TimeoutException("gateway timeout"),
            ),
        ):
            response = client.get(
                f"{TRANSACTIONS_URL}/{created_transaction_id}",
                params={"currency": VALID_CURRENCY},
            )

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_external_api_rate_limiting(self, client, created_transaction_id):
        rate_limit_response = MagicMock(spec=httpx.Response)
        rate_limit_response.status_code = HTTPStatus.TOO_MANY_REQUESTS
        rate_limit_response.json.return_value = {"error": "rate limit exceeded"}

        with (
            patch(_CACHE_MODULE + ".find", return_value=None),
            patch(
                _TREASURY_CLIENT_MODULE + ".TreasuryClient.fetch_all_quartes_currency",
                return_value=rate_limit_response,
            ),
        ):
            response = client.get(
                f"{TRANSACTIONS_URL}/{created_transaction_id}",
                params={"currency": VALID_CURRENCY},
            )

        assert response.status_code in (
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    def test_external_api_response_body_changed(self, client, created_transaction_id):
        unexpected_response = MagicMock(spec=httpx.Response)
        unexpected_response.status_code = HTTPStatus.OK
        unexpected_response.json.return_value = {"unexpected_key": "unexpected_value"}

        with (
            patch(_CACHE_MODULE + ".find", return_value=None),
            patch(
                _TREASURY_CLIENT_MODULE + ".TreasuryClient.fetch_all_quartes_currency",
                return_value=unexpected_response,
            ),
        ):
            response = client.get(
                f"{TRANSACTIONS_URL}/{created_transaction_id}",
                params={"currency": VALID_CURRENCY},
            )

        assert response.status_code in (
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    def test_service_ambiguous_currency(self, client, created_transaction_id):
        from src.txconverter.exceptions.currencies import AmbiguousCurrencyError

        with (
            patch(_CACHE_MODULE + ".find", return_value=None),
            patch(
                _CURRENCIES_SERVICE_MODULE
                + ".CurrencyService.get_curency_for_quarters",
                side_effect=AmbiguousCurrencyError(
                    "Dollar", ["Canada-Dollar", "Australia-Dollar"]
                ),
            ),
        ):
            response = client.get(
                f"{TRANSACTIONS_URL}/{created_transaction_id}",
                params={"currency": "Dollar"},
            )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_service_currency_not_found_for_period(
        self, client, created_transaction_id
    ):
        # Simulates the API returning no records for the currency in the requested date range
        with (
            patch(_CACHE_MODULE + ".find", return_value=None),
            patch(
                _TREASURY_CLIENT_MODULE + ".TreasuryClient.fetch_all_quartes_currency",
                return_value=MagicMock(),
            ),
            patch(
                _CURRENCIES_SERVICE_MODULE + ".treasury_client.get_currencies_or_none",
                return_value=[],
            ),
        ):
            response = client.get(
                f"{TRANSACTIONS_URL}/{created_transaction_id}",
                params={"currency": VALID_CURRENCY},
            )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_cache_write_failure(self, client, created_transaction_id):
        valid_record = [
            {
                "country_currency_desc": VALID_CURRENCY,
                "exchange_rate": "528.0",
                "record_date": "2026-03-31",
            }
        ]
        with (
            patch(_CACHE_MODULE + ".find", return_value=None),
            patch(
                _TREASURY_CLIENT_MODULE + ".TreasuryClient.fetch_all_quartes_currency",
                return_value=MagicMock(),
            ),
            patch(
                _CURRENCIES_SERVICE_MODULE + ".treasury_client.get_currencies_or_none",
                return_value=valid_record,
            ),
            patch(
                _CACHE_MODULE + ".store",
                side_effect=OSError("disk full on cache partition"),
            ),
        ):
            response = client.get(
                f"{TRANSACTIONS_URL}/{created_transaction_id}",
                params={"currency": VALID_CURRENCY},
            )

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_cache_skips_write_when_at_size_limit(self, client, created_transaction_id):
        valid_record = [
            {
                "country_currency_desc": VALID_CURRENCY,
                "exchange_rate": "528.0",
                "record_date": "2026-03-31",
            }
        ]
        with (
            patch("src.txconverter.cache.rates.CACHE_FILE_MAX_BYTES", 0),
            patch(_CACHE_MODULE + ".find", return_value=None),
            patch(
                _TREASURY_CLIENT_MODULE + ".TreasuryClient.fetch_all_quartes_currency",
                return_value=MagicMock(),
            ),
            patch(
                _CURRENCIES_SERVICE_MODULE + ".treasury_client.get_currencies_or_none",
                return_value=valid_record,
            ),
        ):
            response = client.get(
                f"{TRANSACTIONS_URL}/{created_transaction_id}",
                params={"currency": VALID_CURRENCY},
            )

        assert response.status_code == HTTPStatus.OK

    def test_success_response_has_all_expected_fields(
        self, client, created_transaction_id
    ):
        response = client.get(
            f"{TRANSACTIONS_URL}/{created_transaction_id}",
            params={"currency": VALID_CURRENCY},
        )

        assert response.status_code == HTTPStatus.OK
        assert set(response.json().keys()) == {
            "id",
            "description",
            "transaction_date",
            "original_amount",
            "exchange_currency",
            "exchange_rate",
            "converted_amount",
            "record_date",
        }
