import logging

from typing import Any, Optional
from django.core.cache import cache
from apps.common.interfaces import CacheNamespace



logger = logging.getLogger(__name__)

class ProductivityNamespace:
    prefix = "prod"
    ttl = 3600  # 1 Hora

class EligibilityNamespace:
    prefix = "elig"
    ttl = 300   # 5 Minutos

class CacheService:
    @staticmethod
    def _build_key(namespace: type[CacheNamespace], *args: Any) -> str:
        if not args:
            return namespace.prefix
        
        sanitized_args = [str(arg) for arg in args if arg is not None]
        return f"{namespace.prefix}:" + ":".join(sanitized_args)

    @classmethod
    def set(cls, namespace: type[CacheNamespace], value: Any, *args: Any):
        key = cls._build_key(namespace, *args)
        try:
            cache.set(key, value, timeout=namespace.ttl)
        except Exception as e:
            logger.error(f"Cache SET Error | Key: {key} | Error: {e}")

    @classmethod
    def get(cls, namespace: type[CacheNamespace], *args: Any) -> Optional[Any]:
        key = cls._build_key(namespace, *args)
        try:
            return cache.get(key)
        except Exception as e:
            logger.error(f"Cache GET Error | Key: {key} | Error: {e}")
            return None

    @classmethod
    def invalidate(cls, namespace: type[CacheNamespace], *args: Any):
        key = cls._build_key(namespace, *args)
        logger.info(f"Cache Invalidation | Key: {key}")
        cache.delete(key)