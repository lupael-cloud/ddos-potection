"""
Audit log access endpoint. Admin-only, paginated.
"""
import csv
import io
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from models.models import AuditLog, User
from routers.auth_router import get_current_user

router = APIRouter(prefix="/api/v1/audit", tags=["Audit Logs"])


def _require_admin(current_user: User) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def _build_query(
    db: Session,
    user_id: Optional[int],
    path: Optional[str],
    method: Optional[str],
    since: Optional[datetime],
    until: Optional[datetime],
):
    q = db.query(AuditLog)
    if user_id is not None:
        q = q.filter(AuditLog.user_id == user_id)
    if path:
        q = q.filter(AuditLog.path.ilike(f"%{path}%"))
    if method:
        q = q.filter(AuditLog.method == method.upper())
    if since:
        q = q.filter(AuditLog.created_at >= since)
    if until:
        q = q.filter(AuditLog.created_at <= until)
    return q


@router.get("/logs")
def list_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=500),
    user_id: Optional[int] = Query(None),
    path: Optional[str] = Query(None),
    method: Optional[str] = Query(None),
    since: Optional[datetime] = Query(None),
    until: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Paginated list of audit log entries (admin only)."""
    _require_admin(current_user)

    q = _build_query(db, user_id, path, method, since, until)
    total_count = q.count()
    offset = (page - 1) * per_page
    logs = q.order_by(AuditLog.created_at.desc()).offset(offset).limit(per_page).all()

    return {
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "total_pages": (total_count + per_page - 1) // per_page,
        "items": [
            {
                "id": log.id,
                "isp_id": log.isp_id,
                "user_id": log.user_id,
                "username": log.username,
                "method": log.method,
                "path": log.path,
                "status_code": log.status_code,
                "client_ip": log.client_ip,
                "created_at": log.created_at,
            }
            for log in logs
        ],
    }


@router.get("/logs/export")
def export_audit_logs_csv(
    user_id: Optional[int] = Query(None),
    path: Optional[str] = Query(None),
    method: Optional[str] = Query(None),
    since: Optional[datetime] = Query(None),
    until: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export audit logs as CSV download (admin only)."""
    _require_admin(current_user)

    q = _build_query(db, user_id, path, method, since, until)
    logs = q.order_by(AuditLog.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "isp_id", "user_id", "username", "method", "path",
                      "status_code", "client_ip", "created_at"])
    for log in logs:
        writer.writerow([
            log.id, log.isp_id, log.user_id, log.username,
            log.method, log.path, log.status_code, log.client_ip,
            log.created_at.isoformat() if log.created_at else "",
        ])

    output.seek(0)
    filename = f"audit_logs_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
