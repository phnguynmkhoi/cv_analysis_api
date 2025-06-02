from datetime import date
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    ForeignKey,
    Text,
    VARCHAR,
)
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Single Base for all ORM models."""
    pass


class Person(Base):
    __tablename__ = "person"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    email: Mapped[str] = mapped_column(CITEXT(), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(VARCHAR(20))
    summary: Mapped[Optional[str]] = mapped_column(Text)

    # relationships
    educations: Mapped[List["Education"]] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
    )
    resume_files: Mapped[List["ResumeFile"]] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
    )

    # optional helper
    def __repr__(self) -> str:  # pragma: no cover
        return f"<Person(id={self.id}, email={self.email!r})>"


class Education(Base):
    __tablename__ = "education"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("person.id", ondelete="CASCADE"), nullable=False
    )
    institution: Mapped[str] = mapped_column(Text, nullable=False)
    degree: Mapped[Optional[str]] = mapped_column(VARCHAR(100))
    field: Mapped[Optional[str]] = mapped_column(VARCHAR(255))
    start_date: Mapped[Optional[date]]
    end_date: Mapped[Optional[date]]

    person: Mapped["Person"] = relationship(back_populates="educations")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Education(id={self.id}, institution={self.institution!r})>"


class ResumeFile(Base):
    __tablename__ = "resume_file"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("person.id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[Optional[str]] = mapped_column(Text)
    sha256: Mapped[Optional[str]] = mapped_column(VARCHAR(64))
    storage_url: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        VARCHAR(12),
        nullable=False,
        default="QUEUED",
    )

    person: Mapped["Person"] = relationship(back_populates="resume_files")

    __table_args__ = (
        CheckConstraint(
            "status IN ('QUEUED','SUCCESS','ERROR')",
            name="chk_resume_status",
        ),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ResumeFile(id={self.id}, status={self.status})>"
