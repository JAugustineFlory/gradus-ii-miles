from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base, get_db


async def test_get_db_yields_a_session_and_closes_it():
    generator = get_db()

    db = await anext(generator)

    assert isinstance(db, AsyncSession)
    await generator.aclose()


def test_constraints_follow_a_naming_convention():
    convention = Base.metadata.naming_convention

    assert "fk" in convention
    assert "uq" in convention
    assert "pk" in convention
