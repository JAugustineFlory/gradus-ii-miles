"""Phase 2: applications belong to a company.

The request sends `company_id`. The response includes the whole
company as a nested object: {"id": 1, "name": "Acme"}.
"""


async def create_company(client, name="Acme"):
    response = await client.post("/companies", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


async def create_application(client, company_id, **overrides):
    payload = {
        "company_id": company_id,
        "role": "Junior Developer",
        "applied_on": "2026-10-01",
        **overrides,
    }
    response = await client.post("/applications", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


# --- Create -------------------------------------------------------------


async def test_create_returns_201_with_the_company_nested(client):
    acme = await create_company(client, "Acme")

    response = await client.post(
        "/applications",
        json={
            "company_id": acme["id"],
            "role": "Junior Developer",
            "applied_on": "2026-10-01",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "role": "Junior Developer",
        "status": "applied",
        "applied_on": "2026-10-01",
        "company": {"id": acme["id"], "name": "Acme"},
    }


async def test_create_with_an_unknown_company_returns_422(client):
    response = await client.post(
        "/applications",
        json={
            "company_id": 999,
            "role": "Junior Developer",
            "applied_on": "2026-10-01",
        },
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Company not found"}


async def test_create_rejects_a_blank_role(client):
    acme = await create_company(client)

    response = await client.post(
        "/applications",
        json={
            "company_id": acme["id"],
            "role": "  ",
            "applied_on": "2026-10-01",
        },
    )

    assert response.status_code == 422


async def test_create_rejects_an_unknown_status(client):
    acme = await create_company(client)

    response = await client.post(
        "/applications",
        json={
            "company_id": acme["id"],
            "role": "Junior Developer",
            "status": "ghosted",
            "applied_on": "2026-10-01",
        },
    )

    assert response.status_code == 422


# --- List ---------------------------------------------------------------


async def test_list_starts_empty(client):
    response = await client.get("/applications")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_returns_every_application_in_id_order(client):
    acme = await create_company(client)
    await create_application(client, acme["id"], role="Junior Developer")
    await create_application(client, acme["id"], role="QA Analyst")

    response = await client.get("/applications")

    roles = [item["role"] for item in response.json()]
    assert roles == ["Junior Developer", "QA Analyst"]


async def test_list_can_filter_by_status(client):
    acme = await create_company(client)
    await create_application(client, acme["id"], role="Developer")
    await create_application(
        client,
        acme["id"],
        role="Analyst",
        status="offer",
    )

    response = await client.get(
        "/applications",
        params={"status": "offer"},
    )

    roles = [item["role"] for item in response.json()]
    assert roles == ["Analyst"]


async def test_list_can_filter_by_company(client):
    acme = await create_company(client, "Acme")
    globex = await create_company(client, "Globex")
    await create_application(client, acme["id"], role="Developer")
    await create_application(client, globex["id"], role="Analyst")

    response = await client.get(
        "/applications",
        params={"company_id": globex["id"]},
    )

    roles = [item["role"] for item in response.json()]
    assert roles == ["Analyst"]


async def test_list_can_filter_by_status_and_company_together(client):
    acme = await create_company(client, "Acme")
    globex = await create_company(client, "Globex")
    await create_application(client, acme["id"], role="A", status="offer")
    await create_application(client, globex["id"], role="B", status="offer")
    await create_application(client, globex["id"], role="C")

    response = await client.get(
        "/applications",
        params={"status": "offer", "company_id": globex["id"]},
    )

    roles = [item["role"] for item in response.json()]
    assert roles == ["B"]


# --- Get one ------------------------------------------------------------


async def test_get_application_by_id(client):
    acme = await create_company(client)
    created = await create_application(client, acme["id"])

    response = await client.get(f"/applications/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


async def test_get_missing_application_returns_404(client):
    response = await client.get("/applications/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Application not found"}


# --- Update -------------------------------------------------------------


async def test_update_changes_only_the_fields_sent(client):
    acme = await create_company(client)
    created = await create_application(client, acme["id"])

    response = await client.patch(
        f"/applications/{created['id']}",
        json={"status": "interviewing"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "interviewing"
    assert body["role"] == "Junior Developer"
    assert body["company"]["name"] == "Acme"


async def test_update_can_move_to_another_company(client):
    acme = await create_company(client, "Acme")
    globex = await create_company(client, "Globex")
    created = await create_application(client, acme["id"])

    response = await client.patch(
        f"/applications/{created['id']}",
        json={"company_id": globex["id"]},
    )

    assert response.status_code == 200
    assert response.json()["company"]["name"] == "Globex"


async def test_update_to_an_unknown_company_returns_422(client):
    acme = await create_company(client)
    created = await create_application(client, acme["id"])

    response = await client.patch(
        f"/applications/{created['id']}",
        json={"company_id": 999},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Company not found"}


async def test_update_missing_application_returns_404(client):
    response = await client.patch(
        "/applications/999",
        json={"status": "offer"},
    )

    assert response.status_code == 404


# --- Delete -------------------------------------------------------------


async def test_delete_removes_the_application(client):
    acme = await create_company(client)
    created = await create_application(client, acme["id"])

    response = await client.delete(f"/applications/{created['id']}")

    assert response.status_code == 204
    follow_up = await client.get(f"/applications/{created['id']}")
    assert follow_up.status_code == 404


async def test_delete_missing_application_returns_404(client):
    response = await client.delete("/applications/999")

    assert response.status_code == 404
