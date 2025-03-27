from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io

from app.models.attendee import Attendee
from app.models.exceptions import AttendeeNotFoundException, EventFullException, AttendeeAlreadyRegistered
from app.repository.attendee import AttendeeRepository
from app.repository.event import EventRepository
from app.schema.attendee import AttendeeCreate, AttendeeUpdate, AttendeeFilter, AttendeeResponse


class AttendeeService:
    def __init__(
            self,
            attendee_repository: AttendeeRepository,
            event_repository: EventRepository
    ):
        self.attendee_repository = attendee_repository
        self.event_repository = event_repository

    def register_attendee(self, db: Session, attendee_data: AttendeeCreate) -> Attendee:
        # Check if event exists
        event = self.event_repository.get_by_id(db, attendee_data.event_id)

        # Check if event is full
        if event.is_full():
            raise EventFullException(f"Event with ID {event.event_id} has reached maximum capacity")

        # Check if attendee is already registered for this event
        existing_attendee = self.attendee_repository.get_by_email_and_event(
            db, attendee_data.email, attendee_data.event_id
        )
        if existing_attendee:
            raise AttendeeAlreadyRegistered(
                f"Attendee with email {attendee_data.email} is already registered for event {event.event_id}"
            )

        # Create attendee
        attendee = Attendee(
            first_name=attendee_data.first_name,
            last_name=attendee_data.last_name,
            email=attendee_data.email,
            phone_number=attendee_data.phone_number,
            event_id=attendee_data.event_id
        )
        return self.attendee_repository.create(db, attendee)

    def check_in_attendee(self, db: Session, attendee_id: int) -> Attendee:
        attendee = self.attendee_repository.get_by_id(db, attendee_id)
        attendee.check_in_status = True
        return self.attendee_repository.update(db, attendee)

    def bulk_check_in(self, db: Session, attendee_ids: List[int]) -> int:
        return self.attendee_repository.bulk_check_in(db, attendee_ids)

    def process_csv_check_in(self, db: Session, file_content: bytes, event_id: int) -> dict:
        content = io.StringIO(file_content.decode('utf-8'))
        csv_reader = csv.DictReader(content)

        # Get headers and validate required columns
        headers = csv_reader.fieldnames
        required_fields = ['email']
        for field in required_fields:
            if not any(field in h.lower() for h in headers):
                raise ValueError(f"CSV file must contain an '{field}' column")

        # Find column names (case-insensitive)
        email_field = next((h for h in headers if 'email' in h.lower()), None)
        first_name_field = next((h for h in headers if 'first_name' in h.lower()), None)
        last_name_field = next((h for h in headers if 'last_name' in h.lower()), None)
        phone_field = next((h for h in headers if 'phone' in h.lower()), None)

        # Verify the event exists
        event = self.event_repository.get_by_id(db, event_id)

        # Get all attendees for this event
        attendees = self.attendee_repository.list_by_event(db, event_id, limit=1000)
        email_to_attendee = {attendee.email.lower(): attendee for attendee in attendees}

        checked_in = 0
        registered = 0
        not_found = 0
        already_checked_in = 0
        errors = []

        for row in csv_reader:
            email = row[email_field].lower().strip()

            # Skip empty rows
            if not email:
                continue

            if email in email_to_attendee:
                # Existing attendee - check them in
                attendee = email_to_attendee[email]
                if not attendee.check_in_status:
                    attendee.check_in_status = True
                    checked_in += 1
                else:
                    already_checked_in += 1
            else:
                # New attendee - register them if we have all required fields
                if first_name_field and last_name_field:
                    try:
                        first_name = row[first_name_field].strip()
                        last_name = row[last_name_field].strip()
                        phone_number = row.get(phone_field, "").strip() if phone_field else None

                        # Skip if missing required fields
                        if not first_name or not last_name:
                            not_found += 1
                            continue

                        # Create new attendee
                        new_attendee = self.attendee_repository.create(
                            db,
                            Attendee(
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                phone_number=phone_number,
                                event_id=event_id,
                                check_in_status=True  # Auto-check-in new registrations
                            )
                        )
                        registered += 1
                    except Exception as e:
                        errors.append(f"Error registering {email}: {str(e)}")
                else:
                    not_found += 1

        if checked_in > 0 or registered > 0:
            db.commit()

        result = {
            "checked_in": checked_in,
            "registered": registered,
            "not_found": not_found,
            "already_checked_in": already_checked_in
        }

        if errors:
            result["errors"] = errors

        return result

    def get_attendee(self, db: Session, attendee_id: int) -> Attendee:
        return self.attendee_repository.get_by_id(db, attendee_id)

    def update_attendee(self, db: Session, attendee_id: int, attendee_data: AttendeeUpdate) -> Attendee:
        attendee = self.attendee_repository.get_by_id(db, attendee_id)

        # Update fields if provided
        if attendee_data.first_name is not None:
            attendee.first_name = attendee_data.first_name
        if attendee_data.last_name is not None:
            attendee.last_name = attendee_data.last_name
        if attendee_data.phone_number is not None:
            attendee.phone_number = attendee_data.phone_number
        if attendee_data.check_in_status is not None:
            attendee.check_in_status = attendee_data.check_in_status

        return self.attendee_repository.update(db, attendee)

    def list_event_attendees(
            self,
            db: Session,
            event_id: int,
            filters: AttendeeFilter,
            skip: int = 0,
            limit: int = 100
    ) -> List[Attendee]:
        # Check if event exists
        self.event_repository.get_by_id(db, event_id)

        return self.attendee_repository.list_by_event(
            db,
            event_id=event_id,
            check_in_status=filters.check_in_status,
            first_name=filters.first_name,
            last_name=filters.last_name,
            skip=skip,
            limit=limit
        )

    def to_response(self, attendee: Attendee) -> AttendeeResponse:
        """Convert domain model to response schema"""
        return AttendeeResponse(
            attendee_id=attendee.attendee_id,
            first_name=attendee.first_name,
            last_name=attendee.last_name,
            email=attendee.email,
            phone_number=attendee.phone_number,
            event_id=attendee.event_id,
            check_in_status=attendee.check_in_status
        )
