from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.core.security import get_password_hash
from app.api.deps import get_current_active_user

router = APIRouter()


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_user_me(
        user_update: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    if user_update.email is not None:
        # Перевірка, чи новий email не зайнятий іншим користувачем
        db_user = db.query(User).filter(User.email == user_update.email).first()
        if db_user and db_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered")

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, key, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
