from fastapi import FastAPI

from app import models
from app.database import Base, engine
from app.routers import entries


app = FastAPI(title="Gyul Days API")


Base.metadata.create_all(bind=engine)


app.include_router(entries.router)


@app.get("/")
def root():
    return {"message": "Gyul Days API is running"}