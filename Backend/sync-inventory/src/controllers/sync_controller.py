from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from src.controllers.schemas import (
    SyncResponse,
    SyncStatusResponse,
    WebhookRequest,
)
from src.domain.enums import ResourceType

router = APIRouter(tags=["sync"])


def _container(request: Request):
    return request.app.state.container


@router.post("/sync/properties", response_model=SyncResponse)
async def sync_properties(request: Request) -> SyncResponse:
    result = await _container(request).sync_service.sync_properties(trigger="manual")
    return SyncResponse(**result.to_dict())


@router.post("/sync/room-types", response_model=SyncResponse)
async def sync_room_types(request: Request) -> SyncResponse:
    result = await _container(request).sync_service.sync_room_types(trigger="manual")
    return SyncResponse(**result.to_dict())


@router.post("/sync/availability", response_model=SyncResponse)
async def sync_availability(request: Request) -> SyncResponse:
    result = await _container(request).sync_service.sync_availability(trigger="manual")
    return SyncResponse(**result.to_dict())


@router.post("/sync/rates", response_model=SyncResponse)
async def sync_rates(request: Request) -> SyncResponse:
    result = await _container(request).sync_service.sync_rates(trigger="manual")
    return SyncResponse(**result.to_dict())


@router.post("/simulation/events/{resource_type}", response_model=SyncResponse)
async def simulate_event(request: Request, resource_type: ResourceType) -> SyncResponse:
    result = await _container(request).sync_service.sync_generated_event(resource_type)
    return SyncResponse(**result.to_dict())


@router.post("/webhooks/pms/{resource_type}", response_model=SyncResponse)
async def receive_webhook(
    request: Request,
    resource_type: ResourceType,
    payload: WebhookRequest,
) -> SyncResponse:
    if not payload.records:
        raise HTTPException(status_code=400, detail="records must not be empty")
    result = await _container(request).sync_service.process_webhook_event(
        resource_type=resource_type,
        raw_records=payload.records,
        source_event_id=payload.event_id,
        source_system=payload.source_system,
    )
    return SyncResponse(**result.to_dict())


@router.get("/sync/status", response_model=SyncStatusResponse)
async def sync_status(request: Request) -> SyncStatusResponse:
    status = _container(request).sync_service.get_status()
    return SyncStatusResponse(**status)
