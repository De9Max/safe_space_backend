from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.device import Device
from app.models.user import User
from app.models.hub import Hub
from app.models.space import Space
from app.schemas.hub import HubCreate, HubOut, HubUpdate
from app.core.security import generate_api_key
from app.api.deps import get_current_active_user, get_hub_from_api_key

router = APIRouter()


@router.post("/{space_id}/hubs", response_model=HubOut, status_code=status.HTTP_201_CREATED)
def create_hub(
        space_id: int,
        hub: HubCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # Перевірка, чи існує простір і чи належить він поточному користувачу
    space = db.query(Space).filter(Space.id == space_id, Space.owner_id == current_user.id).first()
    if space is None:
        raise HTTPException(status_code=404, detail="Space not found")

    # Генерація API-ключа для хаба
    api_key = generate_api_key()

    db_hub = Hub(
        name=hub.name,
        model=hub.model,
        api_key=api_key,
        space_id=space_id
    )
    db.add(db_hub)
    db.commit()
    db.refresh(db_hub)
    return db_hub


@router.get("/{space_id}/hubs", response_model=List[HubOut])
def read_hubs(
        space_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # Перевірка, чи існує простір і чи належить він поточному користувачу
    space = db.query(Space).filter(Space.id == space_id, Space.owner_id == current_user.id).first()
    if space is None:
        raise HTTPException(status_code=404, detail="Space not found")

    hubs = db.query(Hub).filter(Hub.space_id == space_id).offset(skip).limit(limit).all()

    for hub in hubs:
        hub.device_count = db.query(Device).filter(Device.hub_id == hub.id).count()

    return hubs


@router.get("/hubs/{hub_id}", response_model=HubOut)
def read_hub(
        hub_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # Знаходимо хаб і перевіряємо, чи належить він до простору поточного користувача
    hub = db.query(Hub).join(Space).filter(
        Hub.id == hub_id,
        Space.owner_id == current_user.id
    ).first()

    if hub is None:
        raise HTTPException(status_code=404, detail="Hub not found")
    return hub


@router.put("/hubs/{hub_id}", response_model=HubOut)
def update_hub(
        hub_id: int,
        hub_update: HubUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # Знаходимо хаб і перевіряємо, чи належить він до простору поточного користувача
    hub = db.query(Hub).join(Space).filter(
        Hub.id == hub_id,
        Space.owner_id == current_user.id
    ).first()

    if hub is None:
        raise HTTPException(status_code=404, detail="Hub not found")

    for key, value in hub_update.dict(exclude_unset=True).items():
        setattr(hub, key, value)

    db.add(hub)
    db.commit()
    db.refresh(hub)
    return hub


@router.post("/hubs/{hub_id}/regenerate-api-key", response_model=HubOut)
def regenerate_api_key(
        hub_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # Знаходимо хаб і перевіряємо, чи належить він до простору поточного користувача
    hub = db.query(Hub).join(Space).filter(
        Hub.id == hub_id,
        Space.owner_id == current_user.id
    ).first()

    if hub is None:
        raise HTTPException(status_code=404, detail="Hub not found")

    # Генерація нового API-ключа
    hub.api_key = generate_api_key()

    db.add(hub)
    db.commit()
    db.refresh(hub)
    return hub


@router.post("/hub/ping")
def hub_ping(
        db: Session = Depends(get_db),
        hub: Hub = Depends(get_hub_from_api_key)
):
    # Оновлення часу останнього з'єднання хаба
    hub.last_connection = datetime.utcnow()
    hub.is_active = True
    db.add(hub)
    db.commit()
    db.refresh(hub)
    return {"status": "ok"}
