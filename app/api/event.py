from fastapi import (
    APIRouter, Depends, HTTPException, BackgroundTasks, Query, status
)
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.service.event import EventService
from app.schema.event import EventCreate, EventUpdate, EventResponse, EventFilter
from app.models.exceptions import EventNotFoundException, EventStatusUpdateException
from app.api.dependencies import get_event_service

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    event_service: EventService = Depends(get_event_service),
    db: Session = Depends(get_db),
):
    """Creates a new event."""
    try:
        event = event_service.create_event(db, event_data)
        return event_service.to_response(event)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    event_service: EventService = Depends(get_event_service),
    db: Session = Depends(get_db),
):
    """Retrieves an event by its ID."""
    try:
        event = event_service.get_event(db, event_id)
        return event_service.to_response(event)
    except EventNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    event_service: EventService = Depends(get_event_service),
    db: Session = Depends(get_db),
):
    """Updates an existing event."""
    try:
        event = event_service.update_event(db, event_id, event_data)
        return event_service.to_response(event)
    except EventNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except (ValueError, EventStatusUpdateException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    event_service: EventService = Depends(get_event_service),
    db: Session = Depends(get_db),
):
    """Deletes an event by its ID."""
    try:
        event_service.delete_event(db, event_id)
    except EventNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    return None


@router.get("/", response_model=List[EventResponse])
def list_events(
    status: Optional[str] = None,
    location: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_service: EventService = Depends(get_event_service),
    db: Session = Depends(get_db),
):
    """Lists events based on optional filters."""
    filters = EventFilter(
        status=status, location=location, start_date=start_date, end_date=end_date
    )
    events = event_service.list_events(db, filters, skip, limit)
    return [event_service.to_response(event) for event in events]


def update_completed_events_task(event_service: EventService, db: Session):
    """Background task to update completed events."""
    event_service.update_completed_events(db)
