from datetime import datetime
from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    String,
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