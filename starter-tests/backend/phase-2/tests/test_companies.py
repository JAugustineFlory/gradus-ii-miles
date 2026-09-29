"""Phase 2: companies are their own resource."""


def create_company(client, name):
    response = client.post("/companies", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


def test_create_company_returns_201_and_the_row(client):
    response = client.post("/companies", json={"name": "Acme"})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Acme"}


def test_create_company_strips_surrounding_whitespace(client):
    created = create_company(client, "  Acme  ")

    assert created["name"] == "Acme"


def test_create_company_rejects_a_blank_name(client):
    response = client.post("/companies", json={"name": "   "})

    assert response.status_code == 422


def test_create_duplicate_company_returns_409(client):
    create_company(client, "Acme")

    response = client.post("/companies", json={"name": "Acme"})

    assert response.status_code == 409
    assert response.json() == {"detail": "Company already exists"}


def test_list_companies_starts_empty(client):
    response = client.get("/companies")

    assert response.status_code == 200
    assert response.json() == []


def test_list_companies_is_sorted_by_name(client):
    create_company(client, "Globex")
    create_company(client, "Acme")

    response = client.get("/companies")

    names = [company["name"] for company in response.json()]
    assert names == ["Acme", "Globex"]
