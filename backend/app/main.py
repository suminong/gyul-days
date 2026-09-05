from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.database import Base, engine, get_db
from app.schemas import EntryCreate, EntryResponse


app = FastAPI(title="Gyul Days API")


Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Gyul Days API is running"}


@app.post(
    "/entries",
    response_model=EntryResponse,
    status_code=201,
)
def create_entry(
    entry: EntryCreate,
    db: Session = Depends(get_db),
):
    new_entry = models.Entry(
        content=entry.content,
    )

    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return new_entry


@app.get(
    "/entries",
    response_model=list[EntryResponse],
)
def get_entries(
    db: Session = Depends(get_db),
):
    statement = select(models.Entry).order_by(
        models.Entry.created_at.desc()
    )

    entries = db.scalars(statement).all()

    return entries