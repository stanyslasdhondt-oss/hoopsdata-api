def make_payload(**overrides):
    payload = {
        "home_team": "Lakers",
        "away_team": "Celtics",
        "game_date": "2026-09-08",
        "level": "varsity",
        "uploaded_by": "stan",
    }
    payload.update(overrides)
    return payload


def test_valid_match_return_201(client):
    """check Creat a match valide → 201, status == "pending_upload", id non vide"""
    response = client.post("/matches", json=make_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending_upload"
    assert data["id"]


def test_create_match_invalid_level_returns_422(client):
    """create a game with invalid if --> error 422"""
    response = client.post("/matches", json=make_payload(level="NBA"))
    assert response.status_code == 422


def test_get_match_unknown_id(client):
    """test get match on unknown id --> 404"""
    response = client.get("/matches/does-not-exist")
    assert response.status_code == 404


def test_transition(client):
    """pending_upload → uploaded → 200, then uploaded → done → 409"""
    created = client.post("/matches", json=make_payload())  # create a valid id
    match_id = created.json()["id"]
    assert created.status_code == 201

    response = client.patch(f"/matches/{match_id}", json={"status": "uploaded"})
    assert response.status_code == 200
    assert response.json()["status"] == "uploaded"
    response = client.patch(f"/matches/{match_id}", json={"status": "done"})
    assert "uploaded" in response.json()["detail"]
    assert response.status_code == 409


def test_create_3_match_limit_2(client):
    """create 3 game then return matchs wiht limit=2"""
    for _ in range(3):
        match = client.post("/matches", json=make_payload())
        assert match.status_code == 201

    response = client.get("/matches?limit=2")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 2


def test_delete_then_get(client):
    """check if delete works accordingly"""
    created = client.post("/matches", json=make_payload())  # create a valid id
    match_id = created.json()["id"]

    get = client.get(f"/matches/{match_id}")
    assert get.status_code == 200
    response = client.delete(f"/matches/{match_id}")
    assert response.status_code == 204
    get = client.get(f"/matches/{match_id}")
    assert get.status_code == 404


def test_upload_url_returns_url_and_key(client):
    """POST /upload-url on a pending_upload match → 200 with both fields"""
    match_id = client.post("/matches", json=make_payload()).json()["id"]

    response = client.post(f"/matches/{match_id}/upload-url")
    assert response.status_code == 200
    data = response.json()
    assert data["video_key"] == f"matches/{match_id}/raw.mp4"
    assert data["video_key"] in data["upload_url"]


def test_upload_url_unknown_match_returns_404(client):
    response = client.post("/matches/does-not-exist/upload-url")
    assert response.status_code == 404


def test_upload_url_twice_returns_409(client):
    """Once completed, a match must not get a second upload URL"""
    match_id = client.post("/matches", json=make_payload()).json()["id"]
    client.post(f"/matches/{match_id}/complete")

    response = client.post(f"/matches/{match_id}/upload-url")
    assert response.status_code == 409


def test_complete_sets_status_and_key(client):
    """POST /complete → uploaded, video_key stored"""
    match_id = client.post("/matches", json=make_payload()).json()["id"]

    response = client.post(f"/matches/{match_id}/complete")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "uploaded"
    assert data["video_key"] == f"matches/{match_id}/raw.mp4"

    # the change must be persisted, not just returned
    persisted = client.get(f"/matches/{match_id}").json()
    assert persisted["status"] == "uploaded"


def test_complete_twice_returns_409(client):
    match_id = client.post("/matches", json=make_payload()).json()["id"]
    client.post(f"/matches/{match_id}/complete")

    response = client.post(f"/matches/{match_id}/complete")
    assert response.status_code == 409


def test_preview_url_after_complete(client):
    match_id = client.post("/matches", json=make_payload()).json()["id"]
    client.post(f"/matches/{match_id}/complete")

    response = client.get(f"/matches/{match_id}/preview-url")
    assert response.status_code == 200
    assert f"matches/{match_id}/raw.mp4" in response.json()["preview_url"]


def test_preview_url_without_video_returns_409(client):
    """A match that never completed its upload has no video to preview"""
    match_id = client.post("/matches", json=make_payload()).json()["id"]

    response = client.get(f"/matches/{match_id}/preview-url")
    assert response.status_code == 409
