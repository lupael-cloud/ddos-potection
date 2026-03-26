"""
Attack campaign tracking router.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.models import AttackCampaign, User
from routers.auth_router import get_current_user

router = APIRouter(prefix="/api/v1/campaigns", tags=["Attack Campaigns"])


class CampaignOut(BaseModel):
    id: int
    isp_id: int
    name: str
    campaign_type: Optional[str]
    first_seen: datetime
    last_seen: Optional[datetime]
    total_alerts: int
    peak_pps: int
    peak_bps: int
    source_asns: Optional[list]
    target_prefixes: Optional[list]
    status: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignUpdate(BaseModel):
    notes: Optional[str] = None
    status: Optional[str] = None  # active, resolved


@router.get("/", response_model=List[CampaignOut])
def list_campaigns(
    status: Optional[str] = Query(None, description="Filter by status: active or resolved"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(AttackCampaign).filter(AttackCampaign.isp_id == current_user.isp_id)
    if status:
        q = q.filter(AttackCampaign.status == status)
    return q.order_by(AttackCampaign.last_seen.desc()).all()


@router.get("/{campaign_id}", response_model=CampaignOut)
def get_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    campaign = db.query(AttackCampaign).filter(
        AttackCampaign.id == campaign_id,
        AttackCampaign.isp_id == current_user.isp_id,
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.put("/{campaign_id}", response_model=CampaignOut)
def update_campaign(
    campaign_id: int,
    payload: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in ("admin", "operator"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    campaign = db.query(AttackCampaign).filter(
        AttackCampaign.id == campaign_id,
        AttackCampaign.isp_id == current_user.isp_id,
    ).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if payload.notes is not None:
        campaign.notes = payload.notes
    if payload.status is not None:
        if payload.status not in ("active", "resolved"):
            raise HTTPException(status_code=400, detail="status must be 'active' or 'resolved'")
        campaign.status = payload.status

    db.commit()
    db.refresh(campaign)
    return campaign
