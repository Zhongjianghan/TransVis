from fastapi import FastAPI, UploadFile, Depends
from pydantic import BaseModel
import pandas as pd
import io
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List
import numpy as np

# Import database components
from . import crud, models, schemas
from .database import SessionLocal, engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI backend is running"}

# New endpoint for real-time tracking, now with DB integration
@app.post("/track", response_model=schemas.TrackEvent)
async def track_event(event: schemas.TrackEvent, db: Session = Depends(get_db)):
    return crud.create_event(db=db, event=event)

@app.get("/api/timeline", response_model=List[schemas.SessionTimeline])
def get_timeline_data(db: Session = Depends(get_db)):
    events = crud.get_events(db)
    if not events:
        return []

    # Convert event data to a pandas DataFrame
    df = pd.DataFrame([
        {"session_id": e.session_id, "screen_id": e.screen_id, "timestamp": e.timestamp}
        for e in events
    ])
    df = df.sort_values(by=["session_id", "timestamp"])

    # Calculate duration for each event
    df["next_timestamp"] = df.groupby("session_id")["timestamp"].shift(-1)
    df["duration"] = (df["next_timestamp"] - df["timestamp"]).dt.total_seconds()
    # For the last event of each session, assume 30 seconds duration
    df["duration"] = df["duration"].fillna(30)

    # Convert DataFrame back to response format
    timelines = []
    for session_id, group in df.groupby("session_id"):
        events = []
        for _, row in group.iterrows():
            events.append(schemas.SessionDetail(
                screen_id=row["screen_id"],
                timestamp=row["timestamp"],
                duration=row["duration"]
            ))
        timelines.append(schemas.SessionTimeline(
            session_id=session_id,
            events=events
        ))

    return timelines

@app.post("/upload")
async def upload_csv(file: UploadFile):
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    return {"rows": len(df), "columns": list(df.columns)}
