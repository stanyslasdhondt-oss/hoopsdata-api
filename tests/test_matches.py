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
