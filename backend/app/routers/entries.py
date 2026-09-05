from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import EntryCreate, EntryResponse, EntryUpdate


router = APIRouter(
    tags=["entries"],
)


@router.post(
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


@router.get(
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


@router.get(
    "/entries/{entry_id}",
    response_model=EntryResponse,
)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
):
    entry = db.get(models.Entry, entry_id)

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    return entry


@router.patch(
    "/entries/{entry_id}",
    response_model=EntryResponse,
)
def update_entry(
    entry_id: int,
    entry_update: EntryUpdate,
    db: Session = Depends(get_db),
):
    entry = db.get(models.Entry, entry_id)

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    if entry_update.content is not None:
        entry.content = entry_update.content

    db.commit()
    db.refresh(entry)

    return entry


@router.delete(
    "/entries/{entry_id}",
    status_code=204,
)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
):
    entry = db.get(models.Entry, entry_id)

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    db.delete(entry)
    db.commit()