"""
Traffic forecasting service.
Uses rolling statistics (mean + seasonal decomposition) to predict
traffic volume and flag capacity risks.
"""
import datetime
import logging

import numpy as np
import redis as redis_lib

from config import settings
logger = logging.getLogger(__name__)

_HOURS_PER_WEEK = 168  # 7 * 24


def _get_redis() -> redis_lib.Redis:
    return redis_lib.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )


class ForecastingService:

    def __init__(self):
        self._redis = _get_redis()

    def update_hourly_stats(
        self, prefix: str, hour_of_week: int, pps: float, bps: float
    ) -> None:
        """Store per-prefix per-hour-of-week rolling stats in Redis."""
        max_entries = settings.FORECAST_HISTORY_WEEKS * 1

        for metric, value in (("pps", pps), ("bps", bps)):
            key = f"forecast:{prefix}:{hour_of_week}:{metric}"
            self._redis.rpush(key, value)
            self._redis.ltrim(key, -max_entries, -1)

    def forecast_next_hour(self, prefix: str, current_hour_of_week: int) -> dict:
        """
        Predict traffic for the next hour using rolling mean/std
        of the same hour-of-week from historical data.
        """
        next_hour = (current_hour_of_week + 1) % _HOURS_PER_WEEK

        def _stats(metric: str):
            key = f"forecast:{prefix}:{next_hour}:{metric}"
            raw = self._redis.lrange(key, 0, -1)
            if not raw:
                return 0.0, 0.0, 0
            values = [float(v) for v in raw]
            arr = np.array(values)
            return float(np.mean(arr)), float(np.std(arr)), len(arr)

        pps_mean, pps_std, pps_n = _stats("pps")
        bps_mean, bps_std, bps_n = _stats("bps")

        confidence = min(1.0, (pps_n / max(settings.FORECAST_HISTORY_WEEKS, 1)))

        risk_level = _compute_risk_level(pps_mean, pps_std)

        return {
            "prefix": prefix,
            "next_hour_of_week": next_hour,
            "predicted_pps": pps_mean,
            "predicted_bps": bps_mean,
            "pps_std": pps_std,
            "bps_std": bps_std,
            "confidence": round(confidence, 3),
            "risk_level": risk_level,
            "samples": pps_n,
        }

    def get_capacity_risk(self, prefixes: list) -> list:
        """Return predicted peak and capacity risk level for each prefix."""
        results = []
        now = datetime.datetime.now(datetime.timezone.utc)
        current_hour = now.weekday() * 24 + now.hour

        for prefix in prefixes:
            forecast = self.forecast_next_hour(prefix, current_hour)
            results.append({
                "prefix": prefix,
                "predicted_pps": forecast["predicted_pps"],
                "predicted_bps": forecast["predicted_bps"],
                "risk_level": forecast["risk_level"],
                "confidence": forecast["confidence"],
            })
        return results

    def detect_traffic_anomaly_vs_forecast(
        self, prefix: str, actual_pps: float
    ) -> bool:
        """Return True if actual_pps is >2 std deviations from the predicted mean."""
        now = datetime.datetime.now(datetime.timezone.utc)
        current_hour = now.weekday() * 24 + now.hour

        key = f"forecast:{prefix}:{current_hour}:pps"
        raw = self._redis.lrange(key, 0, -1)
        if len(raw) < 5:
            return False

        values = np.array([float(v) for v in raw])
        mean = float(np.mean(values))
        std = float(np.std(values))
        if std < 1.0:
            std = 1.0
        return actual_pps > mean + 2 * std


def _compute_risk_level(mean_pps: float, std_pps: float) -> str:
    peak = mean_pps + 2 * std_pps
    if peak > 1_000_000:
        return "critical"
    if peak > 100_000:
        return "high"
    if peak > 10_000:
        return "medium"
    return "low"
