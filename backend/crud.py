from sqlalchemy.orm import Session
from . import models, schemas

def get_events(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(models.Event).offset(skip).limit(limit).all()

def create_event(db: Session, event: schemas.TrackEvent):
    db_event = models.Event(
        session_id=event.session_id,
        screen_id=event.screen_id,
        timestamp=event.timestamp
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event
