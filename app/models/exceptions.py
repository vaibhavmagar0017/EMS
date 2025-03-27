class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class EventNotFoundException(DomainException):
    """Raised when an event is not found"""
    pass

class AttendeeNotFoundException(DomainException):
    """Raised when an attendee is not found"""
    pass

class EventFullException(DomainException):
    """Raised when an event has reached maximum capacity"""
    pass

class AttendeeAlreadyRegistered(DomainException):
    """Raised when an attendee with the same email is already registered"""
    pass

class EventStatusUpdateException(DomainException):
    """Raised when an event status cannot be updated"""
    pass