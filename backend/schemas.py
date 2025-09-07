from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict

# Pydantic model for user session details
class SessionDetail(BaseModel):
    screen_id: str
    timestamp: datetime
    duration: float  # duration in seconds

# Pydantic model for session timeline
class SessionTimeline(BaseModel):
    session_id: str
    events: List[SessionDetail]

# Pydantic model for a single tracking event
class TrackEvent(BaseModel):
    session_id: str
    screen_id: str
    timestamp: datetime

    class Config:
        from_attributes = True
