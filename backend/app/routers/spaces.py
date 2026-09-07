from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.ai import suggest_tags
from app import models
from app.database import get_db
from app.security import get_current_user

from app.schemas import (
    AITagAccept, 
    AITagSuggestionsResponse,
    EntryCreate,
    EntryImageResponse,
    EntryResponse,
    EntryTagResponse,
    EntryUpdate,
    SpaceCreate,
    SpaceMemberAdd,
    SpaceResponse,
    SpaceUpdate,
    TagCreate,
)
from pathlib import Path
from uuid import uuid4

router = APIRouter(
    prefix="/spaces",
    tags=["spaces"],
)


UPLOAD_DIR = (
    Path(__file__).resolve().parents[2]
    / "uploads"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


MAX_IMAGE_SIZE = (
    10 * 1024 * 1024
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
        .options(
            selectinload(
                models.Entry.images
            ),

            selectinload(
                models.Entry.tag_links
            ).selectinload(
                models.EntryTag.tag
            ),
        )
        .where(
            models.Entry.space_id == space_id
        )
        .order_by(
            models.Entry.created_at.desc()
        )
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
    # 1. Space member인지 확인
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


    # 2. Entry 찾기
    entry = db.scalar(
        select(models.Entry)
        .options(
            selectinload(models.Entry.images)
        )
        .where(
            models.Entry.id == entry_id,
            models.Entry.space_id == space_id,
        )
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )


    # 3. 작성자만 삭제 가능
    if entry.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own entries",
        )


    # 4. 삭제 전에 이미지 파일 경로 저장
    image_paths = []

    for image in entry.images:
        stored_filename = Path(
            image.file_path
        ).name

        image_paths.append(
            UPLOAD_DIR / stored_filename
        )


    # 5. DB에서 Entry 삭제
    # EntryImage row는 relationship/cascade 때문에 같이 삭제됨
    db.delete(entry)
    db.commit()


    # 6. DB 삭제 성공 후 실제 이미지 파일 삭제
    for image_path in image_paths:
        if image_path.exists():
            image_path.unlink()


    return {
        "message": "Entry deleted"
    }


@router.post(
    "/{space_id}/entries/{entry_id}/images",
    response_model=EntryImageResponse,
    status_code=201,
)
async def upload_entry_image(
    space_id: int,
    entry_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    # 1. Check if current user is a member of this Space
    membership = db.scalar(
        select(
            models.SpaceMember
        ).where(
            models.SpaceMember.space_id
            == space_id,
            models.SpaceMember.user_id
            == current_user.id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=403,
            detail=(
                "You are not a member "
                "of this space"
            ),
        )


    # 2. Check if this Entry exists in this Space
    entry = db.scalar(
        select(
            models.Entry
        ).where(
            models.Entry.id
            == entry_id,
            models.Entry.space_id
            == space_id,
        )
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )


    # 3. Only add pictures in your Entry
    if (
        entry.author_id
        != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "You can only add "
                "images to your own entries"
            ),
        )


    # 4. Check image type
    content_type = (
        file.content_type or ""
    )

    if (
        content_type
        not in ALLOWED_IMAGE_TYPES
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPEG, PNG, "
                "and WebP images "
                "are allowed"
            ),
        )


    # 5. Read file
    contents = await file.read(
        MAX_IMAGE_SIZE + 1
    )

    await file.close()


    # 6. Max 10MB
    if (
        len(contents)
        > MAX_IMAGE_SIZE
    ):
        raise HTTPException(
            status_code=413,
            detail=(
                "Image must be "
                "10 MB or smaller"
            ),
        )


    # 7. Generate random safe file name
    extension = (
        ALLOWED_IMAGE_TYPES[
            content_type
        ]
    )

    stored_filename = (
        f"{uuid4().hex}"
        f"{extension}"
    )

    full_path = (
        UPLOAD_DIR
        / stored_filename
    )


    # 8. Save image file
    full_path.write_bytes(
        contents
    )


    # 9. Record file location in DB
    image = models.EntryImage(
        entry_id=entry.id,
        file_path=(
            f"/uploads/"
            f"{stored_filename}"
        ),
        original_filename=(
            file.filename
        ),
        content_type=(
            content_type
        ),
    )

    db.add(image)
    db.commit()
    db.refresh(image)

    return image

@router.delete(
    "/{space_id}/entries/{entry_id}/images/{image_id}",
)
def delete_entry_image(
    space_id: int,
    entry_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # 1. Check if Space member
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

    # 2. Check if Entry exists in this Space
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

    # 3. Only author can delete picture
    if entry.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete images from your own entries",
        )

    # 4. Find image
    image = db.scalar(
        select(models.EntryImage).where(
            models.EntryImage.id == image_id,
            models.EntryImage.entry_id == entry_id,
        )
    )

    if image is None:
        raise HTTPException(
            status_code=404,
            detail="Image not found",
        )

    # 5. uploads folder file directory
    stored_filename = Path(
        image.file_path
    ).name

    full_path = (
        UPLOAD_DIR
        / stored_filename
    )

    # 6. Delete existing file
    if full_path.exists():
        full_path.unlink()

    # 7. Delete from DB as well
    db.delete(image)
    db.commit()

    return {
        "message": "Image deleted"
    }

@router.post(
    "/{space_id}/entries/{entry_id}/tags",
    response_model=EntryTagResponse,
    status_code=201,
)
def add_entry_tag(
    space_id: int,
    entry_id: int,
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    # Check if Space member 
    membership = db.scalar(
        select(
            models.SpaceMember
        ).where(
            models.SpaceMember.space_id
            == space_id,
            models.SpaceMember.user_id
            == current_user.id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this space",
        )


    # Check Entry 
    entry = db.scalar(
        select(
            models.Entry
        ).where(
            models.Entry.id
            == entry_id,
            models.Entry.space_id
            == space_id,
        )
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )


    # Only able to edit tags in your post 
    if (
        entry.author_id
        != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only tag your own entries",
        )


    # "#Food", " food ", "FOOD"
    # all same as "food" 
    tag_name = (
        tag_data.name
        .strip()
        .lstrip("#")
        .lower()
    )

    if not tag_name:
        raise HTTPException(
            status_code=400,
            detail="Tag cannot be empty",
        )


    # Check if same tag exists in this space 
    tag = db.scalar(
        select(
            models.Tag
        ).where(
            models.Tag.space_id
            == space_id,
            models.Tag.name
            == tag_name,
        )
    )


    # if not generate new tag 
    if tag is None:
        tag = models.Tag(
            space_id=space_id,
            name=tag_name,
        )

        db.add(tag)
        db.flush()


    # Check if it's already attached to this entry 
    existing_link = db.scalar(
        select(
            models.EntryTag
        ).where(
            models.EntryTag.entry_id
            == entry_id,
            models.EntryTag.tag_id
            == tag.id,
        )
    )

    if existing_link is not None:
        raise HTTPException(
            status_code=409,
            detail="Tag is already attached to this entry",
        )


    link = models.EntryTag(
        entry_id=entry_id,
        tag_id=tag.id,
        source="manual",
        confidence=None,
    )

    db.add(link)
    db.commit()
    db.refresh(link)


    return {
        "id": link.id,
        "source": link.source,
        "confidence": link.confidence,
        "tag": tag,
    }

@router.delete(
    "/{space_id}/entries/{entry_id}/tags/{tag_id}",
)
def remove_entry_tag(
    space_id: int,
    entry_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    membership = db.scalar(
        select(
            models.SpaceMember
        ).where(
            models.SpaceMember.space_id
            == space_id,
            models.SpaceMember.user_id
            == current_user.id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this space",
        )


    entry = db.scalar(
        select(
            models.Entry
        ).where(
            models.Entry.id
            == entry_id,
            models.Entry.space_id
            == space_id,
        )
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )


    if (
        entry.author_id
        != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only modify your own entries",
        )


    link = db.scalar(
        select(
            models.EntryTag
        ).where(
            models.EntryTag.entry_id
            == entry_id,
            models.EntryTag.tag_id
            == tag_id,
        )
    )

    if link is None:
        raise HTTPException(
            status_code=404,
            detail="Tag not found on this entry",
        )


    db.delete(link)
    db.commit()

    return {
        "message": "Tag removed"
    }

@router.post(
    "/{space_id}/entries/{entry_id}/tag-suggestions",
    response_model=AITagSuggestionsResponse,
)
def get_ai_tag_suggestions(
    space_id: int,
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    # Check Space member 
    membership = db.scalar(
        select(
            models.SpaceMember
        ).where(
            models.SpaceMember.space_id
            == space_id,

            models.SpaceMember.user_id
            == current_user.id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=403,
            detail=(
                "You are not a member "
                "of this space"
            ),
        )


    # Find Entry  
    entry = db.scalar(
        select(
            models.Entry
        ).where(
            models.Entry.id
            == entry_id,

            models.Entry.space_id
            == space_id,
        )
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )


    # Inform AI existing tag names in this Space  
    existing_tags = list(
        db.scalars(
            select(
                models.Tag.name
            )
            .where(
                models.Tag.space_id
                == space_id
            )
            .order_by(
                models.Tag.name
            )
        ).all()
    )


    try:
        tags = suggest_tags(
            content=entry.content,
            existing_tags=existing_tags,
        )

    except Exception as error:
        print(
            "AI tag suggestion error:",
            error,
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Could not generate "
                "AI tag suggestions"
            ),
        )


    return {
        "tags": tags
    }
@router.post(
    "/{space_id}/entries/{entry_id}/ai-tags",
    response_model=EntryTagResponse,
    status_code=201,
)
def accept_ai_tag(
    space_id: int,
    entry_id: int,
    tag_data: AITagAccept,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
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


    if entry.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only tag your own entries",
        )


    tag_name = (
        tag_data.name
        .strip()
        .lstrip("#")
        .lower()
    )


    if not tag_name:
        raise HTTPException(
            status_code=400,
            detail="Tag cannot be empty",
        )


    tag = db.scalar(
        select(models.Tag).where(
            models.Tag.space_id == space_id,
            models.Tag.name == tag_name,
        )
    )


    if tag is None:
        tag = models.Tag(
            space_id=space_id,
            name=tag_name,
        )

        db.add(tag)
        db.flush()


    existing_link = db.scalar(
        select(models.EntryTag).where(
            models.EntryTag.entry_id == entry_id,
            models.EntryTag.tag_id == tag.id,
        )
    )


    if existing_link is not None:
        raise HTTPException(
            status_code=409,
            detail="Tag is already attached to this entry",
        )


    link = models.EntryTag(
        entry_id=entry_id,
        tag_id=tag.id,
        source="ai",
        confidence=None,
    )

    db.add(link)
    db.commit()
    db.refresh(link)


    return {
        "id": link.id,
        "source": link.source,
        "confidence": link.confidence,
        "tag": tag,
    }