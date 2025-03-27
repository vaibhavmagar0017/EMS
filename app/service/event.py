from typing import List

from sqlalchemy.orm import Session

from app.models.event import Event, EventStatus
from app.repository.event import EventRepository
from app.schema.event import EventCreate, EventUpdate, EventFilter, EventResponse


class EventService:
    def __init__(self, event_repository: EventRepository):
        self.event_repository = event_repository

    def create_event(self, db: Session, event_data: EventCreate) -> Event:
        event = Event(
            name=event_data.name,
            description=event_data.description,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            location=event_data.location,
            max_attendees=event_data.max_attendees,
            status=EventStatus.SCHEDULED
        )
        return self.event_repository.create(db, event)

    def get_event(self, db: Session, event_id: int) -> Event:
        return self.event_repository.get_by_id(db, event_id)

    def update_event(self, db: Session, event_id: int, event_data: EventUpdate) -> Event:
        event = self.event_repository.get_by_id(db, event_id)

        # Update fields if provided
        if event_data.name is not None:
            event.name = event_data.name
        if event_data.description is not None:
            event.description = event_data.description
        if event_data.start_time is not None:
            event.start_time = event_data.start_time
        if event_data.end_time is not None:
            event.end_time = event_data.end_time
        if event_data.location is not None:
            event.location = event_data.location
        if event_data.max_attendees is not None:
            event.max_attendees = event_data.max_attendees
        if event_data.status is not None:
            event.status = event_data.status

        # Validate that start_time is before end_time
        if event.start_time >= event.end_time:
            raise ValueError("start_time must be before end_time")

        return self.event_repository.update(db, event)

    def delete_event(self, db: Session, event_id: int) -> None:
        self.event_repository.delete(db, event_id)

    def list_events(
            self,
            db: Session,
            filters: EventFilter,
            skip: int = 0,
            limit: int = 100
    ) -> List[Event]:
        return self.event_repository.list(
            db,
            status=filters.status,
            location=filters.location,
            start_date=filters.start_date,
            end_date=filters.end_date,
            skip=skip,
            limit=limit
        )

    def update_completed_events(self, db: Session) -> int:

        return self.event_repository.update_completed_events(db)

    def to_response(self, event: Event) -> EventResponse:
        return EventResponse(
            event_id=event.event_id,
            name=event.name,
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
            max_attendees=event.max_attendees,
            status=event.status,
            attendee_count=len(event.attendees)
        )
