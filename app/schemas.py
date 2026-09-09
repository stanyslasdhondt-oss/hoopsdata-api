from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class Level(str, Enum):
    freshman = "freshman"
    jv = "jv"
    varsity = "varsity"


class MatchStatus(str, Enum):
    pending_upload = "pending_upload"
    uploaded = "uploaded"
    processing = "processing"
    done = "done"
    failed = "failed"


# the create model
class MatchCreate(BaseModel):
    home_team: str = Field(min_length=1, max_length=80)
    away_team: str = Field(min_length=1, max_length=80)
    game_date: date
    level: Level
    uploaded_by: str = Field(min_length=1)

    @model_validator(mode="after")
    def teams_must_be_different(self):
        if self.home_team == self.away_team:
            raise ValueError("home_team and away_team must be different")

        return self


# the output model
class MatchOut(MatchCreate):
    model_config = {"from_attributes": True}
    id: str
    status: MatchStatus
    created_at: datetime
    video_key: str | None = None


# the make change model
class MatchUpdate(BaseModel):
    status: MatchStatus | None = None
    video_key: str | None = None
