import datetime

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.space import Space
from app.models.hub import Hub
from app.models.device import Device
from app.models.event import Event, EventType
from app.schemas.event import EventCreate, EventOut
from app.core.event_processor import process_event
from app.api.deps import get_current_active_user, get_hub_from_api_key

router = APIRouter()


@router.get("/{space_id}/events", response_model=List[EventOut])
def read_events(
        space_id: int,
        skip: int = 0,
        limit: int = 100,
        event_type: EventType = None,
        device_id: int = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # Перевірка, чи існує простір і чи належить він поточному користувачу
    space = db.query(Space).filter(Space.id == space_id, Space.owner_id == current_user.id).first()
    if space is None:
        raise HTTPException(status_code=404, detail="Space not found")

    # Формування запиту для подій
    query = db.query(Event).join(Device).filter(Device.space_id == space_id)

    if event_type:
        query = query.filter(Event.type == event_type)

    if device_id:
        query = query.filter(Event.device_id == device_id)

    # Сортування за часом створення (найновіші спочатку)
    query = query.order_by(Event.created_at.desc())

    events = query.offset(skip).limit(limit).all()
    return events


@router.get("/devices/{device_id}/events", response_model=List[EventOut])
def read_events(
        device_id: int,
        skip: int = 0,
        limit: int = 100,
        event_type: EventType = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    device = db.query(Device).filter(Device.id == device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    # Формування запиту для подій
    query = db.query(Event).join(Device).filter(Device.id == device_id)

    if event_type:
        query = query.filter(Event.type == event_type)

    # Сортування за часом створення (найновіші спочатку)
    query = query.order_by(Event.created_at.desc())

    events = query.offset(skip).limit(limit).all()
    print(events)
    return events


@router.post("/hub/events", response_model=EventOut)
async def create_event_from_hub(
        event: EventCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        hub: Hub = Depends(get_hub_from_api_key)
):
    # Перевірка, чи існує пристрій у системі
    device = db.query(Device).filter(
        Device.id == event.device_id,
        Device.hub_id == hub.id
    ).first()

    if device is None:
        # Перевірка, чи можна знайти пристрій за Zigbee ID
        if event.zigbee_id:
            device = db.query(Device).filter(
                Device.zigbee_id == event.zigbee_id,
                Device.hub_id == hub.id
            ).first()

            if device is None:
                raise HTTPException(status_code=404, detail="Device not found")
        else:
            raise HTTPException(status_code=404, detail="Device not found")

    if(event.data.get('battery', None)):
        device.battery_level = event.data.get('battery')
        device.last_seen = datetime.datetime.now()
        db.add(device)
        db.commit()
        db.refresh(device)


    # Створення події в базі даних
    db_event = Event(
        type=event.type,
        data=event.data,
        device_id=device.id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Запуск обробки події у фоновому режимі
    background_tasks.add_task(process_event, db_event.id)

    return db_event
