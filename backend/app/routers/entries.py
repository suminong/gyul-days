from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import EntryCreate, EntryResponse, EntryUpdate

from app.security import get_current_user

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
    current_user: models.User = Depends(get_current_user),
):
    new_entry = models.Entry(
        content=entry.content,
        author_id=current_user.id,
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
    current_user: models.User = Depends(get_current_user),
):
    statement = (
        select(models.Entry)
        .where(models.Entry.author_id == current_user.id)
        .order_by(models.Entry.created_at.desc())
    )

    return db.scalars(statement).all()

@router.get(
    "/entries/{entry_id}",
    response_model=EntryResponse,
)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    entry = db.get(models.Entry, entry_id)

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    if entry.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this entry",
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
    current_user: models.User = Depends(get_current_user),
):
    entry = db.get(models.Entry, entry_id)

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    if entry.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this entry",
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
    current_user: models.User = Depends(get_current_user),
):
    entry = db.get(models.Entry, entry_id)

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    if entry.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this entry",
        )

    db.delete(entry)
    db.commit()