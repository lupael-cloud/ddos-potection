from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Dict, List

from database import get_db
from models.models import TrafficLog, Alert
from routers.auth_router import get_current_user, User
from config import settings
import redis
from collections import Counter
import math

router = APIRouter()

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

class DetectionConfig(BaseModel):
    syn_flood_threshold: int
    udp_flood_threshold: int
    entropy_threshold: float
    
class CollectionStatus(BaseModel):
    netflow_enabled: bool
    sflow_enabled: bool
    ipfix_enabled: bool
    netflow_port: int
    sflow_port: int
    ipfix_port: int

@router.get("/config")
async def get_detection_config(current_user: User = Depends(get_current_user)):
    """Get current detection configuration"""
    return {
        "syn_flood_threshold": settings.SYN_FLOOD_THRESHOLD,
        "udp_flood_threshold": settings.UDP_FLOOD_THRESHOLD,
        "entropy_threshold": settings.ENTROPY_THRESHOLD,
        "icmp_flood_threshold": 10000,
        "dns_amplification_threshold": 500
    }

@router.get("/status")
async def get_collection_status(current_user: User = Depends(get_current_user)):
    """Get traffic collection status"""
    return {
        "netflow": {
            "enabled": True,
            "port": settings.NETFLOW_PORT,
            "version": ["v5", "v9"]
        },
        "sflow": {
            "enabled": True,
            "port": settings.SFLOW_PORT,
            "version": "v5"
        },
        "ipfix": {
            "enabled": True,
            "port": settings.IPFIX_PORT,
            "rfc": "5101"
        }
    }

@router.get("/routers")
async def get_router_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detected routers and their vendors"""
    from sqlalchemy import func, distinct
    
    # Get unique source IPs from traffic logs as potential routers
    routers = db.query(
        TrafficLog.source_ip,
        func.count(TrafficLog.id).label("flow_count"),
        func.max(TrafficLog.timestamp).label("last_seen")
    ).filter(
        TrafficLog.isp_id == current_user.isp_id
    ).group_by(TrafficLog.source_ip).limit(20).all()
    
    return {
        "routers": [
            {
                "ip": r.source_ip,
                "vendor": "Auto-detected",
                "flow_count": r.flow_count,
                "last_seen": r.last_seen.isoformat() if r.last_seen else None
            }
            for r in routers
        ]
    }

@router.get("/entropy")
async def get_entropy_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real-time entropy analysis"""
    # Get recent traffic logs
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)
    
    logs = db.query(TrafficLog).filter(
        TrafficLog.isp_id == current_user.isp_id,
        TrafficLog.timestamp >= five_min_ago
    ).limit(5000).all()
    
    if not logs or len(logs) < 10:
        return {
            "source_entropy": 0.0,
            "destination_entropy": 0.0,
            "protocol_entropy": 0.0,
            "attack_pattern": "none",
            "sample_size": 0
        }
    
    # Calculate entropy for different dimensions
    source_ips = [log.source_ip for log in logs]
    dest_ips = [log.dest_ip for log in logs]
    protocols = [log.protocol for log in logs]
    
    def calculate_entropy(data: List[str]) -> float:
        if not data:
            return 0.0
        frequencies = Counter(data)
        total = len(data)
        entropy = 0.0
        for count in frequencies.values():
            probability = count / total
            entropy -= probability * math.log2(probability)
        return entropy
    
    src_entropy = calculate_entropy(source_ips)
    dst_entropy = calculate_entropy(dest_ips)
    proto_entropy = calculate_entropy(protocols)
    
    # Determine attack pattern
    attack_pattern = "normal"
    if src_entropy < settings.ENTROPY_THRESHOLD and dst_entropy < 1.0:
        attack_pattern = "distributed_ddos"
    elif src_entropy > 5.0 and dst_entropy < 2.0:
        attack_pattern = "volumetric_attack"
    elif src_entropy > 4.0 and dst_entropy > 4.0:
        attack_pattern = "scanning"
    
    return {
        "source_entropy": round(src_entropy, 2),
        "destination_entropy": round(dst_entropy, 2),
        "protocol_entropy": round(proto_entropy, 2),
        "attack_pattern": attack_pattern,
        "sample_size": len(logs),
        "threshold": settings.ENTROPY_THRESHOLD
    }

@router.get("/detection/stats")
async def get_detection_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detection statistics"""
    from sqlalchemy import func
    
    # Get alert counts by type in last 24 hours
    one_day_ago = datetime.utcnow() - timedelta(hours=24)
    
    alert_stats = db.query(
        Alert.alert_type,
        func.count(Alert.id).label("count")
    ).filter(
        Alert.isp_id == current_user.isp_id,
        Alert.created_at >= one_day_ago
    ).group_by(Alert.alert_type).all()
    
    return {
        "detection_types": {
            "syn_flood": next((s.count for s in alert_stats if s.alert_type == "syn_flood"), 0),
            "udp_flood": next((s.count for s in alert_stats if s.alert_type == "udp_flood"), 0),
            "icmp_flood": next((s.count for s in alert_stats if s.alert_type == "icmp_flood"), 0),
            "dns_amplification": next((s.count for s in alert_stats if s.alert_type == "dns_amplification"), 0),
            "distributed_ddos": next((s.count for s in alert_stats if s.alert_type == "distributed_ddos"), 0),
            "volumetric_attack": next((s.count for s in alert_stats if s.alert_type == "volumetric_attack"), 0)
        },
        "period": "24h"
    }
