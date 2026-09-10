from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Match
from app.rules import can_transition
from app.schemas import (
    Level,
    MatchCreate,
    MatchOut,
    MatchStatus,
    MatchUpdate,
    PreviewUrlOut,
    UploadurlOut,
)
from app.storage import FakeStorage, get_storage, video_key_for

# router for matches request
router = APIRouter(prefix="/matches", tags=["matches"])


def get_match_or_404(db: Session, match_id: str) -> Match:
    """Return the match or raise a 404."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if match is None:
        raise HTTPException(404, f"Match {match_id} not found")
    return match


@router.get("", response_model=list[MatchOut])
def get_matches(
    status: MatchStatus | None = None,
    level: Level | None = None,
    uploaded_by: str | None = None,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = db.query(Match)
    if status:
        query = query.filter(Match.status == status)
    if level:
        query = query.filter(Match.level == level)
    if uploaded_by:
        query = query.filter(Match.uploaded_by == uploaded_by)

    return query.order_by(Match.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/{match_id}", response_model=MatchOut)
def get_match(match_id: str, db: Session = Depends(get_db)):
    match = get_match_or_404(db, match_id)
    return match


@router.post("", response_model=MatchOut, status_code=201)
def create_match(match: MatchCreate, db: Session = Depends(get_db)):
    new_match = Match(**match.model_dump())
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return new_match


@router.patch("/{match_id}", response_model=MatchOut)
def update_match(match_id: str, payload: MatchUpdate, db: Session = Depends(get_db)):

    # find the specific game first
    match = get_match_or_404(db, match_id)

    data = payload.model_dump(exclude_unset=True)

    new_status = data.pop("status", None)
    if new_status is not None:
        if not can_transition(MatchStatus(match.status), new_status):
            raise HTTPException(
                409, f"Cannot go from {match.status} to {new_status.value}"
            )
        match.status = new_status.value

    # finish by updating the non pop element
    for key, value in data.items():
        setattr(match, key, value)

    db.commit()
    db.refresh(match)

    return match


@router.delete("/{match_id}", status_code=204)
def delete_match(match_id: str, db: Session = Depends(get_db)):
    match = get_match_or_404(db, match_id)
    db.delete(match)
    db.commit()


@router.post("/{match_id}/upload-url", response_model=UploadurlOut)
def upload_url_video_key(
    match_id: str,
    db: Session = Depends(get_db),
    storage: FakeStorage = Depends(get_storage),
):
    """Return a presigned upload URL for a match still waiting for its video."""
    match = get_match_or_404(db, match_id)

    if match.status != MatchStatus.pending_upload.value:
        raise HTTPException(
            409,
            f"Match is in status {match.status}, expected pending_upload",
        )
    key = video_key_for(match_id)
    upload_url = storage.presigned_put(key)
    return {"upload_url": upload_url, "video_key": key}


@router.post("/{match_id}/complete", response_model=MatchOut)
def complete_upload(match_id: str, db: Session = Depends(get_db)):
    """Mark the upload as finished: set the video key and move to `uploaded`."""
    match = get_match_or_404(db, match_id)
    if not can_transition(MatchStatus(match.status), MatchStatus.uploaded):
        raise HTTPException(
            409,
            f"Match is in status {match.status}, expected pending_upload",
        )
    key = video_key_for(match_id)
    # updates values
    match.status = MatchStatus.uploaded.value
    match.video_key = key

    # update db
    db.commit()
    db.refresh(match)

    return match


@router.get("/{match_id}/preview-url", response_model=PreviewUrlOut)
def preview_url(
    match_id: str,
    db: Session = Depends(get_db),
    storage: FakeStorage = Depends(get_storage),
):
    """return a preview url for an already uploaded game"""
    match = get_match_or_404(db, match_id)
    if not match.video_key:
        raise HTTPException(409, f"match {match_id} does not have a video key")
    key = match.video_key
    preview = storage.presigned_get(key)
    return {"preview_url": preview}
