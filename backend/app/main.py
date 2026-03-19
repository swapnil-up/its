from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from .database import get_db


app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-health")
def db_health(db:Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}