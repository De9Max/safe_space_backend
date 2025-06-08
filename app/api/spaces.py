from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.device import Device
from app.models.hub import Hub
from app.models.user import User
from app.models.space import Space
from app.schemas.space import SpaceCreate, SpaceOut, SpaceUpdate
from app.api.deps import get_current_active_user

router = APIRouter()


@router.post("/", response_model=SpaceOut, status_code=status.HTTP_201_CREATED)
def create_space(
        space: SpaceCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    db_space = Space(
        name=space.name,
        type=space.type,
        address=space.address,
        owner_id=current_user.id
    )
    db.add(db_space)
    db.commit()
    db.refresh(db_space)
    return db_space


@router.get("/", response_model=List[SpaceOut])
def read_spaces(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    spaces = db.query(Space).filter(Space.owner_id == current_user.id).offset(skip).limit(limit).all()

    for space in spaces:
        space.device_count = db.query(Device).filter(Device.space_id == space.id).count()
        space.hub_count = db.query(Hub).filter(Hub.space_id == space.id).count()

    return spaces


@router.get("/{space_id}", response_model=SpaceOut)
def read_space(
        space_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    space = db.query(Space).filter(Space.id == space_id, Space.owner_id == current_user.id).first()
    if space is None:
        raise HTTPException(status_code=404, detail="Space not found")

    space.device_count = db.query(Device).filter(Device.space_id == space.id).count()
    space.hub_count = db.query(Hub).filter(Hub.space_id == space.id).count()

    return space


@router.put("/{space_id}", response_model=SpaceOut)
def update_space(
        space_id: int,
        space_update: SpaceUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    space = db.query(Space).filter(Space.id == space_id, Space.owner_id == current_user.id).first()
    if space is None:
        raise HTTPException(status_code=404, detail="Space not found")

    for key, value in space_update.dict(exclude_unset=True).items():
        setattr(space, key, value)

    db.add(space)
    db.commit()
    db.refresh(space)
    return space


@router.delete("/{space_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_space(
        space_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    space = db.query(Space).filter(Space.id == space_id, Space.owner_id == current_user.id).first()
    if space is None:
        raise HTTPException(status_code=404, detail="Space not found")

    db.delete(space)
    db.commit()
    return None
