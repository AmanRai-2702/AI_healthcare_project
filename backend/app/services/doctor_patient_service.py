from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.doctor_patient import DoctorPatient
from app.models.patient import Patient


def create_access_request(
    db: Session,
    doctor_id: UUID,
    patient_id: UUID,
) -> DoctorPatient:

    patient = db.get(Patient, patient_id)

    if patient is None:
        raise ValueError("Patient not found.")

    existing = db.scalar(
        select(DoctorPatient).where(
            DoctorPatient.doctor_id == doctor_id,
            DoctorPatient.patient_id == patient_id,
        )
    )

    if existing:
        if existing.status != "revoked":
            raise ValueError(
                "An active or pending relationship already exists."
            )

        # Allow a new request after a previous relationship was revoked.
        existing.status = "pending"
        existing.granted_at = None
        relationship = existing

    else:
        relationship = DoctorPatient(
            doctor_id=doctor_id,
            patient_id=patient_id,
            status="pending",
        )
        db.add(relationship)

    try:
        db.commit()
        db.refresh(relationship)
        return relationship
    except Exception:
        db.rollback()
        raise


def update_relationship_status(
    db: Session,
    relationship_id: UUID,
    patient_id: UUID,
    new_status: str,
) -> DoctorPatient:

    relationship = db.scalar(
        select(DoctorPatient).where(
            DoctorPatient.id == relationship_id,
            DoctorPatient.patient_id == patient_id,
        )
    )

    if relationship is None:
        raise ValueError("Relationship not found.")

    if relationship.status == "revoked":
        raise ValueError("This relationship has already been revoked.")

    if new_status not in ("active", "revoked"):
        raise ValueError("Invalid relationship status.")

    relationship.status = new_status

    if new_status == "active":
        relationship.granted_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(relationship)
        return relationship
    except Exception:
        db.rollback()
        raise


def get_patient_relationships(
    db: Session,
    patient_id: UUID,
) -> list[DoctorPatient]:

    return list(
        db.scalars(
            select(DoctorPatient)
            .where(DoctorPatient.patient_id == patient_id)
            .order_by(DoctorPatient.created_at.desc())
        ).all()
    )


def get_doctor_relationships(
    db: Session,
    doctor_id: UUID,
) -> list[DoctorPatient]:

    return list(
        db.scalars(
            select(DoctorPatient)
            .where(DoctorPatient.doctor_id == doctor_id)
            .order_by(DoctorPatient.created_at.desc())
        ).all()
    )