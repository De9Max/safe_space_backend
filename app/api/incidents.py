from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.device import Device
from app.models.event import Event
from app.models.user import User
from app.models.space import Space
from app.models.incident import Incident, IncidentStatus
from app.schemas.incident import IncidentOut, IncidentStatusUpdate
from app.api.deps import get_current_active_user

router = APIRouter()


@router.get("/{space_id}/incidents", response_model=List[IncidentOut])
def read_incidents(
        space_id: int,
        skip: int = 0,
        limit: int = 100,
        status: IncidentStatus = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # Перевірка, чи існує простір і чи належить він поточному користувачу
    space = db.query(Space).filter(Space.id == space_id, Space.owner_id == current_user.id).first()
    if space is None:
        raise HTTPException(status_code=404, detail="Space not found")

    # Формування запиту для інцидентів
    query = db.query(Incident).join(
        Incident.event
    ).join(
        Event.device
    ).filter(
        Device.space_id == space_id
    )

    if status:
        query = query.filter(Incident.status == status)

    # Сортування за часом створення (найновіші спочатку)
    query = query.order_by(Incident.created_at.desc())

    incidents = query.offset(skip).limit(limit).all()
    return incidents


@router.get("/incidents/{incident_id}", response_model=IncidentOut)
def read_incident(
        incident_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # Знаходимо інцидент і перевіряємо, чи належить він до простору поточного користувача
    incident = db.query(Incident).join(
        Incident.event
    ).join(
        Event.device
    ).join(
        Device.space
    ).filter(
        Incident.id == incident_id,
        Space.owner_id == current_user.id
    ).first()

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


@router.put("/incidents/{incident_id}", response_model=IncidentOut)
def update_incident_status(
        incident_id: int,
        incident_update: IncidentStatusUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    # Знаходимо інцидент і перевіряємо, чи належить він до простору поточного користувача
    incident = db.query(Incident).join(
        Incident.event
    ).join(
        Event.device
    ).join(
        Device.space
    ).filter(
        Incident.id == incident_id,
        Space.owner_id == current_user.id
    ).first()

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Оновлення статусу інциденту
    incident.status = incident_update.status

    # Якщо статус "resolved" або "false_alarm", встановлюємо час вирішення
    if incident_update.status in [IncidentStatus.RESOLVED, IncidentStatus.FALSE_ALARM]:
        incident.resolved_at = datetime.utcnow()

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident
