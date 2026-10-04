"""Phase 2: companies are their own resource."""


async def create_company(client, name):
    response = await client.post("/companies", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_company_returns_201_and_the_row(client):
    response = await client.post("/companies", json={"name": "Acme"})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Acme"}


async def test_create_company_strips_surrounding_whitespace(client):
    created = await create_company(client, "  Acme  ")

    assert created["name"] == "Acme"


async def test_create_company_rejects_a_blank_name(client):
    response = await client.post("/companies", json={"name": "   "})

    assert response.status_code == 422


async def test_create_duplicate_company_returns_409(client):
    await create_company(client, "Acme")

    response = await client.post("/companies", json={"name": "Acme"})

    assert response.status_code == 409
    assert response.json() == {"detail": "Company already exists"}


async def test_list_companies_starts_empty(client):
    response = await client.get("/companies")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_companies_is_sorted_by_name(client):
    await create_company(client, "Globex")
    await create_company(client, "Acme")

    response = await client.get("/companies")

    names = [company["name"] for company in response.json()]
    assert names == ["Acme", "Globex"]
