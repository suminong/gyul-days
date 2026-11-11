from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from app.entry_analysis import analyze_entry_text
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.ai import suggest_tags
from app import models
from app.database import get_db
from app.security import get_current_user
import math

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
    StreakResponse,
)

from uuid import uuid4
from app.storage import (
    create_signed_image_url,
    delete_image_from_storage,
    upload_image,
)
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

router = APIRouter(
    prefix="/spaces",
    tags=["spaces"],
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
            selectinload(
                models.Entry.analysis
            ),
        )
        .where(
            models.Entry.space_id == space_id
        )
        .order_by(
            models.Entry.created_at.desc()
        )
    )
 
    entries = db.scalars(
        statement
    ).all()


    for entry in entries:
        for image in entry.images:

            # new Supabase image
            if (
                image.storage_provider
                == "supabase"
                and image.storage_key
            ):
                try:
                    image.display_url = (
                        create_signed_image_url(
                            image.storage_key
                        )
                    )

                except Exception as error:
                    print(
                        "Signed URL error:",
                        error,
                    )

                    image.display_url = None
    return entries

@router.get(
    "/{space_id}/streak",
    response_model=StreakResponse,
)
def get_space_streak(
    space_id: int,
    timezone_name: str = "UTC",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    # 1. Check Space membership
    membership = db.scalar(
        select(models.SpaceMember).where(
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

    # 2. Validate timezone
    try:
        user_timezone = ZoneInfo(
            timezone_name
        )

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid timezone",
        )

    # 3. Get this user's entry dates
    created_times = db.scalars(
        select(
            models.Entry.created_at
        ).where(
            models.Entry.space_id
            == space_id,
            models.Entry.author_id
            == current_user.id,
        )
    ).all()

    # 4. Convert timestamps into local calendar dates
    recorded_dates = set()

    for created_at in created_times:
        if created_at.tzinfo is None:
            created_at = created_at.replace(
                tzinfo=timezone.utc
            )

        local_date = (
            created_at
            .astimezone(user_timezone)
            .date()
        )

        recorded_dates.add(
            local_date
        )

    # No records yet
    if not recorded_dates:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_recorded_days": 0,
            "stage": "none",
            "next_milestone": 7,
        }

    today = (
        datetime.now(
            user_timezone
        ).date()
    )

    yesterday = (
        today - timedelta(days=1)
    )

    # 5. Current streak
    if today in recorded_dates:
        cursor = today

    elif yesterday in recorded_dates:
        cursor = yesterday

    else:
        cursor = None

    current_streak = 0

    while (
        cursor is not None
        and cursor in recorded_dates
    ):
        current_streak += 1
        cursor -= timedelta(days=1)

    # 6. Longest streak
    sorted_dates = sorted(
        recorded_dates
    )

    longest_streak = 1
    running_streak = 1

    for index in range(
        1,
        len(sorted_dates),
    ):
        previous_date = (
            sorted_dates[index - 1]
        )

        current_date = (
            sorted_dates[index]
        )

        if (
            current_date
            == previous_date
            + timedelta(days=1)
        ):
            running_streak += 1

        else:
            running_streak = 1

        longest_streak = max(
            longest_streak,
            running_streak,
        )

    # 7. Gyul milestone
    if current_streak >= 60:
        stage = "tree"
        next_milestone = None

    elif current_streak >= 30:
        stage = "box"
        next_milestone = 60

    elif current_streak >= 14:
        stage = "two_oranges"
        next_milestone = 30

    elif current_streak >= 7:
        stage = "orange"
        next_milestone = 14

    else:
        stage = "none"
        next_milestone = 7

    return {
        "current_streak":
            current_streak,

        "longest_streak":
            longest_streak,

        "total_recorded_days":
            len(recorded_dates),

        "stage":
            stage,

        "next_milestone":
            next_milestone,
    }

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


    # Analyze journal text after the entry
    # itself has safely been saved.
    try:
        analysis_result = (
            analyze_entry_text(
                entry.content
            )
        )

        analysis = models.EntryAnalysis(
            entry_id=entry.id,

            emotional_intensity=
                analysis_result[
                    "emotional_intensity"
                ],

            length_score=
                analysis_result[
                    "length_score"
                ],

            gyul_intensity=
                analysis_result[
                    "gyul_intensity"
                ],

            mood_label=
                analysis_result[
                    "mood_label"
                ],

            detected_language=
                analysis_result[
                    "detected_language"
                ],

            analysis_source="ai",
        )

        db.add(analysis)
        db.commit()

    except Exception as error:
        db.rollback()

        print(
            "Entry analysis failed:",
            error,
        )


    # Reload with relationships
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
            selectinload(
                models.Entry.analysis
            ),
        )
        .where(
            models.Entry.id == entry.id
        )
    )

    return db.scalar(statement)


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
    current_user: models.User = Depends(
        get_current_user
    ),
):
    # 1. Check Space membership
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


    # 2. Find Entry + existing analysis
    entry = db.scalar(
        select(
            models.Entry
        )
        .options(
            selectinload(
                models.Entry.analysis
            )
        )
        .where(
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


    # 3. Only author can edit
    if (
        entry.author_id
        != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "You can only edit "
                "your own entries"
            ),
        )


    content_changed = False


    # 4. Validate new content
    if entry_data.content is not None:
        new_content = (
            entry_data.content.strip()
        )

        if not new_content:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Entry cannot be empty"
                ),
            )

        if (
            new_content
            != entry.content
        ):
            entry.content = new_content
            content_changed = True


    # 5. Re-analyze only if
    #    the text actually changed
    if content_changed:

        try:
            analysis_result = (
                analyze_entry_text(
                    entry.content
                )
            )

            emotional_intensity = (
                analysis_result[
                    "emotional_intensity"
                ]
            )

            length_score = (
                analysis_result[
                    "length_score"
                ]
            )

            gyul_intensity = (
                analysis_result[
                    "gyul_intensity"
                ]
            )

            mood_label = (
                analysis_result[
                    "mood_label"
                ]
            )

            detected_language = (
                analysis_result[
                    "detected_language"
                ]
            )

            analysis_source = "ai"


        except Exception as error:
            print(
                "Entry re-analysis failed:",
                error,
            )

            # IMPORTANT:
            # Do not keep the old analysis.
            # Use a fresh local fallback
            # based on the NEW text length.
            length_score = (
                1
                - math.exp(
                    -len(entry.content)
                    / 700
                )
            )

            emotional_intensity = 0.0

            gyul_intensity = (
                1
                - (
                    1
                    - 0.60
                    * length_score
                )
                * (
                    1
                    - 0.85
                    * emotional_intensity
                )
            )

            mood_label = "reflective"

            detected_language = None

            analysis_source = (
                "length_fallback"
            )


        # 6. Update old analysis,
        #    or create one if missing
        analysis = entry.analysis

        if analysis is None:
            analysis = (
                models.EntryAnalysis(
                    entry_id=entry.id,

                    emotional_intensity=
                        emotional_intensity,

                    length_score=
                        length_score,

                    gyul_intensity=
                        gyul_intensity,

                    mood_label=
                        mood_label,

                    detected_language=
                        detected_language,

                    analysis_source=
                        analysis_source,
                )
            )

            db.add(analysis)

        else:
            analysis.emotional_intensity = (
                emotional_intensity
            )

            analysis.length_score = (
                length_score
            )

            analysis.gyul_intensity = (
                gyul_intensity
            )

            analysis.mood_label = (
                mood_label
            )

            analysis.detected_language = (
                detected_language
            )

            analysis.analysis_source = (
                analysis_source
            )


    # 7. Save Entry + Analysis together
    db.commit()


    # 8. Reload everything needed
    #    by the frontend
    statement = (
        select(
            models.Entry
        )
        .options(
            selectinload(
                models.Entry.images
            ),

            selectinload(
                models.Entry.tag_links
            ).selectinload(
                models.EntryTag.tag
            ),

            selectinload(
                models.Entry.analysis
            ),
        )
        .where(
            models.Entry.id
            == entry.id
        )
    )

    updated_entry = db.scalar(
        statement
    )


    # 9. Re-create signed image URLs
    #    because frontend replaces
    #    the old Entry with this response
    for image in updated_entry.images:

        if (
            image.storage_provider
            == "supabase"
            and image.storage_key
        ):
            try:
                image.display_url = (
                    create_signed_image_url(
                        image.storage_key
                    )
                )

            except Exception as error:
                print(
                    "Signed URL error:",
                    error,
                )

                image.display_url = None


    return updated_entry

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


    # 4. Remember Supabase image keys
    cloud_storage_keys = []

    for image in entry.images:
        if (
            image.storage_provider == "supabase"
            and image.storage_key
        ):
            cloud_storage_keys.append(
                image.storage_key
            )


    # 5. Delete Entry from DB
    # EntryImage rows are deleted through cascade
    db.delete(entry)
    db.commit()


    # 6. Delete actual files from Supabase Storage
    for storage_key in cloud_storage_keys:
        try:
            delete_image_from_storage(
                storage_key
            )

        except Exception as error:
            print(
                "Supabase cleanup error:",
                storage_key,
                error,
            )


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

    # Validate actual image content
    expected_formats = {
        "image/jpeg": "JPEG",
        "image/png": "PNG",
        "image/webp": "WEBP",
    }

    try:
        with Image.open(BytesIO(contents)) as img:
            actual_format = img.format
            img.verify()

    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Invalid image file",
        )

    if actual_format != expected_formats[content_type]:
        raise HTTPException(
            status_code=400,
            detail="Image content does not match Content-Type",
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

    # File Location in Supabase Storage 
    storage_key = (
        f"spaces/{space_id}/"
        f"entries/{entry_id}/"
        f"{stored_filename}"
    )


    # 8. Upload image to Supabase Storage
    try:
        upload_image(
            storage_key=storage_key,
            data=contents,
            content_type=content_type,
        )

    except Exception as error:
        print(
            "Supabase upload error:",
            error,
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Could not upload image "
                "to cloud storage"
            ),
        )


    # 9. Record cloud file location in DB
    image = models.EntryImage(
        entry_id=entry.id,

        storage_provider="supabase",
        storage_key=storage_key,

        original_filename=file.filename,
        content_type=content_type,
    )


    try:
        db.add(image)
        db.commit()
        db.refresh(image)

    except Exception:
        # If fail saving DB, delete already uploaded cloud image
        try:
            delete_image_from_storage(
                storage_key
            )
        except Exception:
            pass

        raise


    image.display_url = (
        create_signed_image_url(
            storage_key
        )
    )

    return image

