from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.service.attendee import AttendeeService
from app.schema.attendee import (
    AttendeeCreate, AttendeeUpdate, AttendeeResponse,
    AttendeeFilter, AttendeeCheckIn, BulkCheckIn
)
from app.models.exceptions import (
    AttendeeNotFoundException, EventFullException,
    AttendeeAlreadyRegistered, EventNotFoundException
)
from app.api.dependencies import get_attendee_service, get_current_user

router = APIRouter(prefix="/attendees", tags=["Attendees"])


@router.post("/", response_model=AttendeeResponse, status_code=status.HTTP_201_CREATED)
def register_attendee(
        attendee_data: AttendeeCreate,
        attendee_service: AttendeeService = Depends(get_attendee_service),
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Registers a new attendee for an event."""
    try:
        attendee = attendee_service.register_attendee(db, attendee_data)
        return attendee_service.to_response(attendee)
    except (EventNotFoundException, EventFullException, AttendeeAlreadyRegistered) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/check-in", response_model=AttendeeResponse)
def check_in_attendee(
        check_in_data: AttendeeCheckIn,
        attendee_service: AttendeeService = Depends(get_attendee_service),
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Checks in an attendee to an event."""
    try:
        attendee = attendee_service.check_in_attendee(db, check_in_data.attendee_id)
        return attendee_service.to_response(attendee)
    except AttendeeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/bulk-check-in", status_code=status.HTTP_200_OK)
def bulk_check_in(
        check_in_data: BulkCheckIn,
        attendee_service: AttendeeService = Depends(get_attendee_service),
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Performs bulk check-in for multiple attendees."""
    updated = attendee_service.bulk_check_in(db, check_in_data.attendee_ids)
    return {"message": f"Successfully checked in {updated} attendees"}


@router.post("/csv-check-in/{event_id}", status_code=status.HTTP_200_OK)
async def csv_check_in(
        event_id: int,
        file: UploadFile = File(...),
        register_new: bool = Query(False, description="Register new attendees if they don't exist"),
        attendee_service: AttendeeService = Depends(get_attendee_service),
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Processes attendee check-in from a CSV file."""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a CSV file")

        contents = await file.read()
        result = attendee_service.process_csv_check_in(db, contents, event_id)
        return result
    except (EventNotFoundException, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing CSV: {str(e)}")


@router.get("/event/{event_id}", response_model=List[AttendeeResponse])
def list_event_attendees(
        event_id: int,
        check_in_status: Optional[bool] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        attendee_service: AttendeeService = Depends(get_attendee_service),
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Lists attendees for a specific event with optional filters."""
    try:
        filters = AttendeeFilter(
            check_in_status=check_in_status,
            first_name=first_name,
            last_name=last_name
        )
        attendees = attendee_service.list_event_attendees(db, event_id, filters, skip, limit)
        return [attendee_service.to_response(attendee) for attendee in attendees]
    except EventNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{attendee_id}", response_model=AttendeeResponse)
def get_attendee(
        attendee_id: int,
        attendee_service: AttendeeService = Depends(get_attendee_service),
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Retrieves details of a specific attendee."""
    try:
        attendee = attendee_service.get_attendee(db, attendee_id)
        return attendee_service.to_response(attendee)
    except AttendeeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{attendee_id}", response_model=AttendeeResponse)
def update_attendee(
        attendee_id: int,
        attendee_data: AttendeeUpdate,
        attendee_service: AttendeeService = Depends(get_attendee_service),
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """Updates an attendee's details."""
    try:
        attendee = attendee_service.update_attendee(db, attendee_id, attendee_data)
        return attendee_service.to_response(attendee)
    except AttendeeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
