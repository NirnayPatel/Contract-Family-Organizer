"""SHA-256-keyed extraction cache stored in .cfo_cache/."""

import hashlib
import json
import os
from pathlib import Path


def _cache_key(file_path: str) -> str:
    path = Path(file_path)
    stat = path.stat()
    raw = f"{path.resolve()}:{stat.st_mtime}:{stat.st_size}"
    return hashlib.sha256(raw.encode()).hexdigest()


def load(file_path: str, cache_dir: str) -> dict | None:
    key = _cache_key(file_path)
    cache_file = Path(cache_dir) / f"{key}.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


def save(file_path: str, cache_dir: str, data: dict) -> None:
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    key = _cache_key(file_path)
    cache_file = Path(cache_dir) / f"{key}.json"
    cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def clear(cache_dir: str) -> int:
    cache_path = Path(cache_dir)
    if not cache_path.exists():
        return 0
    count = 0
    for f in cache_path.glob("*.json"):
        f.unlink()
        count += 1
    return count
