import sys
from contextvars import ContextVar

from loguru import logger

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="-")


def _inject_context(record: dict) -> bool:
    record["extra"]["cid"] = correlation_id_var.get()
    return True


def setup_logging() -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "cid={extra[cid]} pid={process} tid={thread} | "
            "{name}:{line} | {message}"
        ),
        filter=_inject_context,
        colorize=False,
        enqueue=True,
    )
