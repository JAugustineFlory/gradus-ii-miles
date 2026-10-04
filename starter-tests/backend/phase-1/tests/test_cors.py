FRONTEND = "http://localhost:5173"


async def test_frontend_origin_is_allowed(client):
    response = await client.get("/health", headers={"Origin": FRONTEND})

    allowed = response.headers.get("access-control-allow-origin")
    assert allowed == FRONTEND


async def test_other_origins_are_not_allowed(client):
    response = await client.get(
        "/health",
        headers={"Origin": "http://unknown.example"},
    )

    assert "access-control-allow-origin" not in response.headers
