from app.schemas import MatchStatus

# set rules for changing value in a match for parameter status
ALLOWED_TRANSITIONS: dict[MatchStatus, set[MatchStatus]] = {
    MatchStatus.pending_upload: {MatchStatus.uploaded, MatchStatus.failed},
    MatchStatus.uploaded: {MatchStatus.processing, MatchStatus.failed},
    MatchStatus.processing: {MatchStatus.done, MatchStatus.failed},
    MatchStatus.done: set(),
    MatchStatus.failed: {MatchStatus.pending_upload, MatchStatus.processing},
    # `failed` covers two cases: a failed upload (from pending_upload/uploaded)
    # or a failed processing run (from processing). Retry goes back to
    # pending_upload in the first case, to processing in the second.
    # The client is responsible for choosing the right one.
}


# fonction to verified if it is an allowed transtion
def can_transition(current: MatchStatus, target: MatchStatus) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())
