from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import and_

from app.models.attendee import Attendee
from app.models.exceptions import AttendeeNotFoundException


class AttendeeRepository:
    def create(self, db: Session, attendee: Attendee) -> Attendee:
        db.add(attendee)
        db.commit()
        db.refresh(attendee)
        return attendee

    def get_by_id(self, db: Session, attendee_id: int) -> Attendee:
        attendee = db.query(Attendee).filter(Attendee.attendee_id == attendee_id).first()
        if not attendee:
            raise AttendeeNotFoundException(f"Attendee with ID {attendee_id} not found")
        return attendee

    def get_by_email(self, db: Session, email: str) -> Optional[Attendee]:
        return db.query(Attendee).filter(Attendee.email == email).first()

    def get_by_email_and_event(self, db: Session, email: str, event_id: int) -> Optional[Attendee]:
        return db.query(Attendee).filter(
            and_(Attendee.email == email, Attendee.event_id == event_id)
        ).first()

    def update(self, db: Session, attendee: Attendee) -> Attendee:
        db.add(attendee)
        db.commit()
        db.refresh(attendee)
        return attendee

    def delete(self, db: Session, attendee_id: int) -> None:
        attendee = self.get_by_id(db, attendee_id)
        db.delete(attendee)
        db.commit()

    def list_by_event(
            self,
            db: Session,
            event_id: int,
            check_in_status: Optional[bool] = None,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[Attendee]:
        query = db.query(Attendee).filter(Attendee.event_id == event_id)

        if check_in_status is not None:
            query = query.filter(Attendee.check_in_status == check_in_status)

        if first_name:
            query = query.filter(Attendee.first_name.ilike(f"%{first_name}%"))

        if last_name:
            query = query.filter(Attendee.last_name.ilike(f"%{last_name}%"))

        return query.offset(skip).limit(limit).all()

    def bulk_check_in(self, db: Session, attendee_ids: List[int]) -> int:
        updated = 0
        for attendee_id in attendee_ids:
            try:
                attendee = self.get_by_id(db, attendee_id)
                if not attendee.check_in_status:
                    attendee.check_in_status = True
                    updated += 1
            except AttendeeNotFoundException:
                continue

        if updated > 0:
            db.commit()

        return updated
