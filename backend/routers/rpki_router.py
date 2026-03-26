"""
RPKI/ROA validation router.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.models import User
from routers.auth_router import get_current_user
from services.rpki_validator import RPKIValidator

router = APIRouter(prefix="/api/v1/rpki", tags=["RPKI Validation"])


class RouteValidationRequest(BaseModel):
    prefix: str
    origin_asn: int


@router.get("/validate/{asn}/{prefix:path}")
async def validate_route(
    asn: int,
    prefix: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Validate a BGP route against RPKI ROA records."""
    validator = RPKIValidator()
    return await validator.validate_route(prefix, asn)


@router.post("/bulk-validate")
async def bulk_validate(
    routes: List[RouteValidationRequest],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bulk validate multiple BGP routes against RPKI."""
    validator = RPKIValidator()
    route_dicts = [{"prefix": r.prefix, "origin_asn": r.origin_asn} for r in routes]
    return await validator.bulk_validate(route_dicts)