@router.delete(
    "/{space_id}/entries/{entry_id}/images/{image_id}",
)
def delete_entry_image(
    space_id: int,
    entry_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    # 1. Check Space membership
    membership = db.scalar(
        select(models.SpaceMember).where(
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


    # 2. Check Entry
    entry = db.scalar(
        select(models.Entry).where(
            models.Entry.id == entry_id,
            models.Entry.space_id
            == space_id,
        )
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Entry not found",
        )


    # 3. Only author can delete image
    if entry.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail=(
                "You can only delete images "
                "from your own entries"
            ),
        )


    # 4. Find the specific image
    image = db.scalar(
        select(models.EntryImage).where(
            models.EntryImage.id
            == image_id,
            models.EntryImage.entry_id
            == entry_id,
        )
    )

    if image is None:
        raise HTTPException(
            status_code=404,
            detail="Image not found",
        )


    # 5. Delete actual file from Supabase Storage
    if (
        image.storage_provider == "supabase"
        and image.storage_key
    ):
        try:
            delete_image_from_storage(
                image.storage_key
            )

        except Exception as error:
            print(
                "Supabase image delete error:",
                error,
            )

            raise HTTPException(
                status_code=502,
                detail=(
                    "Could not delete image "
                    "from cloud storage"
                ),
            )


    # 6. Delete only this EntryImage row
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
    # Only the entry author can request AI tag suggestions
    if entry.author_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only request AI tags for your own entries",
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