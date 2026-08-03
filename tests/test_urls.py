def test_create_url(client):
    response = client.post("/urls", json={
        "original_url": "https://github.com/JJrendon29",
        "expires_in_hours": 1
    })
    assert response.status_code == 201
    data = response.json()
    assert "code" in data
    assert "short_url" in data
    assert data["clicks"] == 0


def test_redirect_url(client):
    create = client.post("/urls", json={
        "original_url": "https://github.com/JJrendon29",
        "expires_in_hours": 1
    })
    code = create.json()["code"]

    response = client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://github.com/JJrendon29"


def test_url_stats(client):
    create = client.post("/urls", json={
        "original_url": "https://github.com/JJrendon29",
        "expires_in_hours": 1
    })
    code = create.json()["code"]

    client.get(f"/{code}", follow_redirects=False)

    stats = client.get(f"/urls/{code}/stats")
    assert stats.status_code == 200
    assert stats.json()["clicks"] == 1


def test_url_not_found(client):
    response = client.get("/codigoinexistente", follow_redirects=False)
    assert response.status_code == 404
