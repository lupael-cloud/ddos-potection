"""
RPKI/ROA validation service.
Validates BGP route origins against RPKI ROA records via Cloudflare RPKI API.
Flags traffic from RPKI-invalid prefixes.
"""
import asyncio
import ipaddress
import json
import logging
from typing import Optional

import httpx
import redis as redis_lib

from config import settings

logger = logging.getLogger(__name__)

_CACHE_TTL = 3600  # 1 hour


def _get_redis() -> redis_lib.Redis:
    return redis_lib.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )


def _validate_prefix(prefix: str) -> str:
    """Validate and normalize a CIDR prefix. Raises ValueError on invalid input."""
    net = ipaddress.ip_network(prefix, strict=False)
    return str(net)


class RPKIValidator:

    def __init__(self):
        self._redis = _get_redis()

    async def validate_route(self, prefix: str, origin_asn: int) -> dict:
        """
        Validate a BGP route against RPKI ROA records.
        Returns {"valid": bool, "state": "valid|invalid|not-found", "reason": str}
        Caches results in Redis for 1 hour.
        """
        try:
            prefix = _validate_prefix(prefix)
        except ValueError as exc:
            return {"valid": False, "state": "invalid", "reason": f"Invalid prefix: {exc}"}

        cache_key = f"rpki:{prefix}:{origin_asn}"
        cached = self._redis.get(cache_key)
        if cached:
            try:
                return json.loads(cached)
            except Exception:
                pass

        if not settings.RPKI_VALIDATION_ENABLED:
            result = {"valid": True, "state": "not-found", "reason": "RPKI validation disabled"}
            return result

        url = f"{settings.RPKI_API_URL}/{origin_asn}/{prefix}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            logger.warning("RPKI API error for %s AS%d: %s", prefix, origin_asn, exc)
            return {"valid": True, "state": "not-found", "reason": f"API unavailable: {exc}"}

        validity = data.get("result", {}).get("route", {}).get("origin_validity", {})
        state = validity.get("state", "NotFound").lower()
        description = validity.get("description", "")

        if state == "valid":
            result = {"valid": True, "state": "valid", "reason": description}
        elif state == "invalid":
            result = {"valid": False, "state": "invalid", "reason": description}
        else:
            result = {"valid": True, "state": "not-found", "reason": "No ROA found"}

        try:
            self._redis.setex(cache_key, _CACHE_TTL, json.dumps(result))
        except Exception:
            pass

        return result

    async def bulk_validate(self, routes: list) -> list:
        """Validate multiple routes concurrently."""
        tasks = [
            self.validate_route(r.get("prefix", ""), r.get("origin_asn", 0))
            for r in routes
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        output = []
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                output.append({
                    "prefix": routes[i].get("prefix"),
                    "origin_asn": routes[i].get("origin_asn"),
                    "error": str(r),
                    "valid": False,
                    "state": "error",
                })
            else:
                output.append({
                    "prefix": routes[i].get("prefix"),
                    "origin_asn": routes[i].get("origin_asn"),
                    **r,
                })
        return output

    def get_rpki_score(self, prefix: str, origin_asn: int) -> int:
        """Returns 0 (valid/not-found) or 20 (invalid) for threat scoring."""
        cache_key = f"rpki:{prefix}:{origin_asn}"
        cached = self._redis.get(cache_key)
        if cached:
            try:
                data = json.loads(cached)
                return 20 if data.get("state") == "invalid" else 0
            except Exception:
                pass
        return 0
