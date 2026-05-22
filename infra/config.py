import os
from pathlib import Path

from dynaconf import Dynaconf


_infra_dir = Path(__file__).parent
_env = os.getenv("APP_ENV", "local")

settings = Dynaconf(
    envvar_prefix="APP",
    settings_file=str(_infra_dir / f"{_env}.toml"),
)
