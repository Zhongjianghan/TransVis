from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    screen_id = Column(String)
    timestamp = Column(DateTime)
