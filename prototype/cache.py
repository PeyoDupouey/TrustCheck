"""Caches courts et locaux pour éviter de recalculer le même contenu."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


def content_key(value: str) -> str:
    """Retourne une clé opaque : le texte n'est jamais conservé dans le cache."""

    normalized = " ".join(value.casefold().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@dataclass
class _Entry(Generic[T]):
    value: T
    expires_at: float


class MemoryTTLCache(Generic[T]):
    """Cache borné par expiration, adapté au processus local du prototype."""

    def __init__(self, ttl_seconds: float = 300.0, max_entries: int = 256) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._entries: dict[str, _Entry[T]] = {}

    def get(self, key: str) -> T | None:
        entry = self._entries.get(key)
        if entry is None:
            return None
        if entry.expires_at <= time.monotonic():
            del self._entries[key]
            return None
        return entry.value

    def put(self, key: str, value: T) -> None:
        if len(self._entries) >= self.max_entries and key not in self._entries:
            oldest_key = min(self._entries, key=lambda item: self._entries[item].expires_at)
            del self._entries[oldest_key]
        self._entries[key] = _Entry(value=value, expires_at=time.monotonic() + self.ttl_seconds)
