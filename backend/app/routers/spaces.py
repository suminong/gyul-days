from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.security import get_current_user
from app.schemas import (
    EntryCreate,
    EntryResponse,
    EntryUpdate,
    SpaceCreate,
    SpaceMemberAdd,
    SpaceResponse,
    SpaceUpdate,
)

router = APIRouter(
    prefix="/spaces",
    tags=["spaces"],
)


@router.post(
    "",
    response_model=SpaceResponse,
    status_code=201,
)
def create_space(
    space_data: SpaceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    space = models.Space(
        name=space_data.name,
    )

    db.add(space)
    db.flush()

    membership = models.SpaceMember(
        space_id=space.id,
        user_id=current_user.id,
        role="owner",
    )

    db.add(membership)
    db.commit()
    db.refresh(space)

    return space


@router.get(
    "",
    response_model=list[SpaceResponse],
)
def get_spaces(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    statement = (
        select(models.Space)
        .join(models.SpaceMember)
        .where(
            models.SpaceMember.user_id == current_user.id
        )
        .order_by(
            models.Space.created_at.desc()
        )
    )

    return db.scalars(statement).all()


@router.post(
    "/{space_id}/members",
    status_code=201,
)
def add_member(
    space_id: int,
    member_data: SpaceMemberAdd,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    my_membership = db.scalar(
        select(models.SpaceMember).where(
            models.SpaceMember.space_id == space_id,
            models.SpaceMember.user_id == current_user.id,
        )
    )

    if my_membership is None:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this space",
        )

    if my_membership.role != "owner":
        raise HTTPException(
            status_code=403,
            detail="Only the owner can add members",
        )

    user = db.scalar(
        select(models.User).where(
            models.User.username == member_data.username
        )
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    existing_membership = db.scalar(
        select(models.SpaceMember).where(
            models.SpaceMember.space_id == space_id,
            models.SpaceMember.user_id == user.id,
        )
    )

    if existing_membership is not None:
        raise HTTPException(
            status_code=409,
            detail="User is already in this space",
        )

    membership = models.SpaceMember(
        space_id=space_id,
        user_id=user.id,
        role="member",
    )

    db.add(membership)
    db.commit()

    return {
        "message": f"{user.username} added to space"
    }



@router.get(
    "/{space_id}/entries",
    response_model=list[EntryResponse],
)
def get_space_entries(
    space_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    membership = db.scalar(
        select(models.SpaceMember).where(
            models.SpaceMember.space_id == space_id,
            models.SpaceMember.user_id == current_user.id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this space",
        )

    statement = (
        select(models.Entry)
        .where(models.Entry.space_id == space_id)
        .order_by(models.Entry.created_at.desc())
    )

    return db.scalars(statement).all()

@router.post(
    "/{space_id}/entries",
    response_model=EntryResponse,
    status_code=201,
)
def create_space_entry(
    space_id: int,
    entry_data: EntryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    membership = db.scalar(
        select(models.SpaceMember).where(
            models.SpaceMember.space_id == space_id,
            models.SpaceMember.user_id == current_user.id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this space",
        )

    entry = models.Entry(
        content=entry_data.content,
        author_id=current_user.id,
        space_id=space_id,
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return entry


@router.patch(
    "/{space_id}",
    response_model=SpaceResponse,
)
def update_space(
    space_id: int,
    space_data: SpaceUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    membership = db.scalar(
        select(models.SpaceMember).where(
            models.SpaceMember.space_id == space_id,
            models.SpaceMember.user_id == current_user.id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this space",
        )

    if membership.role != "owner":
        raise HTTPException(
            status_code=403,
            detail="Only the owner can rename this space",
        )

    space = db.get(models.Space, space_id)

    if space is None:
        raise HTTPException(
            status_code=404,
            detail="Space not found",
        )

    space.name = space_data.name

    db.commit()
    db.refresh(space)

    return space

@router.patch(
    "/{space_id}/entries/{entry_id}",
    response_model=EntryResponse,
)
def update_space_entry(
    space_id: int,
    entry_id: int,
    entry_data: EntryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Is this user a member of the space?
    membership = db.scalar(
        select(models.SpaceMember).where(
            models.SpaceMember.space_id == space_id,
            models.SpaceMember.user_id == current_user.id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this space",
        )

    # Find the entry inside this space
    entry = db.scalar(
        select(models.Entry).where(
            models.Entry.id == entry_id,
            models.Entry.space_id == space_id,
        )
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    # Only the author can edit it
    if entry.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only edit your own entries",
        )

    if entry_data.content is not None:
        new_content = entry_data.content.strip()

        if not new_content:
            raise HTTPException(
                status_code=400,
                detail="Entry cannot be empty",
            )

        entry.content = new_content

    db.commit()
    db.refresh(entry)

    return entry


@router.delete(
    "/{space_id}/entries/{entry_id}",
)
def delete_space_entry(
    space_id: int,
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    membership = db.scalar(
        select(models.SpaceMember).where(
            models.SpaceMember.space_id == space_id,
            models.SpaceMember.user_id == current_user.id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this space",
        )

    entry = db.scalar(
        select(models.Entry).where(
            models.Entry.id == entry_id,
            models.Entry.space_id == space_id,
        )
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )

    # Only the author can delete it
    if entry.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own entries",
        )

    db.delete(entry)
    db.commit()

    return {
        "message": "Entry deleted"
    }