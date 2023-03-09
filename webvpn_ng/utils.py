from functools import lru_cache
from pathlib import Path


@lru_cache()
def get_cache_path() -> Path:
    cache_dir = Path.home() / ".cache" / "webvpn-ng"
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)

    return cache_dir
