import psutil


def _mb(n: int) -> int:
    return n * 1024 * 1024


def _available_ram() -> int:
    return psutil.virtual_memory().available


TX_FILE_MAX_BYTES: int = min(int(_available_ram() * 0.10), _mb(256))
CACHE_FILE_MAX_BYTES: int = min(int(_available_ram() * 0.05), _mb(128))
