from fastapi import FastAPI
from app.core.config import settings
from app.core.database import Base, engine
from app.api.event import router as event_router
from app.api.attendee import router as attendee_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME,debug=settings.DEBUG)

app.include_router(event_router, prefix=settings.API_PREFIX)
app.include_router(attendee_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Event Management Application",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)