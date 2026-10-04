"""Phase 1: applications, rebuilt with validation and filtering.

Each test's name says what it checks. Make them pass one group at a
time, top to bottom. Every request is awaited: `client` is an httpx
AsyncClient (see conftest.py).
"""

SAMPLE = {
    "company": "Acme",
    "role": "Junior Developer",
    "applied_on": "2026-10-01",
}


async def create_sample(client, **overrides):
    payload = {**SAMPLE, **overrides}
    response = await client.post("/applications", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


# --- Create -------------------------------------------------------------


async def test_create_returns_201_and_the_row(client):
    response = await client.post("/applications", json=SAMPLE)

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "company": "Acme",
        "role": "Junior Developer",
        "status": "applied",
        "applied_on": "2026-10-01",
    }


async def test_create_strips_surrounding_whitespace(client):
    created = await create_sample(client, company="  Acme  ", role=" Analyst ")

    assert created["company"] == "Acme"
    assert created["role"] == "Analyst"


async def test_create_rejects_a_blank_company(client):
    response = await client.post(
        "/applications",
        json={**SAMPLE, "company": "   "},
    )

    assert response.status_code == 422


async def test_create_rejects_a_blank_role(client):
    response = await client.post(
        "/applications",
        json={**SAMPLE, "role": ""},
    )

    assert response.status_code == 422


async def test_create_rejects_an_unknown_status(client):
    response = await client.post(
        "/applications",
        json={**SAMPLE, "status": "ghosted"},
    )

    assert response.status_code == 422


async def test_create_accepts_every_known_status(client):
    for status in ["applied", "interviewing", "offer", "rejected"]:
        created = await create_sample(client, status=status)
        assert created["status"] == status


# --- List ---------------------------------------------------------------


async def test_list_starts_empty(client):
    response = await client.get("/applications")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_returns_every_application_in_id_order(client):
    await create_sample(client, company="Acme")
    await create_sample(client, company="Globex")

    response = await client.get("/applications")

    companies = [item["company"] for item in response.json()]
    assert companies == ["Acme", "Globex"]


async def test_list_can_filter_by_status(client):
    await create_sample(client, company="Acme", status="applied")
    await create_sample(client, company="Globex", status="interviewing")

    response = await client.get(
        "/applications",
        params={"status": "interviewing"},
    )

    companies = [item["company"] for item in response.json()]
    assert companies == ["Globex"]


async def test_list_rejects_an_unknown_status_filter(client):
    response = await client.get(
        "/applications",
        params={"status": "ghosted"},
    )

    assert response.status_code == 422


# --- Get one ------------------------------------------------------------


async def test_get_application_by_id(client):
    created = await create_sample(client)

    response = await client.get(f"/applications/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


async def test_get_missing_application_returns_404(client):
    response = await client.get("/applications/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Application not found"}


# --- Update -------------------------------------------------------------


async def test_update_changes_only_the_fields_sent(client):
    created = await create_sample(client)

    response = await client.patch(
        f"/applications/{created['id']}",
        json={"status": "interviewing"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "interviewing"
    assert body["company"] == "Acme"


async def test_update_rejects_an_unknown_status(client):
    created = await create_sample(client)

    response = await client.patch(
        f"/applications/{created['id']}",
        json={"status": "ghosted"},
    )

    assert response.status_code == 422


async def test_update_missing_application_returns_404(client):
    response = await client.patch(
        "/applications/999",
        json={"status": "offer"},
    )

    assert response.status_code == 404


# --- Delete -------------------------------------------------------------


async def test_delete_removes_the_application(client):
    created = await create_sample(client)

    response = await client.delete(f"/applications/{created['id']}")

    assert response.status_code == 204
    follow_up = await client.get(f"/applications/{created['id']}")
    assert follow_up.status_code == 404


async def test_delete_missing_application_returns_404(client):
    response = await client.delete("/applications/999")

    assert response.status_code == 404
