import asyncio
import json
import os
import time
from pathlib import Path

import portalocker
from loguru import logger

from infra import settings
from src.txconverter.infra.resource_limits import CACHE_FILE_MAX_BYTES

_MAX_AGE_SECONDS = 3600 * 24 * 1


def _cache_path() -> str:
    return str(Path(settings.CACHE_DIR) / "rates.json")


def _lock_path() -> str:
    return str(Path(settings.CACHE_DIR) / "rates.lock")


def _ensure_dir() -> None:
    os.makedirs(settings.CACHE_DIR, exist_ok=True)


def _load() -> dict:
    try:
        with open(_cache_path(), "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


async def find(name: str, possible_dates: list[str]) -> dict | None:
    return await asyncio.to_thread(_find, name, possible_dates)


def _find(name: str, possible_dates: list[str]) -> dict | None:
    """Return the record for `name` on the most recent date found in
    `possible_dates`, or None on a miss.

    Reads without a lock — atomic os.replace writes ensure the file is always
    in a valid JSON state.
    """
    now = time.time()
    cache = _load()

    def _best_record(entry: dict) -> dict | None:
        if now - entry.get("ts", 0) > _MAX_AGE_SECONDS:
            return None
        rates: dict = entry.get("value", {})
        valid = [d for d in possible_dates if d in rates]
        if not valid:
            return None
        return rates[max(valid)]

    entry = cache.get(name)
    if entry is not None:
        return _best_record(entry)

    suffix = f"-{name}"
    matches = [v for k, v in cache.items() if k.endswith(suffix)]
    if len(matches) == 1:
        return _best_record(matches[0])

    return None


async def store(record_date: str, block: dict) -> None:
    await asyncio.to_thread(_store, record_date, block)


def _store(record_date: str, block: dict) -> None:
    """Write currency records keyed by country_currency_desc, with each
    record_date nested inside the entry's value dict.

    Structure: {country_currency_desc: {"value": {record_date: record}, "ts": float}}
    """
    _ensure_dir()
    cache_path = _cache_path()
    current_size = os.path.getsize(cache_path) if os.path.exists(cache_path) else 0
    if current_size >= CACHE_FILE_MAX_BYTES:
        logger.warning(
            "Cache file size ({} bytes) reached limit, skipping write", current_size
        )
        return

    now = time.time()

    with open(_lock_path(), "a") as lock_file:
        portalocker.lock(lock_file, portalocker.LOCK_EX)
        try:
            cache = _load()

            expired = [
                k for k, v in cache.items() if now - v.get("ts", 0) > _MAX_AGE_SECONDS
            ]
            for k in expired:
                del cache[k]

            for desc, record in block.items():
                if desc not in cache:
                    cache[desc] = {"value": {}, "ts": now}
                cache[desc]["value"][record_date] = record
                cache[desc]["ts"] = now

            tmp = _cache_path() + ".tmp"
            with open(tmp, "w") as f:
                json.dump(cache, f)
            os.replace(tmp, _cache_path())
        finally:
            logger.info("Cache was written")
            portalocker.unlock(lock_file)
