"""The database rules from #8, checked against a real Postgres."""

from datetime import date

import pytest
from sqlalchemy import delete, func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Application,
    ApplicationStatus,
    Cv,
    CvKind,
    Job,
    JobMatch,
    Profile,
    StatusHistory,
    StatusSource,
)


@pytest.fixture
async def profile(session: AsyncSession) -> Profile:
    p = Profile(name="Tigran", settings={"keywords": ["ai", "react"]})
    session.add(p)
    await session.flush()  # sends the INSERT, so p.id is filled in
    return p


@pytest.fixture
async def job(session: AsyncSession) -> Job:
    j = Job(
        url="https://example.com/jobs/1",
        source="Ashby",
        title="AI Engineer",
        location_bucket="Remote",
    )
    session.add(j)
    await session.flush()
    return j


async def test_job_gets_defaults_from_postgres(session: AsyncSession, job: Job) -> None:
    await session.refresh(job)  # reload the row to see what Postgres filled in
    assert job.id is not None
    assert job.first_seen is not None
    assert job.first_seen == job.last_seen
    assert job.company is None
    assert job.posted_at is None


async def test_profile_settings_round_trip_as_json(session: AsyncSession, profile: Profile) -> None:
    loaded = await session.scalar(select(Profile.settings).where(Profile.id == profile.id))
    assert loaded == {"keywords": ["ai", "react"]}


async def test_duplicate_job_url_is_rejected(session: AsyncSession, job: Job) -> None:
    session.add(
        Job(url=job.url, source="LinkedIn", title="Same job again", location_bucket="Remote")
    )
    with pytest.raises(IntegrityError, match="jobs_url_key"):
        await session.flush()


async def test_one_match_per_job_and_profile(
    session: AsyncSession, job: Job, profile: Profile
) -> None:
    session.add(JobMatch(job_id=job.id, profile_id=profile.id, score=17.0, open_to_you="yes"))
    await session.flush()

    session.add(JobMatch(job_id=job.id, profile_id=profile.id, score=3.0, open_to_you="yes"))
    with pytest.raises(IntegrityError, match="job_matches_job_id_profile_id_key"):
        await session.flush()


async def test_match_needs_an_existing_job(session: AsyncSession, profile: Profile) -> None:
    session.add(JobMatch(job_id=999_999, profile_id=profile.id, score=1.0, open_to_you="yes"))
    with pytest.raises(IntegrityError, match="job_matches_job_id_fkey"):
        await session.flush()


async def test_deleting_a_job_cascades_to_its_matches(
    session: AsyncSession, job: Job, profile: Profile
) -> None:
    session.add(JobMatch(job_id=job.id, profile_id=profile.id, score=17.0, open_to_you="yes"))
    await session.flush()

    await session.execute(delete(Job).where(Job.id == job.id))

    assert await session.scalar(select(func.count()).select_from(JobMatch)) == 0


async def test_deleting_a_job_with_an_application_is_refused(
    session: AsyncSession, job: Job, profile: Profile
) -> None:
    session.add(Application(job_id=job.id, profile_id=profile.id, status=ApplicationStatus.applied))
    await session.flush()

    with pytest.raises(IntegrityError, match="applications_job_id_fkey"):
        await session.execute(delete(Job).where(Job.id == job.id))


async def test_unknown_status_is_rejected_by_the_database(
    session: AsyncSession, job: Job, profile: Profile
) -> None:
    # Raw SQL on purpose: mypy would stop a typo in Python code, this proves
    # the database also refuses it (e.g. a script or psql writing directly).
    with pytest.raises(IntegrityError, match="applicationstatus"):
        await session.execute(
            text("INSERT INTO applications (job_id, profile_id, status) VALUES (:j, :p, 'aplied')"),
            {"j": job.id, "p": profile.id},
        )


async def test_status_history_first_entry_has_no_from_status(
    session: AsyncSession, job: Job, profile: Profile
) -> None:
    application = Application(job_id=job.id, profile_id=profile.id, status=ApplicationStatus.saved)
    session.add(application)
    await session.flush()

    entry = StatusHistory(
        application_id=application.id,
        from_status=None,
        to_status=ApplicationStatus.saved,
        source=StatusSource.user,
    )
    session.add(entry)
    await session.flush()
    await session.refresh(entry)

    assert entry.at is not None
    assert entry.from_status is None


async def test_master_cv_without_job_is_accepted(session: AsyncSession, profile: Profile) -> None:
    session.add(Cv(profile_id=profile.id, kind=CvKind.master, data={"name": "Tigran"}))
    await session.flush()


@pytest.mark.parametrize(
    ("kind", "with_job"),
    [(CvKind.master, True), (CvKind.tailored, False)],
    ids=["master-with-job", "tailored-without-job"],
)
async def test_cv_kind_and_job_must_agree(
    session: AsyncSession, profile: Profile, job: Job, kind: CvKind, with_job: bool
) -> None:
    session.add(Cv(profile_id=profile.id, kind=kind, job_id=job.id if with_job else None, data={}))
    with pytest.raises(IntegrityError, match="tailored_has_job"):
        await session.flush()


async def test_pgvector_extension_is_enabled(session: AsyncSession) -> None:
    result = await session.scalar(text("SELECT '[1,2,3]'::vector::text"))
    assert result == "[1,2,3]"


async def test_posted_at_stores_a_date(session: AsyncSession, job: Job) -> None:
    job.posted_at = date(2026, 11, 1)
    await session.flush()
    stored = await session.scalar(select(Job.posted_at).where(Job.id == job.id))
    assert stored == date(2026, 11, 1)
