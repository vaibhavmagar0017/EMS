from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.repository.attendee import AttendeeRepository
from app.repository.event import EventRepository
from app.service.attendee import AttendeeService
from app.service.event import EventService


# Repositories
def get_event_repository():
    return EventRepository()


def get_attendee_repository():
    return AttendeeRepository()


# Services
def get_event_service(
        event_repository: EventRepository = Depends(get_event_repository),
):
    return EventService(event_repository)


def get_attendee_service(
        attendee_repository: AttendeeRepository = Depends(get_attendee_repository),
        event_repository: EventRepository = Depends(get_event_repository),
):
    return AttendeeService(attendee_repository, event_repository)


# JWT Authentication (Extra Credit)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return {"username": username}