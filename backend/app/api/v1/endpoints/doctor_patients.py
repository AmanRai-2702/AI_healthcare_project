from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_doctor, get_current_patient
from app.db.session import get_db
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.schemas.doctor_patient import (
    DoctorPatientRequest,
    DoctorPatientStatusUpdate,
    DoctorPatientResponse,
    DoctorPatientListResponse,
)
from app.services.doctor_patient_service import (
    create_access_request,
    update_relationship_status,
    get_patient_relationships,
    get_doctor_relationships,
)

router = APIRouter(tags=["Doctor-Patient Relationships"])


@router.post(
    "/doctors/me/patient-requests",
    response_model=DoctorPatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def request_patient_access(
    request: DoctorPatientRequest,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    try:
        return create_access_request(
            db, current_doctor.id, request.patient_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get(
    "/patients/me/doctor-requests",
    response_model=DoctorPatientListResponse,
)
def list_patient_requests(
    current_patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    relationships = get_patient_relationships(db, current_patient.id)
    return {
        "total": len(relationships),
        "relationships": relationships,
    }


@router.put(
    "/patients/me/doctor-requests/{relationship_id}",
    response_model=DoctorPatientResponse,
)
def respond_to_doctor_request(
    relationship_id: UUID,
    update: DoctorPatientStatusUpdate,
    current_patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    try:
        return update_relationship_status(
            db,
            relationship_id,
            current_patient.id,
            update.status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get(
    "/doctors/me/patients",
    response_model=DoctorPatientListResponse,
)
def list_doctor_patients(
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    relationships = get_doctor_relationships(db, current_doctor.id)
    return {
        "total": len(relationships),
        "relationships": relationships,
    }