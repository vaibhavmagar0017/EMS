from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List


class AttendeeBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None


class AttendeeCreate(AttendeeBase):
    event_id: int


class AttendeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    check_in_status: Optional[bool] = None


class AttendeeCheckIn(BaseModel):
    attendee_id: int


class BulkCheckIn(BaseModel):
    attendee_ids: List[int]


class AttendeeResponse(AttendeeBase):
    attendee_id: int
    event_id: int
    check_in_status: bool

    class Config:
        from_attributes = True


class AttendeeFilter(BaseModel):
    check_in_status: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None