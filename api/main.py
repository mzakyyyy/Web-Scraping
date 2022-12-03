from fastapi import FastAPI
import models
from database import engine, SessionLocal

from routers import properties, users

app = FastAPI(title="Properties KPR",)

models.Base.metadata.create_all(bind=engine)

app.include_router(properties.router)
app.include_router(users.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
















