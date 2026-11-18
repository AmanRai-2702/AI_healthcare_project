from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_doctor
from app.db.session import get_db
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorResponse, DoctorUpdate


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"],
)


@router.get("/me", response_model=DoctorResponse)
def get_my_doctor_profile(
    current_doctor: Doctor = Depends(get_current_doctor),
):
    return current_doctor


@router.put("/me", response_model=DoctorResponse)
def update_my_doctor_profile(
    doctor_data: DoctorUpdate,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    update_data = doctor_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_doctor, field, value)

    try:
        db.commit()
        db.refresh(current_doctor)
        return current_doctor

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to update doctor profile.",
        )