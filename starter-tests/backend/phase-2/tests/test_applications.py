"""Phase 2: applications belong to a company.

The request sends `company_id`. The response includes the whole
company as a nested object: {"id": 1, "name": "Acme"}.
"""


def create_company(client, name="Acme"):
    response = client.post("/companies", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


def create_application(client, company_id, **overrides):
    payload = {
        "company_id": company_id,
        "role": "Junior Developer",
        "applied_on": "2026-10-01",
        **overrides,
    }
    response = client.post("/applications", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


# --- Create -------------------------------------------------------------


def test_create_returns_201_with_the_company_nested(client):
    acme = create_company(client, "Acme")

    response = client.post(
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


def test_create_with_an_unknown_company_returns_422(client):
    response = client.post(
        "/applications",
        json={
            "company_id": 999,
            "role": "Junior Developer",
            "applied_on": "2026-10-01",
        },
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Company not found"}


def test_create_rejects_a_blank_role(client):
    acme = create_company(client)

    response = client.post(
        "/applications",
        json={
            "company_id": acme["id"],
            "role": "  ",
            "applied_on": "2026-10-01",
        },
    )

    assert response.status_code == 422


def test_create_rejects_an_unknown_status(client):
    acme = create_company(client)

    response = client.post(
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


def test_list_starts_empty(client):
    response = client.get("/applications")

    assert response.status_code == 200
    assert response.json() == []


def test_list_returns_every_application_in_id_order(client):
    acme = create_company(client)
    create_application(client, acme["id"], role="Junior Developer")
    create_application(client, acme["id"], role="QA Analyst")

    response = client.get("/applications")

    roles = [item["role"] for item in response.json()]
    assert roles == ["Junior Developer", "QA Analyst"]


def test_list_can_filter_by_status(client):
    acme = create_company(client)
    create_application(client, acme["id"], role="Developer")
    create_application(
        client,
        acme["id"],
        role="Analyst",
        status="offer",
    )

    response = client.get("/applications", params={"status": "offer"})

    roles = [item["role"] for item in response.json()]
    assert roles == ["Analyst"]


def test_list_can_filter_by_company(client):
    acme = create_company(client, "Acme")
    globex = create_company(client, "Globex")
    create_application(client, acme["id"], role="Developer")
    create_application(client, globex["id"], role="Analyst")

    response = client.get(
        "/applications",
        params={"company_id": globex["id"]},
    )

    roles = [item["role"] for item in response.json()]
    assert roles == ["Analyst"]


def test_list_can_filter_by_status_and_company_together(client):
    acme = create_company(client, "Acme")
    globex = create_company(client, "Globex")
    create_application(client, acme["id"], role="A", status="offer")
    create_application(client, globex["id"], role="B", status="offer")
    create_application(client, globex["id"], role="C")

    response = client.get(
        "/applications",
        params={"status": "offer", "company_id": globex["id"]},
    )

    roles = [item["role"] for item in response.json()]
    assert roles == ["B"]


# --- Get one ------------------------------------------------------------


def test_get_application_by_id(client):
    acme = create_company(client)
    created = create_application(client, acme["id"])

    response = client.get(f"/applications/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_missing_application_returns_404(client):
    response = client.get("/applications/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Application not found"}


# --- Update -------------------------------------------------------------


def test_update_changes_only_the_fields_sent(client):
    acme = create_company(client)
    created = create_application(client, acme["id"])

    response = client.patch(
        f"/applications/{created['id']}",
        json={"status": "interviewing"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "interviewing"
    assert body["role"] == "Junior Developer"
    assert body["company"]["name"] == "Acme"


def test_update_can_move_to_another_company(client):
    acme = create_company(client, "Acme")
    globex = create_company(client, "Globex")
    created = create_application(client, acme["id"])

    response = client.patch(
        f"/applications/{created['id']}",
        json={"company_id": globex["id"]},
    )

    assert response.status_code == 200
    assert response.json()["company"]["name"] == "Globex"


def test_update_to_an_unknown_company_returns_422(client):
    acme = create_company(client)
    created = create_application(client, acme["id"])

    response = client.patch(
        f"/applications/{created['id']}",
        json={"company_id": 999},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Company not found"}


def test_update_missing_application_returns_404(client):
    response = client.patch(
        "/applications/999",
        json={"status": "offer"},
    )

    assert response.status_code == 404


# --- Delete -------------------------------------------------------------


def test_delete_removes_the_application(client):
    acme = create_company(client)
    created = create_application(client, acme["id"])

    response = client.delete(f"/applications/{created['id']}")

    assert response.status_code == 204
    follow_up = client.get(f"/applications/{created['id']}")
    assert follow_up.status_code == 404


def test_delete_missing_application_returns_404(client):
    response = client.delete("/applications/999")

    assert response.status_code == 404
