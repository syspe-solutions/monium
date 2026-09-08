from typing import Protocol


class CacheNamespace(Protocol):
    prefix: str
    ttl: int