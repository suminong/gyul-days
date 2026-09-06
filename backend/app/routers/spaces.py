from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import (
    SpaceCreate,
    SpaceMemberAdd,
    SpaceResponse,
)
from app.security import get_current_user


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