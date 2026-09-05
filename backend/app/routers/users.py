from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas import UserCreate, UserResponse
from app.security import hash_password


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    statement = select(models.User).where(
        or_(
            models.User.email == user.email,
            models.User.username == user.username,
        )
    )

    existing_user = db.scalar(statement)

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="Username or email already exists",
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(
            user.password
        ),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user