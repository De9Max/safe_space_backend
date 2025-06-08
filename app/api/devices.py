from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.space import Space
from app.models.hub import Hub
from app.models.device import Device, DeviceType
from app.schemas.device import DeviceCreate, DeviceOut, DeviceUpdate
from app.api.deps import get_current_active_user, get_hub_from_api_key

router = APIRouter()


# Ендпоінт для хабів, щоб реєструвати нові пристрої через API-ключ
@router.post("/hub/devices", response_model=DeviceOut)
def register_device_from_hub(
        device: DeviceCreate,
        db: Session = Depends(get_db),
        hub: Hub = Depends(get_hub_from_api_key)
):
    # Перевіряємо, чи пристрій з таким Zigbee ID вже існує
    if device.zigbee_id:
        existing_device = db.query(Device).filter(Device.zigbee_id == device.zigbee_id).first()
        if existing_device:
            # Якщо пристрій вже зареєстровано, оновлюємо його дані
            for key, value in device.dict(exclude={"zigbee_id", "hub_id", "space_id"}).items():
                setattr(existing_device, key, value)
            db.add(existing_device)
            db.commit()
            db.refresh(existing_device)
            return existing_device

    # Створюємо новий пристрій
    db_device = Device(
        name=device.name,
        type=device.type,
        zigbee_id=device.zigbee_id,
        location=device.location,
        config=device.config,
        hub_id=hub.id,
        space_id=hub.space_id
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


@router.post("/{space_id}/devices", response_model=DeviceOut, status_code=status.HTTP_201_CREATED)
def create_device(
        space_id: int,
        device: DeviceCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # Перевірка, чи існує простір і чи належить він поточному користувачу
    space = db.query(Space).filter(Space.id == space_id, Space.owner_id == current_user.id).first()
    if space is None:
        raise HTTPException(status_code=404, detail="Space not found")

    # Перевірка, чи існує хаб
    if device.hub_id:
        hub = db.query(Hub).filter(Hub.id == device.hub_id, Hub.space_id == space_id).first()
        if hub is None:
            raise HTTPException(status_code=404, detail="Hub not found in this space")

    db_device = Device(
        name=device.name,
        type=device.type,
        zigbee_id=device.zigbee_id,
        location=device.location,
        config=device.config,
        hub_id=device.hub_id,
        space_id=space_id
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


@router.get("/{space_id}/devices", response_model=List[DeviceOut])
def read_devices(
        space_id: int,
        skip: int = 0,
        limit: int = 100,
        device_type: DeviceType = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # Перевірка, чи існує простір і чи належить він поточному користувачу
    space = db.query(Space).filter(Space.id == space_id, Space.owner_id == current_user.id).first()
    if space is None:
        raise HTTPException(status_code=404, detail="Space not found")

    query = db.query(Device).filter(Device.space_id == space_id)
    if device_type:
        query = query.filter(Device.type == device_type)

    devices = query.offset(skip).limit(limit).all()
    return devices


@router.get("/devices/{device_id}", response_model=DeviceOut)
def read_device(
        device_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # Знаходимо пристрій і перевіряємо, чи належить він до простору поточного користувача
    device = db.query(Device).join(Space).filter(
        Device.id == device_id,
        Space.owner_id == current_user.id
    ).first()

    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.put("/devices/{device_id}", response_model=DeviceOut)
def update_device(
        device_id: int,
        device_update: DeviceUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # Знаходимо пристрій і перевіряємо, чи належить він до простору поточного користувача
    device = db.query(Device).join(Space).filter(
        Device.id == device_id,
        Space.owner_id == current_user.id
    ).first()

    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    # Перевірка, чи новий хаб належить до того ж простору
    if device_update.hub_id is not None:
        hub = db.query(Hub).filter(Hub.id == device_update.hub_id, Hub.space_id == device.space_id).first()
        if hub is None:
            raise HTTPException(status_code=400, detail="Hub not found in this space")

    for key, value in device_update.dict(exclude_unset=True).items():
        setattr(device, key, value)

    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
        device_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # Знаходимо пристрій і перевіряємо, чи належить він до простору поточного користувача
    device = db.query(Device).join(Space).filter(
        Device.id == device_id,
        Space.owner_id == current_user.id
    ).first()

    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    db.delete(device)
    db.commit()
    return None

