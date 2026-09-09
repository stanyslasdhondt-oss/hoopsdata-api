from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Match
from app.rules import can_transition
from app.schemas import Level, MatchCreate, MatchOut, MatchStatus, MatchUpdate

# router for matches request
router = APIRouter(prefix="/matches", tags=["matches"])


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
    match = db.query(Match).filter(Match.id == match_id).first()
    if match is None:
        raise HTTPException(404, f"Match {match_id} not found")
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
    match = db.query(Match).filter(Match.id == match_id).first()
    if match is None:
        raise HTTPException(404, f"Match {match_id} not found")

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
    match = db.query(Match).filter(Match.id == match_id).first()
    if match is None:
        raise HTTPException(404, f"Match {match_id} not found")
    db.delete(match)
    db.commit()
