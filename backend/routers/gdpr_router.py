"""
GDPR data governance endpoints.
- Configurable retention policies per ISP
- Right to erasure: purge all data for an ISP
- Subject access request export
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.models import User, GDPRRetentionPolicy, TrafficLog, Alert, Report, AuditLog
from routers.auth_router import get_current_user

router = APIRouter(tags=["GDPR"])


def _require_admin(current_user: User) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


class RetentionPolicyOut(BaseModel):
    id: int
    isp_id: int
    traffic_logs_days: int
    alerts_days: int
    pcap_days: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class RetentionPolicyUpdate(BaseModel):
    traffic_logs_days: Optional[int] = None
    alerts_days: Optional[int] = None
    pcap_days: Optional[int] = None


@router.get("/api/v1/gdpr/retention-policy/{isp_id}", response_model=RetentionPolicyOut)
def get_retention_policy(
    isp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    policy = db.query(GDPRRetentionPolicy).filter(GDPRRetentionPolicy.isp_id == isp_id).first()
    if not policy:
        policy = GDPRRetentionPolicy(isp_id=isp_id)
        db.add(policy)
        db.commit()
        db.refresh(policy)
    return policy


@router.put("/api/v1/gdpr/retention-policy/{isp_id}", response_model=RetentionPolicyOut)
def update_retention_policy(
    isp_id: int,
    payload: RetentionPolicyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_admin(current_user)
    policy = db.query(GDPRRetentionPolicy).filter(GDPRRetentionPolicy.isp_id == isp_id).first()
    if not policy:
        policy = GDPRRetentionPolicy(isp_id=isp_id)
        db.add(policy)

    if payload.traffic_logs_days is not None:
        policy.traffic_logs_days = payload.traffic_logs_days
    if payload.alerts_days is not None:
        policy.alerts_days = payload.alerts_days
    if payload.pcap_days is not None:
        policy.pcap_days = payload.pcap_days

    db.commit()
    db.refresh(policy)
    return policy


@router.delete("/api/v1/admin/isp/{isp_id}/purge-data")
def purge_isp_data(
    isp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Right to erasure: delete all traffic logs, alerts, PCAPs, reports for an ISP."""
    _require_admin(current_user)

    traffic_count = db.query(TrafficLog).filter(TrafficLog.isp_id == isp_id).delete()
    alert_count = db.query(Alert).filter(Alert.isp_id == isp_id).delete()
    report_count = db.query(Report).filter(Report.isp_id == isp_id).delete()

    db.commit()

    return {
        "isp_id": isp_id,
        "deleted": {
            "traffic_logs": traffic_count,
            "alerts": alert_count,
            "reports": report_count,
        },
        "total_deleted": traffic_count + alert_count + report_count,
    }


@router.get("/api/v1/gdpr/export/{isp_id}")
def export_isp_data(
    isp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Subject access request: return all stored data for an ISP as JSON."""
    _require_admin(current_user)

    traffic_logs = db.query(TrafficLog).filter(TrafficLog.isp_id == isp_id).all()
    alerts = db.query(Alert).filter(Alert.isp_id == isp_id).all()
    reports = db.query(Report).filter(Report.isp_id == isp_id).all()
    audit_logs = db.query(AuditLog).filter(AuditLog.isp_id == isp_id).all()

    def _serialize(obj):
        result = {}
        for col in obj.__table__.columns:
            val = getattr(obj, col.name)
            if isinstance(val, datetime):
                val = val.isoformat()
            result[col.name] = val
        return result

    return {
        "isp_id": isp_id,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "traffic_logs": [_serialize(t) for t in traffic_logs],
        "alerts": [_serialize(a) for a in alerts],
        "reports": [_serialize(r) for r in reports],
        "audit_logs": [_serialize(al) for al in audit_logs],
    }
