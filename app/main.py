from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api import auth, users, spaces, hubs, devices, events, incidents
from app.config import settings
from app.database import Base, engine

# Створюємо таблиці в базі даних (в виробничому середовищі краще використовувати міграції Alembic)
Base.metadata.create_all(bind=engine)

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# Налаштування CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # У виробничому середовищі тут буде конкретний список дозволених джерел
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(spaces.router, prefix="/api/spaces", tags=["spaces"])
app.include_router(hubs.router, prefix="/api/spaces", tags=["hubs"])
app.include_router(devices.router, prefix="/api/spaces", tags=["devices"])
app.include_router(events.router, prefix="/api/spaces", tags=["events"])
app.include_router(incidents.router, prefix="/api/spaces", tags=["incidents"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
