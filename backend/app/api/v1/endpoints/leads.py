"""
Leads API endpoints for RiseAgent AI.
Handles lead creation, retrieval, updates, and management.
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app import schemas
from app.core.database import get_db
from app.services.lead_service import LeadService
from app.services.voice_service import VoiceService
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=schemas.LeadCreateResponse)
async def create_lead(
    lead_in: schemas.LeadCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> schemas.LeadCreateResponse:
    """
    Create a new lead and initiate outbound call.

    This endpoint creates a lead record and immediately triggers
    an outbound voice call using the AI agent.
    """
    try:
        # Create lead
        lead_service = LeadService(db)
        lead = await lead_service.create_lead(lead_in)

        # Generate call ID for tracking
        call_id = str(uuid.uuid4())

        # Initiate outbound call in background
        voice_service = VoiceService(db)
        background_tasks.add_task(
            voice_service.initiate_outbound_call,
            lead.lead_id,
            call_id
        )

        logger.info(
            "Lead created and call initiated",
            lead_id=lead.lead_id,
            call_id=call_id
        )

        return schemas.LeadCreateResponse(
            lead=lead,
            call_id=call_id,
            message="Lead created successfully. Outbound call initiated.",
            estimated_wait_time=30  # seconds
        )

    except Exception as e:
        logger.error("Failed to create lead", error=str(e), lead_data=lead_in.dict())
        raise HTTPException(status_code=500, detail="Failed to create lead")


@router.get("/{lead_id}", response_model=schemas.LeadWithStats)
async def get_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
) -> schemas.LeadWithStats:
    """
    Get lead by ID with statistics.
    """
    lead_service = LeadService(db)
    lead = await lead_service.get_lead_with_stats(lead_id)

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return lead


@router.get("/", response_model=List[schemas.LeadSummary])
async def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    classification: Optional[str] = None,
    source: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> List[schemas.LeadSummary]:
    """
    List leads with optional filtering.
    """
    lead_service = LeadService(db)
    leads = await lead_service.list_leads(
        skip=skip,
        limit=limit,
        status=status,
        classification=classification,
        source=source
    )
    return leads


@router.put("/{lead_id}", response_model=schemas.LeadResponse)
async def update_lead(
    lead_id: str,
    lead_update: schemas.LeadUpdate,
    db: AsyncSession = Depends(get_db),
) -> schemas.LeadResponse:
    """
    Update lead information.
    """
    lead_service = LeadService(db)
    lead = await lead_service.update_lead(lead_id, lead_update)

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    logger.info("Lead updated", lead_id=lead_id, updates=lead_update.dict(exclude_unset=True))
    return lead


@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Delete a lead (soft delete - mark as inactive).
    """
    lead_service = LeadService(db)
    success = await lead_service.delete_lead(lead_id)

    if not success:
        raise HTTPException(status_code=404, detail="Lead not found")

    logger.info("Lead deleted", lead_id=lead_id)
    return {"message": "Lead deleted successfully"}


@router.post("/{lead_id}/qualify", response_model=schemas.LeadQualificationResult)
async def qualify_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
) -> schemas.LeadQualificationResult:
    """
    Manually trigger lead qualification process.
    """
    lead_service = LeadService(db)
    result = await lead_service.qualify_lead(lead_id)

    if not result:
        raise HTTPException(status_code=404, detail="Lead not found or no conversation data")

    logger.info("Lead qualification completed", lead_id=lead_id, classification=result.classification)
    return result


@router.post("/{lead_id}/whatsapp-followup")
async def send_whatsapp_followup(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Send WhatsApp follow-up message to lead.
    """
    lead_service = LeadService(db)
    success = await lead_service.send_whatsapp_followup(lead_id)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to send WhatsApp message or lead not eligible")

    logger.info("WhatsApp follow-up sent", lead_id=lead_id)
    return {"message": "WhatsApp follow-up sent successfully"}


@router.post("/{lead_id}/handoff/{rm_id}")
async def handoff_to_rm(
    lead_id: str,
    rm_id: str,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Handoff lead to Relationship Manager.
    """
    lead_service = LeadService(db)
    success = await lead_service.handoff_to_rm(lead_id, rm_id, reason)

    if not success:
        raise HTTPException(status_code=400, detail="Failed to handoff lead or lead not eligible")

    logger.info("Lead handed off to RM", lead_id=lead_id, rm_id=rm_id, reason=reason)
    return {"message": f"Lead handed off to RM {rm_id}"}