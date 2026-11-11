from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

class EntryCreate(BaseModel):
    content: str


class EntryUpdate(BaseModel):
    content: str | None = None

class EntryAuthor(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(
        from_attributes=True
    )


class EntryImageResponse(BaseModel):
    id: int
    entry_id: int

    storage_provider: str | None
    storage_key: str | None

    display_url: str | None = None

    original_filename: str | None
    content_type: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class TagCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=50,
    )


class TagResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class EntryTagResponse(BaseModel):
    id: int
    source: str
    confidence: float | None
    tag: TagResponse

    model_config = ConfigDict(
        from_attributes=True
    )

class EntryAnalysisResponse(BaseModel):
    id: int
    entry_id: int
    emotional_intensity: float
    length_score: float
    gyul_intensity: float
    mood_label: str
    detected_language: str | None
    analysis_source: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class EntryResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: EntryAuthor
    space_id: int | None

    images: list[EntryImageResponse] = Field(
        default_factory=list
    )

    tag_links: list[EntryTagResponse] = Field(
        default_factory=list
    )
    analysis: EntryAnalysisResponse | None = None
    model_config = ConfigDict(
        from_attributes=True
    )



class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
    )

    email: str = Field(
        min_length=5,
        max_length=320,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str

class SpaceCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )


class SpaceResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SpaceMemberAdd(BaseModel):
    username: str

class SpaceUpdate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

class AITagSuggestionsResponse(
    BaseModel
):
    tags: list[str]

class AITagAccept(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=50,
    )

class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    total_recorded_days: int
    stage: str
    next_milestone: int | None

class SleepSessionCreate(BaseModel):
    start_at: datetime
    end_at: datetime

    session_type: str = "main_sleep"
    source: str = "manual"


class SleepSessionResponse(BaseModel):
    id: int
    user_id: int

    start_at: datetime
    end_at: datetime

    session_type: str
    source: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class DailyCheckInCreate(BaseModel):
    energy: int = Field(
        ge=1,
        le=5,
    )

    focus: int = Field(
        ge=1,
        le=5,
    )

    mood: int = Field(
        ge=1,
        le=5,
    )

    stress: int = Field(
        ge=1,
        le=5,
    )

    overall_condition: int = Field(
        ge=1,
        le=5,
    )

    note: str | None = None


class DailyCheckInResponse(BaseModel):
    id: int
    user_id: int
    checkin_date: date

    energy: int
    focus: int
    mood: int
    stress: int
    overall_condition: int

    note: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
