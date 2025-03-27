from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.event import Event, EventStatus
from app.models.exceptions import EventNotFoundException


class EventRepository:
    def create(self, db: Session, event: Event) -> Event:
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    def get_by_id(self, db: Session, event_id: int) -> Event:
        event = db.query(Event).filter(Event.event_id == event_id).first()
        if not event:
            raise EventNotFoundException(f"Event with ID {event_id} not found")
        return event

    def update(self, db: Session, event: Event) -> Event:
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    def delete(self, db: Session, event_id: int) -> None:
        event = self.get_by_id(db, event_id)
        db.delete(event)
        db.commit()

    def list(
            self,
            db: Session,
            status: Optional[EventStatus] = None,
            location: Optional[str] = None,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[Event]:
        query = db.query(Event)

        if status:
            query = query.filter(Event.status == status)

        if location:
            query = query.filter(Event.location.ilike(f"%{location}%"))

        if start_date:
            query = query.filter(Event.start_time >= start_date)

        if end_date:
            query = query.filter(Event.start_time <= end_date)

        return query.offset(skip).limit(limit).all()

    def update_completed_events(self, db: Session) -> int:
        """Update all events that have ended to 'completed' status"""
        now = datetime.now()
        events = (
            db.query(Event)
            .filter(Event.end_time < now)
            .filter(Event.status == EventStatus.SCHEDULED)
            .all()
        )

        count = 0
        for event in events:
            event.status = EventStatus.COMPLETED
            count += 1

        if count > 0:
            db.commit()

        return count