from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from app.models.event import EventStatus


class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: str
    max_attendees: int = Field(gt=0)

    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    max_attendees: Optional[int] = Field(default=None, gt=0)
    status: Optional[EventStatus] = None

    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class EventResponse(EventBase):
    event_id: int
    status: EventStatus
    attendee_count: int = 0

    class Config:
        from_attributes = True


class EventFilter(BaseModel):
    status: Optional[EventStatus] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None