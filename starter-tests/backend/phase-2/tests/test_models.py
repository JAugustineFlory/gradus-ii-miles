from datetime import date

from sqlalchemy import select

from app.models import Application, Company


def test_new_application_defaults_to_applied(session):
    acme = Company(name="Acme")
    session.add(
        Application(
            company=acme,
            role="Junior Developer",
            applied_on=date(2026, 10, 1),
        )
    )
    session.commit()

    saved = session.scalars(select(Application)).one()

    assert saved.id is not None
    assert saved.status == "applied"


def test_a_company_has_many_applications(session):
    acme = Company(name="Acme")
    acme.applications = [
        Application(role="Junior Developer", applied_on=date(2026, 10, 1)),
        Application(role="QA Analyst", applied_on=date(2026, 10, 2)),
    ]
    session.add(acme)
    session.commit()

    saved = session.scalars(select(Company)).one()

    roles = {application.role for application in saved.applications}
    assert roles == {"Junior Developer", "QA Analyst"}


def test_an_application_knows_its_company(session):
    acme = Company(name="Acme")
    session.add(
        Application(
            company=acme,
            role="Junior Developer",
            applied_on=date(2026, 10, 1),
        )
    )
    session.commit()

    saved = session.scalars(select(Application)).one()

    assert saved.company.name == "Acme"
    assert saved.company_id == saved.company.id
