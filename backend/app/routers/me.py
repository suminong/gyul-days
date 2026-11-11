from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.security import get_current_user

from app.schemas import (
    DailyCheckInCreate,
    DailyCheckInResponse,
    SleepSessionCreate,
    SleepSessionResponse,
)


router = APIRouter(
    prefix="/me",
    tags=["me"],
)


# -------------------------
# Sleep
# -------------------------

@router.post(
    "/sleep",
    response_model=SleepSessionResponse,
    status_code=201,
)
def create_sleep_session(
    sleep_data: SleepSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    # 시간대 정보 없는 datetime은
    # 나중에 HealthKit과 합칠 때 문제가 됨
    if (
        sleep_data.start_at.tzinfo is None
        or sleep_data.start_at.utcoffset()
        is None
        or sleep_data.end_at.tzinfo is None
        or sleep_data.end_at.utcoffset()
        is None
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "start_at and end_at "
                "must include a timezone"
            ),
        )

    if (
        sleep_data.end_at
        <= sleep_data.start_at
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "end_at must be later "
                "than start_at"
            ),
        )

    if sleep_data.session_type not in {
        "main_sleep",
        "nap",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "session_type must be "
                "main_sleep or nap"
            ),
        )

    if sleep_data.source not in {
        "manual",
        "healthkit",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "source must be "
                "manual or healthkit"
            ),
        )

    sleep_session = models.SleepSession(
        user_id=current_user.id,

        start_at=
            sleep_data.start_at,

        end_at=
            sleep_data.end_at,

        session_type=
            sleep_data.session_type,

        source=
            "manual",
    )

    db.add(
        sleep_session
    )

    db.commit()

    db.refresh(
        sleep_session
    )

    return sleep_session


@router.get(
    "/sleep",
    response_model=
        list[SleepSessionResponse],
)
def get_sleep_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    statement = (
        select(
            models.SleepSession
        )
        .where(
            models.SleepSession.user_id
            == current_user.id
        )
        .order_by(
            models.SleepSession
            .start_at
            .desc()
        )
    )

    return db.scalars(
        statement
    ).all()


# -------------------------
# Daily check-in
# -------------------------

@router.put(
    "/check-in/{checkin_date}",
    response_model=
        DailyCheckInResponse,
)
def save_daily_check_in(
    checkin_date: date,
    checkin_data: DailyCheckInCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    existing = db.scalar(
        select(
            models.DailyCheckIn
        ).where(
            models.DailyCheckIn.user_id
            == current_user.id,

            models.DailyCheckIn.checkin_date
            == checkin_date,
        )
    )

    # 오늘 기록이 처음이면 새 row
    if existing is None:
        check_in = (
            models.DailyCheckIn(
                user_id=
                    current_user.id,

                checkin_date=
                    checkin_date,

                energy=
                    checkin_data.energy,

                focus=
                    checkin_data.focus,

                mood=
                    checkin_data.mood,

                stress=
                    checkin_data.stress,

                overall_condition=
                    checkin_data
                    .overall_condition,

                note=
                    checkin_data.note,
            )
        )

        db.add(
            check_in
        )

    # 이미 기록했으면 update
    else:
        check_in = existing

        check_in.energy = (
            checkin_data.energy
        )

        check_in.focus = (
            checkin_data.focus
        )

        check_in.mood = (
            checkin_data.mood
        )

        check_in.stress = (
            checkin_data.stress
        )

        check_in.overall_condition = (
            checkin_data
            .overall_condition
        )

        check_in.note = (
            checkin_data.note
        )

    db.commit()

    db.refresh(
        check_in
    )

    return check_in


@router.get(
    "/check-in/{checkin_date}",
    response_model=
        DailyCheckInResponse,
)
def get_daily_check_in(
    checkin_date: date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    check_in = db.scalar(
        select(
            models.DailyCheckIn
        ).where(
            models.DailyCheckIn.user_id
            == current_user.id,

            models.DailyCheckIn.checkin_date
            == checkin_date,
        )
    )

    if check_in is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No check-in for this date"
            ),
        )

    return check_in
@router.put(
    "/sleep/{sleep_id}",
    response_model=SleepSessionResponse,
)
def update_sleep_session(
    sleep_id: int,
    sleep_data: SleepSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        get_current_user
    ),
):
    sleep_session = db.scalar(
        select(
            models.SleepSession
        ).where(
            models.SleepSession.id
            == sleep_id,

            models.SleepSession.user_id
            == current_user.id,
        )
    )

    if sleep_session is None:
        raise HTTPException(
            status_code=404,
            detail="Sleep session not found",
        )

    if (
        sleep_data.start_at.tzinfo
        is None
        or sleep_data.start_at.utcoffset()
        is None
        or sleep_data.end_at.tzinfo
        is None
        or sleep_data.end_at.utcoffset()
        is None
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "start_at and end_at "
                "must include a timezone"
            ),
        )

    if (
        sleep_data.end_at
        <= sleep_data.start_at
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "end_at must be later "
                "than start_at"
            ),
        )

    if sleep_data.session_type not in {
        "main_sleep",
        "nap",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "session_type must be "
                "main_sleep or nap"
            ),
        )

    # manual UI에서 수정한 데이터는
    # provenance도 manual로 유지
    sleep_session.start_at = (
        sleep_data.start_at
    )

    sleep_session.end_at = (
        sleep_data.end_at
    )

    sleep_session.session_type = (
        sleep_data.session_type
    )

    sleep_session.source = "manual"

    db.commit()

    db.refresh(
        sleep_session
    )

    return sleep_session