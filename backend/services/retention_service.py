"""
Data retention background service.
Cleans up expired traffic_logs and alerts based on per-ISP GDPR retention policies.
"""
import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from models.models import GDPRRetentionPolicy, TrafficLog, Alert, AuditLog, ISP

logger = logging.getLogger(__name__)


async def cleanup_expired_data(db: Session) -> dict:
    """
    Delete traffic_logs and alerts older than the ISP's retention policy.
    Returns counts of deleted records per ISP.
    """
    results = {}
    now = datetime.now(timezone.utc)

    policies = db.query(GDPRRetentionPolicy).all()
    all_isp_ids = [isp.id for isp in db.query(ISP).all()]
    policy_map = {p.isp_id: p for p in policies}

    for isp_id in all_isp_ids:
        policy = policy_map.get(isp_id)
        traffic_days = policy.traffic_logs_days if policy else 90
        alerts_days = policy.alerts_days if policy else 365

        traffic_cutoff = now - timedelta(days=traffic_days)
        alerts_cutoff = now - timedelta(days=alerts_days)

        deleted_traffic = (
            db.query(TrafficLog)
            .filter(
                TrafficLog.isp_id == isp_id,
                TrafficLog.timestamp < traffic_cutoff,
            )
            .delete(synchronize_session=False)
        )

        deleted_alerts = (
            db.query(Alert)
            .filter(
                Alert.isp_id == isp_id,
                Alert.created_at < alerts_cutoff,
                Alert.status == "resolved",
            )
            .delete(synchronize_session=False)
        )

        if deleted_traffic > 0 or deleted_alerts > 0:
            results[isp_id] = {
                "traffic_logs_deleted": deleted_traffic,
                "alerts_deleted": deleted_alerts,
            }
            log_entry = AuditLog(
                isp_id=isp_id,
                user_id=None,
                username="retention_service",
                method="DELETE",
                path="/internal/retention-cleanup",
                status_code=200,
                request_body=str(results[isp_id]),
            )
            db.add(log_entry)

    try:
        db.commit()
    except Exception as exc:
        logger.error("retention_service: commit failed: %s", exc)
        db.rollback()

    logger.info("retention cleanup complete: %s", results)
    return results
