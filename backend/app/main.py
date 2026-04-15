from contextlib import asynccontextmanager

from alembic.config import Config
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from alembic import command

from .core.dependencies import get_current_user
from .database import get_db
from .models import User
from .routers import attachments, auth, comments, issues, users, ws
from .storage import ensure_bucker_exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    ensure_bucker_exists()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health/")
def health():
    return {"status": "ok"}


@app.get("/db-health/")
def db_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}


@app.get("/me/")
def me(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "id": str(current_user.id),
        "full_name": current_user.full_name,
    }


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(issues.router)
app.include_router(users.router)
app.include_router(comments.router)
app.include_router(ws.router)
app.include_router(attachments.router)
