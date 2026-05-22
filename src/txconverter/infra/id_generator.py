import os
from sonyflake import SonyFlake


def _resolve_machine_id() -> int:
    """Each node gets a unique integer ID set via environment variable.
    Valid range: 1–65535 (16 bits).
    """
    machine_id = os.getenv("MACHINE_ID", 1)
    return int(machine_id)


sf = SonyFlake(machine_id=_resolve_machine_id)
