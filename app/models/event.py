from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.common.enum import EventStatus
from app.core.database import Base

class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String(255), nullable=False)
    max_attendees = Column(Integer, nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.SCHEDULED, nullable=False)

    attendees = relationship("Attendee", back_populates="event", cascade="all, delete-orphan")

    def is_full(self):
        return len(self.attendees) >= self.max_attendees

    def should_complete(self):
        return self.status != EventStatus.CANCELED and datetime.now() > self.end_time