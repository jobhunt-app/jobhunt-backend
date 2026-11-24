from datetime import date, datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ApplicationStatus(StrEnum):
    new = "new"
    saved = "saved"
    applied = "applied"
    interview = "interview"
    rejected = "rejected"
    not_relevant = "not_relevant"
    expired = "expired"


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    settings: Mapped[dict[str, Any]] = mapped_column(JSONB)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(unique=True)
    source: Mapped[str] = mapped_column(index=True)
    title: Mapped[str]
    company: Mapped[str | None]
    location: Mapped[str | None]
    location_bucket: Mapped[str] = mapped_column(index=True)
    posted_at: Mapped[date | None] = mapped_column(index=True)
    description: Mapped[str | None]
    salary: Mapped[str | None]
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class JobMatch(Base):
    __tablename__ = "job_matches"
    __table_args__ = (UniqueConstraint("job_id", "profile_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"))
    score: Mapped[float]
    matched: Mapped[str | None]
    open_to_you: Mapped[str]


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("job_id", "profile_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), index=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, native_enum=False, create_constraint=True), index=True
    )
    notes: Mapped[str | None]
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
