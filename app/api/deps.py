from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.hub import Hub
from app.config import settings
from app.schemas.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_hub_from_api_key(
        api_key: str = Depends(api_key_header),
        db: Session = Depends(get_db)
):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
        )

    hub = db.query(Hub).filter(Hub.api_key == api_key).first()
    if not hub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return hub
