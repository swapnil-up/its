from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from .database import get_db
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, issues, users, comments, ws, attachments

from .core.dependencies import get_current_user
from .models import User
from .storage import ensure_bucker_exists

from contextlib import asynccontextmanager
from alembic.config import Config
from alembic import command


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
