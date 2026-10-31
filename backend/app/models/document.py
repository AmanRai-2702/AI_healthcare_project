
import uuid
from datetime import datetime, date

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    __table_args__ = (
        CheckConstraint(
            "document_type IN "
            "('prescription', 'lab_report', 'medical_report', "
            "'chest_xray', 'other')",
            name="ck_documents_valid_type",
        ),
        CheckConstraint(
            "processing_status IN "
            "('uploaded', 'pending', 'processing', "
            "'completed', 'failed')",
            name="ck_documents_valid_status",
        ),
        CheckConstraint(
            "file_size_bytes > 0",
            name="ck_documents_positive_file_size",
        ),
        UniqueConstraint(
            "storage_provider",
            "storage_file_id",
            name="uq_document_storage_file",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    document_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    # Identifies the storage backend, currently Google Drive.
    storage_provider: Mapped[str] = mapped_column(
        String(40),
        default="google_drive",
        nullable=False,
    )

    # Google Drive file ID; populated after successful upload.
    storage_file_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # SHA-256 checksum for integrity verification.
    file_checksum: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    processing_status: Mapped[str] = mapped_column(
        String(30),
        default="uploaded",
        nullable=False,
    )

    clinical_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    patient: Mapped["Patient"] = relationship(
        back_populates="documents",
    )

    uploader: Mapped["User"] = relationship(
        back_populates="uploaded_documents",
    )
    
    analyses: Mapped[list["Analysis"]] = relationship(
    back_populates="document",
    cascade="all, delete-orphan",
    )
