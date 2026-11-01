from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_patient
from app.db.session import get_db
from app.models.patient import Patient
from app.schemas.patient import PatientResponse, PatientUpdate


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@router.get("/me", response_model=PatientResponse)
def get_my_patient_profile(
    current_patient: Patient = Depends(get_current_patient),
):
    return current_patient


@router.put("/me", response_model=PatientResponse)
def update_my_patient_profile(
    patient_data: PatientUpdate,
    current_patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    update_data = patient_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_patient, field, value)

    try:
        db.commit()
        db.refresh(current_patient)
        return current_patient

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to update patient profile.",
        )