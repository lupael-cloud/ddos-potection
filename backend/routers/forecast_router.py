"""
Traffic forecasting router.
"""
import datetime
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models.models import User
from routers.auth_router import get_current_user
from services.forecasting_service import ForecastingService

router = APIRouter(prefix="/api/v1/forecast", tags=["Traffic Forecasting"])


def _get_forecaster() -> ForecastingService:
    return ForecastingService()


@router.get("/capacity-risk")
def capacity_risk(
    prefixes: str = Query(..., description="Comma-separated list of prefixes"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get capacity risk for all specified prefixes."""
    prefix_list = [p.strip() for p in prefixes.split(",") if p.strip()]
    forecaster = _get_forecaster()
    return forecaster.get_capacity_risk(prefix_list)


@router.get("/{prefix:path}")
def get_forecast(
    prefix: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get traffic forecast for a specific prefix."""
    now = datetime.datetime.now(datetime.timezone.utc)
    current_hour = now.weekday() * 24 + now.hour
    forecaster = _get_forecaster()
    return forecaster.forecast_next_hour(prefix, current_hour)
