from datetime import datetime
from datetime import date
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    String,
    Integer,
    Text,
    UniqueConstraint,
    func,
)




from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    entries: Mapped[list["Entry"]] = relationship(
        back_populates="author"
    )

    memberships: Mapped[list["SpaceMember"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

class Space(Base):
    __tablename__ = "spaces"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    members: Mapped[list["SpaceMember"]] = relationship(
        back_populates="space",
        cascade="all, delete-orphan",
    )

    entries: Mapped[list["Entry"]] = relationship(
        back_populates="space",
    )

    tags: Mapped[list["Tag"]] = relationship(
        back_populates="space",
        cascade="all, delete-orphan",
    )


class SpaceMember(Base):
    __tablename__ = "space_members"

    id: Mapped[int] = mapped_column(primary_key=True)

    space_id: Mapped[int] = mapped_column(
        ForeignKey("spaces.id"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="member",
        nullable=False,
    )

    space: Mapped["Space"] = relationship(
        back_populates="members",
    )

    user: Mapped["User"] = relationship(
        back_populates="memberships",
    )

class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True)

    content: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    author: Mapped["User"] = relationship(
        back_populates="entries"
    )
    space_id: Mapped[int | None] = mapped_column(
        ForeignKey("spaces.id"),
        nullable=True,
    )

    space: Mapped["Space | None"] = relationship(
        back_populates="entries",
    )

    images: Mapped[list["EntryImage"]] = relationship(
        back_populates="entry",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    tag_links: Mapped[list["EntryTag"]] = relationship(
        back_populates="entry",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    analysis: Mapped[
        "EntryAnalysis | None"
    ] = relationship(
        back_populates="entry",
        cascade="all, delete-orphan",
        uselist=False,
    )
class EntryAnalysis(Base):
    __tablename__ = "entry_analyses"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    entry_id: Mapped[int] = mapped_column(
        ForeignKey(
            "entries.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
    )

    emotional_intensity: Mapped[
        float
    ] = mapped_column(
        Float,
        nullable=False,
    )

    length_score: Mapped[
        float
    ] = mapped_column(
        Float,
        nullable=False,
    )

    gyul_intensity: Mapped[
        float
    ] = mapped_column(
        Float,
        nullable=False,
    )

    mood_label: Mapped[
        str
    ] = mapped_column(
        String(50),
        nullable=False,
    )

    detected_language: Mapped[
        str | None
    ] = mapped_column(
        String(30),
        nullable=True,
    )

    analysis_source: Mapped[
        str
    ] = mapped_column(
        String(50),
        default="ai",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    entry: Mapped["Entry"] = relationship(
        back_populates="analysis"
    )
    segments: Mapped[
        list["EntryAnalysisSegment"]
    ] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="EntryAnalysisSegment.segment_index",
    )


class EntryImage(Base):
    __tablename__ = "entry_images"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    entry_id: Mapped[int] = mapped_column(
        ForeignKey(
            "entries.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )


    storage_provider: Mapped[
        str | None
    ] = mapped_column(
        String(50),
        nullable=True,
    )

    storage_key: Mapped[
        str | None
    ] = mapped_column(
        String(500),
        nullable=True,
    )

    original_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    content_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    entry: Mapped["Entry"] = relationship(
        back_populates="images",
    )

class Tag(Base):
    __tablename__ = "tags"

    __table_args__ = (
        UniqueConstraint(
            "space_id",
            "name",
            name="uq_tag_space_name",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    space_id: Mapped[int] = mapped_column(
        ForeignKey(
            "spaces.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    space: Mapped["Space"] = relationship(
        back_populates="tags",
    )

    entry_links: Mapped[list["EntryTag"]] = relationship(
        back_populates="tag",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class EntryTag(Base):
    __tablename__ = "entry_tags"

    __table_args__ = (
        UniqueConstraint(
            "entry_id",
            "tag_id",
            name="uq_entry_tag",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    entry_id: Mapped[int] = mapped_column(
        ForeignKey(
            "entries.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    tag_id: Mapped[int] = mapped_column(
        ForeignKey(
            "tags.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(20),
        default="manual",
        nullable=False,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    entry: Mapped["Entry"] = relationship(
        back_populates="tag_links",
    )

    tag: Mapped["Tag"] = relationship(
        back_populates="entry_links",
    )

class EntryAnalysisSegment(Base):
    __tablename__ = "entry_analysis_segments"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    analysis_id: Mapped[int] = mapped_column(
        ForeignKey(
            "entry_analyses.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # 문장 순서
    segment_index: Mapped[int] = mapped_column(
        nullable=False,
    )

    # 실제 문장
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # 원문에서 시작/끝 위치
    start_offset: Mapped[int] = mapped_column(
        nullable=False,
    )

    end_offset: Mapped[int] = mapped_column(
        nullable=False,
    )

    # 해당 문장의 감정적 무게
    # 0.0 = 매우 가벼움
    # 1.0 = 매우 무겁거나 힘든 뉘앙스
    intensity: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    # 예: neutral / sad / stressed / tired
    tone: Mapped[str] = mapped_column(
        String(50),
        default="neutral",
        nullable=False,
    )

    analysis: Mapped["EntryAnalysis"] = relationship(
        back_populates="segments"
    )

class SleepSession(Base):
    __tablename__ = "sleep_sessions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # 잠들기 시작한 시간
    start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # 깬 시간
    end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # main_sleep / nap
    session_type: Mapped[str] = mapped_column(
        String(30),
        default="main_sleep",
        nullable=False,
    )

    # manual / healthkit
    source: Mapped[str] = mapped_column(
        String(30),
        default="manual",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class DailyCheckIn(Base):
    __tablename__ = "daily_check_ins"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "checkin_date",
            name="uq_daily_checkin_user_date",
        ),

        CheckConstraint(
            "energy BETWEEN 1 AND 5",
            name="ck_daily_checkin_energy",
        ),

        CheckConstraint(
            "focus BETWEEN 1 AND 5",
            name="ck_daily_checkin_focus",
        ),

        CheckConstraint(
            "mood BETWEEN 1 AND 5",
            name="ck_daily_checkin_mood",
        ),

        CheckConstraint(
            "stress BETWEEN 1 AND 5",
            name="ck_daily_checkin_stress",
        ),

        CheckConstraint(
            "overall_condition BETWEEN 1 AND 5",
            name="ck_daily_checkin_condition",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    checkin_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    energy: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    focus: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    mood: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # 여기서는 1 = stress 낮음, 5 = stress 높음
    stress: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # ML에서 중요한 target
    overall_condition: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )