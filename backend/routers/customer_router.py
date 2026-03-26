"""
Customer self-service portal API.
Read-only access scoped to the customer's registered IP prefixes.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import get_db
from models.models import User, Alert, Report, CustomerSettings
from routers.auth_router import get_current_user

router = APIRouter(prefix="/api/v1/customer", tags=["Customer Portal"])


def _require_customer(current_user: User) -> User:
    if current_user.role not in ("customer", "admin"):
        raise HTTPException(status_code=403, detail="Customer access required")
    return current_user


class CustomerSettingsOut(BaseModel):
    id: int
    user_id: int
    isp_id: int
    notification_email: Optional[str]
    webhook_url: Optional[str]
    alert_threshold: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CustomerSettingsUpdate(BaseModel):
    notification_email: Optional[EmailStr] = None
    webhook_url: Optional[str] = None
    alert_threshold: Optional[str] = None  # low, medium, high, critical


@router.get("/my-protection")
def my_protection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List IP prefixes/hostgroups assigned to this customer."""
    _require_customer(current_user)
    return {
        "user_id": current_user.id,
        "isp_id": current_user.isp_id,
        "username": current_user.username,
        "protection_scope": "isp_wide",
        "message": "Contact your ISP administrator to configure specific prefix protection.",
    }


@router.get("/my-alerts")
def my_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Active alerts affecting customer's ISP prefixes (last 30 days)."""
    _require_customer(current_user)
    since = datetime.now(timezone.utc) - timedelta(days=30)
    alerts = (
        db.query(Alert)
        .filter(
            Alert.isp_id == current_user.isp_id,
            Alert.created_at >= since,
        )
        .order_by(Alert.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": a.id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "status": a.status,
            "source_ip": a.source_ip,
            "target_ip": a.target_ip,
            "description": a.description,
            "created_at": a.created_at,
            "resolved_at": a.resolved_at,
        }
        for a in alerts
    ]


@router.get("/my-reports")
def my_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List available reports for this customer."""
    _require_customer(current_user)
    reports = (
        db.query(Report)
        .filter(Report.isp_id == current_user.isp_id)
        .order_by(Report.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": r.id,
            "report_type": r.report_type,
            "period_start": r.period_start,
            "period_end": r.period_end,
            "file_format": r.file_format,
            "created_at": r.created_at,
        }
        for r in reports
    ]


@router.get("/my-settings", response_model=CustomerSettingsOut)
def my_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get notification preferences for this customer."""
    _require_customer(current_user)
    settings = (
        db.query(CustomerSettings)
        .filter(CustomerSettings.user_id == current_user.id)
        .first()
    )
    if not settings:
        settings = CustomerSettings(
            user_id=current_user.id,
            isp_id=current_user.isp_id,
            alert_threshold="high",
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.put("/my-settings", response_model=CustomerSettingsOut)
def update_my_settings(
    payload: CustomerSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update notification preferences (email, webhook URL)."""
    _require_customer(current_user)

    valid_thresholds = ("low", "medium", "high", "critical")
    if payload.alert_threshold and payload.alert_threshold not in valid_thresholds:
        raise HTTPException(
            status_code=400,
            detail=f"alert_threshold must be one of: {valid_thresholds}",
        )

    settings = (
        db.query(CustomerSettings)
        .filter(CustomerSettings.user_id == current_user.id)
        .first()
    )
    if not settings:
        settings = CustomerSettings(
            user_id=current_user.id,
            isp_id=current_user.isp_id,
            alert_threshold="high",
        )
        db.add(settings)

    if payload.notification_email is not None:
        settings.notification_email = payload.notification_email
    if payload.webhook_url is not None:
        settings.webhook_url = payload.webhook_url
    if payload.alert_threshold is not None:
        settings.alert_threshold = payload.alert_threshold

    db.commit()
    db.refresh(settings)
    return settings
