from datetime import date

from sqlalchemy import select

from app.models import Application


async def test_new_application_defaults_to_applied(session):
    application = Application(
        company="Acme",
        role="Junior Developer",
        applied_on=date(2026, 10, 1),
    )
    session.add(application)
    await session.commit()

    result = await session.scalars(select(Application))
    saved = result.one()

    assert saved.id is not None
    assert saved.company == "Acme"
    assert saved.status == "applied"
