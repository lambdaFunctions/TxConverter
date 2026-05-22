import asyncio
import fcntl
import json
import os
from decimal import Decimal
from pathlib import Path

import ijson

from infra import settings
from src.txconverter.api.common.pagination import PageParams, PaginatedResult
from src.txconverter.api.public.schemas.transactions import GetTransactionListRequest
from src.txconverter.exceptions.transactions import (
    TxStorageCorruptedError,
    TxStorageFullError,
)
from src.txconverter.infra.resource_limits import TX_FILE_MAX_BYTES
from src.txconverter.models.transactions_model import TransactionsModel


def _read_data(f) -> dict:
    try:
        return json.load(f)
    except json.JSONDecodeError as e:
        raise TxStorageCorruptedError() from e


def _check_file_size(path: Path) -> None:
    size = path.stat().st_size if path.exists() else 0
    if size >= TX_FILE_MAX_BYTES:
        raise TxStorageFullError()


def _path() -> Path:
    return Path(settings.TRANSACTIONS_FILE_PATH)


def _ensure_file() -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        os.write(fd, b"{}")
        os.close(fd)
    except FileExistsError:
        pass


def _matches(tx: dict, f: GetTransactionListRequest) -> bool:
    if f.description and f.description.lower() not in tx.get("description", "").lower():
        return False
    if f.date_from and tx.get("date", "") < str(f.date_from):
        return False
    if f.date_to and tx.get("date", "") > str(f.date_to):
        return False
    if f.amount_min is not None and Decimal(tx.get("amount", "0")) < f.amount_min:
        return False
    if f.amount_max is not None and Decimal(tx.get("amount", "0")) > f.amount_max:
        return False
    return True


class TxRepository:
    def __init__(self) -> None:
        _ensure_file()

    async def create(self, tx: TransactionsModel) -> TransactionsModel:
        return await asyncio.to_thread(self._create, tx)

    def _create(self, tx: TransactionsModel) -> TransactionsModel:
        path = _path()
        _check_file_size(path)
        tmp = path.with_suffix(".tmp")

        with open(path, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                data = _read_data(f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

        data[str(tx.id)] = tx.model_dump(mode="json")

        with open(tmp, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                json.dump(data, f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

        os.replace(tmp, path)
        return tx

    async def get_by_id(self, id: int) -> TransactionsModel | None:
        return await asyncio.to_thread(self._get_by_id, id)

    def _get_by_id(self, id: int) -> TransactionsModel | None:
        with open(_path(), "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                data = _read_data(f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
        record = data.get(str(id))
        return TransactionsModel(**record) if record else None

    async def get_list(
        self, filters: GetTransactionListRequest, params: PageParams
    ) -> PaginatedResult[TransactionsModel]:
        items, total = await asyncio.to_thread(self._get_list, filters, params)
        return PaginatedResult.build(
            [TransactionsModel(**item) for item in items], total, params
        )

    def _get_list(
        self, filters: GetTransactionListRequest, params: PageParams
    ) -> tuple[list[dict], int]:
        offset = (params.page - 1) * params.page_size
        matched = 0
        page_items: list[dict] = []

        try:
            with open(_path(), "rb") as f:
                for _, tx in ijson.kvitems(f, ""):
                    if _matches(tx, filters):
                        matched += 1
                        if matched > offset and len(page_items) < params.page_size:
                            page_items.append(tx)
        except FileNotFoundError:
            pass

        return page_items, matched
