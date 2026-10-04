"""Phase 2 model tests.

In async SQLAlchemy, related objects are never loaded behind your back.
`selectinload(...)` asks for them explicitly, in the same query. See
guide/03-companies.md, "Loading related objects in async code".
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Application, Company


async def test_new_application_defaults_to_applied(session):
    acme = Company(name="Acme")
    session.add(
        Application(
            company=acme,
            role="Junior Developer",
            applied_on=date(2026, 10, 1),
        )
    )
    await session.commit()

    result = await session.scalars(select(Application))
    saved = result.one()

    assert saved.id is not None
    assert saved.status == "applied"


async def test_a_company_has_many_applications(session):
    acme = Company(name="Acme")
    acme.applications = [
        Application(role="Junior Developer", applied_on=date(2026, 10, 1)),
        Application(role="QA Analyst", applied_on=date(2026, 10, 2)),
    ]
    session.add(acme)
    await session.commit()
    session.expunge_all()

    result = await session.scalars(
        select(Company).options(selectinload(Company.applications))
    )
    saved = result.one()

    roles = {application.role for application in saved.applications}
    assert roles == {"Junior Developer", "QA Analyst"}


async def test_an_application_loads_its_company(session):
    session.add(
        Application(
            company=Company(name="Acme"),
            role="Junior Developer",
            applied_on=date(2026, 10, 1),
        )
    )
    await session.commit()
    session.expunge_all()

    result = await session.scalars(select(Application))
    saved = result.one()

    assert saved.company.name == "Acme"
    assert saved.company_id == saved.company.id
