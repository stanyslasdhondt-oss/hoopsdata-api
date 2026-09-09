from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.schemas import MatchStatus


class Match(Base):
    __tablename__ = "matches"
    id: Mapped[str] = mapped_column(
        primary_key=True, default=lambda: str(uuid4())
    )  # create unique id
    status: Mapped[str] = mapped_column(default=MatchStatus.pending_upload.value)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    video_key: Mapped[str | None]
    home_team: Mapped[str]
    away_team: Mapped[str]
    game_date: Mapped[date]
    level: Mapped[str]
    uploaded_by: Mapped[str]
