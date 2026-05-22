import os
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient

os.environ.setdefault("APP_ENV", "test")

from loguru import logger  # noqa: E402
from src.txconverter.main import app  # noqa: E402

logger.remove()


TRANSACTIONS_URL = "/transactions"


# Valid payload constants

VALID_AMOUNT = "100.00"
VALID_DESCRIPTION = "Test purchase"
VALID_DATE = str(date.today() - timedelta(days=30))

# A real currency that exists in the Treasury API for recent quarters
VALID_CURRENCY = "Yemen-Rial"

# A currency known to exist only up to a specific cutoff (Ireland-Pound → until 2008-01-31)
LEGACY_CURRENCY = "Ireland-Pound"
LEGACY_CURRENCY_CUTOFF = "2008-01-31"

VALID_TRANSACTION_BODY = {
    "amount": VALID_AMOUNT,
    "date": VALID_DATE,
    "description": VALID_DESCRIPTION,
}


# Invalid payload constants 

DESCRIPTION_MAX_LEN = 50
TOO_LONG_DESCRIPTION = "A" * (DESCRIPTION_MAX_LEN + 1)

NEGATIVE_AMOUNT = "-50.00"
HUGE_INTEGER_AMOUNT = "9" * 18 + ".00"
HUGE_DECIMAL_AMOUNT = "1." + "9" * 18
LARGE_DECIMAL_VALUE = "9" * 17 + ".99"  # 17-digit integer part, exceeds MAX_AMOUNT

FUTURE_DATE = str(date.today() + timedelta(days=1))

# A currency string longer than any real country_currency_desc
VERY_LONG_CURRENCY_NAME = "A" * 200


@pytest.fixture(scope="session")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def created_transaction(client):
    """Creates a transaction and returns its response body."""
    response = client.post(TRANSACTIONS_URL, json=VALID_TRANSACTION_BODY)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def created_transaction_id(created_transaction):
    return created_transaction["id"]
